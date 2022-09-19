from typing import Tuple
from pathlib import Path
from io import TextIOWrapper
from ruamel.yaml import YAML
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from extras.models import CustomField
from .exceptions import *


class BaseInitializer:
    """
    Abstract initializer class to facilitate importing of netbox assets/records
    """
    _updates_allowed = False

    def __init__(self, data_file_path: str) -> None:
        self.data_file_path = data_file_path

    @property.getter
    def data_file_name(self) -> str:
        raise NotImplementedError(f"BaseInitializer derived classes must implement data_file_name property")

    @property.getter
    def nb_model(self) -> type:
        raise NotImplementedError(f"BaseInitializer derived classes must implement nb_model property to "
                                  f"yield its Netbox model class")

    @property.getter
    def name(self) -> str:
        raise NotImplementedError(f"BaseInitializer derived classes must implement name property to return "
                                  f"its human readable name")

    @property.getter
    def icon(self):
        raise NotImplementedError(f"BaseInitializer derived classes must implement icon property to return "
                                  f"its icon character")

    @property.getter
    def required_associations(self) -> dict[str, (type, str)]:
        """override if required associations exist - ex. {"local_field": (Model, "model_field")}"""
        return {}

    @property.getter
    def optional_associations(self) -> dict[str, (type, str)]:
        """override if optional associations exist - ex. {"local_field": (Model, "model_field")}"""
        return {}

    @property.getter
    def ignored_params(self) -> list[str]:
        """override if ignored parameters exist"""
        return []

    @property.getter
    def unique_params(self) -> list[str]:
        """override if unique fields different from below"""
        return ["name", "slug"]

    @classmethod
    def set_updates_allowed(cls):
        cls._updates_allowed = True

    @classmethod
    def updates_allowed(cls) -> bool:
        return cls._updates_allowed

    def load_data(self):
        with self.open_yaml() as yaml_file:
            yaml = self.parse_yaml(yaml_file)

        for params in yaml:
            try:
                self.pre_process_params(params)
            except SurvivableError as se:
                print(se)
                continue
            except ImportNotNeeded:
                continue

            custom_field_data = self.pop_custom_fields(params)
            for ignored_param in self.ignored_params:
                params.pop(ignored_param, None)

            self.process_required_associations(params)

            self.process_optional_associations(params)

            matching_params, defaults = self.split_params(params, self.matching_params)

            instance, created = self.nb_model.objects.get_or_create(
                **matching_params, defaults=defaults
            )
            instance_name = getattr(instance, next(iter(matching_params.keys())))
            if created:
                print(f"{self.icon}  Created {self.name}", instance_name)

            updated = self.set_custom_fields_values(instance, custom_field_data)

            if not created and self.__class__.updates_allowed():
                # if existing record and updates are allowed..
                self.process_updates(instance, params, instance_name)
                # if new record or updates not allowed for this class, we're done.
            return instance, created

    def open_yaml(self, data_file_name=None) -> TextIOWrapper:
        if data_file_name:
            yf = Path(f"{self.data_file_path}/{data_file_name}")
        else:
            yf = Path(f"{self.data_file_path}/{self.data_file_name}")
        if not yf.is_file():
            return None
        return yf.open("r")

    def parse_yaml(self, stream, name=None) -> list[dict[str, str]]:
        yaml = YAML(typ="safe")
        objects = yaml.load(stream)
        if isinstance(objects, dict):
            # if yaml is dict format, we convert it to a list to be robust
            as_list = []
            unique_key = next(iter(self.unique_params))
            for key, params in objects.items():
                params[unique_key] = key
                as_list.append(params)
            return as_list
        elif isinstance(objects, list):
            return objects
        else:
            name = name or self.data_file_name
            raise InvalidYamlError(f"Invalid yaml in {name} - type is {type(objects)}")

    def pre_process_params(self, params):
        pass

    def process_required_associations(self, params):
        for assoc, details in self.required_associations.items():
            model, field = details
            query = {field: params.pop(assoc)}
            params[assoc] = model.objects.get(**query)

    def process_optional_associations(self, params):
        for assoc, details in self.optional_associations.items():
            if assoc in params:
                model, field = details
                query = {field: params.pop(assoc)}
                params[assoc] = model.objects.get(**query)

    def process_updates(self, instance, params, instance_name):
        for k, v in params.items():
            if v != getattr(instance, k):
                updated = True
                setattr(instance, k, v)
        if updated:
            print(f"{self.icon}  Updated {self.name}", instance_name)
            instance.save()

    def pop_custom_fields(self, params):
        if "custom_field_data" in params:
            return params.pop("custom_field_data")
        elif "custom_fields" in params:
            print("⚠️ Please rename 'custom_fields' to 'custom_field_data'!")
            return params.pop("custom_fields")

        return None

    def validate_custom_field(self, entity, key):
        try:
            cf = CustomField.objects.get(name=key)
            ct = ContentType.objects.get_for_model(entity)
            if ct not in cf.content_types.all():
                raise CustomFieldNotEnabledError(key)
        except ObjectDoesNotExist:
            raise CustomFieldMissingError(key)

    def set_custom_fields_values(self, entity, custom_field_data):
        if not custom_field_data:
            return

        missing_cfs = []
        disabled_cfs = []
        save = False
        for key, value in custom_field_data.items():
            value = value.strip('"\'')  # needed for quoted json etc
            try:
                self.validate_custom_field(entity, key)

                if key not in entity.custom_field_data or \
                   self._updates_allowed and entity.custom_field_data[key] != value:
                    entity.custom_field_data[key] = value
                    save = True

            except CustomFieldMissingError:
                missing_cfs.append(key)
            except CustomFieldNotEnabledError:
                disabled_cfs.append(key)

        if missing_cfs:
            raise Exception(
                f"⚠️ Custom field(s) '{missing_cfs}' requested for {entity} but not found in Netbox!"
                "Please check the custom_fields.yml"
            )
        elif disabled_cfs:
            raise Exception(
                f"⚠️ Custom field(s) '{disabled_cfs}' are not enabled for {entity}'s model!"
                "Please check the 'on_objects' for that custom field in custom_fields.yml"
            )

        if save:
            entity.save()

        return save

    def split_params(self, params: dict, unique_params: list = None) -> Tuple[dict, dict]:
        """Split params dict into dict with matching params and a dict with default values"""
        if not isinstance(params, dict):
            raise AttributeError(f"params: {params} is not a dict?")
        if unique_params is None:
            unique_params = self.unique_params

        matching_params = {}
        for unique_param in unique_params:
            param = params.pop(unique_param, None)
            if param:
                matching_params[unique_param] = param
        return matching_params, params

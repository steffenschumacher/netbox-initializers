
class InitializerConfig:
    _updatable_classes = None

    @classmethod
    def is_updatable(cls, nb_cls_name: str):
        """
        Checks if the Netbox model class name is configured for updates
        """
        if cls._updatable_classes is None:
            from django.conf import settings
            from ... import NetBoxInitializersConfig
            plugin_config = settings.PLUGINS_CONFIG.get(NetBoxInitializersConfig.name)
            if plugin_config and isinstance(plugin_config, dict):
                value = plugin_config.get('updatable_objects')
                if value == "all":
                    cls._updatable_classes = value
                elif isinstance(value, list):
                    cls._updatable_classes = [clz.lower().strip() for clz in value]
                else:
                    cls._updatable_classes = []
            else:
                cls._updatable_classes = []
        if cls._updatable_classes == "all":
            return True
        return nb_cls_name.lower() in cls._updatable_classes


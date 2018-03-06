import importlib


class Importer():

    @staticmethod
    def get_class(class_path):
        """Get a class by its path."""
        module_parts = class_path.split('.')
        module_name = ".".join(module_parts[:-1])
        module = importlib.import_module(module_name)

        return module.__dict__[module_parts[-1:][0]]

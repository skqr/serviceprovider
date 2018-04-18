import importlib


class Importer():

    @classmethod
    def get_func(cls, func_path):
        """Get a function by its path."""
        return cls.get_class(func_path)

    @staticmethod
    def get_class(class_path):
        """Get a class by its path."""
        module_parts = class_path.split('.')
        module_name = ".".join(module_parts[:-1])
        module = importlib.import_module(module_name)

        return module.__dict__[module_parts[-1:][0]]

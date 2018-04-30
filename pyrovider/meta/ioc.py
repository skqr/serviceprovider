import importlib


class Importer():

    @staticmethod
    def get_obj(obj_path):
        """Get an object by its path."""
        module_parts = obj_path.split('.')
        module_name = ".".join(module_parts[:-1])
        module = importlib.import_module(module_name)

        return module.__dict__[module_parts[-1:][0]]

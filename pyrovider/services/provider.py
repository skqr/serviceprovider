import os

from dotenv import find_dotenv, load_dotenv
from pyrovider.meta.construction import Singleton
from pyrovider.meta.ioc import Importer
from pyrovider.tools.dicttools import dictpath

# Loads env vars from .env file
load_dotenv(find_dotenv())


class ServiceProviderError(Exception):

    pass


class UnknownServiceError(ServiceProviderError):

    pass


class TooManyCreationMethodsError(ServiceProviderError):

    pass


class NoCreationMethodError(ServiceProviderError):

    pass


class NotAServiceFactoryError(ServiceProviderError):

    pass


class BadConfPathError(ServiceProviderError):

    pass


class ServiceFactory():

    def build(self):
        raise NotImplementedError()


# class ServiceProvider():
class ServiceProvider(metaclass=Singleton):

    UNKNOWN_SERVICE_ERRMSG = '"{}" is not a service we know of.'
    TOO_MANY_CREATION_METHODS_ERRMSG = 'You must define either a class or a factory for the service "{}", not both.'
    NO_CREATION_METHOD_ERRMSG = 'You must define either a class or a factory for the service "{}", none was found.'
    NOT_A_SERVICE_FACTORY_ERRMSG = 'The factory class for the service "{}" does not have a "build" method.'
    BAD_CONF_PATH_ERRMSG = 'The path "{}" was not found in the app configuration.'

    def __init__(self):
        self.importer = Importer()  # Can't inject it, obviously.
        self.service_conf = {}
        self.app_conf = {}
        self.service_classes = {}
        self.factory_classes = {}
        self.set_services = {}

    def reset(self):
        self.service_classes = {}
        self.factory_classes = {}

    def conf(self, service_conf: dict, app_conf: dict = None):
        if app_conf is None:
            app_conf = {}

        self.service_conf = service_conf
        self.app_conf = app_conf

    def get(self, name: str):
        if name not in self.service_conf:
            raise UnknownServiceError(self.UNKNOWN_SERVICE_ERRMSG.format(name))

        return self._get_set_service(name) or self._get_built_service(name)

    def _get_set_service(self, name: str):
        if name in self.set_services:
            return self.set_services[name]

    def _get_built_service(self, name: str):
        if self.service_conf[name] and all(k in self.service_conf[name] for k in ('class', 'factory')):
            raise TooManyCreationMethodsError(self.TOO_MANY_CREATION_METHODS_ERRMSG.format(name))

        if self.service_conf[name] and 'class' in self.service_conf[name]:
            return self._instance_service_with_class(name)
        elif self.service_conf[name] and 'factory' in self.service_conf[name]:
            return self._instance_service_with_factory(name)
        else:
            raise NoCreationMethodError(self.NO_CREATION_METHOD_ERRMSG.format(name))

    def set(self, name, service):
        if name not in self.service_conf:
            raise UnknownServiceError(self.UNKNOWN_SERVICE_ERRMSG.format(name))

        self.set_services[name] = service

    def _instance_service_with_class(self, name: str):
        if name not in self.service_classes:
            self.service_classes[name] = self.importer.get_class(self.service_conf[name]['class'])

        return self.service_classes[name](*self._get_args(name))

    def _instance_service_with_factory(self, name: str):
        if name not in self.factory_classes:
            factory_class = self.importer.get_class(self.service_conf[name]['factory'])

            if not hasattr(factory_class, 'build') or not callable(factory_class.build):
                raise NotAServiceFactoryError(self.NOT_A_SERVICE_FACTORY_ERRMSG.format(name))

            self.factory_classes[name] = factory_class

        return self.factory_classes[name](*self._get_args(name)).build()

    def _get_args(self, name: str):
        if 'arguments' in self.service_conf[name]:
            return [self._get_arg(ref) for ref in self.service_conf[name]['arguments']]
        else:
            return []

    def _get_arg(self, ref: any):
        if isinstance(ref, str):
            if '@' == ref[0]:
                return self.get(ref[1:])
            elif '%' == ref[0] == ref[-1:]:
                return self._get_conf(ref[1:-1])
            elif '$' == ref[0]:
                return self._get_env(ref[1:])
        elif isinstance(ref, list):
            if '$' == ref[0][0]:
                return self._get_env(ref[0][1:], ref[1])

        return ref  # Literal

    def _get_conf(self, path: str):
        parts = path.split('.')

        try:
            trunk = self.app_conf[parts[0]]
        except KeyError as e:
            raise BadConfPathError(self.BAD_CONF_PATH_ERRMSG.format(parts[0]))

        try:
            return dictpath(trunk, parts[1:])
        except KeyError as e:
            raise BadConfPathError(self.BAD_CONF_PATH_ERRMSG.format(e.args[0]))

    def _get_env(self, var: str, default: any = None):
        default = self._get_arg(default)

        return os.environ.get(var, default)

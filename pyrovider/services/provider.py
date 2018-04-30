import os

from dotenv import find_dotenv, load_dotenv
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


class ServiceProvider():

    UNKNOWN_SERVICE_ERRMSG = '"{}" is not a service we know of.'
    TOO_MANY_CREATION_METHODS_ERRMSG = 'You must define either a class or a factory for the service "{}", not both.'
    NO_CREATION_METHOD_ERRMSG = 'You must define either a class or a factory for the service "{}", none was found.'
    NOT_A_SERVICE_FACTORY_ERRMSG = 'The factory class for the service "{}" does not have a "build" method.'
    BAD_CONF_PATH_ERRMSG = 'The path "{}" was not found in the app configuration.'

    _service_meths = {'function': '_get_service_func',
                      'class': '_instance_service_with_class',
                      'factory': '_instance_service_with_factory'}

    def __init__(self):
        self.importer = Importer()  # Can't inject it, obviously.
        self.service_conf = {}
        self.app_conf = {}
        self.set_services = {}
        self.service_funcs = {}
        self.service_classes = {}
        self.factory_classes = {}

    def conf(self, service_conf, app_conf=None):
        if app_conf is None:
            app_conf = {}

        self.service_conf = service_conf
        self.app_conf = app_conf

    def get(self, name):
        if name not in self.service_conf:
            raise UnknownServiceError(self.UNKNOWN_SERVICE_ERRMSG.format(name))

        return self._get_set_service(name) or self._get_built_service(name)

    def _get_set_service(self, name):
        if name in self.set_services:
            return self.set_services[name]

    def _get_built_service(self, name):
        if self.service_conf[name] and self._has_multiple_creation_methods(name):
            raise TooManyCreationMethodsError(self.TOO_MANY_CREATION_METHODS_ERRMSG.format(name))

        for service_type, method in self._service_meths.iteritems():
            if self.service_conf[name] and service_type in self.service_conf[name]:
                return getattr(self, method)(name)
        else:
            raise NoCreationMethodError(self.NO_CREATION_METHOD_ERRMSG.format(name))

    def set(self, name, service):
        if name not in self.service_conf:
            raise UnknownServiceError(self.UNKNOWN_SERVICE_ERRMSG.format(name))

        self.set_services[name] = service

    def _has_multiple_creation_methods(self, name):
        if not self.service_conf[name]:
            raise NoCreationMethodError(self.NO_CREATION_METHOD_ERRMSG.format(name))

        return 1 < len([k for k in self._service_meths.keys() if k in self.service_conf[name]])

    def _get_service_func(self, name):
        if name not in self.service_funcs:
            self.service_funcs[name] = self.importer.get_func(self.service_conf[name]['function'])

        return self.service_funcs[name]

    def _instance_service_with_class(self, name):
        if name not in self.service_classes:
            self.service_classes[name] = self.importer.get_class(self.service_conf[name]['class'])

        return self.service_classes[name](*self._get_args(name))

    def _instance_service_with_factory(self, name):
        if name not in self.factory_classes:
            factory_class = self.importer.get_class(self.service_conf[name]['factory'])

            if not hasattr(factory_class, 'build') or not callable(factory_class.build):
                raise NotAServiceFactoryError(self.NOT_A_SERVICE_FACTORY_ERRMSG.format(name))

            self.factory_classes[name] = factory_class

        return self.factory_classes[name](*self._get_args(name)).build()

    def _get_args(self, name):
        if 'arguments' in self.service_conf[name]:
            return [self._get_arg(ref) for ref in self.service_conf[name]['arguments']]
        else:
            return []

    def _get_arg(self, ref):
        if isinstance(ref, str):
            if '@' == ref[0]:
                return self.get(ref[1:])
            elif '%' == ref[0] == ref[-1:]:
                return self._get_conf(ref[1:-1])
            elif '$' == ref[0]:
                return self._get_env(ref[1:-1])
        elif isinstance(ref, list):
            if '$' == ref[0][0]:
                return self._get_env(ref[0][1:], ref[1])

        return ref  # Literal

    def _get_conf(self, path):
        parts = path.split('.')

        try:
            trunk = self.app_conf[parts[0]]
        except KeyError as e:
            raise BadConfPathError(self.BAD_CONF_PATH_ERRMSG.format(parts[0]))

        try:
            return dictpath(trunk, parts[1:])
        except KeyError as e:
            raise BadConfPathError(self.BAD_CONF_PATH_ERRMSG.format(e.args[0]))

    def _get_env(self, var, default=None):
        default = self._get_arg(default)

        return os.environ.get(var, default)

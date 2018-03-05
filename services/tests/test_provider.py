import unittest

import yaml
from services.provider import (NoCreationMethodError, NotAServiceFactoryError,
                               ServiceFactory, ServiceProvider,
                               TooManyCreationMethodsError,
                               UnknownServiceError, BadConfPathError)


class ModelSchemataTest(unittest.TestCase):

    maxDiff = None
    service_conf_path = 'services/tests/test_provider/service_conf.yaml'
    app_conf_path = 'services/tests/test_provider/app_conf.yaml'

    def setUp(self):
        # Given...
        self.provider = ServiceProvider()
        with open(self.service_conf_path, 'r') as fp:
            self.service_conf = yaml.load(fp.read())
        with open(self.app_conf_path, 'r') as fp:
            self.app_conf = yaml.load(fp.read())
        self.provider.conf(self.service_conf, self.app_conf)

    def test_getting_a_service_with_a_service_dependency(self):
        # When...
        service_b = self.provider.get('service-b')
        # Then...
        self.assertIsInstance(service_b.service_a, MockServiceA)

    def test_getting_a_service_with_a_config_dependency(self):
        # When...
        service_b = self.provider.get('service-b')
        # Then...
        self.assertEqual({'version': '1',
                          'url': "https://api.some-app.com/v1/"},
                         service_b.some_configuration)

    def test_getting_a_service_with_an_env_var_dependency(self):
        # When...
        import os
        os.environ['SOME_ENV_VAR'] = 'Not the default value.'
        service_b = self.provider.get('service-b')
        del os.environ['SOME_ENV_VAR']
        # Then...
        self.assertEqual('Not the default value.', service_b.some_env_var)

    def test_getting_a_service_with_an_env_var_dependency_with_a_literal_default(self):
        # When...
        service_b = self.provider.get('service-b')
        # Then...
        self.assertEqual('Some default value.', service_b.some_env_var)

    def test_getting_a_service_with_an_env_var_dependency_with_a_config_default(self):
        # When...
        service_b = self.provider.get('service-b')
        # Then...
        self.assertEqual("https://api.some-app.com/v1/", service_b.other_env_var)

    def test_getting_a_service_with_a_literal_dependency(self):
        # When...
        service_b = self.provider.get('service-b')
        # Then...
        self.assertEqual('A literal value.', service_b.some_literal_value)

    def test_getting_a_service_with_a_factory(self):
        # When...
        service_c = self.provider.get('service-c')
        # Then...
        self.assertIsInstance(service_c.service_b, MockServiceB)

    def test_getting_unknown_service(self):
        with self.assertRaises(UnknownServiceError) as context:
            self.provider.get('service-unknown')
        self.assertEqual('"service-unknown" is not a service we know of.',
                         str(context.exception))

    def test_getting_no_creation_methods(self):
        with self.assertRaises(NoCreationMethodError) as context:
            self.provider.get('service-d')
        self.assertEqual('You must define either a class or a factory for the service "service-d", none was found.',
                         str(context.exception))

    def test_getting_too_many_creation_methods(self):
        with self.assertRaises(TooManyCreationMethodsError) as context:
            self.provider.get('service-e')
        self.assertEqual('You must define either a class or a factory for the service "service-e", not both.',
                         str(context.exception))

    def test_getting_not_a_service_factory(self):
        with self.assertRaises(NotAServiceFactoryError) as context:
            self.provider.get('service-f')
        self.assertEqual('The factory class for the service "service-f" does not have a "build" method.',
                         str(context.exception))

    def test_getting_a_service_with_broken_dependencies(self):
        # When...
        self.provider = ServiceProvider()
        self.provider.conf(self.service_conf)
        with self.assertRaises(BadConfPathError) as context:
            self.provider.get('service-b')
        # Then...
        self.assertEqual('The path "some_app" was not found in the app configuration.',
                         str(context.exception))

    def test_getting_service_factory_without_build(self):
        with self.assertRaises(NotImplementedError) as context:
            self.provider.get('service-g')
        self.assertIsInstance(context.exception, NotImplementedError)


class MockServiceA():

    pass


class MockServiceB():

    def __init__(self,
                 service_a,
                 some_configuration,
                 some_env_var,
                 other_env_var,
                 some_literal_value):
        self.service_a = service_a
        self.some_configuration = some_configuration
        self.some_env_var = some_env_var
        self.other_env_var = other_env_var
        self.some_literal_value = some_literal_value


class MockServiceC():

    def __init__(self):
        self.service_b = None


class MockServiceFactory(ServiceFactory):

    def __init__(self, service_b):
        self.service_b = service_b

    def build(self):
        service_c = MockServiceC()
        service_c.service_b = self.service_b

        return service_c


class MockServiceFactoryWithoutBuild(ServiceFactory):

    pass


if __name__ == '__main__':
    unittest.main()

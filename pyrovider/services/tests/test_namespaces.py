import unittest
import yaml

from unittest import mock
from pyrovider.meta.construction import Singleton
from pyrovider.services.provider import (BadConfPathError,
                                         NoCreationMethodError,
                                         NotAServiceFactoryError,
                                         ServiceFactory, ServiceProvider,
                                         TooManyCreationMethodsError,
                                         UnknownServiceError)


class NamespaceTest(unittest.TestCase):

    service_conf_path = 'pyrovider/services/tests/test_provider/service_conf_with_namespaces.yaml'

    def setUp(self):
        # Given...
        self.provider = ServiceProvider()
        with open(self.service_conf_path, 'r') as fp:
            self.service_conf = yaml.safe_load(fp.read())

        self.provider.conf(self.service_conf)

    def test_getting_available_namespaces(self):
        self.assertEqual(list(self.provider.namespaces),["foo"])
        self.assertEqual(list(self.provider.service_names),["service1"])

        self.assertEqual(list(self.provider.foo.namespaces),["bar"])
        self.assertEqual(list(self.provider.foo.service_names),["service2", "service3"])

        self.assertEqual(list(self.provider.foo.bar.namespaces),[])
        self.assertEqual(list(self.provider.foo.bar.service_names),["service4"])

    def test_getting_namespace_services(self):
        from ..tests.test_provider import MockServiceA, MockServiceI

        assert self.provider.service1
        assert isinstance(self.provider.service1, MockServiceA)

        # Access by key
        assert self.provider.get("service1")
        assert isinstance(self.provider.get("service1"), MockServiceA)

        assert self.provider.foo.service2
        assert isinstance(self.provider.foo.service2, MockServiceI)

        # Access by key
        assert self.provider.get("foo.service2")
        assert isinstance(self.provider.get("foo.service2"), MockServiceI)

        assert self.provider.foo.get("service2")
        assert isinstance(self.provider.foo.get("service2"), MockServiceI)

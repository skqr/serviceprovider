import unittest
import yaml

from unittest import mock
from pyrovider.meta.construction import Singleton
from pyrovider.services import factories


class FactoryTest(unittest.TestCase):

    def test_build_from_one_namespace(self):
        p = factories.service_provider_from_namespaces(
            ("test", "pyrovider/services/tests/test_provider/service_conf_2.yaml", False),
        )

        # Services are stored in the test namespace
        assert [] == list(p.service_names)
        assert ["test"] == list(p.namespaces)
        assert ["serviceA", "serviceB"] == list(p.test.service_names)

        p = factories.service_provider_from_namespaces(
            ("test", "pyrovider/services/tests/test_provider/service_conf_2.yaml", True),
        )

        # Services should be stored at the root level (using is_root flag when building)
        assert ["serviceA", "serviceB"] == list(p.service_names)
        assert [] == list(p.namespaces)

    def test_build_from_multiple_namespaces(self):
        p = factories.service_provider_from_namespaces(
            ("test", "pyrovider/services/tests/test_provider/service_conf_2.yaml", False),
            ("test2", "pyrovider/services/tests/test_provider/service_conf_with_namespaces.yaml", False),
        )

        # Services are stored in its own namespace
        assert [] == list(p.service_names)
        assert sorted(["test", "test2"]) == list(p.namespaces)
        assert ["serviceA", "serviceB"] == list(p.test.service_names)
        assert ["service1"] == list(p.test2.service_names)

        p = factories.service_provider_from_namespaces(
            ("test", "pyrovider/services/tests/test_provider/service_conf_2.yaml", True),
            ("test2", "pyrovider/services/tests/test_provider/service_conf_with_namespaces.yaml", False),
        )

        # Services should be stored at the root level (using is_root flag when building)
        assert ["serviceA", "serviceB"] == list(p.service_names)
        assert ["test2"] == list(p.namespaces)
        assert ["service1"] == list(p.test2.service_names)
        assert ["foo"] == list(p.test2.namespaces)


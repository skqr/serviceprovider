import unittest
import yaml

from unittest import mock
from pyrovider.meta.construction import Singleton
from pyrovider.services import factories


class FactoryTest(unittest.TestCase):

    def test_build_from_one_source(self):
        p = factories.service_provider_from_sources(
            factories.ServiceDefinitionSource(
                "test", "pyrovider/services/tests/test_provider/service_conf_2.yaml"
            )
        )

        # Services are stored in the test namespace
        assert [] == list(p.service_names)
        assert ["test"] == list(p.namespaces)
        assert ["serviceA", "serviceB"] == list(p.test.service_names)

        p = factories.service_provider_from_sources(
            factories.ServiceDefinitionSource(
                "test", "pyrovider/services/tests/test_provider/service_conf_2.yaml", False
            ),
        )

        # Services should be stored at the root level (using is_root flag when building)
        assert ["serviceA", "serviceB"] == list(p.service_names)
        assert [] == list(p.namespaces)

    def test_build_from_multiple_sources(self):
        p = factories.service_provider_from_sources(
            factories.ServiceDefinitionSource(
                "test", "pyrovider/services/tests/test_provider/service_conf_2.yaml"
            ),
            factories.ServiceDefinitionSource(
                "test2", "pyrovider/services/tests/test_provider/service_conf_with_namespaces.yaml"
            ),
        )

        # Services are stored in its own namespace
        assert [] == list(p.service_names)
        assert sorted(["test", "test2"]) == list(p.namespaces)
        assert ["serviceA", "serviceB"] == list(p.test.service_names)
        assert ["service1"] == list(p.test2.service_names)

        p = factories.service_provider_from_sources(
            factories.ServiceDefinitionSource(
                "test", "pyrovider/services/tests/test_provider/service_conf_2.yaml", False
            ),
            factories.ServiceDefinitionSource(
                "test2", "pyrovider/services/tests/test_provider/service_conf_with_namespaces.yaml"
            ),
        )

        # Services should be stored at the root level (using is_root flag when building)
        assert ["serviceA", "serviceB"] == list(p.service_names)
        assert ["test2"] == list(p.namespaces)
        assert ["service1"] == list(p.test2.service_names)
        assert ["foo"] == list(p.test2.namespaces)

    def test_build_with_parent(self):
        parent = factories.service_provider_from_yaml(
            "pyrovider/services/tests/test_provider/service_conf_2.yaml"
        )

        # Give it a name (the yaml doesn't have one)
        parent.name = "parent"

        p = factories.service_provider_from_yaml(
            "pyrovider/services/tests/test_provider/service_conf_with_namespaces.yaml", parent
        )

        assert sorted(["foo", "parent"]) == sorted(p.namespaces)
        assert ["service1"] == list(p.service_names)

        assert ["serviceA", "serviceB"] == list(p.parent.service_names)
        assert [] == list(p.parent.namespaces)

        assert p.get("parent.serviceA")
        assert p.parent.get("serviceA")

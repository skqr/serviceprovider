import yaml
import os

from typing import Tuple

from .provider import ServiceProvider


def service_provider_from_yaml(service_conf_path: str, *providers, app_conf_path: str = None):
    provider = ServiceProvider(*providers)

    with open(service_conf_path, 'r') as fp:
        service_conf = yaml.full_load(fp.read())

    if app_conf_path is not None:
        with open(app_conf_path, 'r') as fp:
            app_conf = yaml.full_load(fp.read())
    else:
        app_conf = None

    provider.conf(service_conf, app_conf)

    return provider


class ServiceDefinitionSource:

    def __init__(self, name, path, as_namespace=True):
        self.name = name
        self.path = path
        self.as_namespace = as_namespace


def service_provider_from_sources(
    *sources: ServiceDefinitionSource,
    create_alt_names_for_dashes=True
):
    """
    Builds a service provider from multiple sources

    Parameters
      sources: A list of ServiceDefinitionSource

      create_alt_names_for_dashes: For every entry with dashes in its name
                  we will create a new one with underscores os if needed it
                  can be accessed as a namespace attribute

    """
    provider = ServiceProvider()

    merged_conf = {}
    errors = []

    for source in sources:
        if not isinstance(source, ServiceDefinitionSource):
            raise TypeError(f"source must be a {ServiceDefinitionSource.__name__} instance")

        with open(source.path, 'r') as fp:
            service_conf = yaml.full_load(fp.read())

            for key, value in service_conf.items():
                service_key = f"{source.name}.{key}" if source.as_namespace else key
                alt_service_key = None

                # If there was an entry name with dashes
                # we create an alternate name with dashboards so
                # it's a valid python attribute name and can be accessed
                # with dot notation
                if create_alt_names_for_dashes and '-' in service_key:
                    alt_service_key = service_key.replace('-', '_')

                if service_key in merged_conf or alt_service_key in merged_conf:
                    errors.append(
                        f"Duplicated entry {key} from source {name} ({source.path})"
                    )

                merged_conf[service_key] = value

                if alt_service_key:
                    merged_conf[alt_service_key] = value

    if errors:
        raise ValueError("\n".join(errors))

    provider.conf(merged_conf)

    return provider


import yaml
from pyrovider.services.provider import ServiceProvider


def service_provider_from_yaml(service_conf_path: str, app_conf_path: str = None):
    provider = ServiceProvider()

    with open(service_conf_path, 'r') as fp:
        service_conf = yaml.full_load(fp.read())

    if app_conf_path is not None:
        with open(app_conf_path, 'r') as fp:
            app_conf = yaml.full_load(fp.read())
    else:
        app_conf = None

    provider.conf(service_conf, app_conf)

    return provider

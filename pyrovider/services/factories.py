import yaml
import os

from .provider import ServiceProvider


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


def service_provider_from_path(root_path: str, app_conf_path: str = None, conf_name: str = None):
    provider = ServiceProvider()

    root_path = root_path.rstrip("/")

    print(f"{root_path}, {os.path.split(root_path)}")

    root_module = os.path.split(root_path)[-1]
    merged_conf = {}

    for dpath, dnames, fnames in os.walk(root_path):
        for f in fnames:
            if (conf_name or "services.yaml") in f:
                print(f"Inspecting file {f}")
                parent = os.path.split(dpath)[-1]
                service_conf_file = os.path.join(dpath, f)

                with open(service_conf_file, 'r') as fp:
                    service_conf = yaml.full_load(fp.read())

                    print(f"{parent} == {root_module}")
                    if parent == root_module:
                        merged_conf.update(service_conf)
                    else:
                        for key, value in service_conf.items():
                            namespace_key = f"{parent}.{key}"
                            print(f"Collecting namespace {namespace_key}")
                            if namespace_key in merged_conf:
                                raise ValueError(f"Duplicated entry {namespace_key}")

                            merged_conf[namespace_key] = value

    if app_conf_path is not None:
        with open(app_conf_path, 'r') as fp:
            app_conf = yaml.full_load(fp.read())
    else:
        app_conf = None

    provider.conf(merged_conf, app_conf)

    return provider

import yaml
import os

from typing import Tuple

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


def service_provider_from_namespaces(
    *namespaces: Tuple[str, str, bool],
    create_alt_names_for_dashes=True
):
    """
    Builds a service provider based on the given namespaces

    Parameters
      namespaces: A tuple with (namepsace, yaml_file, root path).
                  If root is True, the definitions are stored at the root
                  namespace so there's no need to access them by namespace

    """
    provider = ServiceProvider()

    merged_conf = {}
    errors = []

    for namespace, file_path, is_root in namespaces:
        with open(file_path, 'r') as fp:
            service_conf = yaml.full_load(fp.read())

            for key, value in service_conf.items():
                namespace_key = key if is_root else f"{namespace}.{key}"
                alt_namespace_key = None

                # If there was an entry named with dashes
                # we create an alternate name with dashboards so
                # its a valid python attribute name and can be accessed
                # with dot notation
                if create_alt_names_for_dashes and '-' in namespace_key:
                    alt_namespace_key = namespace_key.replace('-', '_')

                if namespace_key in merged_conf or alt_namespace_key in merged_conf:
                    errors.append(
                        f"Duplicated entry {key} from namespace {namespace} in file {file_path}"
                    )

                merged_conf[namespace_key] = value

                if alt_namespace_key:
                    merged_conf[alt_namespace_key] = value

    if errors:
        raise ValueError("\n".join(errors))

    provider.conf(merged_conf)

    return provider

"""Get config.ini containing all configuration settings."""

import os
import configparser

DEFAULT_CONFIG_PATH = "~/config.ini"


def get_config(config_location=DEFAULT_CONFIG_PATH):
    """Get config from config.ini.

    Args:
        config_location (str): Location for the config file
    Returns:
        config: Parsed config
    """

    config_location = os.path.expanduser(config_location)

    if not os.path.exists(config_location):
        raise ValueError("Configuration file "
                         "{file_path} does not exist".format(
                            file_path=config_location))

    config = configparser.ConfigParser()
    config.read(config_location)
    return config

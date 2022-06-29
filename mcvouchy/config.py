from __future__ import annotations

import configparser
import os
import logging
import logging.handlers
import sys
from typing import Optional


logger = logging.getLogger(__name__)


def get_config() -> configparser.RawConfigParser:
    return singleton.get_config()


class ManagedLogger:
    def __init__(self) -> None:
        self.cli_handler = logging.StreamHandler(sys.stderr)
        self.syslog_handler = logging.handlers.SysLogHandler()
        self.file_handler: Optional[logging.FileHandler] = None
        logging.getLogger().addHandler(self.cli_handler)
        logging.getLogger().addHandler(self.syslog_handler)
        logging.getLogger().setLevel(logging.DEBUG)

    def parse_level(self, level_str: str) -> int:
        try:
            level = getattr(logging, level_str.upper())
            assert isinstance(level, int)
            return level
        except AttributeError:
            raise ValueError("Unknown log level: %s" % (level_str))

    def load_config(self, config: configparser.RawConfigParser) -> None:
        self.cli_handler.setLevel(self.parse_level(config["logging"]["cli_level"]))

        cli_formatter = logging.Formatter(
            config["logging"]["cli_format"], datefmt=config["logging"]["date_format"]
        )
        self.cli_handler.setFormatter(cli_formatter)

        self.syslog_handler.setLevel(
            self.parse_level(config["logging"]["syslog_level"])
        )

        try:
            self.file_handler = logging.FileHandler(config["logging"]["file_target"])
            self.file_handler.setLevel(
                self.parse_level(config["logging"]["file_level"])
            )
            self.file_handler.setFormatter(cli_formatter)
            logging.getLogger().addHandler(self.file_handler)
        except KeyError:
            # ignore, just don't log to files
            pass

    def setup_formatter(self) -> None:
        pass


class Config:
    default_config = {
        "logging": {
            "date_format": "%Y-%m-%d %H:%M:%S %z",
            "cli_target": "stdout",
            "cli_level": "warning",
            "cli_format": "[%(asctime)s] [%(levelname) 7s] [%(name)  21s] %(message)s",
            "file_level": "info",
            "syslog_level": "warn",
        },
        "mcvouchy": {
            "airlock_channel": "#welcome",
            "limits_window": "1d",
            "limits_exempt_roles": "Moderator",
            "verified_role": "Verified",
            "invitations_limit": "3",
            "vouch_limit": "3",
            "vouch_threshold": "3",
            "auto_vouch_by_inviter": "true",
            "invitation_lifetime": "1d",
        },
    }

    search_paths = (
        os.path.join(os.getcwd(), "conf", "mcvouchy.ini"),
        "/etc/mcvouchy/mcvouchy.ini",
    )

    def __init__(self) -> None:
        """
        Load the application configuration.
        """
        self.managed_logger = ManagedLogger()
        self.loaded_config = configparser.RawConfigParser()
        self.loaded_config.read_dict(self.default_config)
        # Do an initial logging config to set up our formatter. On the first
        # pass, this won't load the configuration from a file.
        self.configure_logging()

        path = self.read_config_from_file()

        if path is not None:
            logger.info("Successfully loaded the configuration from %s" % (path))

        self.configure_logging()

    def read_config_from_file(self) -> Optional[str]:
        for path in self.search_paths:
            if os.path.isfile(path):
                return self.force_load_file(path)

        return None

    def force_load_file(self, path: str) -> Optional[str]:
        if not os.path.isfile(path):
            logger.error("Cannot read config file: %s" % (path))

        try:
            logger.debug("Trying to open config path: %s" % (path))
            with open(path, "r") as fp:
                self.loaded_config.read_file(fp)

            return path
        except (PermissionError, FileNotFoundError) as e:
            logger.debug(
                "Unable to open config: %s: %s: %s"
                % (path, e.__class__.__name__, repr(e))
            )

        return None

    def configure_logging(self) -> None:
        self.managed_logger.load_config(self.loaded_config)

    def get_config(self) -> configparser.RawConfigParser:
        return self.loaded_config


singleton = Config()

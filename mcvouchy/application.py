import argparse
import logging
from .bot import create_bot
from .config import singleton as config_singleton

logger = logging.getLogger("mcvouchy.application")


class Application:
    """
    Entrypoint for the main mcvouchy application. Invoked from mcvouchy.py.
    """

    def __init__(self):
        desc = """
        Discord bot that allows single-use invitations to be generated and new
        members to be democratically vouched for.
        """.strip()

        self.argparse = argparse.ArgumentParser(description=desc)

        self.argparse.add_argument(
            "-c",
            "--config",
            default=None,
            required=False,
            help="Configuration file to load - defaults to conf/mcvouchy.ini",
        )

    def run(self):
        """
        Parse arguments, load configuration and start the application.
        """
        args = self.argparse.parse_args()

        if args.config:
            config_singleton.force_load_file(args.config)

        config = config_singleton.get_config()

        create_bot(config)

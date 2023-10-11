#!/usr/bin/env python
import os
import sys
import argparse
import logging

from dotenv import load_dotenv

from src.api import add_api_command
from src.auth import add_token_command
from src.shared import realpath_type


# import websockets


def perc():
    return run(argparse.ArgumentParser)


def run(arg_parser, non_cli_args=None):
    load_local_env()

    parser = arg_parser(prog="perc", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug messages to console")
    parser.add_argument("-l", "--log-dir", dest='log_dir', type=str, help="Write log files to the specified location")
    parser.add_argument("-p", "--profile", action="store_true", help="Profile the run")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    parser.add_argument("-t", "--token-file", dest='token_file', type=realpath_type, help="Token file location",
                        default=os.path.join(script_dir, 'tokens.json'))

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    subparser_dict = {}
    # subparser_dict |= add_chroma_command(subparsers)
    subparser_dict |= add_token_command(subparsers)
    subparser_dict |= add_api_command(subparsers)
    # TODO: add function to go update all existing items in DB for missing file_state/status -> need utilities to manage DB
    # subparser_dict |= add_db_command(subparsers)

    # NOTE: non_cli_args is not needed to pass in here, but is needed for testing
    args = parser.parse_args(non_cli_args)
    configure_logging(console_debug=args.debug, log_dir=args.log_dir)
    # WARNING: Any logging before this point will not be configured
    logging.debug(f"Parsed CLI Arguments: {args}")
    command = getattr(args, 'command', None)
    if hasattr(args, 'func'):
        return args.func(args)
    elif command in subparser_dict.keys():
        subcommand = getattr(args, f'{command}_command', None)
        command = subcommand if subcommand is not None else command
        subparser = subparser_dict.get(command)
        subparser.error(f"specify a '{command}' subcommand")  # exit 2
    else:
        parser.error(f"specify a subcommand")  # exit 2


def load_local_env():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    env_file = os.path.join(script_dir, '../.env')
    if not os.path.isfile(env_file):
        raise Exception("No .env file found in the root directory. Please create one and try again.")
    load_dotenv(dotenv_path=env_file)


def file_link_format(profile_log: str) -> str:
    # This syntax was not working with the default run console until [X] Run with Python Console was checked
    return "file://{}".format(
        str(profile_log))  # The following only works if the file already exists... which most of the time the log isn't created until  # after the process is nearly complete so this won't work  # return f"""File "{profile_log}", line 1, in log"""


def configure_logging(console_debug: bool, log_dir: str) -> None:
    """
    Configures the default logging variable with DEBUG going to the .cache/run output file by default (even if -d is not
    set). The STDOUT will be set to INFO messages by default. The DEBUG logs will have the timestamps and threads added
    to them, but those are added to the far right in the log file so the messages are easily viewed without having to
    scroll. If the timestamps are needed, then scroll.
    :param log_dir: This is used to write the out (with debug messages) to by default
    :param console_debug: This boolean can be used to toggle the printing of debug messages in the console/STDOUT
    :return:
    """
    logging.getLogger().setLevel(logging.DEBUG)
    out_handler = logging.StreamHandler(sys.stdout)
    out_handler.setLevel(logging.DEBUG if console_debug else logging.INFO)
    out_handler.setFormatter(logging.Formatter("%(message)s"))
    logging.getLogger().addHandler(out_handler)
    if log_dir:
        run_log = os.path.join(log_dir, 'run.log')
        file_handler = logging.FileHandler(run_log)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(levelname)-5s: %(message)-320s %(asctime)s %(threadName)s"))
        logging.getLogger().addHandler(file_handler)
        logging.info(">> Run log: {}".format(file_link_format(run_log)))


if __name__ == "__main__":
    return_code = perc()
    exit(return_code)

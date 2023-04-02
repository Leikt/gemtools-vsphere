import argparse

from .client import VSphereClient, VSphereClientException, VSphereClientBuilderException, VSphereClientBuilder
from .cli import cmd_get, VALID_GETTERS

CMD = 'vsphere'


def setup_main_parser(parser: argparse.ArgumentParser):
    parser.description = 'vSphere server interaction.'


def main(args: list[str]):
    from pathlib import Path

    # >>> Main Parser
    parser_main = argparse.ArgumentParser(prog='gemtools vsphere')
    parser_main.description = 'A generic management tool used to interact with vSphere apis.'
    subparsers_main = parser_main.add_subparsers(title='command', dest='command')
    subparsers_main.required = True

    # Configuration group
    parser_config = argparse.ArgumentParser()
    group = parser_config.add_argument_group('Configuration')
    group.add_argument('--config', type=Path, required=True,
                       help='Configuration file.')
    group.add_argument('--config-key', type=Path,
                       help='Encryption key for the configuration file. Required if the configuration is encrypted.')

    # >>> Getters parser
    parser_getters = subparsers_main.add_parser('get', parents=[parser_config], conflict_handler='resolve')
    parser_getters.description = 'Get information from the vSphere API.'
    parser_getters.add_argument('getter', type=str, choices=[],
                                help='Which getter to use. Use --print-details to display the possibile getters.')
    parser_getters.add_argument('--verbose', '-v', action='count', default=0, help='Increase the log verbosity.')
    parser_getters.add_argument('--output-file', '-o', type=Path,
                                help='File or directory where to store the getter result. Depends on the getter.')
    parser_getters.add_argument('--target', '-t', type=str, nargs='*', default='*',
                                help='List of vSphere API to deal with. Names are defined in the configuration file.')
    # parser_getters.add_argument('--filter', '-f', type=GetterFilter, action='append',
    #                             help='Add a filter to the item to get.')

    # >>> Parse arguments
    args = parser_main.parse_args(args)
    if args.command == 'get':
        cmd_get(args)

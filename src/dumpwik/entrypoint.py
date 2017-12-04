import click
import collections
import json
import logging

from .backup import backup as do_backup
from .prune import prune as do_prune
from ._version import version as __version__


def load_config(filename):
    with open(filename) as file:
        config = json.load(file)

    defaults = {
        'port': 3306,
        'compress': 'bzip2',
        'exclude': [],
        'include': [],
        'keep': {
        },
    }

    def rupdate(d, u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                d[k] = rupdate(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    rupdate(defaults, config)
    config = defaults

    if not 'name' in config:
        raise Exception('Missing name in configuration')
    if not 'username' in config:
        raise Exception('Missing username in configuration')
    if not 'password' in config:
        raise Exception('Missing password in configuration')
    if not 'directory' in config:
        raise Exception('Missing directory in configuration')
    if not 'filename' in config:
        raise Exception('Missing filename in configuration')
    if not config['compress'] in ['none', 'bzip2']:
        raise Exception('Invalid compression format ' + config['compress'])

    if not 'hostname' in config:
        config['hostname'] = config['name']
    config['port'] = int(config['port'])
    config['directory'] = config['directory'].rstrip('/') + '/'

    return config


@click.group()
@click.option(
    '--config',
    '-c',
    help='Config file',
    required=True
)
@click.option(
    '--debug',
    'loglevel',
    flag_value='DEBUG',
    help='Set log level to DEBUG'
)
@click.option(
    '--error',
    'loglevel',
    flag_value='ERROR',
    help='Set log level to ERROR'
)
@click.option(
    '--info ',
    'loglevel',
    flag_value='INFO',
    help='Set log level to INFO'
)
@click.option(
    '--log-file',
    'logfile',
    help='Set log file filename'
)
@click.option(
    '--log-file-debug',
    'logfilelevel',
    flag_value='DEBUG',
    help='Set log file log level to DEBUG'
)
@click.option(
    '--log-file-error',
    'logfilelevel',
    flag_value='ERROR',
    help='Set log file log level to ERROR'
)
@click.option(
    '--log-file-info ',
    'logfilelevel',
    flag_value='INFO',
    help='Set log file log level to INFO'
)
@click.option(
    '--log-file-warning',
    'logfilelevel',
    flag_value='WARNING',
    default=True,
    help='Set log file log level to WARNING (default)'
)
@click.option(
    '--warning',
    'loglevel',
    flag_value='WARNING',
    default=True,
    help='Set log level to WARNING (default)'
)
@click.version_option(
    version=__version__
)
@click.pass_context
def main(ctx, **kwargs):
    level = eval('logging.' + kwargs['loglevel'])
    fmt = '%(asctime)s\t%(levelname)s\t%(message)s'
    fmt = logging.Formatter(fmt)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console.setLevel(level)
    root.addHandler(console)

    if kwargs['logfile'] is not None:
        fh = logging.FileHandler(kwargs['logfile'])
        fh.setFormatter(fmt)
        level = eval('logging.' + kwargs['logfilelevel'])
        fh.setLevel(level)
        root.addHandler(fh)

    ctx.obj = load_config(kwargs['config'])


@click.command()
@click.option(
    '--prune/--no-prune',
    default=True,
    help='Prune archives once backup ended'
)
@click.pass_obj
def backup(config, **kwargs):
    do_backup(config)
    if kwargs['prune']:
        do_prune(config)


@click.command()
@click.pass_obj
def prune(config):
    do_prune(config)
    return


main.add_command(backup)
main.add_command(prune)

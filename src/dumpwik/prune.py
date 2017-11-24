import glob
import logging
import os

from collections import OrderedDict
from datetime import datetime
from operator import itemgetter

from .pathhelper import get_dump_glob
from .pathhelper import get_dump_matcher


# Inspired by Borg Backup code
# https://github.com/borgbackup/borg/blob/master/src/borg/helpers/misc.py#L32
PRUNING_PATTERNS = OrderedDict([
    ('secondly', '%Y-%m-%d %H:%M:%S'),
    ('minutely', '%Y-%m-%d %H:%M'),
    ('hourly', '%Y-%m-%d %H'),
    ('daily', '%Y-%m-%d'),
    ('weekly', '%G-%V'),
    ('monthly', '%Y-%m'),
    ('yearly', '%Y'),
])


def prune(config):
    candidates = glob.iglob(get_dump_glob(config))
    archives = {}
    matcher = get_dump_matcher(config)
    for filename in candidates:
        matches = matcher.match(filename)
        if matches is not None:
            database = matches.group('database')
            if database not in archives:
                archives[database] = []
            archives[database].append({
                'filename': filename,
                'date': datetime.fromtimestamp(os.path.getmtime(filename)),
            })

    for database in archives:
        _prune_database(config, database, archives[database])


def _prune_database(config, database, archives):
    logging.info('Pruning database {0}...'.format(database))
    keep = []
    kept_because = {}

    for rule in PRUNING_PATTERNS.keys():
        if rule in config['keep']:
            num = config['keep'][rule]
            if num is not None and num != 0:
                keep += _prune_split(archives, rule, num, kept_because)

    for archive in archives:
        filename = archive['filename']
        if filename not in keep:
            logging.debug('Removing archive {0}'.format(filename))
            os.remove(filename)
            directory = os.path.dirname(filename)
            while directory + '/' != config['directory'] \
                    and not len(os.listdir(directory)):
                logging.debug('Removing empty directory {0}'.format(directory))
                os.rmdir(directory)
                directory = os.path.dirname(directory)


# Inspired by Borg Backup code
# https://github.com/borgbackup/borg/blob/master/src/borg/helpers/misc.py#L43
def _prune_split(archives, rule, n, kept_because=None):
    last = None
    keep = []
    pattern = PRUNING_PATTERNS[rule]
    if kept_because is None:
        kept_because = {}
    if n == 0:
        return keep
    for a in sorted(archives, key=itemgetter('date'), reverse=True):
        period = a['date'].strftime(pattern)
        if period != last:
            last = period
            if a['filename'] not in kept_because:
                keep.append(a['filename'])
                kept_because[a['filename']] = (rule, len(keep))
                if len(keep) == n:
                    break
    return keep

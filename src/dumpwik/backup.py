import logging
import mysql.connector as mysql
import os
import subprocess

from contextlib import closing
from datetime import datetime

from .pathhelper import get_dump_filename


def _fill_bzip2_compressed_dump(config, database, filehandler):
    cmd = _get_mysqldump_cmd(config, database)
    dump = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True
    )
    comp = subprocess.Popen(
        ['bzip2'],
        stdin=dump.stdout,
        stdout=filehandler,
        stderr=subprocess.PIPE,
        close_fds=True
    )
    dump.stdout.close()
    out, err = comp.communicate()
    err = dump.stderr.read() + err
    if len(err) > 0:
        raise Exception(err.decode('utf-8').strip())


def _fill_uncompressed_dump(config, database, filehandler):
    cmd = _get_mysqldump_cmd(config, database)
    dump = subprocess.Popen(
        cmd,
        stdout=filehandler,
        stderr=subprocess.PIPE,
        close_fds=True
    )
    out, err = dump.communicate()
    if len(err) > 0:
        raise Exception(err.decode('utf-8').strip())


def _get_mysqldump_cmd(config, database):
    cmd = [
        'mysqldump',
        '--host=' + config['hostname'],
        '--user=' + config['username'],
        '--password=' + config['password'],
        '--port=' + str(config['port']),

        '--add-drop-table',
        '--add-locks',
        '--compress',
        '--create-options',
        '--disable-keys',
        '--extended-insert',
        '--lock-tables',
        '--no-create-db',
        '--quick',
        '--set-charset',
        '--skip-dump-date',

        #'--events',
        '--routines',
        '--triggers',
        database,
    ]
    return cmd


def create_dump(config, database, filename):
    workfile = filename + '.running'
    try:
        wfh = open(workfile, 'w')
    except PermissionError:
        raise Exception('Unable to open temporary file "{0}"'.format(workfile))

    try:
        with wfh as fh:
            if config['compress'] == 'bzip2':
                _fill_bzip2_compressed_dump(config, database, fh)
            else:
                _fill_uncompressed_dump(config, database, fh)
        os.rename(workfile, filename)
    except Exception as e:
        os.remove(workfile)
        raise e


def backup(config):
    excludes = config['exclude']
    excludes.append('information_schema')
    excludes.append('performance_schema')
    includes = config['include']

    logging.info('Running MySQL backup named {0}'.format(config['name']))
    logging.debug('Connecting as {0}@{1}'
                  .format(config['username'], config['hostname']))
    logging.debug('Excluding: '.format(', '.join(config['exclude'])))
    logging.debug('Including: '.format(', '.join(config['include'])))
    logging.debug('Directory is {0}'.format(config['directory']))
    logging.debug('Filename pattern is {0}'.format(config['filename']))

    cnx = mysql.connect(host=config['hostname'], port=config['port'],
                        user=config['username'], password=config['password'])

    logging.debug('Retrieving database list')
    with closing(cnx.cursor(dictionary=True)) as cur:
        cur.execute('SHOW DATABASES;')
        databases = []
        for row in cur:
            database = row['Database']
            if not database in excludes:
                if not includes or database in includes:
                    databases.append(database)

    logging.info('Found {0} databases'.format(len(databases)))

    for database in databases:
        logging.info('Dumping {0} database'.format(database))
        now = datetime.now()
        filename = get_dump_filename(config, database, now)
        logging.debug('Dump file will be {0}'.format(filename))

        directory = os.path.dirname(filename)
        if not os.path.isdir(directory):
            os.makedirs(directory)

        try:
            create_dump(config, database, filename)
        except Exception as e:
            logging.error('Unable to do a complete dump. This database '
                          'dump file will not be kept!')
            logging.warning(str(e))

import re

from datetime import tzinfo


PLACEHOLDER_PATTERN = '\{(?P<kw>[a-zA-Z]*)(?::(?P<fmt>[^}]*))?\}'


def get_dump_filename(config, database, now):
    def repl(matches):
        kw = matches.group('kw')
        if kw == 'name':
            return config['name']
        elif kw == 'hostname':
            return config['hostname']
        elif kw == 'username':
            return config['username']
        elif kw == 'database':
            return database
        elif kw == 'now':
            date = now
        elif kw == 'utcnow':
            date = now.astimezone(tzinfo('UTC'))
        else:
            raise Exception('Invalid placeholder ' + kw +
                            ' in filename pattern')

        fmt = matches.group('fmt')
        if fmt is None:
            return fmt.isoformat()
        return date.strftime(fmt)

    filename = re.sub(PLACEHOLDER_PATTERN, repl, config['filename'])
    return config['directory'] + filename


def get_dump_glob(config):
    def repl(matches):
        kw = matches.group('kw')
        if kw == 'name':
            return config['name']
        elif kw == 'hostname':
            return config['hostname']
        elif kw == 'username':
            return config['username']
        elif kw == 'database':
            return '*'
        elif kw == 'now':
            return '*'
        elif kw == 'utcnow':
            return '*'
        else:
            raise Exception('Invalid placeholder ' + kw +
                            ' in filename pattern')
    filename = re.sub(PLACEHOLDER_PATTERN, repl, config['filename'])
    return config['directory'] + filename


def get_dump_matcher(config):
    def repl(matches):
        kw = matches.group('kw')
        if kw == 'name':
            return config['name']
        elif kw == 'hostname':
            return config['hostname']
        elif kw == 'username':
            return config['username']
        elif kw == 'database':
            if repl.db_kw_present:
                return '[a-zA-Z0-9_]+'
            else:
                repl.db_kw_present = True
                return '(?P<database>[a-zA-Z0-9_]+)'
        elif kw == 'now':
            return '[^/]+'
        elif kw == 'utcnow':
            return '[^/]+'
        else:
            raise Exception('Invalid placeholder ' + kw +
                            ' in filename pattern')
    repl.db_kw_present = False
    pattern = re.sub(PLACEHOLDER_PATTERN, repl, config['filename'])
    if not repl.db_kw_present:
        raise Exception('Database name must be present in filename pattern '
                        'to allow prune')
    return re.compile(config['directory'] + pattern)

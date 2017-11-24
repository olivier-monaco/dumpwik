# Dumpwik

Dumpwik is built around mysqldump to automate regular dump of some or all databases of one or more servers for a backup purpose.

THIS IS A WORK IN PROGRESS even if I use it on production systems.


## JSON job file

A JSON file must be provided to Dumpwik as the option `--config`. This file contains information about one backup job. A job is always limited to one host and can backup all or only some of its databases. Different jobs can backup the same MySQL/MariaDB server.

Here is an example job file:
```json
{
    "name": "myserver",
    "hostname": "myserver.example.com",
    "port": 3306,
    "username": "backup",
    "password": ".P-#A1S958S=W..or:d",
    "directory": "/var/backups/dumps",
    "filename": "{name}/{database}/{now:%Y%m%d-%H%M%S}.sql.bz2",
    "compress": "bzip2",
    "exclude": [
        "test"
    ],
    "keep": {
        "daily": 7,
        "weekly": 4,
        "monthly": -1
    }
}
```

A job file must include (**required**):
* **name**: the job name,
* **username**: the user name to connect as,
* **password**: the password to connect with,
* **directory**: the directory where to save the dumps,
* **filename**: the filename of the dumps (see below),

It can also contains (**optionnal**):
* **hostname**: the host name to connect to (defaults to the job **name**)
* **port**: the port to connect to (defaults to 3306)
* **compress**: *none* or *bzip2*. The compression algorithm to use (defaults to bzip2). For *bzip2*, Dumpwik will use the external command bzip2 which must be installed.
* **exclude**: a list of databases to exclude (defaults to empty, implicitly includes *information_schema* and *performance_schema*)
* **include**: a list of databases to limit the backup to. If empty (the default), all databases will be backed up. The **exclude** list is applied to the **include** list.
* **keep**: number of backup to keep when pruning (see below).

The **filename** field must be a path relatively to the **directory** field and including the file extension. It can contain subdirectories and the following placeholder:
* **{name}**: the job name,
* **{hostname}**: the host name,
* **{username}**: the user name,
* **{database}**: the database name,
* **{now}**: the current local time in ISO-8601 format. Custom format string can be provided like *{now:%Y%m%d-%H%M%S}*,
* **{utcnow}**: the current UTC time in ISO-8601 format. Custom format string can be provided like *{utcnow:%Y%m%d-%H%M%S}*,

The **keep** field can have the following sub-fields:
* **secondly**: number of dump to keep by second,
* **minutely**: number of dump to keep by minute,
* **hourly**: number of dump to keep by hour,
* **daily**: number of dump to keep by day,
* **weekly**: number of dump to keep by week,
* **monthly**: number of dump to keep by month,
* **yearly**: number of dump to keep by year.

Each of them accept :
* A positive value N: keep the last N dumps,
* A zero value: do not keep dumps,
* A negative value: keep all dumps

The prune algorithm works like the Borg Backup prune algorithm.


## Running Dumpwik

Dumpwik offer two actions: *backup* and *prune*. Whatever is the action, the JSON job file must be provied using the *--config* (or *-c*) option. This option must be specified before the action.

### Backup

To backup a job:
```bash
$ dumpwik -c myserver.json backup
```

The *backup* action will be followed be a *prune* action. You can avoid the *prune* action using the *--no-prune* option:
```bash
$ dumpwik -c myserver.json backup --no-prune
```


### Prune

To prune a job:
```bash
$ dumpwik -c myserver.json prune
```


### Log level

Dumpwik can be more or less verbose using the options **--debug**, **--info**, **--warning** (default) and **--error**. These options must be provided before the action:
```bash
$ dumpwik --debug -c myserver.json backup
```

## Create MySQL user for backups

Even if you can use the root user and password, we strongly recommend to use a dedicated one with only read access. You can create a user using the following query:
```sql
GRANT SELECT, SHOW VIEW, LOCK TABLES ON *.* TO '<user>'@'%' IDENTIFIED BY '<password>';
```

Replace `<user>` and `<password>` with the right values. You can also limit the host allowed to use this user by replacing `%`.

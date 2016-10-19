# coding=utf8

"""
every opt of used should bu define first


this options is based on tornado.options
"""

from tornado.options import define, parse_command_line, \
    parse_config_file, options

common_opts = [
    {
        "name": 'debug',
        "default": False,
        "help": 'if logged debug info',
        "type": bool,
    },
    {
        "name": 'verbose',
        "default": False,
        "help": 'if log detail',
        "type": bool,
    },
    {
        "name": 'config',
        "default": '/etc/TestNovaCase/test_nova_case.conf',
        "help": 'path of config file',
        "type": str,
        "callback": lambda path: parse_config_file(path, final=False)
    },
    # {
    #     "name": 'config',
    #     "default": 'F:/projects/python/TestNovaCase/etc/test_nova_case.conf',
    #     "help": 'path of config file',
    #     "type": str,
    #     "callback": lambda path: parse_config_file(path, final=False)
    # },
    {
        "name": 'db_driver',
        "default": 'ops.db.api',
        "help": 'default db driver',
        "type": str,
    },
    {
        "name": 'api_port',
        "default": 4362,
        "help": 'listen port of api',
        "type": int,
    },
    {
        "name": 'lock_path',
        "default": '/var/lock',
        "help": 'path of config file',
        "type": str,
    },
]


def register_opt(opt, group=None):
    """Register an option schema
    opt = {
            "name": 'config',
            "default": 'webinstall.conf',
            "help": 'path of config file',
            "tyle": str,
            "callback": lambda path: parse_config_file(path, final=False)
        }
    """
    if opt.get('name', ''):
        optname = opt.pop('name')
        if optname in options._options.keys():
            options._options.pop(optname)
        define(optname, **opt)


def register_opts(opts, group=None):
    """Register multiple option schemas at once."""
    for opt in opts:
        register_opt(opt, group)
    return options


def get_options(opts=None, group=None):
    if opts:
        register_opts(opts, group)
    options = register_opts(common_opts, 'common')
    if options.as_dict().get('extra_opts', ''):
        try:
            extra_opts = __import__(options.extra_opts)
            options = register_opts(extra_opts.config.opts, 'extra')
        except Exception as e:
            print("get config error")
            raise e
    parse_config_file(options.config, final=False)
    parse_command_line()
    return options


if __name__ == "__main__":
    print get_options().as_dict()
    options = get_options()
    print options.get('sql_connection', None)

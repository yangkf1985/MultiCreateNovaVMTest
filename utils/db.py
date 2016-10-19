#! /usr/lib/env python
# -*- coding: utf-8 -*-

""" created by yang on 2016/9/6
"""

import MySQLdb
from sqlalchemy.engine import url
from utils.options import get_options
from utils.common import singleton, save_csv
from utils.log import LOG

__author__ = "muyidixin2006@126.com"
string_types = basestring,

__all__ = ["getLogger",
           "LOG"]

db_opts = [
    {
        "name": 'sql_conn',
        "default": 'mysql://root:rootpassword@192.168.111.2:3306/nova?charset=utf8',
        "help": 'nova db connection string',
        "type": str,
    },
]

options = get_options(db_opts, 'db')


@singleton
def get_conn():
    try:
        connection_dict = url.make_url(options.sql_conn)
        conn = MySQLdb.connect(host=connection_dict.host,
                               user=connection_dict.username,
                               passwd=connection_dict.password,
                               db=connection_dict.database)
    except Exception as e:
        LOG.error("get mysql connection: %s" % e)
        raise e
    return conn


def query(sql):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows
    except Exception as e:
        LOG.error("get mysql connection: %s" % e)
        raise None


def get_server_info(server_id=None, server_name_prefix=None, server_count=1):
    if server_id:
        sql = "select uuid, display_name, created_at, " \
              "launched_at, timediff(launched_at, created_at) as create_interval,  `host`, vm_state" \
              " from instances where id = '%s'" % server_id
    else:
        sql = "select uuid, display_name, created_at, " \
              "launched_at, timediff(launched_at, created_at) as create_interval,  `host`, vm_state" \
              " from instances where display_name like '%%%s%%' " \
              "order by created_at desc limit %s" % (server_name_prefix, server_count)

    servers = query(sql)
    return servers


def get_servers_and_save(csv_file_name, server_id=None,
                         server_name_prefix=None, server_count=1):
    servers = get_server_info(server_id, server_name_prefix, server_count)
    if servers:
        header = ["vm_id", "name", "created_at",
                  "launched_at", "create_interval", "host", "status"]
        save_csv(csv_file_name, header, servers)


def main():
    get_servers_and_save("F:\i.csv", server_name_prefix="local", server_count=2)


if __name__ == "__main__":
    main()

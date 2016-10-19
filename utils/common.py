#! /usr/lib/env python
# -*- coding: utf-8 -*-

""" created by yang on 2016/9/6
"""
import os
import csv
import time
import uuid
import random
import socket
import datetime
import functools

from utils.log import LOG

__author__ = "muyidixin2006@126.com"
__VM_NAME_PREFIX = "test_nova"


class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kwargs)
        return cls._instance


def singleton(cls, *args, **kwargs):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return _singleton


def timeit(func):
    @functools.wraps(func)
    def warp(*args, **kwargs):
        handle_obj = kwargs.get("handle_obj")
        start = get_local_time()
        str_start = get_str_local_time(start)
        LOG.info("execute '%s': [%s] start %s" %
                 (func.__name__,
                  handle_obj,
                  str_start))

        ret = func(*args, **kwargs)
        end = get_local_time()
        str_end = get_str_local_time(end)
        elapsed = (end - start).seconds
        LOG.info("execute '%s': [%s] end %s, elapsed time: %.3s s" %
                 (func.__name__,
                  handle_obj,
                  str_end,
                  elapsed))
        # save_csv("test_nova_case.csv", rows=[(handle_obj, str_start,
        #                                       str_end, elapsed)])
        return ret

    return warp


def gen_local_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_local_time():
    return datetime.datetime.now()


def get_str_local_time(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


def random_mac():
    mac = [0x52, 0x54, 0x00,
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: '%02x' % x, mac))


def random_uuid():
    return str(uuid.uuid1())


def gen_uu_name(vm_name_prefix):
    """ generate uu name
    :param vm_name_prefix: vm name prefix
    :return:
    """
    random_list = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return "%s_%s" % (vm_name_prefix if vm_name_prefix else __VM_NAME_PREFIX,
                      ''.join(random.sample(random_list, 20)))


def gen_vm_name(vm_name_prefix, vm_index):
    """ generate uu name
    :param vm_name_prefix: vm name prefix
    :param vm_index
    :return:
    """
    return "%s_%s" % (vm_name_prefix if vm_name_prefix else __VM_NAME_PREFIX, vm_index)


def gen_utc_now():
    """Overridable version of utils.gen_utc_now."""
    return datetime.datetime.utcnow()


def save_csv(file_name, header=None, rows=None):
    """
    create and write cvs file
    :param file_name: cvs file path
    :param header: cvs header: []
    :param rows: cvs rows: [()]
    :return:
    """
    file_mode = "ab+" if os.path.exists(file_name) else "wb+"
    with file(file_name, file_mode) as cvs_file:
        writer = csv.writer(cvs_file)
        if header:
            writer.writerow(header)
        if rows:
            writer.writerows(rows)


def ping_vm_port(server_ip, server_port, timeout=1):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(timeout)
    try:
        sk.connect((server_ip, server_port))
        return True
    except socket.error:
        return False
    finally:
        sk.close()


def main():
    start = get_local_time()
    time.sleep(1)
    end = get_local_time()
    elapsed = end - start
    print(start)
    print(end)
    print(elapsed)


if __name__ == "__main__":
    main()

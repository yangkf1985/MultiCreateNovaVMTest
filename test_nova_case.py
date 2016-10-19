#! /usr/lib/env python
# -*- coding: utf-8 -*-

""" created by yang on 2016/9/6
"""
import os
import sys
from utils.common import gen_vm_name, gen_local_time
from utils import server
from utils.request import sync_get_session
from utils.log import LOG
from utils.options import get_options

import eventlet
eventlet.monkey_patch()

__author__ = "muyidixin2006@126.com"
FILE_VMS = "vm_id.txt"
test_options = [
    {
        "name": "default_flavor",
        "default": "1",
        "help": "default vm flavor",
        "type": str
    },
    {
        "name": "default_image",
        "default": "WindowBase-20G",
        "help": "default vm image",
        "type": str
    },
    {
        "name": "default_network",
        "default": "ext-net",
        "help": "default vm network",
        "type": str
    },
    {
        "name": "thread_pool_size",
        "default": 50,
        "help": "thread pool size",
        "type": int
    },
    {
        "name": "vm_prefix",
        "default": "test_vm",
        "help": "vm prefix",
        "type": str
    },
]

options = get_options(test_options, "test")
pool = eventlet.GreenPool(options.thread_pool_size)


def log_vm(vm_id):
    file_mode = "ab+" if os.path.exists(FILE_VMS) else "wb+"
    with file(FILE_VMS, file_mode) as vms:
        vms.write('%s\n' % vm_id)


def _create_server(server_info):
    vm_prefix = server_info.get("vm_prefix")
    index = server_info.get("index")
    token = server_info.get("token")

    vm_name = gen_vm_name(vm_prefix, index)
    server_info = {
        "server": {
            "name": vm_name,
            "imageRef": options.default_image,
            "flavorRef": options.default_flavor,
            "networks": [{"uuid": options.default_network}]
        }
    }
    ret_ok = server.create_server(token=token,
                                  server_info=server_info,
                                  handle_obj=vm_name)
    if ret_ok:
        vm_id = ret_ok.get("id")
        server.get_server(token=token, server_id=vm_id, handle_obj=vm_id)
    else:
        vm_id = None
    return vm_id


def test_create_server(vm_prefix, create_num=1):
    token = sync_get_session()
    params = [{"token": token, "vm_prefix": vm_prefix, "index": i}
              for i in range(create_num)]
    for result in pool.imap(_create_server, params):
        if result:
            log_vm(result)


def _delete_server(delete_info):
    vm_id = delete_info.get("vm_id")
    if not vm_id:
        return

    token = delete_info.get("token")
    ret_ok = server.delete_server(token=token,
                                  server_id=vm_id,
                                  handle_obj=vm_id)
    return ret_ok


def test_delete_server():
    token = sync_get_session()
    with file(FILE_VMS, mode='r') as vms:
        params = [{"token": token, "vm_id": vm_id.strip("\n"),
                   "handle_obj": vm_id} for vm_id in vms]
        for result in pool.imap(_delete_server, params):
            pass

    with file(FILE_VMS, mode="w") as vms:
        vms.truncate()


def main():
    os.chdir(sys.path[0])
    test_type = sys.argv[1]
    if test_type:
        try:
            vm_num = int(sys.argv[2])
        except (IndexError, ValueError):
            vm_num = 40

        try:
            create = int(sys.argv[3])
        except (IndexError, ValueError):
            create = 1

        LOG.info(u"测试%s性能, %s %s VM, Time: %s" %
                 (test_type, u"创建" if create else u"删除", vm_num, gen_local_time()))

        if create:

            vm_prefix = "%s_%s_%s" % (options.vm_prefix, vm_num, test_type)
            test_create_server(vm_prefix=vm_prefix, create_num=vm_num)
        else:
            test_delete_server()


if __name__ == "__main__":
    main()

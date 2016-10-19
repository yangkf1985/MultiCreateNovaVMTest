#! /usr/lib/env python
# -*- coding: utf-8 -*-

""" created by yang on 2016/9/7
"""
import os
import sys
from utils import db
from utils.log import LOG
from utils.common import gen_local_time
from utils.options import get_options

__author__ = "muyidixin2006@126.com"
options = get_options()


def main():
    os.chdir(sys.path[0])
    test_type = sys.argv[1]
    if test_type:
        try:
            vm_num = int(sys.argv[2])
        except (IndexError, ValueError):
            vm_num = 1

        LOG.info(u"测试%s性能, 获取 %s VM, Time: %s" %
                 (test_type, vm_num, gen_local_time()))
        csv_file = "test_vm_%s_%s.csv" % (vm_num, test_type)
        db.get_servers_and_save(csv_file, server_name_prefix=test_type, server_count=vm_num)


if __name__ == "__main__":
    main()

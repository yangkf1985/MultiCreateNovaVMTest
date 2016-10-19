#! /usr/lib/env python
# -*- coding: utf-8 -*-

""" created by yang on 2016/9/6
"""
import eventlet
from utils import request
from utils.log import LOG
from utils.common import timeit, \
    ping_vm_port
from utils import exception
from utils.options import get_options


__author__ = "muyidixin2006@126.com"
__all__ = ["create_server",
           "delete_server",
           "get_server"]

server_opts = [
    {
        "name": "request_timeout_seconds",
        "default": 30,
        "help": "ASP request timeout seconds",
        "type": int
    },
]

options = get_options(server_opts, 'server')


@timeit
def create_server(token, server_info, handle_obj):
    try:
        ret_ok = request.sync_ops_request(token=token,
                                          service_type=request.TYPE_COMPUTE,
                                          url="/servers",
                                          body=server_info,
                                          method=request.METHOD_POST,
                                          response_key="server")
    except Exception as e:
        LOG.error("create server error: %s" % e)
        return None
    else:
        return ret_ok


@timeit
def delete_server(token, server_id, handle_obj):
    try:
        url = "/servers/%s" % server_id
        ret_ok = request.sync_ops_request(token=token,
                                          service_type=request.TYPE_COMPUTE,
                                          url=url,
                                          method=request.METHOD_DELETE)
    except Exception as e:
        LOG.error("delete server error: %s" % e)
        return None
    else:
        return ret_ok


def __get_server(token, server_id):
    try:
        url = "/servers/%s" % server_id
        ret_ok = request.sync_ops_request(token=token,
                                          service_type=request.TYPE_COMPUTE,
                                          url=url,
                                          method=request.METHOD_GET,
                                          response_key="server")
    except Exception as e:
        LOG.error("get server error: %s" % e)
        return None
    else:
        if ret_ok and ret_ok.get("metadata"):
            return ret_ok.get("metadata")
        else:
            return None


@timeit
def get_server(token, server_id, handle_obj):
    try:
        loop_counter = 0
        while 1:
            loop_counter += 1
            server_metadata = __get_server(token=token, server_id=server_id)
            if not server_metadata:
                continue

            server_ip = server_metadata.get("host_ip")
            server_port = int(server_metadata.get("port"))
            ping_ok = ping_vm_port(server_ip=server_ip, server_port=server_port)
            if ping_ok:
                LOG.info("server %s 's ip: %s and port: %s network be reasonable."
                         % (server_id, server_ip, server_port))
                break
            eventlet.sleep(1)
            if loop_counter >= options.request_timeout_seconds:
                raise exception.RequestTimeOut()
    except Exception as e:
        LOG.error("get server status ok error %s" % e)


def main():
    pass


if __name__ == "__main__":
    main()

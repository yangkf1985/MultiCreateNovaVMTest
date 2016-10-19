#! /usr/lib/env python
# -*- coding: utf-8 -*-

""" created by yang on 2016/7/15
"""
import requests
import simplejson as json

from utils.log import LOG
from utils import exception
from utils.options import get_options

__author__ = "muyidixin2006@126.com"

TYPE_COMPUTE = "compute"
TYPE_NETWORK = "network"
TYPE_VOLUME = "volumev2"
TYPE_IDENTITY = "identity"
TYPE_IMAGE = "image"
TYPE_METERING = "metering"
TYPE_HEAT = "orchestration"

METHOD_POST = "POST"
METHOD_GET = "GET"
METHOD_PUT = "PUT"
METHOD_DELETE = "DELETE"
METHOD_PATCH = "PATCH"

REQUEST_TYPES = (TYPE_COMPUTE, TYPE_IDENTITY, TYPE_NETWORK,
                 TYPE_VOLUME, TYPE_IMAGE, TYPE_METERING, TYPE_HEAT)

INTF_TYPE_ADMIN = "admin"
INTF_TYPE_PUBLIC = "public"
INTF_TYPE_INTERNAL = "internal"
__SESSION = ""

RESPONSE_OK = 200
RESPONSE_ACCEPTED = 202
RESPONSE_NO_CONTENT = 204
RESPONSE_OKS = (RESPONSE_OK, RESPONSE_ACCEPTED)

__all__ = ["async_request",
           "ops_request",
           "sync_request",
           "sync_get_session",
           "sync_ops_request",
           "TYPE_HEAT",
           "TYPE_COMPUTE",
           "TYPE_IMAGE",
           "TYPE_IDENTITY",
           "TYPE_METERING",
           "TYPE_NETWORK",
           "TYPE_VOLUME",
           "METHOD_POST",
           "METHOD_GET",
           "METHOD_PUT",
           "METHOD_DELETE",
           "METHOD_PATCH",
           "Response"]

request_options = [
    {
        "name": "auth_url",
        "default": "http://keystone.halfss.com:35357/v2.0",
        "help": "the endpoint of keystone url",
        "type": str
    },
    {
        "name": "tenant_name",
        "default": "admin",
        "help": "default auth tenant",
        "type": str
    },
    {
        "name": "user_name",
        "default": "admin",
        "help": "default auth user",
        "type": str
    },
    {
        "name": "user_password",
        "default": "admin_pass",
        "help": "default auth user password",
        "type": str
    },
    {
        "name": "region_name",
        "default": "RegionOne",
        "help": "default region name",
        "type": str
    },
]

options = get_options(request_options, "request")


class Session(object):
    id = str
    urls = dict
    token = str
    tenant_id = str
    user_id = str

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", None)
        self.urls = kwargs.get("urls", None)
        self.token = kwargs.get("token", None)
        self.tenant_id = kwargs.get("tenant_id", None)
        self.user_id = kwargs.get("user_id", None)


class Response(object):
    success = bool
    msg = str
    code = int
    result = object

    def __init__(self, **kwargs):
        self.success = kwargs.get('success', True)
        self.msg = kwargs.get('msg', 'success')
        self.result = kwargs.get('result', None)
        self.code = kwargs.get('code', 200)


def __gen_header(method, token=None):
    """
    generate request header.
    :param token: request token,default None.
    :return: the dict of request header
    """
    hdr = {"Accept": "*/*"}
    if token:
        hdr["X-Auth-Token"] = token
    if method == METHOD_PATCH:
        hdr["Content-Type"] = "application/openstack-images-v2.1-json-patch"
    else:
        hdr["Content-Type"] = "application/json"

    return hdr


def __sync_get_admin_token():
    """get in activities admin token
    :return:token
    """
    global __SESSION
    try:
        if __SESSION:
            sync_verify_token(__SESSION.id)
        else:
            __SESSION = __sync_get_token()
    except Exception as e:
        __SESSION = __sync_get_token(tenant=None)
        raise e
    return __SESSION


def sync_verify_token(token):
    """
    verify request token
    :param token: request token
    :return: verify result
    """
    try:
        verify_token_body = {"auth": {"token": {"id": token},
                                      "tenantName": options.tenant_name}}
        resp = sync_request(url=options.auth_url, body=verify_token_body, method=METHOD_POST)
        if resp:
            session = __get_session(resp)
        else:
            raise exception.OpenStackError
    except Exception as e:
        LOG.error(e)
        raise e
    return session


def sync_get_session(tenant=None, username=None, password=None):
    if tenant:
        token = __sync_get_token(tenant=tenant,
                                 username=username,
                                 password=password)
    else:
        token = __sync_get_admin_token()
    return token


def __sync_get_token(tenant=None, username=None, password=None):
    """
    get the token of specific tenant, default tenant is admin, user is admin.
    :param tenant: tenant id, default None
    :return: the session of specific tenant
    """
    try:
        login_body = __gen_auth_body(tenant=tenant,
                                     username=username,
                                     password=password)

        resp = sync_request(url=options.auth_url,
                            body=login_body,
                            method=METHOD_POST,
                            response_key="access")
        if resp:
            session = __get_session(resp)
        else:
            raise exception.OpenStackError
    except Exception as e:
        LOG.error(e)
        raise e
    return session


def __gen_auth_body(tenant=None, username=None, password=None):
    login_body = {"auth": {"tenantName": options.tenant_name,
                           "passwordCredentials": {"username": options.user_name,
                                                   "password": options.user_password}}}
    if tenant:
        login_body["auth"].pop("tenantName")
        login_body["auth"]["tenantId"] = tenant
    if username and password:
        login_body["auth"]["passwordCredentials"]["username"] = username
        login_body["auth"]["passwordCredentials"]["password"] = password

    return login_body


def __get_session(token):
    """get the session of OpenStack service link.
    :param token: request token
    :return: the session of request
    """

    try:
        token_id = token.get("token").get("id")
        services = token.get("serviceCatalog")
        tenant_id = token.get("token").get("tenant").get("id")
        user_id = token.get("user").get("id")

        urls = {}
        for item in services:
            if item.get("type") in REQUEST_TYPES:
                for endpoint in item.get("endpoints"):
                    if endpoint.get('region') == options.region_name:
                        urls[item.get("type")] = endpoint

        session = Session(id=token_id, urls=urls,
                          token=token, tenant_id=tenant_id,
                          user_id=user_id)
    except Exception as e:
        LOG.error(e)
        raise e
    return session


def sync_ops_request(token, service_type, url, method,
                     response_key=None, body=None, interface=INTF_TYPE_ADMIN):
    """ sync request OpenStack REST API
    :param token: OpenStack request session: Session
    :param response_key:
    :param service_type: service type
    :param url: request url
    :param method:request method
    :param body:request body
    :param interface: 'admin' - default, 'public', 'internal'
    :return: the dict of response
    """
    interface_key = interface + 'URL'
    if service_type in token.urls \
            and interface_key in token.urls[service_type]:
        service_url = token.urls[service_type][interface_key]
    else:
        raise Exception()
    try:
        url = "%s%s" % (service_url, url)
        resp = sync_request(url=url, method=method,
                            body=body, token=token.id,
                            response_key=response_key)
    except Exception as e:
        LOG.error("ops_request failed: %s" % e)
        raise e
    else:
        return resp


def sync_request(url, method, body=None, headers=None,
                 token=None, response_key=None):
    """
    wrap async request
    :param url: request url
    :param token: OpenStack request session: Session
    :param body: the dict of request body
    :param headers: the dict of request headers
    :param method: request method: GET\POST\DELETE\PUT
    :param response_key:
    :return: the dict of response body
    """
    try:
        hdr = __gen_header(method=method, token=token)
        if headers:
            hdr = hdr.copy()
            hdr.update(hdr, **headers)

        if body:
            str_body = json.dumps(body)
        else:
            str_body = None

        if method == METHOD_GET:
            resp = requests.get(url=url, headers=hdr)
        elif method == METHOD_POST:
            resp = requests.post(url=url, data=str_body, headers=hdr)
        elif method == METHOD_PUT:
            resp = requests.put(url=url, data=str_body,  headers=hdr)
        elif method == METHOD_DELETE:
            resp = requests.delete(url=url, headers=hdr)
        elif method == METHOD_PATCH:
            resp = requests.patch(url=url, data=str_body, headers=hdr)
        else:
            raise exception.UnSupportMethodError(method=method)
    except Exception as e:
        LOG.error("sync_request failed: %s" % e)
        raise e
    else:
        if resp.status_code in RESPONSE_OKS:
            rep = resp.json()
            if response_key and response_key in rep:
                rep = rep[response_key]
        elif resp.status_code == RESPONSE_NO_CONTENT:
            rep = None
        else:
            LOG.error("sync_request failed: %s" % resp.json())
            rep = None
    return rep


def main():
    session = sync_get_session()
    print(session.id)


if __name__ == "__main__":
    main()

#! /usr/lib/env python
# -*- coding: utf-8 -*-

""" created by yang on 2016/7/27
"""
from utils.log import LOG

__author__ = "muyidixin2006@126.com"


class PrePoolException(Exception):
    message = "An unknown exception occurred."
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.message % kwargs

            except Exception as e:
                message = self.message
                LOG.error(e)

        super(PrePoolException, self).__init__(message)


class RequiredParamNotExist(PrePoolException):
    """required params is not exist
    """
    message = "Param %(param_name)s is required, can not be found"
    code = 400


class InvalidateParam(PrePoolException):
    """invalidate  param
    """
    message = "Param %(param_name)s invalidate"
    code = 400


class TimeOut(PrePoolException):
    message = "Request Timeout"
    code = 408


class DialogueTimeOut(TimeOut):
    """required time out
    """
    message = "Dialogue timeout"


class RequestTimeOut(TimeOut):
    """required time out
    """
    message = "PrePool Request timeout"


class UnSupportMethodError(PrePoolException):
    """ can not support request method
    """
    message = "Request method: %(method)s can not support"


class OpenStackError(PrePoolException):
    """ openstack error
    """
    message = "OpenStack Error"


class ClassCastException(PrePoolException):
    message = "Class %(class_name)s can not be cast"


class Duplicate(PrePoolException):
    pass


class Error(Exception):
    message = "db error"
    code = 500


class DBError(Error):
    """Wraps an implementation specific exception."""

    def __init__(self, inner_exception=None):
        self.inner_exception = inner_exception
        super(DBError, self).__init__(str(inner_exception))


def wrap_db_error(f):
    def _wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except UnicodeEncodeError as e:
            raise e
        except Exception as e:
            LOG.exception('DB exception wrapped.')
            raise DBError(e)

    _wrap.func_name = f.func_name
    return _wrap


class NotFound(PrePoolException):
    message = "Resource could not be found."
    code = 404


class NotAuth(PrePoolException):
    message = "Unauthorized"
    code = 401



def main():
    pass


if __name__ == "__main__":
    main()

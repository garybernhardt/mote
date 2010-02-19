from __future__ import with_statement
import socket
import urllib2 as mod
from urllib2 import HTTPHandler, URLError

from mote import isolate
from dingus import Dingus, DontCare, exception_raiser
from expecter import expect


@isolate(HTTPHandler, exclude=['URLError'])
def describe_HTTP_handler():
    def describe_with_no_URL():
        req = Dingus(get_host__returns=None)

        def raises_URL_error():
            with expect.raises(URLError):
                HTTPHandler().http_open(req)

        def doesnt_make_a_request():
            assert not current_http_connection().calls('request')

    def describe_making_a_http_connection():
        req = Dingus(get_host__returns='example.com')

        def passes_request_data_to_http_connection():
            HTTPHandler().http_open(req)
            http_connection = current_http_connection()
            assert http_connection.calls('request',
                                         req.get_method(),
                                         req.get_selector(),
                                         req.data,
                                         DontCare).once()

        def raises_URL_error_when_socket_error_happens():
            mod.socket.error = socket.error
            current_http_connection().request = exception_raiser(
                mod.socket.error)
            with expect.raises(URLError):
                HTTPHandler().http_open(req)

    def describe_processing_a_post():
        mod.splittype.return_value = Dingus.many(2)
        mod.splithost.return_value = Dingus.many(2)

        def adds_headers_from_request_object():
            parent = Dingus(addheaders=[('some-header', 'some-value')])
            req = Dingus(has_header__returns=False)
            handler = handler_with_parent_and_request(parent, req)
            assert req.calls('add_unredirected_header',
                             'Some-header',
                             'some-value').once()

        def describe_without_a_content_header():
            parent = Dingus(addheaders=[])
            req = Dingus(has_data__returns=True,
                         has_header={'Content-type': False,
                                     'Content-length': True}.get)
            handler = handler_with_parent_and_request(parent, req)

            def adds_content_header():
                assert req.calls('add_unredirected_header',
                                 'Content-type',
                                 'application/x-www-form-urlencoded').once()


def current_http_connection():
    http_connection_class = mod.httplib.HTTPConnection
    return http_connection_class()


def handler_with_parent_and_request(parent, req):
    handler = HTTPHandler()
    handler.add_parent(parent)
    handler.http_request(req)
    return handler

# Output:
#
# HTTP handler with no URL
#   - raises URL error
#   - doesnt make a request
# HTTP handler making a http connection
#   - passes request data to http connection
#   - raises URL error when socket error happens
# HTTP handler processing a post
#   - adds headers from request object
# HTTP handler processing a post without a content header
#   - adds content header
# OK


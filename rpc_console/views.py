from django.http import HttpResponse

from json_rpc_client import JSONRPCClient

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def json_rpc_client_test(request):
    try:
        JSONRPCClient('', '', '').call(method='', params='')
        return HttpResponse("OK!")
    except Exception as e:
        return HttpResponse(str(e))
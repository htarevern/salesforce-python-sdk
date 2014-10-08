import requests


class HTTPConnection(object):
    def __init__(self):
        super(HTTPConnection, self).__init__()

    def __call__(self, method, url, **kwargs):
        raise NotImplementedError

    def get(self, url, **kwargs):
        raise NotImplementedError

    def post(self, url, **kwargs):
        raise NotImplementedError


class Requests(HTTPConnection):
    __MAX_REQUEST = 15

    def __init__(self):
        super(Requests, self).__init__()

        self.__request = requests.Session()
        self.__request_count = 0

    def __call__(self, method, url, **kwargs):
        return self.__request.request(method, url, **kwargs)

    def get(self, url, **kwargs):
        self.__request_count += 1
        if self.__is_exceeded():
            self.__request.close()

        return self.__request.get(url, **kwargs)

    def post(self, url, **kwargs):
        self.__request_count += 1
        if self.__is_exceeded():
            self.__request.close()

        return self.__request.post(url, **kwargs)

    def set_max_request(self, max_request):
        self.__MAX_REQUEST = max_request

    def __is_exceeded(self):
        return self.__request_count > self.__MAX_REQUEST

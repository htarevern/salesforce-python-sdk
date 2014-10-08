class SObject(object):
    def __init__(self, httplib, auth, url_resources):
        super(SObject, self).__init__()

        self.__httplib = httplib
        self.__auth = auth
        self.__url_resources = url_resources

    @property
    def httplib(self):
        return self.__httplib

    @property
    def auth(self):
        return self.__auth

    @property
    def url_resources(self):
        return self.__url_resources 

    def describe(self):
        raise NotImplementedError

    def create(self, data):
        raise NotImplementedError

    def update(self, data):
        raise NotImplementedError

    def delete(self, data):
        raise NotImplementedError

    def post(self, data, **kwargs):
        raise NotImplementedError

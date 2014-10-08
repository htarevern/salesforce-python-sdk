from login import Authentication
from httpClient import Requests
from httpClient import HTTPConnection


class SalesforceAPI(object):
    def __init__(self, url_resources, httplib=Requests(),  auth=None):
        super(SalesforceAPI, self).__init__()

        self.__httplib = httplib
        self.__url_resources = url_resources
        self.__auth = auth
        self.__login = None

    @property
    def url_resources(self):
        return self.__url_resources

    @property
    def auth(self):
        return self.__auth

    @auth.setter
    def auth(self, auth):
        if not isinstance(auth, Authentication):
            raise TypeError("Must be a subclass of Authentication!")

        self.__auth = auth

    @property
    def httplib(self):
        return self.__httplib

    @httplib.setter
    def httplib(self, httplib):
        if not isinstance(httplib, HTTPConnection):
            raise TypeError("Must be a subclass of HTTPConnection!")

        self.__httplib = httplib

    def __getattr__(self, name):
        raise NotImplementedError

    def authenticate(self, **kwargs):
        raise NotImplementedError

    def query(self, query_string):
        raise NotImplementedError

    def query_all(self, query_string):
        raise NotImplementedError

    def query_more(self, query_url):
        raise NotImplementedError

    def search(self, search_string):
        raise NotImplementedError

    def get(self, params, **kwargs):
        raise NotImplementedError

    def post(self, data, url_or_action):
        raise NotImplementedError
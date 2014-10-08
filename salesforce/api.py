from salesforceSoapApi import SalesforceSoapAPI
from salesforceRestApi import SalesforceRestAPI
from version import Version
from httpClient import HTTPConnection
from httpClient import Requests
from urlResources import RestUrlResources, SoapUrlResources
import utils


class Salesforce(object):
    def __init__(self, **kwargs):
        super(Salesforce, self).__init__()

        self.__api = None

        self.__sandbox = None
        self.__soap = None
        self.__httplib = None
        self.__version = None
        self.__domain = None

        self.sandbox = kwargs.get('sandbox', False)
        self.soap = kwargs.get('soap', False)
        self.httplib = kwargs.get('httplib', Requests())
        self.domain = kwargs.get('domain', 'test' if self.sandbox else 'login')
        self.version = kwargs.get('version', Version.get_latest_version(self.httplib))

        self.__api = self.__get_api(self.soap)

    def get_auth_uri(self, **kwargs):
        return self.__get_api(False).get_auth_uri(**kwargs)

    def authenticate(self, soap=None, **kwargs):
        self.__api.auth = self.__get_api(soap).authenticate(**kwargs)

    def query(self, query_string, soap=None):
        return self.__get_api(soap).query(query_string)

    def query_all(self, query_string, soap=None):
        return self.__get_api(soap).query_all(query_string)

    def query_more(self, query_url, soap=None):
        return self.__get_api(soap).query_more(query_url)

    def search(self, search_string, soap=None):
        return self.__get_api(soap).search(search_string)

    def get(self, get_url, params=None, soap=None, **kwargs):
        return self.__get_api(soap).get(get_url, params)

    def post(self, post_url, data, soap=None):
        return self.__get_api(soap).post(post_url, data)

    def __getattr__(self, name):
        if not name[0].isalpha():
            return super(Salesforce, self).__getattribute__(name)

        return SObjectFacade(
            name, self.__api, self.domain, self.sandbox, self.version, self.soap)

    @property
    def sandbox(self):
        return self.__sandbox

    @sandbox.setter
    def sandbox(self, sandbox):
        utils.validate_boolean_input(sandbox, 'sanbox')

        self.__sandbox = sandbox

        if self.__api is not None:
            print self.__api.url_resources.sandbox
            self.__api.url_resources.sandbox = sandbox
            self.__api.url_resources.domain = 'test' if self.sandbox else 'login'

    @property
    def soap(self):
        return self.__soap

    @soap.setter
    def soap(self, soap):
        utils.validate_boolean_input(soap, 'soap')

        if self.__api is not None:
            self.__api = self.__get_api(soap)

        self.__soap = soap

    @property
    def httplib(self):
        return self.__httplib

    @httplib.setter
    def httplib(self, httplib):
        if not isinstance(httplib, HTTPConnection):
            raise TypeError("Must be a subclass of HTTPConnection!")

        self.__httplib = httplib

        if self.__api is not None:
            self.__api.httplib = httplib

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, version):
        try:
            round_version = round(version, 1)
        except TypeError:
            raise TypeError('Version should be a number!')

        self.__version = round_version

        if self.__api is not None:
            self.__api.url_resources.version = round_version

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __get_api(self, soap):
        if soap is None:
            soap = self.soap

        if soap == self.soap and self.__api is not None:
            return self.__api
        else:
            auth = None if self.__api is None else self.__api.auth

            if soap:
                url_resources = SoapUrlResources(self.domain, self.sandbox, self.version)
                return SalesforceSoapAPI(url_resources=url_resources,
                                         httplib=self.httplib,
                                         auth=auth)
            else:
                url_resources = RestUrlResources(self.domain, self.sandbox, self.version)
                return SalesforceRestAPI(url_resources=url_resources,
                                         httplib=self.httplib,
                                         auth=auth)


class SObjectFacade(object):
    def __init__(self, name, api, domain, sandbox, version, soap):
        super(SObjectFacade, self).__init__()
        self.__api = api

        self.name = name
        self.domain = domain
        self.sandbox = sandbox
        self.version = version
        self.soap = soap

    def describe(self, soap=None):
        return self.__get_api(soap).__getattr__(self.name).describe()

    def create(self, data, soap=None):
        return self.__get_api(soap).__getattr__(self.name).create(data)

    def update(self, data, soap=None):
        return self.__get_api(soap).__getattr__(self.name).update(data)

    def delete(self, record_id, soap=None):
        return self.__get_api(soap).__getattr__(self.name).delete(record_id)

    def post(self, data, record_id=None, soap=None):
        return self.__get_api(soap).__getattr__(self.name).post(data, record_id)

    def get(self, record_id=None, params=None, soap=None):
        return self.__get_api(soap).__getattr__(self.name).get(record_id, params)

    def __get_api(self, soap):
        if soap is None:
            soap = self.soap

        if soap == self.soap and self.__api is not None:
            return self.__api
        else:
            if soap:
                url_resources = SoapUrlResources(self.domain, self.sandbox, self.version)
                return SalesforceSoapAPI(url_resources=url_resources,
                                         httplib=self.__api.httplib,
                                         auth=self.__api.auth)
            else:
                url_resources = RestUrlResources(self.domain, self.sandbox, self.version)
                return SalesforceRestAPI(url_resources=url_resources,
                                         httplib=self.__api.httplib,
                                         auth=self.__api.auth)

from login import LoginWithRestAPI
from urlResources import ResourcesName
from salesforceApi import SalesforceAPI
from exception import AuthenticationFailed
from sObject import SObject
import utils
import json


class SalesforceRestAPI(SalesforceAPI):
    def __init__(self,
                 httplib,
                 url_resources,
                 auth=None):
        super(SalesforceRestAPI, self).__init__(url_resources, httplib, auth)

        self.__login_api = None

    def authenticate(self, **kwargs):
        if 'code' in kwargs:
            if not self.__login_api:
                raise AuthenticationFailed("You first need to use the get_auth_uri() to get the 'code'")

        else:
            self.__login_api = login_api = LoginWithRestAPI(
                self.httplib,
                self.url_resources,
                **kwargs)

        return self.__login_api.authenticate(**kwargs)

    def get_auth_uri(self, **kwargs):
        self.__login_api = login_api = LoginWithRestAPI(
            self.httplib,
            self.url_resources,
            **kwargs)

        return login_api.get_auth_uri()

    @utils.authenticate
    def query(self, query_string):
        query_url = self.url_resources.get_full_resource_url(
            self.auth.instance_url,
            ResourcesName.get_resource_name("query"))

        params = {'q': query_string}
        return self.get(query_url, params)

    @utils.authenticate
    def query_all(self, query_string):
        query_url = self.url_resources.get_full_resource_url(
            self.auth.instance_url,
            ResourcesName.get_resource_name("queryAll"))

        params = {'q': query_string}
        resp = self.get(query_url, params)

        def do_query_all(response):
            if response['done']:
                return response
            else:
                result = self.query_more(response['nextRecordsUrl'])

                response['done'] = result['done']
                response['totalSize'] += result['totalSize']
                response['records'].extend(result['records'])

                return do_query_all(response)

        return do_query_all(resp)

    @utils.authenticate
    def query_more(self, url):
        query_url = self.url_resources.get_full_resource_url(
            self.auth.instance_url,
            ResourcesName.get_resource_name("query"))

        if url.startswith(query_url,
                          len(self.auth.instance_url)):
            get_url = '{0}/{1}'.format(self.auth.instance_url, url)
        else:
            get_url = '{0}/{1}'.format(query_url, url)

        return self.get(get_url)

    @utils.authenticate
    def search(self, search_string):
        search_url = self.url_resources.get_full_resource_url(
            self.auth.instance_url,
            ResourcesName.get_resource_name("search"))

        params = {'q': search_string}
        print params
        return self.get(search_url, params)

    @utils.authenticate
    def quick_search(self, search_string):
        return self.search('FIND {%s}' % search_string)

    @utils.authenticate
    def get(self, get_url, params=None):
        return self.__send_request('GET',
                                   get_url,
                                   params=params)

    @utils.authenticate
    def post(self, data, post_url):
        return self.__send_request('POST',
                                   post_url,
                                   data=json.dumps(data))

    @utils.authenticate
    def __getattr__(self, name):
        if not name[0].isalpha():
            return object.__getattribute__(self, name)

        return RestSObject(name,
                           self.httplib,
                           self.auth,
                           self.url_resources)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __send_request(self, method, url, **kwargs):
        headers = utils.json_content_headers(self.auth.access_token)

        request_url = utils.get_request_url(url, self.auth.instance_url, self.url_resources.get_resource_url())

        return utils.send_request(method,
                                  self.httplib,
                                  request_url,
                                  headers,
                                  **kwargs)


class RestSObject(SObject):
    def __init__(self, name, httplib, auth, url_resources):
        super(RestSObject, self).__init__(httplib, auth, url_resources)

        self.__name = name

    @utils.authenticate
    def describe(self):
        return self.get('/describe')

    @utils.authenticate
    def create(self, data):
        return self.post(data)

    @utils.authenticate
    def update(self, data):
        if not isinstance(data, list):
            raise TypeError("'update' require a parameter type 'list'")

        record_id = data[0]
        records = data[1]

        update_url = '{0}/{1}'.format(
            self.url_resources.get_resource_sobject_url(
                self.auth.instance_url,
                ResourcesName.get_resource_name("sobject"),
                self.__name),
            record_id)

        return self.__send_request('PATCH',
                                   update_url,
                                   data=json.dumps(records))

    @utils.authenticate
    def delete(self, record_id):
        delete_url = '{0}/{1}'.format(
            self.url_resources.get_resource_sobject_url(
                self.auth.instance_url,
                ResourcesName.get_resource_name("sobject"),
                self.__name),
            record_id)

        return self.__send_request('DELETE',
                                   delete_url)

    @utils.authenticate
    def post(self, data, record_id=None):
        post_url = self.url_resources.get_resource_sobject_url(
            self.auth.instance_url,
            ResourcesName.get_resource_name("sobject"),
            self.__name)

        if record_id is not None:
            post_url += '/' + record_id

        return self.__send_request('POST',
                                   post_url,
                                   data=json.dumps(data))

    @utils.authenticate
    def get(self, url=None, params=None):
        get_url = self.url_resources.get_resource_sobject_url(
            self.auth.instance_url,
            ResourcesName.get_resource_name("sobject"),
            self.__name)

        if url is not None:
            get_url += url

        return self.__send_request('GET',
                                   get_url,
                                   params=params)

    def __send_request(self, method, url, **kwargs):
        headers = utils.json_content_headers(self.auth.access_token)

        request_url = utils.get_request_url(url, self.auth.instance_url, self.url_resources.get_resource_url())

        return utils.send_request(method,
                                  self.httplib,
                                  request_url,
                                  headers,
                                  **kwargs)

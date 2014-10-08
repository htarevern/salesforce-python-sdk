from salesforceApi import SalesforceAPI
from login import LoginWithSoapAPI
from sObject import SObject
import utils
import xml.dom.minidom


class SalesforceSoapAPI(SalesforceAPI):
    def __init__(self,
                 httplib,
                 url_resources,
                 auth=None):
        super(SalesforceSoapAPI, self).__init__(url_resources, httplib, auth)

        self.__login_api = None

    def authenticate(self, **kwargs):
        self.__login_api = LoginWithSoapAPI(
            self.httplib,
            self.url_resources,
            **kwargs)

        return self.__login_api.authenticate()

    @utils.authenticate
    def query(self, query_string):
        return self.post(query_string, SalesforceSoapAPI.Action.QUERY)

    @utils.authenticate
    def query_all(self, query_string):
        response = self.post(query_string, SalesforceSoapAPI.Action.QUERYALL)
        xml_resp_value = xml.dom.minidom.parseString(response.text)

        def do_query_all(xml_response_value):
            done = utils.get_element_by_name(xml_response_value, 'done')

            if done:
                return response
            else:
                query_locator = utils.get_element_by_name(xml_response_value, 'queryLocator')

                result = self.query_more(query_locator)
                xml_result_value = xml.dom.minidom.parseString(result.text)

                done = utils.get_element_by_name(xml_result_value, 'done')
                total_size = utils.get_element_by_name(xml_result_value, 'totalSize')
                records = utils.get_element_by_name(xml_result_value, 'records')

                xml_response_value.getElementsByTagName('done').item(0).firstChild.nodeValue = done
                xml_response_value.getElementsByTagName('totalSize').item(0).firstChild.nodeValue += total_size
                xml_response_value.getElementsByTagName('records').appendChild(records)

                return do_query_all(xml_response_value)

        return do_query_all(xml_resp_value)

    @utils.authenticate
    def query_more(self, query_string):
        return self.post(query_string, SalesforceSoapAPI.Action.QUERYMORE)

    @utils.authenticate
    def search(self, search_string):
        return self.post(search_string, SalesforceSoapAPI.Action.SEARCH)

    @utils.authenticate
    def quick_search(self, search_string):
        return self.search('FIND {%s}' % search_string)

    @utils.authenticate
    def post(self, data, action):
        body = ''

        if action == SalesforceSoapAPI.Action.QUERY:
            body = query_body = utils.get_soap_query_body(data)

        elif action == SalesforceSoapAPI.Action.QUERYMORE:
            body = utils.get_soap_query_more_body(data)

        elif action == SalesforceSoapAPI.Action.QUERYALL:
            body = utils.get_soap_query_body(data)

        elif action == SalesforceSoapAPI.Action.SEARCH:
            body = utils.get_soap_search_body(data)

        else:
            raise ValueError("'action' " + action + " is not supported!")

        request_body = utils.soap_request_header().format(
            access_token=self.auth.access_token,
            method=action,
            request=body)

        post_url = self.url_resources.get_full_resource_url(
            self.auth.instance_url)

        return self.__send_request('POST',
                                   post_url,
                                   action,
                                   data=request_body)

    @utils.authenticate
    def get(self, get_url, params=None):
        pass

    @utils.authenticate
    def __getattr__(self, name):
        if not name[0].isalpha():
            return object.__getattribute__(self, name)

        return SoapSObject(name,
                           self.httplib,
                           self.auth,
                           self.url_resources)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    def __send_request(self, method, url, action, **kwargs):
        headers = utils.xml_content_headers(len(kwargs['data']), action)

        request_url = utils.get_request_url(url, self.auth.instance_url, self.url_resources.get_resource_url())

        return utils.send_request(method,
                                  self.httplib,
                                  request_url,
                                  headers,
                                  **kwargs)

    class Action(object):
        QUERY = 'query'
        QUERYALL = 'queryAll'
        QUERYMORE = 'queryMore'
        SEARCH = 'search'


class SoapSObject(SObject):
    def __init__(self, name, httplib, auth, url_resources):
        super(SoapSObject, self).__init__(httplib, auth, url_resources)

        self.__name = name

    @utils.authenticate
    def describe(self):
        return self.post(None, SoapSObject.Action.DESCRIBE)

    @utils.authenticate
    def create(self, data):
        if not isinstance(data, list):
            raise TypeError("'create' require a parameter type 'list'")

        return self.post(data, SoapSObject.Action.CREATE)

    @utils.authenticate
    def update(self, data):
        if not isinstance(data, list):
            raise TypeError("'update' require a parameter type 'list of lists'")

        return self.post(data, SoapSObject.Action.UPDATE)

    @utils.authenticate
    def delete(self, record_ids):
        if not isinstance(record_ids, list):
            raise TypeError("'update' require a parameter type 'list of lists'")

        return self.post(record_ids, SoapSObject.Action.DELETE)

    @utils.authenticate
    def post(self, data, action=None):
        if action is None:
            raise ValueError("'action' is required")

        if action != SoapSObject.Action.DESCRIBE and not isinstance(data, list):
            raise TypeError("'create' require a parameter type 'list'")

        body = ''
        if action == SoapSObject.Action.DESCRIBE:
            body = utils.get_soap_describe_body(self.__name)

        elif action == SoapSObject.Action.CREATE:
            body = utils.get_soap_create_body(self.__name, data)

        elif action == SoapSObject.Action.UPDATE:
            body = utils.get_soap_update_body(self.__name, data)

        elif action == SoapSObject.Action.DELETE:
            body = utils.get_soap_delete_body(data)

        else:
            raise ValueError("'action' " + action + " is not supported!")

        request_body = utils.soap_request_header().format(
            access_token=self.auth.access_token,
            method=action,
            request=body)

        post_url = self.url_resources.get_full_resource_url(
            self.auth.instance_url)

        return self.__send_request('POST',
                                   post_url,
                                   action,
                                   data=request_body)

    @utils.authenticate
    def get(self, record_id=None, params=None):
        pass

    def __send_request(self, method, url, action, **kwargs):
        headers = utils.xml_content_headers(len(kwargs['data']), action)

        request_url = utils.get_request_url(url, self.auth.instance_url, self.url_resources.get_resource_url())

        return utils.send_request(method,
                                  self.httplib,
                                  request_url,
                                  headers,
                                  **kwargs)

    class Action(object):
        DESCRIBE = 'describeSObject'
        CREATE = 'create'
        DELETE = 'delete'
        UPDATE = 'update'

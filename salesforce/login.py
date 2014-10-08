import urllib
import utils
from urlparse import urlparse
from exception import AuthenticationFailed
import xml.dom.minidom


class Authentication(object):
    def __init__(self, access_token='', instance_url=''):
        super(Authentication, self).__init__()

        self.__access_token = access_token
        self.__instance_url = instance_url

    @property
    def access_token(self):
        return self.__access_token

    @property
    def instance_url(self):
        return self.__instance_url

    def is_authenticated(self):
        return self.access_token != '' and self.instance_url != ''


class Login(object):
    def __init__(self, httplib, url_resources):
        super(Login, self).__init__()

        self.httplib = httplib
        self.url_resources = url_resources


class LoginWithRestAPI(Login):
    AUTH_SITE = 'https://{domain}.salesforce.com'
    TOKEN_PATH = '/services/oauth2/token'
    AUTH_PATH = '/services/oauth2/authorize'

    def __init__(self, httplib, url_resources, **kwargs):
        super(LoginWithRestAPI, self).__init__(httplib, url_resources)

        self.__validate_kwargs(**kwargs)

        if 'response_type' in kwargs and kwargs['response_type'] == 'code':
            self.redirect_uri = kwargs['redirect_uri']
            self.response_type = kwargs['response_type']
            self.client_secret = kwargs['client_secret']
            self.client_id = kwargs['client_id']
            self.redirect = True

        else:
            self.username = kwargs['username']
            self.password = kwargs['password']
            self.client_secret = kwargs['client_secret']
            self.client_id = kwargs['client_id']
            self.redirect = False

    def get_auth_uri(self):
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        endpoint_url = self.__get_auth_endpoint()
        params = self.__get_server_or_user_params()
        print params
        return endpoint_url + '?' + urllib.urlencode(params)

    def authenticate(self, **kwargs):
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        endpoint_url = self.__get_token_endpoint()
        data = None

        if self.redirect:
            if 'code' not in kwargs:
                raise AuthenticationFailed("You first need to use the get_auth_uri() to get the 'code'")

            code = kwargs['code']
            data = self.__get_token_using_code_params(code)
        else:
            data = self.__get_token_using_password_params()

        response = utils.send_request('POST',
                                      self.httplib,
                                      endpoint_url,
                                      headers,
                                      data=data)

        access_token = response['access_token']
        instance_url = response['instance_url']

        return Authentication(access_token, instance_url)

    def __get_token_endpoint(self):
        domain_name = self.url_resources.domain

        return '{0}{1}'.format(
            self.AUTH_SITE.format(domain=domain_name),
            self.TOKEN_PATH)

    def __get_auth_endpoint(self):
        domain_name = self.url_resources.domain

        return '{0}{1}'.format(
            self.AUTH_SITE.format(domain=domain_name),
            self.AUTH_PATH)

    @staticmethod
    def __validate_kwargs(**kwargs):
        if 'response_type' in kwargs:
            if 'response_type' not in kwargs or \
               'client_id' not in kwargs or \
               'client_secret' not in kwargs or \
               'redirect_uri' not in kwargs:

                raise ValueError("Required fields: 'response_type', 'client_id',"
                                 "'client_secret', and 'redirect_uri'")

            if kwargs['response_type'] != 'code':
                raise ValueError("Required fields: 'response_type': 'code' or 'token'")
        else:
            if 'client_id' not in kwargs or \
               'client_secret' not in kwargs or \
               'username' not in kwargs or \
               'password' not in kwargs:

                raise ValueError("Required fields: 'client_id', 'client_secret', 'username', and 'password'")

    def __get_token_using_password_params(self):
        return {'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': self.username,
                'password': self.password}

    def __get_token_using_code_params(self, code):
        return {'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'code': code}

    def __get_server_or_user_params(self):
        return {'response_type': self.response_type,
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri}


class LoginWithSoapAPI(Login):
    AUTH_SITE = "https://{domain}.salesforce.com/services/Soap/u/{version}"

    def __init__(self, httplib, url_resources, **kwargs):
        super(LoginWithSoapAPI, self).__init__(httplib, url_resources)

        self.__validate_kwargs(**kwargs)

        self.username = kwargs['username']
        self.password = kwargs['password']

    def authenticate(self):
        login_url = self.__get_token_endpoint()
        data = self.__get_params()
        headers = utils.xml_content_headers(len(data), 'login')

        response = utils.send_request('POST',
                                      self.httplib,
                                      login_url,
                                      headers,
                                      data=data)

        xml_value = xml.dom.minidom.parseString(response.text)
        access_token = utils.get_element_by_name(xml_value, 'sessionId')
        url = urlparse(utils.get_element_by_name(xml_value, 'serverUrl'))
        instance_url = '{0}://{1}'.format(url.scheme, url.netloc)

        return Authentication(access_token, instance_url)

    def __get_token_endpoint(self):
        domain_name = self.url_resources.domain

        return self.AUTH_SITE.format(
            domain=domain_name,
            version=self.url_resources.version)

    @staticmethod
    def __validate_kwargs(**kwargs):
        if 'username' not in kwargs or \
           'password' not in kwargs:

            raise ValueError("Required fields: 'username', and 'password'")

    def __get_params(self):
        login_body = utils.get_soap_login_body(
            self.username,
            self.password)

        return utils.soap_login_header().format(
            request=login_body)

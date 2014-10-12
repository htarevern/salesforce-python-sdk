import requests
from exception import RequestFailed, AuthenticationFailed


def json_content_headers(access_token):
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token,
        'X-PrettyPrint': '1',
        'Accept': 'application/json'
    }


def xml_content_headers(length, action):
    return {
        'Content-Type': 'text/xml',
        'charset': 'utf-8',
        'Content-length': '%d' % length,
        'SOAPAction': action,
    }


def get_soap_env():
    return """<?xml version="1.0" encoding="utf-8" ?>
        <soapenv:Envelope
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:urn="urn:partner.soap.sforce.com"
            xmlns:urn1="urn:sobject.partner.soap.sforce.com"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            {header}
            {body}
        </soapenv:Envelope>"""


def get_soap_header():
    return '''<soapenv:Header>
                  <urn:SessionHeader>
                      <urn:sessionId>{access_token}</urn:sessionId>
                  </urn:SessionHeader>
              </soapenv:Header>'''


def get_soap_body():
    return '''<soapenv:Body>
                  <urn:{method}>
                      {request}
                  </urn:{method}>
              </soapenv:Body>'''


def get_login_soap_body():
    return '''<soapenv:Body>
                  {request}
              </soapenv:Body>'''


def get_soap_login_body(username, password):
    return '''
        <n1:login xmlns:n1="urn:partner.soap.sforce.com">
            <n1:username>{0}</n1:username>
            <n1:password>{1}</n1:password>
        </n1:login>'''.format(username, password)


def soap_login_header():
    return get_soap_env().format(
        header='',
        body=get_login_soap_body())


def soap_request_header():
    return get_soap_env().format(
        header=get_soap_header(),
        body=get_soap_body())


def get_soap_query_body(query_string):
    return '<urn:queryString>{0}</urn:queryString>'.format(query_string)


def get_soap_query_more_body(query_string):
    return '<urn:queryLocator>{0}</urn:queryLocator>'.format(query_string)


def get_soap_search_body(search_string):
    return '<urn:searchString>{0}</urn:searchString>'.format(search_string)


def get_soap_describe_body(sobject):
    return '<urn:sObjectType>{0}</urn:sObjectType>'.format(sobject)


def get_soap_create_body(sobject, data):
    create_body = ''

    for item in data:
        create_body += '<urn:sObjects xsi:type="urn1:{0}"> \n'.format(sobject)

        for key, value in item.iteritems():
            create_body += '<{0}>{1}</{0}> \n'.format(key, value)

        create_body += '</urn:sObjects> \n'

    return create_body


def get_soap_delete_body(ids):
    delete_body = ''

    for sf_id in ids:
        delete_body += '<urn:Ids>{0}</urn:Ids>'.format(sf_id)

    return delete_body


def get_soap_update_body(sobject, data):
    update_body = ''

    for item in data:
        if not isinstance(item, list):
            raise TypeError("'update' require a parameter type 'list of lists'")

        update_body += '<urn:sObjects xsi:type="urn1:{0}"> \n'.format(sobject)
        update_body += '<urn:Id>{0}</urn:Id>'.format(item[0])

        for key, value in item[1].iteritems():
            update_body += '<urn:{0}>{1}</urn:{0}> \n'.format(key, value)

        update_body += '</urn:sObjects> \n'

    return update_body


def verify_response(response):
    if response.status_code >= requests.codes.multiple_choices:
        error_code = response.status_code
        message = response.text

        raise RequestFailed(error_code, message)


def send_request(method, httplib, url, headers, **kwargs):
    print method + ": Sending request to " + url + "\n"

    response = httplib(method,
                       url,
                       headers=headers,
                       **kwargs)
    try:
        verify_response(response)
    except RequestFailed:
        raise

    if headers and 'SOAPAction' in headers:
        return response
    else:
        return response.json()


def get_request_url(url, instance_url, resource_url):
    if url.startswith(instance_url + resource_url):
        return url

    elif url.startswith(resource_url):
        return '{0}{1}'.format(instance_url, url)

    return '{0}{1}{2}'.format(instance_url, resource_url, url)


def get_element_by_name(xml_string, element_name):
    elements = xml_string.getElementsByTagName(element_name)

    if len(elements) > 0:
        return elements.item(0).firstChild.nodeValue

    return None


def authenticate(func):
    def authenticate_and_call(self, *args, **kwargs):
        if self.auth is None or not self.auth.is_authenticated():
            raise AuthenticationFailed("You need to first authentificate!")

        return func(self, *args, **kwargs)

    return authenticate_and_call


def validate_boolean_input(value, name):
    if value not in (True, False):
        raise TypeError(name + ' should be True or False')
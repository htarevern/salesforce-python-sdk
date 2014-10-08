salesforce-python-sdk
=====================

Salesforce Python SDK supports Salesforce REST and Partner SOAP APIs.

Install
-------
python setup.py install

Example
-------
    import salesforce as sf
    sfdc = sf.Salesforce()
    
    sfdc.authenticate(client_id=client_id,
                      client_secret=client_secret,
                      username=username,
                      password=password)
    
    #SOAP call
    sfdc.Contact.create(
        [
            {
                'FirstName': 'John',
                'LastName': 'Varges',
            },
            {
                'FirstName': 'Clark',
                'LastName': 'Fisher',
            }
        ],
        soap=True)
    
    #REST Call
    sfdc.Contact.create({
            'FirstName': 'John',
            'LastName': 'Varges'})

You can switch between REST and SOAP by passing soap parameter.


Supported APIs
-------
get_auth_uri
authenticate
query
query_all
query_more
search
get
post

sObject:
describe
create
update
delete
post
get
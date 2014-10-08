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
    get_auth_uri(self, **kwargs)
    
    authenticate(self, soap=None, **kwargs)
    
    query(self, query_string, soap=None)
    
    query_all(self, query_string, soap=None)
    
    query_more(self, query_url, soap=None)
    
    search(self, search_string, soap=None)
    
    get(self, get_url, params=None, soap=None, **kwargs)
    
    post(self, post_url, data, soap=None)

On sObject:

    describe(self, soap=None)
    
    create(self, data, soap=None)
    
    update(self, data, soap=None)
    
    delete(self, record_id, soap=None)
    
    post(self, data, record_id=None, soap=None)
    
    get(self, record_id=None, params=None, soap=None)
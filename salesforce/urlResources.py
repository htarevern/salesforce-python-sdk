class UrlResources(object):
    def __init__(self, domain, sandbox, version):
        super(UrlResources, self).__init__()

        self.domain = domain
        self.sandbox = sandbox
        self.version = version

    def get_resource_url(self):
        return self.get_resource_path().format(version=self.version)

    def get_full_resource_url(self, **kwargs):
        raise NotImplementedError

    def get_resource_path(self):
        raise NotImplementedError


class RestUrlResources(UrlResources):
    RESOURCE_PATH = "/services/data/v{version}"

    def __init__(self, domain, sandbox, version):
        super(RestUrlResources, self).__init__(domain, sandbox, version)

    def get_resource_path(self):
        return RestUrlResources.RESOURCE_PATH

    def get_full_resource_url(self, instance_url, resource_name):
        return '{0}{1}{2}'.format(
            instance_url,
            RestUrlResources.RESOURCE_PATH.format(version=self.version),
            resource_name)

    def get_resource_sobject_url(self,
                                 instance_url,
                                 resource_name,
                                 sobject_name):
        return '{0}{1}'.format(
            self.get_full_resource_url(instance_url, resource_name),
            sobject_name)


class SoapUrlResources(UrlResources):
    RESOURCE_PATH = "/services/Soap/u/{version}"

    def __init__(self, domain, sandbox, version):
        super(SoapUrlResources, self).__init__(domain, sandbox, version)

    def get_resource_path(self):
        return SoapUrlResources.RESOURCE_PATH

    def get_full_resource_url(self, instance_url):
        return '{0}{1}'.format(
            instance_url,
            SoapUrlResources.RESOURCE_PATH.format(version=self.version))


class ResourcesName(object):
    __RESOURCES_NAME = {
        'query': '/query/',
        'queryAll': '/queryAll/',
        'sobject': '/sobjects/',
        'search': '/search/',
    }

    @staticmethod
    def get_resource_name(name):
        if name in ResourcesName.__RESOURCES_NAME:
            return ResourcesName.__RESOURCES_NAME[name]
        else:
            raise ValueError('Not a valid name %s' % name)

import utils


class Version(object):
    VERSION_PATH = "http://na1.salesforce.com/services/data/"

    def __init__(self):
        super(Version, self).__init__()

    @staticmethod
    def get_latest_version(httplib):
        version_api_url = Version.VERSION_PATH
        latest_version = 0

        response = utils.send_request('GET',
                                      httplib,
                                      version_api_url,
                                      None)

        for value in response:
            if float(value['version']) > latest_version:
                latest_version = float(value['version'])

        return latest_version

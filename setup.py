import sys
from setuptools import setup

INSTALL_REQUIRES = ['requests']
assert sys.version_info >= (2, 6), "We only support Python 2.6+"

with open('LICENSE.rst') as f:
    license_text = f.read()

with open('README.rst') as f:
    readme_text = f.read()

setup(
    name='salesforce-python-sdk',
    version='0.1.3',
    description='This is Salesforce Python SDK for REST and SOAP APIs',
    long_description=readme_text,
    author='Hormoz Tarevern',
    author_email='htarevern@yahoo.com',
    url='https://github.com/htarevern/salesforce-python-sdk',
    packages=['salesforce'],
    package_data={'salesforce': ['*rst']},
    install_requires=INSTALL_REQUIRES,
    keywords="Salesforce python sdk salesforce.com salesforce-python-sdk SalesforcePythonSDK",
    license=license_text
)
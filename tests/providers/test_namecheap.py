# Test for one implementation of the interface
from lexicon.providers.dnsimple import Provider
from integration_tests import IntegrationTests
from unittest import TestCase

# Hook into testing framework by inheriting unittest.TestCase and reuse
# the tests which *each and every* implementation of the interface must
# pass, by inheritance from define_tests.TheTests
class NamecheapProviderTests(TestCase, IntegrationTests):

    Provider = Provider
    provider_name = 'namecheap'
    domain = 'capsulecd.com'
    provider_opts = {'api_endpoint': 'https://api.sandbox.namecheap.com/xml.response'}
    def _filter_query_parameters(self):
        return ['ApiKey', 'ApiUser','UserName','ClientIp']
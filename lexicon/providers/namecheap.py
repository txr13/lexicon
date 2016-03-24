from base import Provider as BaseProvider
import requests
import socket
from xml.etree import ElementTree

class Provider(BaseProvider):

    def __init__(self, options, provider_options={}):
        super(Provider, self).__init__(options)
        self.domain_id = None
        self.api_endpoint = provider_options.get('api_endpoint') or 'https://api.namecheap.com/xml.response'

    def authenticate(self):

        payload = self._get('namecheap.domains.getList', {
            'SearchTerm': self.options['domain']
        })

        found_domain = payload.find('CommandResponse').find('DomainGetListResult').find('Domain')
        if not found_domain:
            raise StandardError('No domain found')
        if len(payload.find('CommandResponse').find('DomainGetListResult').findall('Domain')) > 1:
            raise StandardError('Too many domains found. This should not happen')

        self.domain_id = found_domain.get('ID')
    #
    #
    # # Create record. If record already exists with the same content, do nothing'
    # def create_record(self, type, name, content):
    #     payload = self._post('/zones/{0}/dns_records'.format(self.domain_id), {'type': type, 'name': name, 'content': content})
    #
    #     print 'create_record: {0}'.format(payload['success'])
    #     return payload['success']
    #
    # # List all records. Return an empty list if no records found
    # # type, name and content are used to filter records.
    # # If possible filter during the query, otherwise filter after response is received.
    # def list_records(self, type=None, name=None, content=None):
    #     filter = {'per_page': 100}
    #     if type:
    #         filter['type'] = type
    #     if name:
    #         name = name.rstrip('.')  # strip trailing period
    #         #check if the name is fully qualified
    #         if not name.endswith(self.options['domain']):
    #             name = '{0}.{1}'.format(name, self.options['domain'])
    #         filter['name'] = name
    #     if content:
    #         filter['content'] = content
    #
    #     payload = self._get('/zones/{0}/dns_records'.format(self.domain_id), filter)
    #
    #     records = []
    #     for record in payload['result']:
    #         processed_record = {
    #             'type': record['type'],
    #             'name': record['name'],
    #             'ttl': record['ttl'],
    #             'content': record['content'],
    #             'id': record['id']
    #         }
    #         records.append(processed_record)
    #
    #     print 'list_records: {0}'.format(records)
    #     return records
    #
    # # Create or update a record.
    # def update_record(self, identifier, type=None, name=None, content=None):
    #
    #     data = {}
    #     if type:
    #         data['type'] = type
    #     if name:
    #         data['name'] = name
    #     if content:
    #         data['content'] = content
    #
    #     payload = self._put('/zones/{0}/dns_records/{1}'.format(self.domain_id, identifier), data)
    #
    #     print 'update_record: {0}'.format(payload['success'])
    #     return payload['success']
    #
    # # Delete an existing record.
    # # If record does not exist, do nothing.
    # def delete_record(self, identifier=None, type=None, name=None, content=None):
    #     if not identifier:
    #         records = self.list_records(type, name, content)
    #         print records
    #         if len(records) == 1:
    #             identifier = records[0]['id']
    #         else:
    #             raise StandardError('Record identifier could not be found.')
    #     payload = self._delete('/zones/{0}/dns_records/{1}'.format(self.domain_id, identifier))
    #
    #     print 'delete_record: {0}'.format(payload['success'])
    #     return payload['success']


    # Helpers
    def _get(self, command='', query_params={}):
        return self._request('GET', command, query_params=query_params)

    def _post(self, command='', data={}, query_params={}):
        return self._request('POST', command, data=data, query_params=query_params)

    def _put(self, command='', data={}, query_params={}):
        return self._request('PUT', command, data=data, query_params=query_params)

    def _delete(self, command='', query_params={}):
        return self._request('DELETE', command, query_params=query_params)

    def _request(self, action='GET',  command='', data={}, query_params={}):

        query_params['Command'] = command
        query_params['ApiUser'] = self.options['auth_username']
        query_params['ApiKey'] = self.options.get('auth_password') or self.options.get('auth_token')
        query_params['UserName'] = self.options['auth_username']

        # Hacky method to retrieve the current computer's external ip address
        # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        query_params['ClientIp'] = s.getsockname()[0]
        s.close()

        r = requests.request(action, self.api_endpoint, params=query_params,
                             data=json.dumps(data),
                             headers={
                                 'Content-Type': 'application/json'
                             })
        r.raise_for_status()  # if the request fails for any reason, throw an error.

        # TODO: check if the response is an error using
        tree = ElementTree.fromstring(r.content)
        root = tree.getroot()
        if root.attrib['Status'] == 'ERROR':
            #TODO: raise error message here
            print r.content
        else:
            return root
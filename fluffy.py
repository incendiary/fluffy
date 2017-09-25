from Common.common import initalsetup, get_list_from_config_parser
#from Classes.azure import Azure
import getpass
import sys
from beeprint import pp
from Classes.account import Aws_account, Api_access_key
import pytz
from datetime import datetime, timedelta
import os
import json



from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient

## AADTokenCredentials for multi-factor authentication
from msrestazure.azure_active_directory import AADTokenCredentials



## Other required imports
import adal, uuid, time

## AADTokenCredentials for multi-factor authentication
from msrestazure.azure_active_directory import AADTokenCredentials


def authenticate_device_code(client):
    """
    Authenticate the end-user using device auth.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    tenant = client['tenantId']
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'
    client_id = client['clientId']

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    code = context.acquire_user_code(resource_uri, client_id)
    print(code['message'])
    mgmt_token = context.acquire_token_with_device_code(resource_uri, code, client_id)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials

def authenticate_client_key(client):
    """
    Authenticate using service principal w/ key.
    """
    authority_host_uri = 'https://login.microsoftonline.com'
    tenant = client['tenantId']
    authority_uri = authority_host_uri + '/' + tenant
    resource_uri = 'https://management.core.windows.net/'
    client_id = client['clientId']
    client_secret = client['clientSecret']

    context = adal.AuthenticationContext(authority_uri, api_version=None)
    mgmt_token = context.acquire_token_with_client_credentials(resource_uri, client_id, client_secret)
    credentials = AADTokenCredentials(mgmt_token, client_id)

    return credentials

def comparetwodates(date1, date2, deltainseconds):
    if (date1 - date2) > timedelta(seconds=deltainseconds):
        return True
    else:
        return False

if __name__ == "__main__":
    logging, args, config = initalsetup()
    utc = pytz.UTC
    current = datetime.now()
    current_utc = pytz.utc.localize(current)

    last_key_used_delta = config.getint('apikeys', 'lastused')
    longest_key_unused_delta = config.getint('apikeys', 'unused')

    #Azure

    if config.get('azure', 'azureauthenvvar'):

        client = get_client_from_auth_file(ComputeManagementClient)

        #https://github.com/AzureAD/azure-activedirectory-library-for-python/blob/dev/sample/website_sample.py

        parameters_file = os.environ.get('AZURE_AUTH_LOCATION')
        if parameters_file:
            with open(parameters_file, 'r') as f:
                parameters = f.read()
            auth_parameters = json.loads(parameters)
        else:
            raise ValueError('Please provide parameter file with account information.')

        client_dict = {'clientId': auth_parameters.get('clientId').encode('ascii'),
                       "clientSecret" : auth_parameters.get('clientSecret').encode('ascii'),
                       "tenantId" : auth_parameters.get('tenantId').encode('ascii'),
                       "activeDirectoryGraphResourceId" : auth_parameters.get('activeDirectoryGraphResourceId').encode('ascii')
                       }

        print client_dict
        from azure.common.credentials import ServicePrincipalCredentials

        credentials = ServicePrincipalCredentials(
            client_id=client_dict['clientId'],
            secret=client_dict['clientSecret'],
            tenant=client_dict['tenantId'],
            resource=client_dict['activeDirectoryGraphResourceId']
        )

        from azure.graphrbac import GraphRbacManagementClient
        from azure.graphrbac.operations import groups_operations
        from azure.graphrbac.operations import objects_operations


        from azure.graphrbac.operations import users_operations
        #https://docs.microsoft.com/en-us/python/api/azure.graphrbac.models?view=azure-python

        graphrbac_client = GraphRbacManagementClient(
            credentials,
            client_dict['tenantId']
        )

        #print "Current User: %s " % (graphrbac_client.objects.get_current_user())
        #https://stackoverflow.com/questions/43670829/resource-not-found-for-the-segment-me

        for application in graphrbac_client.applications.list():
            print application
            print application.app_id
            try:
                for key in graphrbac_client.applications.list_password_credentials(application_object_id = application.object_id):
                    print key
            except graphrbac.models.graph_error.GraphErrorException as e:
                print "nokey?"

        for user in graphrbac_client.users.list():
            print user
            try:

                groups = graphrbac_client.users.get_member_groups(object_id = user.object_id,
                                                                  security_enabled_only = True)
                print type(groups)
            except AttributeError as e:
                print "no group"
        print "g"
        for group in graphrbac_client.groups.list():

            for AADObject in graphrbac_client.groups.get_group_members(object_id = group.object_id):
                print AADObject
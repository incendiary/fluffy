from msrestazure.azure_active_directory import AADTokenCredentials
from azure.graphrbac import models
from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.compute import ComputeManagementClient
from azure.common.credentials import ServicePrincipalCredentials
import adal
import os
import json
from Classes.accountclass import AzureAccount

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

def azure_application_list(graphrbac_client, this_account):
    for application in graphrbac_client.applications.list():
        print application
        print application.app_id
        try:
            for key in graphrbac_client.applications.list_password_credentials(
                    application_object_id=application.object_id):
                print key
        except models.graph_error.GraphErrorException as e:
            print "nokey?"

def azure_group_list(graphrbac_client, this_account):
    for group in graphrbac_client.groups.list():

        for AADObject in graphrbac_client.groups.get_group_members(object_id=group.object_id):
            print AADObject

def azure_account_list(graphrbac_client, this_account):
    for user in graphrbac_client.users.list():
        print user
        try:
            groups = graphrbac_client.users.get_member_groups(object_id=user.object_id,
                                                              security_enabled_only=True)
            print type(groups)
        except AttributeError as e:
            print "no group"

def azure_client(credentials, client_dict):
    from azure.graphrbac import GraphRbacManagementClient

    graphrbac_client = GraphRbacManagementClient(
        credentials,
        client_dict['tenantId']
    )
    return graphrbac_client


def azure_credentials(config):

    if config.get('azure', 'azureauthenvvar'):
        # here, we should have an env var pointing to azure info

        parameters_file = os.environ.get('AZURE_AUTH_LOCATION')
        if parameters_file:
            with open(parameters_file, 'r') as f:
                parameters = f.read()
            auth_parameters = json.loads(parameters)
            client_dict = {'clientId': auth_parameters.get('clientId').encode('ascii'),
                           "clientSecret": auth_parameters.get('clientSecret').encode('ascii'),
                           "tenantId": auth_parameters.get('tenantId').encode('ascii'),
                           "activeDirectoryGraphResourceId": auth_parameters.get('activeDirectoryGraphResourceId').encode(
                               'ascii')
                           }
        else:
            raise ValueError('Please provide parameter file with account information.')

    elif config.get('azure', 'clientId') and config.get('azure', 'clientSecret') and config.get('azure', 'tenantId') and \
            config.get('azure', 'activeDirectoryGraphResourceId'):
        #here - we  have config info to use

        client_dict = {'clientId': config.get('azure', 'clientId'),
                       "clientSecret": config.get('azure', 'clientSecret'),
                       "tenantId": config.get('azure', 'tenantId'),
                       "activeDirectoryGraphResourceId": config.get('azure', 'activeDirectoryGraphResourceId'),
                       }

    credentials = ServicePrincipalCredentials(
        client_id=client_dict['clientId'],
        secret=client_dict['clientSecret'],
        tenant=client_dict['tenantId'],
        resource=client_dict['activeDirectoryGraphResourceId']
    )

    return credentials, client_dict


def azure_checks(graphrbac_client, args, config, logging):

    logging.info('[*] Creating Azure Account Object')
    this_account = AzureAccount(args, config, logging)

    logging.info('[*] Performing Checks on Azure\n[i] Application Listing')
    azure_application_list(graphrbac_client, this_account)
    logging.info('[i] Group listing')
    azure_group_list(graphrbac_client, this_account)
    logging.info('[i] User listing')
    azure_account_list(graphrbac_client, this_account)
    logging.info('[*] Azure Checks complete')
    return logging
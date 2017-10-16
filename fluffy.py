from Common.common import inital_setup, get_list_from_config_parser
import getpass
import sys
from beeprint import pp
import os
import json
## Other required imports
import uuid
import msrest.exceptions as msrestexecptions


#our Azure stuff
from CSP.azurecsp import azure_checks, azure_client, azure_credentials

#our AWS imports
from Classes.accountclass import AwsAccount, ApiAccessKey

#our AWS stuff


if __name__ == "__main__":
    logging, args, config = inital_setup()


    last_key_used_delta = config.getint('apikeys', 'lastused')
    longest_key_unused_delta = config.getint('apikeys', 'unused')

    #Azure
    if args.az:
        try:
            credentials, client_dict = azure_credentials(config)
        except msrestexecptions.AuthenticationError as e:
            logging.critical('[E] Looks like some sort of connection error')
            logging.critical('[E] %s' % e)
            sys.exit()
        graphrbac_client = azure_client(credentials, client_dict)
        azure_checks(graphrbac_client, args, config, logging)


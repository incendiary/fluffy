from Common.common import initalsetup
#from Classes.azure import Azure
import getpass
import sys


from beeprint import pp

from azure.common.credentials import ServicePrincipalCredentials

from Classes.user import User, Api_access_key

import pytz

from datetime import datetime, timedelta

import boto3

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



    client = boto3.client(
        'iam',
        aws_access_key_id=config._sections['awscredentials']['aws_access_key_id'],
        aws_secret_access_key=config._sections['awscredentials']['aws_secret_access_key'],
    )

    users = client.list_users()

    print users
    exit()

    for user in users['Users']:
        thisuser = User(user['UserName'])

        response_list_access_keys = client.list_access_keys(
            UserName=user['UserName'],
        )

        if len(response_list_access_keys['AccessKeyMetadata']) >= 1:

            for eachAccessKey in response_list_access_keys['AccessKeyMetadata']:
                if 'AccessKeyId' in eachAccessKey:

                    accesskeyid = eachAccessKey['AccessKeyId']
                    createdate = eachAccessKey['CreateDate']

                    thisapikey = Api_access_key(accesskeyid, createdate)


                    access_key_details_dict =  client.get_access_key_last_used(AccessKeyId = accesskeyid)
                    access_key_last_used_dict =  access_key_details_dict['AccessKeyLastUsed']


                    if comparetwodates(current_utc, createdate, config.getint('apikeys', 'maxage')):
                        thisapikey.set_create_date(createdate, True)
                    else:
                        thisapikey.set_create_date(createdate, False)

                    if 'LastUsedDate' in access_key_last_used_dict:
                        access_key_last_used_date =  access_key_last_used_dict['LastUsedDate']
                        if comparetwodates(current_utc, access_key_last_used_date, config.getint('apikeys', 'lastused')):
                            thisapikey.set_last_used(access_key_last_used_date=access_key_last_used_date,
                                                     api_access_key_last_used_too_long=True)
                        else:
                            thisapikey.set_last_used(access_key_last_used_date=access_key_last_used_date,
                                                     api_access_key_last_used_too_long=False)
                    else:
                        if comparetwodates(current_utc, createdate, config.getint('apikeys', 'unused')):
                            thisapikey.set_unused()

                    pp(thisapikey)

                    thisuser.appended_api_access_key(thisapikey)

        response_list_mfa = client.list_mfa_devices(
            UserName=user['UserName'],
            Marker='string',
            MaxItems=123
        )

        print thisuser.return_api_access_keys_list()



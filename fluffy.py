from Common.common import initalsetup, get_list_from_config_parser
#from Classes.azure import Azure
import getpass
import sys
from beeprint import pp
from azure.common.credentials import ServicePrincipalCredentials
from Classes.user import User, Api_access_key
import pytz
from datetime import datetime, timedelta
import boto3
import os
import jinja2
import json

def comparetwodates(date1, date2, deltainseconds):
    if (date1 - date2) > timedelta(seconds=deltainseconds):
        return True
    else:
        return False

def createreport(userlist):

    cwd = os.getcwd()
    templatedir = cwd +  "/templates"
    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    maintemplate = templateEnv.get_template(templatedir + "/main.jinja")
    keytemplate = templateEnv.get_template(templatedir + "/key.jinja")
    tabletemplate  = templateEnv.get_template(templatedir + "/table.jinja")

    keytablecontent = ""
    for auser in userlist:
        for key in auser.return_api_access_keys_json():
            templateVars = {"key": json.loads(key)}
            keytablecontent += keytemplate.render(templateVars)

    keyheadings = ["Name", "Creation", "ID", "Unused", "LastUsedTooLong", "KeyTooOld"]
    tableid = "keys"
    keytabletemplateVars = {"headings": keyheadings,
                    "tablecontents": keytablecontent,
                    "id": tableid,
                        }

    keytablecontent = tabletemplate.render(keytabletemplateVars)

    maintemplateVars = {"title": "Fluffy Output",
                    "description": "Hopefully simple output",
                    "keytablecontents": keytablecontent
                    }

    with open("output.html", "wb") as fh:
        fh.write(maintemplate.render(maintemplateVars))


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

    userlist = []
    users = client.list_users()
    known_aws_admin_policies = get_list_from_config_parser(config.get('aws', 'knownadminpolicies'))
    print known_aws_admin_policies
    exit()
    for user in users['Users']:
        thisuser = User(user['UserName'])


        response_list_mfa = client.list_mfa_devices(
            UserName=user['UserName'],
        )

        if len(response_list_mfa['MFADevices']) == 0:
            # user doesnt have mfa enabled
            thisuser.set_mfa_enabled(False)
        elif len(response_list_mfa['MFADevices']) >= 1:
            thisuser.set_mfa_enabled(True)

        response_list_groups_for_user = client.list_groups_for_user(
            UserName=user['UserName'],
        )
        response_inline_policies_for_user = client.list_attached_user_policies(
            UserName=user['UserName'],
        )

        if len(response_inline_policies_for_user['AttachedPolicies']) > 0:
            thisuser.set_inline_enabled(True)
            for policy in response_inline_policies_for_user['AttachedPolicies']:
                thisuser.append_inline_policy(policy)

        if thisuser.inline_enabled:
            print thisuser.inline_policy_list

        response_list_access_keys = client.list_access_keys(
            UserName=user['UserName'],
        )

        if len(response_list_access_keys['AccessKeyMetadata']) >= 1:

            for eachAccessKey in response_list_access_keys['AccessKeyMetadata']:
                if 'AccessKeyId' in eachAccessKey:

                    accesskeyid = eachAccessKey['AccessKeyId']
                    createdate = eachAccessKey['CreateDate']

                    thisapikey = Api_access_key(accesskeyid, createdate, thisuser.username)

                    access_key_details_dict =  client.get_access_key_last_used(AccessKeyId = accesskeyid)
                    access_key_last_used_dict =  access_key_details_dict['AccessKeyLastUsed']

                    if comparetwodates(current_utc, createdate, config.getint('apikeys', 'maxage')):
                        thisapikey.set_create_date(createdate, True)
                    else:
                        thisapikey.set_create_date(createdate, False)

                    #do I want to move these checks into the class itself?
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
                    thisuser.appended_api_access_key(thisapikey)





        userlist.append(thisuser)
    #createreport(userlist)

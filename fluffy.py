from Common.common import initalsetup, get_list_from_config_parser
#from Classes.azure import Azure
import getpass
import sys
from beeprint import pp
from azure.common.credentials import ServicePrincipalCredentials
from Classes.user import Aws_user, Api_access_key
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

def report_inline_user():
    pass

def createreport(userlist):

    cwd = os.getcwd()
    templatedir = cwd +  "/templates"
    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    maintemplate = templateEnv.get_template(templatedir + "/main.jinja")
    keytemplate = templateEnv.get_template(templatedir + "/key.jinja")
    tabletemplate  = templateEnv.get_template(templatedir + "/table.jinja")
    inlineusertemplate = templateEnv.get_template(templatedir + "/inlineuser.jinja")

    keytablecontent = ""
    for auser in userlist:
        for key in auser.return_api_access_keys_json():
            templateVars = {"key": json.loads(key)}
            keytablecontent += keytemplate.render(templateVars)

    keyheadings = ["Name", "Creation", "ID", "Unused", "LastUsedTooLong", "KeyTooOld"]

    keytabletemplateVars = {"headings": keyheadings,
                    "tablecontents": keytablecontent,
                    "id": "keys",
                        }

    keytablecontent = tabletemplate.render(keytabletemplateVars)

    #table for inline policy users
    inlineusers = ""
    for auser in userlist:
        if auser.inline_enabled:
            inlinetemplatevars  = {"name": auser.username,
                "inline_policy_list": auser.inline_policy_list,
                }

            inlineusers += inlineusertemplate.render(inlinetemplatevars)

    inlineusers = "<ul>%s</ul>" % inlineusers


    maintemplateVars = {"title": "Fluffy Output",
                    "description": "Hopefully simple output",
                    "keytablecontents": keytablecontent,
                    "inlineusers": inlineusers,
                    }

    with open("Output/index.html", "wb") as fh:
        fh.write(maintemplate.render(maintemplateVars))


if __name__ == "__main__":
    logging, args, config = initalsetup()
    utc = pytz.UTC
    current = datetime.now()
    current_utc = pytz.utc.localize(current)
    known_aws_admin_policies = get_list_from_config_parser(config.get('aws', 'known_aws_admin_policies'))
    known_aws_admin_groups = get_list_from_config_parser(config.get('aws', 'known_aws_admin_groups'))
    last_key_used_delta = config.getint('apikeys', 'lastused')
    longest_key_unused_delta = config.getint('apikeys', 'unused')
    userlist = []

    client = boto3.client(
        'iam',
        aws_access_key_id=config._sections['awscredentials']['aws_access_key_id'],
        aws_secret_access_key=config._sections['awscredentials']['aws_secret_access_key'],
    )
    users = client.list_users()

    for user in users['Users']:
        #pp("===========================\n\n\n")
        thisuser = Aws_user(user['UserName'])

        ###MFA Section####
        response_list_mfa = client.list_mfa_devices(
            UserName=user['UserName'],
        )

        if len(response_list_mfa['MFADevices']) == 0:
            # user doesnt have mfa enabled
            thisuser.set_mfa_enabled(False)
        elif len(response_list_mfa['MFADevices']) >= 1:
            thisuser.set_mfa_enabled(True)

        #######

        response_list_groups_for_user = client.list_groups_for_user(
            UserName=user['UserName'],
        )

        if response_list_groups_for_user >0:
            thisuser.group_membership_enabled = True
            for group in response_list_groups_for_user['Groups']:
                thisuser.append_group(group)


        ###Inline policy section####
        response_inline_policies_for_user = client.list_attached_user_policies(
            UserName=user['UserName'],
        )

        if len(response_inline_policies_for_user['AttachedPolicies']) > 0:
            thisuser.set_inline_enabled(True)
            for policy in response_inline_policies_for_user['AttachedPolicies']:
                thisuser.append_inline_policy(policy)

        ###Access Key Section####

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

                    #do I want to move these checks into the class itself? Perhaps its best on insertion
                    if 'LastUsedDate' in access_key_last_used_dict:
                        access_key_last_used_date =  access_key_last_used_dict['LastUsedDate']
                        if comparetwodates(current_utc, access_key_last_used_date, last_key_used_delta):
                            thisapikey.set_last_used(access_key_last_used_date=access_key_last_used_date,
                                                     api_access_key_last_used_too_long=True)
                        else:
                            thisapikey.set_last_used(access_key_last_used_date=access_key_last_used_date,
                                                     api_access_key_last_used_too_long=False)
                    else:
                        if comparetwodates(current_utc, createdate, longest_key_unused_delta):
                            thisapikey.set_unused()
                    thisuser.appended_api_access_key(thisapikey)


        thisuser.do_aws_checks(known_aws_admin_policies, known_aws_admin_groups)
        #pp(thisuser)

        userlist.append(thisuser)

    createreport(userlist)

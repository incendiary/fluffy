import boto3
from beeprint import pp
from Classes.accountclass import AwsAccount, ApiAccessKey


def aws_create_client(config):
    client = boto3.client(
        'iam',
        aws_access_key_id=config._sections['awscredentials']['aws_access_key_id'],
        aws_secret_access_key=config._sections['awscredentials']['aws_secret_access_key'],
    )
    return client


def aws_account_list(users):
    for user in users:
        thisuser = AwsAccount(user['UserName'])


def awsbits(config):
    client = aws_create_client(config)
    users = client.list_users()

    for user in users['Users']:

        # pp("===========================\n\n\n")
        this_account = AwsAccount(user['UserName'])

        ###MFA Section####
        response_list_mfa = client.list_mfa_devices(
            UserName=user['UserName'],
        )

        if len(response_list_mfa['MFADevices']) == 0:
            # user doesnt have mfa enabled
            this_account.set_mfa_enabled(False)
        elif len(response_list_mfa['MFADevices']) >= 1:
            this_account.set_mfa_enabled(True)

        #######

        response_list_groups_for_user = client.list_groups_for_user(
            UserName=user['UserName'],
        )

        if response_list_groups_for_user > 0:
            this_account.group_membership_enabled = True
            for group in response_list_groups_for_user['Groups']:
                this_account.append_group(group)

        # user checks


        iam = boto3.resource('iam')
        response_specific_user = iam.User(user['UserName'])

        this_account.set_create_date(response_specific_user.create_date)
        this_account.set_arn(response_specific_user.arn)
        this_account.set_user_id(response_specific_user.user_id)
        this_account.set_last_used(response_specific_user.password_last_used)

        # https://gist.github.com/jonathanwcrane/68ddff397ec85a8dddae

        profile = response_specific_user.LoginProfile()
        try:
            profile.load()
        except Exception as e:
            if 'NoSuchEntity' in e.response['Error']['Code']:
                this_account.set_service_account(True)
            else:
                this_account.set_service_account(False)

        ###Inline policy section####
        response_inline_policies_for_user = client.list_attached_user_policies(
            UserName=user['UserName'],
        )

        if len(response_inline_policies_for_user['AttachedPolicies']) > 0:
            this_account.set_inline_enabled(True)
            for policy in response_inline_policies_for_user['AttachedPolicies']:
                this_account.append_inline_policy(policy)

        ###Access Key Section####

        response_list_access_keys = client.list_access_keys(
            UserName=user['UserName'],
        )

        if len(response_list_access_keys['AccessKeyMetadata']) >= 1:

            for eachAccessKey in response_list_access_keys['AccessKeyMetadata']:
                if 'AccessKeyId' in eachAccessKey:

                    accesskeyid = eachAccessKey['AccessKeyId']
                    createdate = eachAccessKey['CreateDate']

                    thisapikey = Api_access_key(accesskeyid, createdate, this_account.username)

                    access_key_details_dict = client.get_access_key_last_used(AccessKeyId=accesskeyid)
                    access_key_last_used_dict = access_key_details_dict['AccessKeyLastUsed']

                    if comparetwodates(current_utc, createdate, config.getint('apikeys', 'maxage')):
                        thisapikey.set_create_date(createdate, True)
                    else:
                        thisapikey.set_create_date(createdate, False)

                    # do I want to move these checks into the class itself? Perhaps its best on insertion
                    if 'LastUsedDate' in access_key_last_used_dict:
                        access_key_last_used_date = access_key_last_used_dict['LastUsedDate']
                        if comparetwodates(current_utc, access_key_last_used_date, last_key_used_delta):
                            thisapikey.set_last_used(access_key_last_used_date=access_key_last_used_date,
                                                     api_access_key_last_used_too_long=True)
                        else:
                            thisapikey.set_last_used(access_key_last_used_date=access_key_last_used_date,
                                                     api_access_key_last_used_too_long=False)
                    else:
                        if comparetwodates(current_utc, createdate, longest_key_unused_delta):
                            thisapikey.set_unused()
                    this_account.appended_api_access_key(thisapikey)

        this_account.do_aws_checks(known_aws_admin_policies, known_aws_admin_groups)
        pp(this_account)
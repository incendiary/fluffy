import json
import random
import os
import base64
from Common.common import compare_two_dates, compare_date_to_now
from datetime import timedelta
import pytz

class ApiAccessKey(object):

    def __init__(self, keydescriptor, createdate, user, config):
        self.api_access_key = keydescriptor
        self.api_access_key_create_date = createdate
        self.user = user
        self.config = config
        self.createdate = createdate
        self.expiry = None
        self.api_access_key_unused = None
        self.api_access_key_last_used_too_long = None
        self.api_key_too_old = None
        self.set_create_date()

    def set_create_date(self):
        self.api_key_too_old = compare_date_to_now(self.createdate, self.config.getint('apikeys', 'maxage'))


    def set_last_used(self, access_key_last_used_date, api_access_key_last_used_too_long):
        self.api_access_key_last_used = access_key_last_used_date
        self.api_access_key_last_used_too_long = api_access_key_last_used_too_long

    def set_unused(self):
        #logic is, if the access key is unused, then the last time it was used is to long by default.
        self.api_access_key_last_used_too_long = True
        self.api_access_key_unused = True

    def create_api_key_dictionary(self):
        self.dict = {'user': self.user,
                     'api_access_key': self.api_access_key,
                     'api_access_key_create_date': str(self.api_access_key_create_date),
                     'api_access_key_unused': self.api_access_key_unused,
                     'api_access_key_last_used_too_long': self.api_access_key_last_used_too_long,
                     'api_key_too_old': self.api_key_too_old
                     }

    def return_api_key_dictionary(self):
        self.create_api_key_dictionary()
        return self.dict

    def return_api_key_json(self):
        self.create_api_key_dictionary()
        return json.dumps(self.dict)


class Account(object):
    def __init__(self, username, avatar=False):
        # Username of account
        self.username = username
        # API keys associated with account
        self.api_access_keys_list = []
        # Inline Policies used by AWS - Maybe Azure equivalent? TBC
        self.inline_enabled = None
        # does the account have MFA enabled
        self.mfa_enabled = None
        self.administrative = None
        self.group_membership_enabled = None
        self.administrative_not_mfa = None
        self.groups = []
        self.last_used = None
        self.create_date = None
        self.service_account = None

        if not avatar:
            #no avatar passed, setting random one
            avatar_directory = "imgs/avatars/"
            with open(avatar_directory + random.choice(os.listdir(avatar_directory)), "rb") as image_file:
                data = image_file.read()
                self.avatar = data.encode("base64").replace('\n', '')


    def set_last_used(self, date):
        #used to store the last time an account was used, seperate to key usage if supproted.
        self.last_used = date

    def return_last_used(self):
        return self.last_used

    def set_create_date(self, createdate):
        self.create_date = createdate

    def return_create_date(self):
        return self.create_date

    def set_user_id(self, id):
        self.user_id = id

    def return_user_id(self):
        return self.user_id

    def appended_api_access_key(self, key):
        #append api access key objects to the api access key list
        self.api_access_keys_list.append(key)

    def return_api_access_keys_list(self):
        #returns api acces key lists
        return self.api_access_keys_list

    def return_api_access_keys_json(self):
        #attempts to return keys as json
        list = []
        for key in self.api_access_keys_list:
            list.append(key.return_api_key_json())
        return list

    def set_service_account(self, state):
        self.service_account = state

    def return_service_account(self):
        return self.service_account

    def set_mfa_enabled(self, state):
        self.mfa_enabled = state

    def user_can_login(self, login):
        #used to store if a user can login or if its just api access.
        self.can_login =  login

    def do_checks(self):
        #tempory list of checks
        # password and key aging
        # 2fa on critical accounts
        pass


class AwsAccount(Account):

    def set_inline_enabled(self, state):
        #Maybe aws specific
        self.inline_enabled = state
        self.inline_policy_list = []

    def append_inline_policy(self, policy):
        self.inline_policy_list.append(policy)

    def append_group(self, group):
        self.groups.append(group)

    def set_arn(self, arn):
        self.arn = arn

    def return_arn(self):
        return self.arn

    def do_aws_checks(self, known_aws_admin_policies, known_aws_admin_groups):
        # known_aws_admin_policies & known_aws_admin_groups both come via the config file.
        # Inline Policy Check
        if self.inline_enabled:
            for policy in self.inline_policy_list:
                if policy['PolicyName'] in known_aws_admin_policies:
                    self.administrative = True

        # Group membership Check
        if self.group_membership_enabled:
            for group in self.groups:
                if group['GroupName'] in ['Administrators', 'Admin']:
                    self.administrative = True
                if group['GroupName'] in known_aws_admin_groups:
                    self.administrative = True

        if self.administrative:
            if not self.mfa_enabled:
                self.administrative_not_mfa = True


class AzureAccount(Account):

    def do_azure_checks(self):
        pass
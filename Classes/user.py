import json

class Api_access_key(object):

    def __init__(self, keydescriptor, createdate, user):
        self.api_access_key = keydescriptor
        self.api_access_key_create_date = createdate
        self.user = user

        self.api_access_key_unused = False
        self.api_access_key_last_used_too_long = False
        self.api_key_too_old = False


    def set_create_date(self, createdate, tooold):
        self.api_access_key_create_date = createdate
        self.api_key_too_old = tooold

    def set_last_used(self, access_key_last_used_date, api_access_key_last_used_too_long):
        self.api_access_key_last_used = access_key_last_used_date
        self.api_access_key_last_used_too_long = api_access_key_last_used_too_long


    def set_unused(self):
        self.api_access_key_unused = True

    def createselfdict(self):
        self.dict = {'user': self.user,
                     'api_access_key': self.api_access_key,
                     'api_access_key_create_date': str(self.api_access_key_create_date),
                     'api_access_key_unused': self.api_access_key_unused,
                     'api_access_key_last_used_too_long': self.api_access_key_last_used_too_long,
                     'api_key_too_old': self.api_key_too_old
                     }

    def returndictkey(self):
        self.createselfdict()
        return self.dict

    def returnjsonkey(self):
        self.createselfdict()
        return json.dumps(self.dict)




class User(object):
    def __init__(self, username):
        self.username = username
        self.api_access_keys_list = []
        self.inline_enabled = False
        self.mfa_enabled = False
        self.administrative = False
        self.group_membership_enabled = False
        self.administrative_not_mfa = False
        self.groups = []

    def appended_api_access_key(self, key):
        self.api_access_keys_list.append(key)

    def return_api_access_keys_list(self):
        return self.api_access_keys_list

    def return_api_access_keys_json(self):
        list = []
        for key in self.api_access_keys_list:
            list.append(key.returnjsonkey())
        return list

    def set_mfa_enabled(self, state):
        self.mfa_enabled = state

    def do_checks(self):
        #tempory list of checks
        # password and key aging
        # 2fa on critical accounts
        pass

class Aws_user(User):

    def set_inline_enabled(self, state):
        #Maybe aws specific
        self.inline_enabled = state
        self.inline_policy_list = []

    def append_inline_policy(self, policy):
        self.inline_policy_list.append(policy)

    def append_group(self, group):
        self.groups.append(group)

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

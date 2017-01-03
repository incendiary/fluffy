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

    def set_inline_enabled(self, state):
        #Maybe aws specific
        self.inline_enabled = state
        self.inline_policy_list = []

    def append_inline_policy(self, policy):
        self.inline_policy_list.append(policy)

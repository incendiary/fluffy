class Api_access_key(object):

    def __init__(self, keydescriptor, createdate):
        self.api_access_key = keydescriptor
        self.api_access_key_create_date = createdate

    def set_create_date(self, createdate, tooold):
        self.api_access_key_create_date = createdate
        self.api_key_too_old = tooold

    def set_last_used(self, access_key_last_used_date, api_access_key_last_used_too_long):
        self.api_access_key_last_used = access_key_last_used_date
        self.api_access_key_last_used_too_long = api_access_key_last_used_too_long


    def set_unused(self):
        self.api_access_key_unused = True





class User(object):
    def __init__(self, username):
        self.username = username
        self.api_access_keys_list = []

    def appended_api_access_key(self, key):
        self.api_access_keys_list.append(key)


    def return_api_access_keys_list(self):
        return self.api_access_keys_list
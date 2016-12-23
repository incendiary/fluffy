import sys

class Azure(object):
    def __init__(self, args, config, logging):
        self.args = args
        self.config = config
        self.logging = logging
        print sys.path

    def doauthentication(self):
        self.credentials = ServicePrincipalCredentials(
            client_id=self.config._sections['azure']['clientid'],
            secret=self.config._sections['azure']['key'],
            tenant=self.config._sections['azure']['tennant'],
        )

    def setcredentials(self, credentials):
        #this is a work around, as I cant seem to import the azure elements into the class
        self.credentials = credentials

    def setthis(self, this):
        self.this = this
        print self.this


#below from main

        # if config.has_option('azure', 'user'):
        # azureuser = config.get('azure', 'user')
        # print "[*] Username & Password Auth Detected:\n[*]\tPlease enter password for account: %s" % (azureuser)
        # azurepassword = getpass.getpass()


credentials = ServicePrincipalCredentials(
    client_id=config._sections['azure']['clientid'],
    secret=config._sections['azure']['key'],
    tenant=config._sections['azure']['tennant'],
)

azureobject = Azure(args, config, logging)
__author__ = 'adz'
import argparse
import logging
import ConfigParser
import datetime
import os


def createdirifnotexists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def yesnoquestion(string):
    while True:
        response = raw_input("%s [Y/n]" % (string)).lower()
        while response not in ("yes", "no", "y", "n"):
            response = raw_input("%s [Y/n]" % (string)).lower()
        if response == "no" or response == "n":
            return False
            break
        if response == "yes" or response == "y":
            return True
            break

def get_list_from_config_parser(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default,
       split on a comma and strip whitespaces."""
    return [ chunk.strip(chars) for chunk in option.split(sep) ]


def loggingobject(args):
    #creates the logging object
    createdirifnotexists(args.log)
    filename = "%s/%s" % (args.log, args.logname)

    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=filename,
                    filemode='w')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    return logging



def config_parser_rename_section(config, section_from, section_to, destructive=False):
    if destructive:
        config.remove_section(section_to)
    items = config.items(section_from)
    config.add_section(section_to)
    for item in items:
        config.set(section_to, item[0], item[1])
    config.remove_section(section_from)

def initalsetup():

    parser = argparse.ArgumentParser(description='This is fluffy, I try to automate Cloud auditing elemetns'
                                                 'so you can get on with more interesting things')

    #check for pre existing aws creds
    awsconfig = os.path.expanduser('~') + '/.aws/credentials'
    if os.path.isfile(awsconfig) and os.access(awsconfig, os.R_OK):
        awsresponse = yesnoquestion("[A] AWS credential folder found, would you like me to look here for credentials?")

    parser.add_argument('--cfg', '-c', help="Where is the config file?", required=True)


    parser.add_argument('--log', '-l', help="any log dir? defaults to logs",
                        required=False, default='logs')

    parser.add_argument('--logname', '-lf', help="log file name defaults too: %s.<date>.log", default="%s.log"
                        % (datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")))

    args = parser.parse_args()
    #logging to file and screen


    config = ConfigParser.SafeConfigParser()

    #should only be true, if above check as returned so.
    if awsresponse:
        config.read([os.path.expanduser(args.cfg)])
        config.read(['/Users/adz/.aws/credentials'])
        config_parser_rename_section(config, 'default', 'awscredentials', destructive=True)

    else:
        config.read([os.path.expanduser(args.cfg)])

    logging = loggingobject(args)

    return logging, args, config


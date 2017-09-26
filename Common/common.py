__author__ = 'adz'
import argparse
import logging
import ConfigParser
import datetime
import os
from os import environ
from beeprint import pp
from datetime import timedelta

def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def yes_no_question(string):
    while True:
        response = raw_input("%s [Y/n]" % (string)).lower()
        while response not in ("yes", "no", "y", "n"):
            response = raw_input("%s [Y/n]" % (string)).lower()

        return str2bool(response)


def get_list_from_config_parser(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default,
       split on a comma and strip whitespaces."""
    return [ chunk.strip(chars) for chunk in option.split(sep) ]


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def loggingobject(args):
    #creates the logging object
    create_dir_if_not_exists(args.log)
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


def comparetwodates(date1, date2, deltainseconds):
    if (date1 - date2) > timedelta(seconds=deltainseconds):
        return True
    else:
        return False


def config_parser_rename_section(config, section_from, section_to, destructive=False):
    if destructive:
        config.remove_section(section_to)
    items = config.items(section_from)
    config.add_section(section_to)
    for item in items:
        config.set(section_to, item[0], item[1])
    config.remove_section(section_from)


def inital_setup():
    parser = argparse.ArgumentParser(description='This is fluffy, I try to automate Cloud auditing elemetns'
                                                 'so you can get on with more interesting things')

    parser.add_argument('--cfg', '-c', help="Where is the config file?", required=True)

    parser.add_argument('--log', '-l', help="any log dir? defaults to logs", required=False, default='logs')

    parser.add_argument('--logname', '-lf', help="log file name defaults too: %s.<date>.log", default="%s.log"
                        % (datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")))

    parser.add_argument('--az', '-az', help="Want me to look at azure?", required=False, default=False, type=str2bool)
    parser.add_argument('--aws', '-aws', help="Want me to look at aws?", required=False, default=False, type=str2bool)
    args = parser.parse_args()
    #logging to file and screen
    logging = loggingobject(args)

    config = ConfigParser.SafeConfigParser()

    if args.az:
        config.read([os.path.expanduser(args.cfg)])
        if config.get('azure', 'azureauthlocation') in os.environ:
            azureresponse = yes_no_question(
                "[A] Azure credential file in envvar (%s) found, would you like me to look here for credentials?"
                % environ.get(config.get('azure', 'azureauthlocation')))
        else:
            ### logic here - no env var set TBD
            logging.info('No Azure enviroment var found so using config')
            azureresponse = None

        if azureresponse:
            config.set('azure', 'azureauthenvvar', 'Found')

    if args.aws:
        #check for pre existing aws creds
        awsconfig = os.path.expanduser('~') + '/.aws/credentials'
        if os.path.isfile(awsconfig) and os.access(awsconfig, os.R_OK):
            awsresponse = yes_no_question("[A] AWS credential folder found,"
                                          " would you like me to look here for credentials?")

        #should only be true, if above check as returned so.
        if awsresponse:
            config.read([os.path.expanduser(args.cfg)])
            config.read(['/Users/adz/.aws/credentials'])
            config_parser_rename_section(config, 'default', 'awscredentials', destructive=True)
        else:
            config.read([os.path.expanduser(args.cfg)])

    return logging, args, config
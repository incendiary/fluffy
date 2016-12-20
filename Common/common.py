__author__ = 'adz'
import argparse
import logging
import ConfigParser
import datetime
import os

def createdirifnotexists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def loggingobject(args, logging):
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

def initalsetup():
    parser = argparse.ArgumentParser(description='This is fluffy, I try to automate Cloud auditing elemetns'
                                                 'so you can get on with more interesting things')

    parser.add_argument('--cfg', '-c', help="Where is the config file?", required=True)
    parser.add_argument('--log', '-l', help="any log dir? defaults to logs",
                        required=False, default='logs')

    parser.add_argument('--logname', '-lf', help="log file name defaults too: %s.<date>.log", default="%s.log"
                        % (datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")))

    args = parser.parse_args()
    #logging to file and screen


    config = ConfigParser.ConfigParser()
    config.read([os.path.expanduser(args.cfg)])

    logging = loggingobject(args)

    return logging, args, config
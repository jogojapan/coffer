'''
Created on 2011/04/17

@author: gollerjo
'''

import sys
import getopt
from ConfigParser import SafeConfigParser
from command_shell import CommandShell
from feed_storage import FeedStorage
from item_storage import Item

def usage():
    sys.stderr.write('Usage: coffer [-c <config-path>]\n')

def main():
    # Determine path to config file
    config_path = '../config/standard.cfg'
    try:
        opts = getopt.getopt(sys.argv[1:],'hc:',[])[0]
    except getopt.GetoptError,err:
        sys.stderr.write(str(err))
        usage()
        sys.exit(1)
    for o,a in opts:
        if o == '-h':
            usage()
            sys.exit(0)
        elif o == '-c':
            config_path = a
        else:
            usage()
            sys.exit(1)
    config_parser = SafeConfigParser()
    config_parser.read(config_path)

    database_path = 'test'
    if config_parser.has_option('FeedStorage','database-path'):
        database_path = config_parser.get('FeedStorage','database-path')

    feed_storage = FeedStorage(database_path)
    shell = CommandShell(feed_storage)
    shell.cmdloop()

if __name__ == '__main__':
    main()

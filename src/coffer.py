'''
Created on 2011/04/17

@author: gollerjo
'''

import sys
import getopt
import os.path
from os import mkdir
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ConfigParser import SafeConfigParser
from command_shell import CommandShell
from feed_storage import FeedStorage
from item_storage import ItemStorage
import feedparser

class Coffer:
    def __init__(self,database_path):
        # Connect to engine
        dir = os.path.dirname(database_path)
        if not os.path.exists(dir):
            mkdir(dir)
        sys.stderr.write('Connecting to database at "%s"\n' % database_path)
        self._engine = create_engine('sqlite:///%s' % database_path,echo=True)

        # Start session
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        # Initialize feed storage
        self._feed_storage = FeedStorage(self._engine,self._session)
        # Initialize item storage
        self._item_storage = ItemStorage(self._engine,self._session)

    def run_command_shell(self):
        shell = CommandShell(self)
        shell.cmdloop()
    
    def current_items(self):
        '''
        Returns a generator for the list of current items, i.e. the
        current list of fresh items returned by all known feeds.
        '''
        for feed in self._feed_storage.feeds():
            feed_results = feedparser.parse(feed.get_url())
            for entry in feed_results.entries:
                sys.stdout.write((u'%s\n' % entry.title).encode('utf-8'))
                

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
    if config_parser.has_option('Database','path'):
        database_path = config_parser.get('Database','path')

    coffer = Coffer(database_path)
    coffer.run_command_shell()


if __name__ == '__main__':
    main()

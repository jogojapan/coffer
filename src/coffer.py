'''
Created on 2011/04/17

@author: gollerjo
'''

import sys
import getopt
import os.path
import re
from os import mkdir
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ConfigParser import SafeConfigParser
from command_shell import CommandShell
from feed_storage import FeedStorage
from item_storage import ItemStorage
import feedparser

class Coffer:
    def __init__(self,
                 database_path,
                 database_debug = False):
        # Connect to engine
        dir = os.path.dirname(database_path)
        if not os.path.exists(dir):
            mkdir(dir)
        sys.stderr.write('Connecting to database at "%s"\n' % database_path)
        self._engine = create_engine('sqlite:///%s' % database_path,echo=database_debug)

        # Start session
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        # Initialize feed storage
        self._feed_storage = FeedStorage(self._engine,self._session)
        # Initialize item storage
        self._item_storage = ItemStorage(self._engine,self._session)
        # A list of subprocess.Popen processes that will be maintained
        # by the Coffer object.
        self._external_processes = []

    def finish(self):
        '''
        Waits for all external processes started by coffer to finish.
        '''
        sys.stderr.write('Waiting for sub-processes to finish..\n')
        for process in self._external_processes:
            process.wait()
        sys.stderr.write('  ..finished.\n\n')

    def check_processes(self):
        '''
        Checks if some of the external processes have finished and
        removes them from the external-process list if they have.
        '''
        end_i = len(self._external_processes)
        i     = 0
        while i < end_i:
            if self._external_processes[i].poll() is not None:
                del self._external_processes[i]
                end_i -= 1
            else:
                i += 1

    def run_command_shell(self):
        shell = CommandShell(self)
        shell.cmdloop()
    
    def current_items(self, enable_ad_filter = False, check_existence = False):
        '''
        Returns a generator for the list of current items, i.e. the
        current list of fresh items returned by all known feeds.
        @param enable_ad_filter: if True, advertisements will be filtered out
                       using the predefined regex
        @param check_existence: if True, only entries that are not already
                       stored in the items database will be returned.
        '''
        for feed in self._feed_storage.feeds():
            if enable_ad_filter:
                exclude_pattern = re.compile(u'|'.join(feed.ad_filters))
            feed_results = feedparser.parse(feed.get_url())
            for entry in feed_results.entries:
                if check_existence:
                    if self._item_storage.exists(entry.id):
                        continue
                if (not enable_ad_filter) or (not exclude_pattern.search(entry.title)):
                    yield (feed.get_id(),entry)
                

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
    database_debug = False
    if config_parser.has_option('Database','debug'):
        database_debug = config_parser.getboolean('Database','debug')
    

    coffer = Coffer(database_path,database_debug)
    coffer.run_command_shell()
    coffer.finish()

if __name__ == '__main__':
    main()

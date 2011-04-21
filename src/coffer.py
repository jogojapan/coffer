# -*- coding: utf-8 -*-

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
from util.config_parsing import get_from_config_parser
from util.config_parsing import get_boolean_from_config_parser
from util.config_parsing import get_int_from_config_parser
from command_shell import CommandShell
from feed_storage import FeedStorage
from item_storage import ItemStorage
from file_storage import FileStorage
import file_storage
import feedparser
from fetcher import Fetcher

class Coffer:
    def __init__(self,config_parser):
        # Connect to engine
        database_path  = get_from_config_parser(config_parser,'Database','path','database')
        database_debug = get_boolean_from_config_parser(config_parser,'Database','debug',False)
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
        # File storage (data dump)
        file_storage_path = get_from_config_parser(config_parser,'FileStorage','path','datadump')
        max_block_size    = get_int_from_config_parser(config_parser,'FileStorage','max-block-size',
                                                       file_storage.DEFAULT_MAX_BLOCK_SIZE)
        bzip2_path = get_from_config_parser(config_parser,'FileStorage','bzip2-path','/usr/bin/bzip2')
        self._file_storage = FileStorage(self._external_processes,file_storage_path,
                                         max_block_size,bzip2_path)
        # Content fetcher configuration
        self._fetcher = Fetcher(config_parser)

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

    def fetch_and_store(self,targets):
        '''
        Download target URLs and store them in the file storage.
        @param targets: A list of (feed-id,URL) pairs.
        '''
        text_objs_dict = self._fetcher.fetch(targets)
        self._file_storage.store_all(text_objs_dict)

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

    # Parse config file
    config_parser = SafeConfigParser()
    config_parser.read(config_path)

    # Set up and run coffer
    coffer = Coffer(config_parser)
    coffer.run_command_shell()
    coffer.finish()

if __name__ == '__main__':
    main()

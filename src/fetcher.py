# -*- coding: utf-8 -*-

'''
Created on 2011/04/19

@author: gollerjo
'''

from util.config_parsing import get_int_from_config_parser
from threading import Thread
from urllib2 import build_opener
from time import sleep

class OneSiteFetcher(Thread):
    '''
    Downloads a list of URLs and implements a sleeping time between
    each download. The idea is that all URLs belonging to the same
    site (or the same RSS-feed) are given to one OneSiteFetcher,
    and several OneSiteFetchers are run in parallel.
    '''
    def __init__(self,opener,waiting_time,timeout):
        '''
        Constructor.
        @param url_list: A list of (feed-source,URL) pairs.
        '''
        Thread.__init__()
        self._url_list     = []
        self._waiting_time = waiting_time
        self._results      = []
        self._opener       = opener
        self._timeout      = timeout
    
    def append_url(self,feed_source,url):
        '''
        Appends a (feed-source,URL) pair to the target list. This MUST be done
        before the thread is started.
        '''
        self._url_list.append((feed_source,url))
    
    def run(self):
        for (feed,url) in self._url_list:
            stream = self._opener.open(url,timeout=self._timeout)
            if stream:
                self._results.append((feed,url,unicode(stream.read(),'utf-8')))
            sleep(self._waiting_time)

class Fetcher(object):
    '''
    Operates a predefined number of OneSiteFetcher threads in parallel to download
    a given set of source-specific articles quickly. The articles will be grouped
    by feed-source and all articles belonging to the same source will be handled
    by one thread in order to keep under control the maximum load put on a single
    target server.
    '''        

    def __init__(self,config_parser):
        '''
        Constructor
        '''
        self._max_threads  = get_int_from_config_parser(config_parser,'Fetcher','max-threads',5)
        self._waiting_time = get_int_from_config_parser(config_parser,'Fetcher','wait',3)
        self._timeout      = get_int_from_config_parser(config_parser,'Fetcher','timeout',15)
        self._opener       = build_opener()
        self._opener.addheaders = [('User-agent','Mozilla/5.0')]

    def fetch(self,targets):
        '''
        Fetch content from the target URLs.
        @param targets: a list of (feed-source,URL) pairs. The feed-source
        '''
        # Create thread pool
        thread_pool = [OneSiteFetcher(self._opener,self._waiting_time,self._timeout) \
                       for _ in range(self._max_threads)]
        # Assign feeds/URLs to threads
        current_thread = 0
        assignments    = {}
        for (feed,url) in targets:
            if feed not in assignments:
                assignments[feed] = thread_pool[current_thread]
                current_thread += 1
                if current_thread >= self._max_threads:
                    current_thread = 0
            assignments[feed].append_url(feed,url)
        # Run the threads
        for fetcher in thread_pool:
            fetcher.start()
        # Wait for them to finish
        for fetcher in thread_pool:
            fetcher.join()
        results = []
        for fetcher in thread_pool:
            results.extend(fetcher._results)
        return results

# -*- coding: utf-8 -*-

'''
Created on 2011/04/19

@author: gollerjo
'''

from util.config_parsing import get_int_from_config_parser
from threading import Thread
from urllib2 import build_opener, HTTPError
from time import sleep
from langid.html import HtmlLangid
from langid import get_decoder
import sys

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
        '''
        Thread.__init__(self)
        self._url_list     = []
        self._waiting_time = waiting_time
        self._results      = []
        self._opener       = opener
        self._timeout      = timeout
        self._langid       = HtmlLangid()
    
    def append_url(self,feed_id,url,metainfo):
        '''
        Appends a (feed-id,URL,metainfo) pair to the target list. This MUST be done
        before the thread is started.
        '''
        self._url_list.append((feed_id,url,metainfo))
    
    def run(self):
        for (feed_id,url,metainfo) in self._url_list:
            try:
                stream = self._opener.open(url,timeout=self._timeout)
                if stream:
                    contents = stream.read()
                    stream.close()
                    self._langid.reset()
                    self._langid.feed(contents)
                    decoder = get_decoder(self._langid._result_encoding,'utf-8')
                    (decoded_text,decoded_input_len) = decoder(contents,'ignore')
                    if decoded_input_len != len(contents):
                        sys.stderr.write("Warning: Downloaded text was not decoded " + \
                                         "to Unicode completely. " + \
                                         ("Only %d out of %d " % (decoded_input_len,len(contents))) + \
                                         "bytes were decoded.\n")
                    self._results.append((feed_id,url,decoded_text,metainfo))
            except HTTPError,err:
                sys.stderr.write((u'Could not download "%s": %s\n' \
                                  % (url,repr(err))).encode('utf-8'))
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
        @param targets: a list of (feed_id-id,URL,metainfo) pairs. The metainfo
                   object may contain anything; it will be re-attached to the
                   results for this URL. The feed_id-id is used to determine the
                   fetcher thread the URL will be assigned to.
        '''
        # Create thread pool
        thread_pool = [OneSiteFetcher(self._opener,self._waiting_time,self._timeout) \
                       for _ in range(self._max_threads)]
        # Assign feeds/URLs to threads
        current_thread = 0
        assignments    = {}
        for (feed_id,url,metainfo) in targets:
            if feed_id not in assignments:
                assignments[feed_id] = thread_pool[current_thread]
                current_thread += 1
                if current_thread >= self._max_threads:
                    current_thread = 0
            assignments[feed_id].append_url(feed_id,url,metainfo)
        # Run the threads
        for fetcher in thread_pool:
            fetcher.start()
        # Wait for them to finish
        for fetcher in thread_pool:
            fetcher.join()
        results = {}
        for fetcher in thread_pool:
            for (feed_id,url,contents,metainfo) in fetcher._results:
                if feed_id not in results:
                    results[feed_id] = []
                results[feed_id].append((metainfo,contents))
        return results

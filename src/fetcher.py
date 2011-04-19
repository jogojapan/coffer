# -*- coding: utf-8 -*-

'''
Created on 2011/04/19

@author: gollerjo
'''

from util.config_parsing import *
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
    def __init__(self,opener,url_list,waiting_time,timeout):
        Thread.__init__()
        self._url_list     = url_list
        self._waiting_time = waiting_time
        self._results      = []
        self._opener       = opener
        self._timeout      = timeout
    
    def run(self):
        for url in self._url_list:
            stream = self._opener.open(url,timeout=self._timeout)
            if stream:
                self._results.append((url,unicode(stream.read(),'utf-8')))
            sleep(self._waiting_time)
        

class Fetcher(object):
    '''
    classdocs
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

    
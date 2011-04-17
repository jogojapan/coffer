# -*- coding: utf-8 -*-

'''
Created on 2011/04/17

@author: gollerjo
'''

from cmd import Cmd
import shlex
#import getopt
import sys

class CommandShell(Cmd):
    '''
    Implements a command shell for the COFFER application.
    '''

    def __init__(self,coffer):
        Cmd.__init__(self)
        self._coffer  = coffer
        self._end_now = False        

    def do_list(self,parameters):
        self._coffer._feed_storage.list_feeds(sys.stdout)

    def do_add(self,parameters):
        parameters = shlex.split(parameters)
        if len(parameters) != 2:
            sys.stderr.write("'add' requires 2 arguments\n")
        else:
            self._coffer._feed_storage.add_feed(parameters[0],parameters[1])

    def do_quit(self,parameters):
        sys.stdout.write('\n')
        self._end_now = True
    
    def do_current(self,parameters):
        self._coffer.current_items()

    def do_EOF(self,parameters):
        sys.stdout.write('\n')
        self._end_now = True

    def postcmd(self,stop,line):
        return self._end_now

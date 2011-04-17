# -*- coding: utf-8 -*-

'''
Created on 2011/04/17

@author: gollerjo
'''

from cmd import Cmd
import shlex
import getopt
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
        if len(parameters) < 1:
            sys.stderr.write("'add' requires more arguments\n")
        else:
            if parameters[0] == 'feed' and len(parameters) == 3:
                self._coffer._feed_storage.add_feed(parameters[1],parameters[2])
            elif parameters[0] == 'regex' and len(parameters) == 3:
                self._coffer._feed_storage.add_regex(parameters[1],parameters[2],sys.stderr)
            else:
                sys.stderr.write('Wrong number of type of arguments in call to "add".\n')

    def do_quit(self,parameters):
        sys.stdout.write('\n')
        self._end_now = True

    def do_current(self,parameters):
        enable_filter = False
        parameters = shlex.split(parameters)
        try:
            opts,args = getopt.getopt(parameters,'f',[])
            for o,a in opts:
                if o == '-f':
                    enable_filter = True
            for entry in self._coffer.current_items(enable_filter):
                sys.stdout.write((u'%s\n' % entry.title).encode('utf-8'))

        except getopt.GetoptError,err:
            sys.stderr.write(str(err) + '\n')


    def do_EOF(self,parameters):
        sys.stdout.write('\n')
        self._end_now = True

    def postcmd(self,stop,line):
        return self._end_now

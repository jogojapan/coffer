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
    
    def __init__(self,feedstorage):
        Cmd.__init__(self)
        self._feed_storage = feedstorage        
    
    def interpret_cmd(self,command_tokens):
        #feed_storage.add_feed('Asahi 政治','http://rss.asahi.com/f/asahi_politics')
        if len(command_tokens) < 1:
            return False
        try:
            if command_tokens[0] == 'list':
                self._feed_storage.list_feeds(sys.stdout)
            elif command_tokens[0] == 'add':
                if len(command_tokens) != 3:
                    sys.stderr.write("Expected 2 arguments to 'add'.\n")
                else:
                    self._feed_storage.add_feed(command_tokens[1],command_tokens[2])
            else:
                sys.stderr.write('Unknown command "%s".\n' % command_tokens[0])
        except getopt.GetoptError,err:
            sys.stderr.write('%s\n' % str(err))
    
    def postcmd(self,stop,line):
        command_tokens = shlex.split(line)
        return self.interpret_cmd(command_tokens)

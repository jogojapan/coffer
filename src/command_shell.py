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

    def postcmd(self,stop,line):
        self._coffer.check_processes()

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
        enable_ad_filter   = False
        check_existence = False
        parameters = shlex.split(parameters)
        try:
            opts,args = getopt.getopt(parameters,'fc',[])
            for o,a in opts:
                if o == '-f':
                    enable_ad_filter = True
                elif o == '-c':
                    check_existence = True
            for (feed_id,entry) in self._coffer.current_items(enable_ad_filter=enable_ad_filter,
                                                    check_existence=check_existence):
                sys.stdout.write((u'%s\n' % entry.title).encode('utf-8'))

        except getopt.GetoptError,err:
            sys.stderr.write(str(err) + '\n')

    def do_update(self,parameters):
        counter            = 0
        enable_ad_filter   = True
        parameters = shlex.split(parameters)
        try:
            opts,args = getopt.getopt(parameters,'',["no-ad-filter"])
            for o,a in opts:
                if o == '--no-ad-filter':
                    enable_ad_filter = False
            for (feed_id,entry) in self._coffer.current_items(enable_ad_filter=enable_ad_filter,
                                                    check_existence=True):
                self._coffer._item_storage.add(feed        = feed_id,
                                               item_id     = entry.id,
                                               title       = entry.title,
                                               date_parsed = entry.date_parsed,
                                               link        = entry.link,
                                               description = entry.description)
                counter += 1
        except getopt.GetoptError,err:
            sys.stderr.write(str(err) + '\n')
        self._coffer._item_storage.flush()
        sys.stdout.write((u'Added %d data records.\n' % counter).encode('utf-8'))

    def do_EOF(self,parameters):
        sys.stdout.write('\n')
        self._end_now = True

    def postcmd(self,stop,line):
        return self._end_now

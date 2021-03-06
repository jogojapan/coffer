# -*- coding: utf-8 -*-

'''
Created on 2011/04/17

@author: gollerjo
'''

from cmd import Cmd
import shlex
import getopt
import sys
import re
from file_storage import FileStorageException
from time import gmtime,strftime

class CommandShell(Cmd):
    '''
    Implements a command shell for the COFFER application.
    '''

    def __init__(self,coffer):
        Cmd.__init__(self)
        self._coffer  = coffer
        self._end_now = False
        self.prompt   = 'coffer> '

    def postcmd(self,stop,line):
        self._coffer.check_processes()
        return self._end_now

    def do_list(self,parameters):
        show_items          = False
        show_storage_blocks = False
        show_date           = False
        parameters = shlex.split(parameters)
        try:
            opts,_args = getopt.getopt(parameters,'',["items","storage-blocks","date"])
            for o,_ in opts:
                if o == '--items':
                    show_items = True
                elif o == '--storage-blocks':
                    show_storage_blocks = True
                elif o == '--date':
                    show_date = True
        except getopt.GetoptError,err:
            sys.stderr.write(str(err) + '\n')
            return
        if show_items:
            for item in self._coffer._item_storage.items():
                outstrs = []
                if show_storage_blocks:
                    outstrs.append(u'%d' % item.storage_block)
                if show_date:
                    outstrs.append(u'%s' % strftime("%y/%m/%d %H:%M",gmtime(item.date)))
                outstrs.append(u'%s\n' % item.title)
                sys.stdout.write((u'\t'.join(outstrs)).encode('utf-8'))
        else:
            self._coffer._feed_storage.list_feeds(sys.stdout)

    def do_add(self,parameters):
        parameters = shlex.split(parameters)
        if len(parameters) < 1:
            sys.stderr.write("'add' requires more arguments\n")
        else:
            if parameters[0] == 'feed' and len(parameters) == 2:
                feed_title = self._coffer.get_feed_info(parameters[1])
                self._coffer._feed_storage.add_feed(feed_title,
                                                    parameters[1])
                sys.stdout.write((u'Added "%s"\n' % feed_title).encode('utf-8','ignore'))
            elif parameters[0] == 'feed' and len(parameters) == 3:
                self._coffer._feed_storage.add_feed(parameters[2],parameters[1])
            elif parameters[0] == 'regex' and len(parameters) == 3:
                self._coffer._feed_storage.add_regex(parameters[1],parameters[2],sys.stderr)
            else:
                sys.stderr.write('Wrong number of type of arguments in call to "add".\n')

    def do_info(self,parameters):
        parameters = shlex.split(parameters)
        if len(parameters) < 1:
            sys.stderr.write("'info' requires a URL\n")
        else:
            feed_info = self._coffer.get_feed_info(parameters[0])
            sys.stdout.write((u'%s\n' % feed_info).encode('utf-8','ignore'))

    def do_quit(self,parameters):
        sys.stdout.write('\n')
        self._end_now = True

    def do_current(self,parameters):
        enable_ad_filter   = False
        check_existence    = False
        debug_enabled      = False
        parameters = shlex.split(parameters)
        try:
            opts,_ = getopt.getopt(parameters,'fc',[])
            for o,_ in opts:
                if o == '-f':
                    enable_ad_filter = True
                elif o == '-c':
                    check_existence = True
                elif o == '-d':
                    debug_enabled = True
            for (_,entryid,entry) in self._coffer.current_items(enable_ad_filter=enable_ad_filter,
                                                                check_existence=check_existence,
                                                                debug_enabled=debug_enabled):
                sys.stdout.write((u'[%s] %s\n' % (entryid,entry.title)).encode('utf-8'))

        except getopt.GetoptError,err:
            sys.stderr.write(str(err) + '\n')

    def do_update(self,parameters):
        counter            = 0
        enable_ad_filter   = True
        parameters = shlex.split(parameters)
        try:
            opts,_ = getopt.getopt(parameters,'',["no-ad-filter"])
            for o,_ in opts:
                if o == '--no-ad-filter':
                    enable_ad_filter = False
            # Store meta information
            fetch_targets = []
            for (feed_id,entryid,entry) in \
                         self._coffer.current_items(enable_ad_filter=enable_ad_filter,
                                                    check_existence=True):
                item = self._coffer._item_storage.add(feed        = feed_id,
                                                      item_id     = entryid,
                                                      title       = entry.title,
                                                      date_parsed = entry.date_parsed,
                                                      link        = entry.link,
                                                      description = entry.description)
                fetch_targets.append((str(feed_id),entry.link,entryid,item))
                counter += 1
            # Download contents
            try:
                self._coffer.fetch_and_store(fetch_targets)
            except FileStorageException,err:
                sys.stderr.write((u'Error: %s\n' % repr(err)).encode('utf-8'))
        except getopt.GetoptError,err:
            sys.stderr.write(str(err) + '\n')
            return
        self._coffer._item_storage.flush()
        sys.stdout.write((u'Added %d data records.\n' % counter).encode('utf-8'))

    def do_retrieve(self,parameters):
        '''
        Retrieval from the content repository, i.e. the file storage.
        '''
        is_regex    = False
        ignore_case = True
        list_items  = False
        extract     = None
        parameters = shlex.split(parameters)
        try:
            opts,args = getopt.getopt(parameters,'pcle:',
                                      ["pattern","case-sensitive","extract"])
            for o,a in opts:
                if o in ('-p','--pattern'):
                    is_regex = True
                elif o in ('-c','--case-sensitive'):
                    ignore_case = False
                elif o == '-l':
                    list_items = True
                elif o in ('-e','--extract'):
                    extract = a
        except getopt.GetoptError,err:
            sys.stderr.write(str(err) + '\n')
            return
        if len(args) == 0:
            sys.stderr.write('No feed name was specified.\n')
            return
        name_pattern = unicode(args[0],'utf-8')
        if not is_regex:
            name_pattern = re.escape(name_pattern)
        if ignore_case:
            p = re.compile(name_pattern,re.I)
        else:
            p = re.compile(name_pattern)
        feeds = filter(lambda y:p.search(y.name),self._coffer._feed_storage.feeds())
        for feed in feeds:
            sys.stdout.write((u'%d\t%s\n' % (feed.id,feed.name)).encode('utf-8'))
            if list_items:
                for text_id in self._coffer._file_storage.items(feed.id):
                    sys.stdout.write((u'\t\t%s\n' % text_id).encode('utf-8'))
            elif extract is not None:
                stream = self._coffer._file_storage.retrieve(feed.id,extract)
                if stream:
                    unicode_contents = unicode(stream.read(),'utf-8')
                    sys.stdout.write((u'%s\n' % unicode_contents).encode('utf-8'))

    def do_tablesync(self,parameters):
        '''
        For every item in the item storage that has its storage-block
        set to -1, check if we can find it in the file storage and
        update the storage-block accordingly.
        '''
        total_rows       = self._coffer._item_storage.total()
        processed_rows   = 0
        processed_tenths = 0
        need_to_update   = []
        for item in self._coffer._item_storage.items():
            if not item.is_stored():
                need_to_update.append(item)
            processed_rows += 1
            processed_percentage = int(100 * float(processed_rows) / total_rows)
            if (processed_percentage / 10) > processed_tenths:
                sys.stderr.write('Checked %d of %d rows, %d%%\n' % \
                                 (processed_rows,total_rows,processed_percentage))
                processed_tenths = processed_percentage / 10
        sys.stderr.write('Now updating storage block indicators...\n')
        no_updated = 0
        for item in need_to_update:
            sb = self._coffer._file_storage.determine_storage_block(item.feed,item.original_id)
            if sb is not None:
                item.set_storage_block(sb)
                no_updated += 1
        success_rate = int(100 * float(no_updated) / len(need_to_update))
        sys.stderr.write('...done. Successfully updated %d of %d (%d%%) records.\n' % \
                         (no_updated,len(need_to_update),success_rate))
        self._coffer._item_storage.flush()

    def do_reset(self,parameters):
        for item in self._coffer._item_storage.items():
            item.set_storage_block(-1)
        self._coffer._item_storage.flush()

    def do_fetch(self,parameters):
        '''
        Download articles that are missing from the file storage.
        '''
        counter = 0
        fetch_targets = []
        for item in self._coffer._item_storage.items_to_fetch():
            fetch_targets.append((str(item.feed),item.link,item.original_id,item))
            counter += 1
        # Download contents
        sys.stderr.write('Now downloading %d items.\n' % counter)
        try:
            self._coffer.fetch_and_store(fetch_targets)
        except FileStorageException,err:
            sys.stderr.write((u'Error: %s\n' % repr(err)).encode('utf-8'))
        self._coffer._item_storage.flush()
        sys.stdout.write((u'Added %d data records.\n' % counter).encode('utf-8'))

    def do_EOF(self,parameters):
        sys.stdout.write('\n')
        self._end_now = True

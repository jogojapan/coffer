# -*- coding: utf-8 -*-

'''
Created on 2011/06/11

@author: Johannes Goller
'''

from PyQt4 import QtCore

class QCounterUpdateThread(QtCore.QThread):
    def __init__(self,qcoffer,itemlist):
        '''
        itemlist must be a list of pairs QViewFeedItems
        objects.
        '''
        QtCore.QThread.__init__(self)
        self.qcoffer  = qcoffer
        self.itemlist = itemlist
        self.do_stop  = False

    def stop_now(self):
        self.do_stop = True

    def run(self):
        for qview_feed_items in self.itemlist:
            # qview_feed_items.setText('...')
            if self.do_stop:
                break
            feed_source = qview_feed_items.feed_source
            count = 0
            for _item in self.qcoffer.coffer.current_items_feed(self.qcoffer.coffer.clone_db_session(),
                                                               feed_source,True,True,False):
                count += 1
            qview_feed_items.setText('%d' % count)

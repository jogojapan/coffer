# -*- coding: utf-8 -*-

'''
Created on 2011/06/11

@author: Johannes Goller
'''

import sys
from coffer import Coffer
from PyQt4 import QtGui,QtCore

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
            if self.do_stop:
                break
            feed_source = qview_feed_items.feed_source
            count = 0
            for item in self.qcoffer.coffer.current_items_feed(self.qcoffer.coffer.clone_db_session(),
                                                               feed_source,True,True,False):
                count += 1
            qview_feed_items.setText('%d' % count)

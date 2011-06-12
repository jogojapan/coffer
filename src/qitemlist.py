# -*- coding: utf-8 -*-

'''
Created on 2011/04/17

@author: gollerjo
'''

from coffer import Coffer
from PyQt4 import QtGui,QtCore

class QItemList(QtGui.QDockWidget):
    def __init__(self,parent,coffer,feed_source):
        QtGui.QDockWidget.__init__(self,feed_source.name,parent)
        self._coffer = coffer

        table_data = []
        for item in coffer.current_items_feed(coffer._session,feed_source,True,True,False):
            table_data.append(item)
        item_table = QtGui.QTableWidget(len(table_data),2,self)
        row = 0
        for (feed_id,entry_id,entry) in table_data:
            item_table.setItem(row,0,QtGui.QTableWidgetItem(entry.title))
            item_table.setItem(row,1,QtGui.QTableWidgetItem(feed_id))
            row += 1
        item_table.resizeColumnsToContents()
        self.setWidget(item_table)
        self.item_table = item_table

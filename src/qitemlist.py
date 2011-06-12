# -*- coding: utf-8 -*-

'''
Created on 2011/04/17

@author: gollerjo
'''

from PyQt4 import QtGui

class QItemList(QtGui.QDockWidget):
    def __init__(self,parent,coffer,feed_source):
        QtGui.QDockWidget.__init__(self,feed_source.name,parent)
        self._coffer = coffer

        table_data = []
        for item in coffer.current_items_feed(coffer._session,feed_source,True,True,False):
            table_data.append(item)
        item_table = QtGui.QTableWidget(len(table_data),2,self)
        row = 0
        for (_feed_id,_entry_id,entry) in table_data:
            item_table.setItem(row,0,QtGui.QTableWidgetItem(entry.title))
            item_table.setItem(row,1,QtGui.QTableWidgetItem(entry.link))
            row += 1
        item_table.resizeColumnsToContents()
        item_table.resizeRowsToContents()
        self.setWidget(item_table)
        self.item_table = item_table

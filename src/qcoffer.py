# -*- coding: utf-8 -*-

'''
Created on 2011/06/11

@author: Johannes Goller
'''

import sys
import getopt
from ConfigParser import SafeConfigParser
from coffer import Coffer
from PyQt4 import QtGui,QtCore
from qitemlist import QItemList
from qcounter_update_thread import QCounterUpdateThread

class QViewFeedItems(QtGui.QTableWidgetItem):
    TYPE = QtGui.QTableWidgetItem.UserType
    def __init__(self,feed_source):
        QtGui.QTableWidgetItem.__init__(self,
                                        QtGui.QIcon.fromTheme('zoom-in'),
                                        ' ? ',
                                        QViewFeedItems.TYPE)
        self.setStatusTip('View new items for %s' % feed_source.name)
        self.feed_source = feed_source

class QCoffer(QtGui.QMainWindow):
    def __init__(self,config_path):
        QtGui.QMainWindow.__init__(self)
        self.setWindowIcon(QtGui.QIcon('gui/icons/coffer.ico'))

        # Parse config file
        config_parser = SafeConfigParser()
        config_parser.read(config_path)
        # Set up coffer
        self.coffer = Coffer(config_parser)

        self.setGeometry(1800,300,500,350)
        self.setWindowTitle(u'Coffer - A Corpus Feed Reader')

        feed_count = self.coffer._feed_storage.num_feeds()
        self.feed_table = QtGui.QTableWidget(feed_count,3,self)
        row = 0
        for feed_source in self.coffer._feed_storage.feeds():
            # Function
            action_item = QViewFeedItems(feed_source)
            self.feed_table.setItem(row,0,action_item)
            # Contents
            self.feed_table.setItem(row,1,QtGui.QTableWidgetItem(feed_source.name))
            self.feed_table.setItem(row,2,QtGui.QTableWidgetItem(feed_source.url))
            row += 1
        self.feed_table.resizeColumnsToContents()
        self.feed_table.itemClicked.connect(self.view_feed_items)
        self.adjust_width()
        self.setCentralWidget(self.feed_table)

        self.acQuit = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'),'Quit',self)
        self.acQuit.setShortcut('Ctrl+Q')
        self.acQuit.setStatusTip('Quit Coffer')
        self.connect(self.acQuit,QtCore.SIGNAL('triggered()'),QtCore.SLOT('close()'))

        self.acUpdateCounters = QtGui.QAction(QtGui.QIcon.fromTheme('view-refresh'),'Update counters',self)
        self.acUpdateCounters.setShortcut('F5')
        self.acUpdateCounters.setStatusTip('Update counters')
        self.connect(self.acUpdateCounters,QtCore.SIGNAL('triggered()'),self.update_counters)

        self.acUpdateDB = QtGui.QAction(QtGui.QIcon('gui/icons/coffer.ico'),'Update DB',self)
        #self.acUpdateDB.setShortcut('F5')
        self.acUpdateDB.setStatusTip('Update DB')
        self.connect(self.acUpdateDB,QtCore.SIGNAL('triggered()'),self.update_database)

        self.acAddFeed = QtGui.QAction(QtGui.QIcon.fromTheme('list-add'),'Add feed',self)
        self.acAddFeed.setShortcut('Strg+Ins')
        self.acAddFeed.setStatusTip('Add feed')
        self.connect(self.acAddFeed,QtCore.SIGNAL('triggered()'),self.add_feed)

        self.acDeleteFeed = QtGui.QAction(QtGui.QIcon.fromTheme('list-remove'),'Delete feed',self)
        self.acDeleteFeed.setShortcut('Strg+Del')
        self.acDeleteFeed.setStatusTip('Delete feed')
        # self.connect(self.acDeleteFeed,QtCore.SIGNAL('triggered()'),QtCore.SLOT('close()'))

        self.toolbar = self.addToolBar(u'Feeds')
        self.toolbar.addAction(self.acQuit)
        self.toolbar.addAction(self.acUpdateCounters)
        self.toolbar.addAction(self.acUpdateDB)
        self.toolbar.addAction(self.acAddFeed)
        self.toolbar.addAction(self.acDeleteFeed)

        self.statusBar()

        self.menubar = self.menuBar()
        self.menuFeeds = self.menubar.addMenu('&Feeds')
        self.menuFeeds.addAction(self.acAddFeed)
        self.menuFeeds.addAction(self.acDeleteFeed)
        self.menuFeeds.addAction(self.acQuit)

        self.threads_access = QtCore.QMutex()
        self.threads = []
        self.update_counters()

    def update_counters(self):
        thread = QCounterUpdateThread(self,
                                      [self.feed_table.item(row,0) \
                                       for row in range(self.feed_table.rowCount())])
        self.add_thread(thread)
        thread.start()

    def view_feed_items(self,table_widget_item):
        if table_widget_item.type() == QViewFeedItems.TYPE:
            dock = QItemList(self,self.coffer,table_widget_item.feed_source)
            dock.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea,dock)

    def add_thread(self,new_thread):
        self.threads_access.lock()
        aux_threads = []
        for thread in self.threads:
            if thread.isRunning():
                aux_threads.append(thread)
        aux_threads.append(new_thread)
        self.threads = aux_threads
        self.threads_access.unlock()

    def del_thread(self,thread):
        self.threads_access.lock()
        if thread in self.threads:
            self.threads.remove(thread)
        self.threads_access.unlock()

    def closeEvent(self,event):
        # QtGui.QMessageBox.information(self,u'Notification',u'Finishing.',
        #                               QtGui.QMessageBox.Ok)
        for thread in self.threads:
            if thread.isRunning():
                thread.stop_now()
                thread.wait()
        self.coffer.finish()
        event.accept()

    def add_feed(self):
        feed_url,ok = QtGui.QInputDialog.getText(self,u'New feed',u'URL:',text=u'http://')
        if ok:
            self.setStatusTip(u'Loading feed from %s' % feed_url)
            feed_url = str(feed_url)
            feed_title = self.coffer.get_feed_info(feed_url)
            if feed_title is None:
                QtGui.QMessageBox.warning(self,u'Invalid URL',u'Could not retrieve information from %s.' % feed_url,
                                              QtGui.QMessageBox.Ok)
                return
            self.coffer._feed_storage.add_feed(feed_title,feed_url)
            row = self.feed_table.rowCount()
            self.feed_table.insertRow(row)
            self.feed_table.setItem(row,0,QtGui.QTableWidgetItem(feed_title))
            self.feed_table.setItem(row,1,QtGui.QTableWidgetItem(feed_url))
            self.setStatusTip(u'')

    def update_database(self):
        pass

    def adjust_width(self):
        self.resize(50 + reduce(lambda x,y:x+y,
                                [self.feed_table.columnWidth(i) \
                                 for i in range(self.feed_table.columnCount())]),
                    350)


def usage():
    sys.stderr.write('Usage: coffer [-c <config-path>]\n')

def main():
    # Determine path to config file
    config_path = '../config/standard.cfg'
    try:
        opts = getopt.getopt(sys.argv[1:],'hc:',[])[0]
    except getopt.GetoptError,err:
        sys.stderr.write(str(err))
        usage()
        sys.exit(1)
    for o,a in opts:
        if o == '-h':
            usage()
            sys.exit(0)
        elif o == '-c':
            config_path = a
        else:
            usage()
            sys.exit(1)

    app = QtGui.QApplication(sys.argv)
    qcoffer = QCoffer(config_path)
    qcoffer.show()
    app.exec_()

if __name__ == '__main__':
    main()

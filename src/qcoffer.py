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

class QCoffer(QtGui.QMainWindow):
    def __init__(self,config_path):
        QtGui.QMainWindow.__init__(self)

        # Parse config file
        config_parser = SafeConfigParser()
        config_parser.read(config_path)
        # Set up coffer
        self._coffer = Coffer(config_parser)

        self.setGeometry(1800,300,500,350)
        self.setWindowTitle(u'Coffer - A Corpus Feed Reader')

        feed_count = self._coffer._feed_storage.num_feeds()
        self.feed_table = QtGui.QTableWidget(feed_count,2,self)
        row = 0
        for feed_source in self._coffer._feed_storage.feeds():
            self.feed_table.setItem(row,0,QtGui.QTableWidgetItem(feed_source.name))
            self.feed_table.setItem(row,1,QtGui.QTableWidgetItem(feed_source.url))
            row += 1
        self.feed_table.resizeColumnsToContents()
        self.adjust_width()
        self.setCentralWidget(self.feed_table)

        self.acQuit = QtGui.QAction(QtGui.QIcon.fromTheme('application-exit'),'Quit',self)
        self.acQuit.setShortcut('Ctrl+Q')
        self.acQuit.setStatusTip('Quit Coffer')
        self.connect(self.acQuit,QtCore.SIGNAL('triggered()'),QtCore.SLOT('close()'))

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
        self.toolbar.addAction(self.acAddFeed)
        self.toolbar.addAction(self.acDeleteFeed)

        self.statusBar()

        self.menubar = self.menuBar()
        self.menuFeeds = self.menubar.addMenu('&Feeds')
        self.menuFeeds.addAction(self.acAddFeed)
        self.menuFeeds.addAction(self.acDeleteFeed)
        self.menuFeeds.addAction(self.acQuit)

    def closeEvent(self,event):
        # QtGui.QMessageBox.information(self,u'Notification',u'Finishing.',
        #                               QtGui.QMessageBox.Ok)
        self._coffer.finish()
        event.accept()

    def add_feed(self):
        feed_url,ok = QtGui.QInputDialog.getText(self,u'New feed',u'URL:',text=u'http://')
        if ok:
            self.setStatusTip(u'Loading feed from %s' % feed_url)
            feed_url = str(feed_url)
            feed_title = self._coffer.get_feed_info(feed_url)
            if feed_title is None:
                QtGui.QMessageBox.warning(self,u'Invalid URL',u'Could not retrieve information from %s.' % feed_url,
                                              QtGui.QMessageBox.Ok)
                return
            self._coffer._feed_storage.add_feed(feed_title,feed_url)
            row = self.feed_table.rowCount()
            self.feed_table.insertRow(row)
            self.feed_table.setItem(row,0,QtGui.QTableWidgetItem(feed_title))
            self.feed_table.setItem(row,1,QtGui.QTableWidgetItem(feed_url))
            self.setStatusTip(u'')

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

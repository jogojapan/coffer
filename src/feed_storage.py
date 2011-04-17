# -*- coding: utf-8 -*-

import sys
import getopt
import os.path
from os import mkdir
from ConfigParser import SafeConfigParser
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer,String
from sqlalchemy import Column
from sqlalchemy.orm import sessionmaker
from command_shell import CommandShell
# import feedparser

Base = declarative_base()
class FeedSource(Base):
    __tablename__ = 'feed-sources'

    id   = Column(Integer,primary_key=True)
    name = Column(String)
    url  = Column(String)
    
    def __init__(self,name,url):
        self.name = name
        self.url  = url
    
    def __repr__(self):
        return u'FeedSource("%s","%s")' % (self.name,self.url)


class FeedStorage:
    def __init__(self,database_path):
        # Connect to engine
        dir = os.path.dirname(database_path)
        if not os.path.exists(dir):
            mkdir(dir)
        sys.stderr.write('Connecting to database at "%s"\n' % database_path)
        self._engine = create_engine('sqlite:///%s' % database_path,echo=True)

        # Create tables that don't exits yet
        FeedSource.metadata.create_all(self._engine)

        # Start session
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
    
    def add_feed(self,name,url):
        self._session.add(FeedSource(name,url))
        self._session.commit()
    
    def list_feeds(self,out_strm):
        for feed_source in self._session.query(FeedSource).all():
            out_strm.write('%s\n' % str(feed_source))
        

def usage():
    sys.stderr.write('Usage: feed_update [-c <config-path>]\n')

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
    config_parser = SafeConfigParser()
    config_parser.read(config_path)

    database_path = 'test'
    if config_parser.has_option('FeedStorage','database-path'):
        database_path = config_parser.get('FeedStorage','database-path')

    feed_storage = FeedStorage(database_path)
    shell = CommandShell(feed_storage)
    shell.cmdloop()

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer,String
from sqlalchemy import Column

Base = declarative_base()
class FeedSource(Base):
    '''
    Representation of one feed as a database record.
    '''
    __tablename__ = 'feed-sources'

    id   = Column(Integer,primary_key=True)
    name = Column(String)
    url  = Column(String)
    
    def __init__(self,name,url):
        self.name = name
        self.url  = url
    
    def __repr__(self):
        return u'FeedSource("%s","%s")' % (self.name,self.url)
    
    def get_name(self):
        return self.name
    def get_url(self):
        return self.url


class FeedStorage:
    '''
    Representation of the feeds table.
    '''
    def __init__(self,engine,session):
        self._engine  = engine
        self._session = session
        # Create tables that don't exits yet
        FeedSource.metadata.create_all(self._engine)

    def add_feed(self,name,url):
        self._session.add(FeedSource(name,url))
        self._session.commit()
    
    def list_feeds(self,out_strm):
        for feed_source in self._session.query(FeedSource).all():
            out_strm.write('%s\n' % str(feed_source))

    def feeds(self):
        for feed_source in self._session.query(FeedSource).all():
            yield feed_source

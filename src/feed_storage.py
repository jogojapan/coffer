# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer,String,PickleType
from sqlalchemy import Column

Base = declarative_base()
class FeedSource(Base):
    '''
    Representation of one feed as a database record.
    '''
    __tablename__ = 'feed-sources'

    id         = Column(Integer,primary_key=True)
    name       = Column(String(convert_unicode=True))
    url        = Column(String)
    # A list of regular expressions used to filter titles of advertisements
    ad_filters = Column(PickleType)
    
    def __init__(self,name,url):
        self.name       = name
        self.url        = url
        self.ad_filters = []
    
    def __repr__(self):
        return u'FeedSource("%s","%s",%s)' % (self.name,
                                              self.url,
                                              self.ad_filters)
    
    def get_name(self):
        return self.name
    def get_url(self):
        return self.url
    def get_id(self):
        return self.id
    def add_ad_regex(self,regex):
        self.ad_filters.append(regex)


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

    def add_regex(self,filter_string,regex,out_stream):
        counter = 0
        for feed_source in self._session.query(FeedSource). \
                filter(FeedSource.name.like(filter_string)):
            out_stream.write((u'%s\n' % feed_source.name).encode('utf-8'))
            feed_source.add_ad_regex(regex)
            counter += 1
        self._session.commit()
        out_stream.write('Added filter regex to %d feed definitions.\n' % counter)

'''
Created on 2011/04/17

@author: gollerjo
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer,String,BigInteger
from sqlalchemy import Column
from time import gmtime,strptime
from calendar import timegm

Base = declarative_base()
class Item(Base):
    '''
    Representation of an item, i.e. an article obtained from an RSS or Atom feed.
    '''
    __tablename__ = 'items'
    
    # Primary key
    id          = Column(Integer,primary_key=True)
    # Reference to the feed this came from
    feed        = Column(Integer,index=True)
    # ID obtained from the feed
    original_id = Column(String,index=True)
    title       = Column(String(convert_unicode=True))
    date        = Column(BigInteger,index=True)
    link        = Column(String)
    description = Column(String(convert_unicode=True))
    # If the link was downloaded and stored in the file storage,
    # this specifies the block number. Otherwise it will be set
    # to -1.
    storage_block = Column(Integer,default=-1)

    def __init__(self,feed,original_id,title,date_parsed,link,description):
        self.feed        = feed
        self.original_id = original_id
        self.title       = title
        self.date        = timegm(date_parsed)
        self.link        = link
        self.description = description

    def __repr__(self):
        return u'Item(%s,"%s",%s)' % (strptime(gmtime(self.date)),
                                      self.title,
                                      self.link)

    def is_stored(self):
        return (self.storage_block != -1)

    def set_storage_block(self,sb):
        self.storage_block = sb

class ItemStorage:
    '''
    Representation of the items table.
    '''
    def __init__(self,engine,session):
        self._engine  = engine
        self._session = session
        # Create tables that don't exits yet
        Item.metadata.create_all(self._engine)

    def exists(self,original_id):
        c = self._session.query(Item).filter(Item.original_id == original_id).count()
        return (c != 0)

    def items(self):
        for item in self._session.query(Item).all():
            yield item

    def items_to_fetch(self):
        for item in self._session.query(Item).filter(Item.storage_block == -1):
            yield item

    def total(self):
        return self._session.query(Item).count()

    def add(self,feed,item_id,title,date_parsed,link,description):
        '''
        Create a new item and insert it into the database.
        @return: The item that was created, in case the caller wants to
           modify it.
        '''
        item = Item(feed=feed,
                    original_id  = item_id,
                    title        = title,
                    date_parsed  = date_parsed,
                    link         = link,
                    description  = description)
        self._session.add(item)
        return item

    def flush(self):
        self._session.commit()

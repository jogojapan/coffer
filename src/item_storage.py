'''
Created on 2011/04/17

@author: gollerjo
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer,String,BigInteger
from sqlalchemy import Column
from time import gmtime,strptime

Base = declarative_base()
class Item(Base):
    '''
    Representation of an item, i.e. an article obtained from an RSS or Atom feed.
    '''
    __tablename__ = 'items'
    
    # Primary key
    id          = Column(Integer,primary_key=True)
    # ID obtained from the feed
    original_id = Column(String,index=True)
    title       = Column(String,convert_unicode=True)
    date        = Column(BigInteger,index=True)
    link        = Column(String)
    description = Column(String,convert_unicode=True)

    def __init__(self,original_id,title,date,link,description):
        self.original_id = original_id
        self.title       = title
        self.date        = date
        self.link        = link
        self.description = description

    def __repr__(self):
        return u'Item(%s,"%s",%s)' % (strptime(gmtime(self.date)),
                                      self.title,
                                      self.link)

class ItemStorage:
    '''
    Representation of the items table.
    '''
    def __init__(self,engine,session):
        self._engine  = engine
        self._session = session
        # Create tables that don't exits yet
        Item.metadata.create_all(self._engine)
    
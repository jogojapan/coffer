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
    _id          = Column(Integer,primary_key=True)
    # ID obtained from the feed
    _original_id = Column(String,index=True)
    _title       = Column(String)
    _date        = Column(BigInteger,index=True)
    _link        = Column(String)
    _description = Column(String)

    def __init__(self,original_id,title,date,link,description):
        self._original_id = original_id
        self._title       = title
        self._date        = date
        self._link        = link
        self._description = description

    def __repr__(self):
        return u'Item(%s,"%s",%s)' % (strptime(gmtime(self._date)),
                                      self._title,
                                      self._link)

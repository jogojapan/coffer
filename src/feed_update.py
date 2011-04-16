from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer,String
from sqlalchemy import Column
from sqlalchemy.orm import sessionmaker
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


def main():
    engine = create_engine('sqlite:///test',echo=True)
    session = sessionmaker(bind=engine)
    session.add(FeedSource('Asahi 政治','http://rss.asahi.com/f/asahi_politics'))
    session.commit()

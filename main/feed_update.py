from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import feedparser

Base = declarative_base()
class FeedSource(Base):
    __tablename__ = 'feed-sources'

    id   = Column(Integer,primary_key=True)
    name = Column(String)
    url  = Column(String)


def main():
    engine = create_engine('sqlite:///test',echo=True)

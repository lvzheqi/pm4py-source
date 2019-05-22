from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('sqlite://', echo=False)

df = pd.DataFrame({'name': ['User 1', 'User 2', 'User 3']})

# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# # Base = declarative_base()
#
#
# class PTreeDB(Base):
#     __tablename__ = "ptree"
#
#     id = Column(Integer, primary_key=True)
#     tree = Column(String)
#     root = Column(String)
#
#
# class MPTreeDB(Base):
#     __tablename__ = "mptree"
#
#     id = Column(Integer, primary_key=True)
#     tree = Column(id, ForeignKey('ptree.id'))
#     mtree = Column(String)
#     root = Column(String)
#
#
# class LogDB(Base):
#     __tablename__= "log"
#
#     id = Column(Integer, primary_key=True)
#     log = Column(String)

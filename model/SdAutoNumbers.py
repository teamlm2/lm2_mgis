__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, ForeignKey,Sequence
from sqlalchemy.orm import relationship, backref
from Base import *

class SdAutoNumbers(Base):

    __tablename__ = 'auto_numbers'

    id = Column(String, primary_key=True)
    name = Column(String)
    number = Column(Integer)
    created_at = Column(String)
    updated_at = Column(String)
    classes = Column(String)
    format = Column(String)
    length = Column(Integer)


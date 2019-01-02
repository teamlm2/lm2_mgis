__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, ForeignKey,Sequence
from sqlalchemy.orm import relationship, backref
from Base import *

class SdConfiguration(Base):

    __tablename__ = 'sd_configuration'

    id = Column(String, primary_key=True)
    code = Column(String)
    value = Column(String)
    description = Column(String)
    updated_at = Column(String)
    created_at = Column(String)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    is_fixed = Column(Integer)


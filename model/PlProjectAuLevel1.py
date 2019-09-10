__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from Base import *

class PlProjectAuLevel1(Base):

    __tablename__ = 'pl_project_au_level1'

    created_at = Column(DateTime)
    created_by = Column(Integer)
    is_all_au2 = Column(Boolean)
    # foreign keys:

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    au1_code = Column(Integer, ForeignKey('au_level1.code'), primary_key=True)
    au1_ref = relationship("AuLevel1")



__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from Base import *

class PlProjectAuLevel2(Base):

    __tablename__ = 'pl_project_au_level2'

    created_at = Column(DateTime)
    created_by = Column(Integer)
    is_all_au3 = Column(Boolean)

    # foreign keys:

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    au2_code = Column(Integer, ForeignKey('au_level2.code'), primary_key=True)
    au2_ref = relationship("AuLevel2")



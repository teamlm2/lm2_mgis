__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float, Boolean
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from Base import *

class PlProjectAuLevel3(Base):

    __tablename__ = 'pl_project_au_level3'

    created_at = Column(DateTime)
    created_by = Column(Integer)

    # foreign keys:

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    au3_code = Column(Integer, ForeignKey('au_level3.code'), primary_key=True)
    au3_ref = relationship("AuLevel3")



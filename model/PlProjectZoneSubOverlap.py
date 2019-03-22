__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Base import *


class PlProjectZoneSubOverlap(Base):

    __tablename__ = 'pl_project_zone_sub_overlap'

    zone_sub_id_src = Column(String, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_id_src_ref = relationship("ClZoneSub")

    zone_sub_id_trg = Column(String, ForeignKey('cl_zone_sub.zone_sub_id'), primary_key=True)
    zone_sub_id_trg_ref = relationship("ClZoneSub")

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    created_at = Column(DateTime)
    created_by = Column(Integer)
__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Base import *


class PlProjectZoneActivity(Base):

    __tablename__ = 'pl_project_zone_activity'

    zone_activity_id = Column(String, ForeignKey('cl_zone_activity.zone_activity_id'), primary_key=True)
    zone_activity_ref = relationship("ClZoneActivity")

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    created_at = Column(DateTime)
    created_by = Column(Integer)
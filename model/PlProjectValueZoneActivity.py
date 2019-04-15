__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Base import *
from PlProjectParcelZoneActivity import *

class PlProjectValueZoneActivity(Base):

    __tablename__ = 'pl_project_value_zone_activity'

    attribute_id = Column(Integer, ForeignKey('cl_attribute_zone.attribute_id'), primary_key=True)
    attribute_ref = relationship("ClAttributeZone")

    parcel_id = Column(String, ForeignKey('pl_project_parcel_zone_activity.parcel_id'), primary_key=True)
    parcel_ref = relationship("PlProjectParcelZoneActivity")

    attribute_value = Column(String)

    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)
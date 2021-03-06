__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from LdProcessPlan import *

class ClAttributeZoneMainZoneValue(Base):

    __tablename__ = 'ld_attribute_main_zone_value'

    id = Column(Integer, primary_key=True)
    attribute_value = Column(String)
    description = Column(String)

    # foreign keys:
    attribute_process_id = Column(Integer, ForeignKey('ld_attribute_process.id'))
    attribute_process_ref = relationship("ClAttributeZoneProcess")

    parcel_id = Column(Integer, ForeignKey('ld_project_main_zone_parcel.parcel_id'))
    parcel_ref = relationship("LdProjectMainZone")

    plan_draft_id = Column(Integer, ForeignKey('ld_project_plan.plan_draft_id'))
    plan_draft_ref = relationship("LdProjectPlan")


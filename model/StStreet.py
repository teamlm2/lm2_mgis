__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from Base import *
from ClAddressSource import *
from ClStreetType import *

class StStreet(Base):

    __tablename__ = 'st_street'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    name_en = Column(String)
    decision_date = Column(Date)
    decision_no = Column(String)
    description = Column(String)
    is_active = Column(Boolean)
    valid_from = Column(Date)
    valid_till = Column(Date)
    area_m2 = Column(Float)
    geometry = Column(Geometry('MULTIPOLYGON', 4326))
    line_geom = Column(Geometry('MULTILINESTRING', 4326))
    parent_id = Column(Integer)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    decision_level_id = Column(Integer, ForeignKey('cl_plan_decision_level.plan_decision_level_id'))
    decision_level_id_ref = relationship("ClPlanDecisionLevel")

    street_type_id = Column(Integer, ForeignKey('cl_street_type.code'))
    street_type_id_ref = relationship("ClStreetType")

    in_source = Column(Integer, ForeignKey('cl_address_source.code'))
    in_source_ref = relationship("ClAddressSource")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    au3 = Column(String, ForeignKey('au_level3.code'))
    au3_ref = relationship("AuLevel3")
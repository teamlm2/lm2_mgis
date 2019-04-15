__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from LdProcessPlan import *

class LdProjectSubZone(Base):

    __tablename__ = 'ld_project_sub_zone_parcel'

    parcel_id = Column(Integer, primary_key=True)
    area_m2 = Column(Float)
    area_ha = Column(Float)
    gazner = Column(String)
    txt = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)
    polygon_geom = Column(Geometry('POLYGON', 4326))

    # foreign keys:
    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    plan_draft_id = Column(Integer, ForeignKey('ld_project_plan.plan_draft_id'))
    plan_draft_ref = relationship("LdProjectPlan")

    badedturl = Column(Integer, ForeignKey('ld_process_plan.code'))
    process_ref = relationship("LdProcessPlan")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    au3 = Column(String, ForeignKey('au_level3.code'))
    au3_ref = relationship("AuLevel3")

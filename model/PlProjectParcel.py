__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from CtApp1Ext import *
from ClPlanZone import *

class PlProjectParcel(Base):

    __tablename__ = 'pl_project_parcel'

    parcel_id = Column(Integer, primary_key=True)
    area_m2 = Column(Float)
    area_ha = Column(Float)
    gazner = Column(String)
    txt = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)
    badedturl = Column(String)
    is_active = Column(Boolean)

    polygon_geom = Column(Geometry('POLYGON', 4326))
    line_geom = Column(Geometry('LINESTRING', 4326))
    point_geom = Column(Geometry('POINT', 4326))

    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    # foreign keys:
    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    project_id = Column(Integer, ForeignKey('pl_project.project_id'))
    project_ref = relationship("PlProject")

    plan_zone_id = Column(Integer, ForeignKey('cl_plan_zone.plan_zone_id'))
    plan_zone_ref = relationship("ClPlanZone")

    right_form_id = Column(Integer, ForeignKey('cl_right_form.right_form_id'))
    right_form_ref = relationship("ClRightForm")

    right_type_code = Column(Integer, ForeignKey('cl_right_type.code'))
    right_type_ref = relationship("ClRightType")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    au3 = Column(String, ForeignKey('au_level3.code'))
    au3_ref = relationship("AuLevel3")

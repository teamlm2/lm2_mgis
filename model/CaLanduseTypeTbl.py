
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *

class CaLanduseTypeTbl(Base):

    __tablename__ = 'ca_landuse_type_tbl'

    parcel_id = Column(String, primary_key=True)
    is_active = Column(Boolean)
    area_m2 = Column(Float)
    documented_area_m2 = Column(Float)
    address_khashaa = Column(String)
    address_streetname = Column(String)
    address_neighbourhood = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)
    geometry = Column(Geometry('POLYGON', 4326))

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    case_id = Column(Integer)

    # foreign keys:
    cad_parcel_id = Column(Integer, ForeignKey('ca_parcel_tbl.parcel_id'))
    cad_parcel_id_ref = relationship("CaParcelTbl")

    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    landuse_level1 = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_level1_ref = relationship("ClLanduseType")

    landuse_level2 = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_level2_ref = relationship("ClLanduseType")

    #applications = relationship("CtApplication")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    au3 = Column(String, ForeignKey('au_level3.code'))
    au3_ref = relationship("AuLevel3")
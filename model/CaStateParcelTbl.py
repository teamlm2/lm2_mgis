
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from ClStateParcelType import *

class CaStateParcelTbl(Base):

    __tablename__ = 'ca_state_parcel_tbl'

    id = Column(Integer, primary_key=True)
    parcel_id = Column(String)
    land_name = Column(String)
    address_neighbourhood = Column(String)
    area_m2 = Column(Float)
    spa_law = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)

    geometry = Column(Geometry('POLYGON', 4326))

    # foreign keys:
    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    department_id = Column(String, ForeignKey('hr_department.department_id'))
    department_ref = relationship("SdDepartment")

    state_parcel_type = Column(Integer, ForeignKey('cl_state_parcel_type.code'))
    state_parcel_type_ref = relationship("ClStateParcelType")

__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from ClUbEditStatus import *

class CaUBParcelTbl(Base):

    __tablename__ = 'ca_ub_parcel_tbl'

    parcel_id = Column(String)
    old_parcel_id = Column(String, primary_key=True)
    geo_id = Column(String)
    area_m2 = Column(Float)
    documented_area_m2 = Column(Float)
    address_khashaa = Column(String)
    address_streetname = Column(String)
    address_neighbourhood = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)
    geometry = Column(Geometry('POLYGON', 4326))
    parcel_base_id = Column(String)
    # foreign keys:
    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    edit_status = Column(Integer, ForeignKey('cl_ub_edit_status.code'))
    edit_status_ref = relationship("ClUbEditStatus")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    ub_parcel_type = Column(String, ForeignKey('cl_ub_parcel_type.code'))
    ub_parcel_type_ref = relationship("ClUbParcelType")

    deleted_status_date = Column(Date)
    deleted_status_decision_date = Column(Date)
    deleted_status_decision_no = Column(String)
    deleted_status_comment = Column(String)
    deleted_status_user = Column(String)

    type_created_by = Column(Integer)
    type_updated_by = Column(Integer)

    type_created_at = Column(Date)
    type_updated_at = Column(Date)
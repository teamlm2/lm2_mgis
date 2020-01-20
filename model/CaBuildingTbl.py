
__author__ = 'Ankhaa'
from sqlalchemy import Column, String, Float, Date, Integer
from geoalchemy2 import Geometry
from Base import *

class CaBuildingTbl(Base):

    __tablename__ = 'ca_building_tbl'

    building_id = Column(String, primary_key=True)
    building_no = Column(String)
    geo_id = Column(String)
    area_m2 = Column(Float)
    address_khashaa = Column(String)
    address_streetname = Column(String)
    address_neighbourhood = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)
    geometry = Column(Geometry('POLYGON', 4326))
    org_type = Column(Integer)
    au2 = Column(String)
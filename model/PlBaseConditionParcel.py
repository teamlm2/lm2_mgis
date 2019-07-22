__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime, Table, Float
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry
from ClLanduseType import *
from ClBaseConditionType import *

class PlBaseConditionParcel(Base):

    __tablename__ = 'pl_base_condition_parcel'

    parcel_id = Column(Integer, primary_key=True)
    name = Column(String)
    place_name = Column(String)
    description = Column(String)
    area_m2 = Column(Float)

    geometry = Column(Geometry('POLYGON', 4326))

    # foreign keys:
    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    base_condition_type = Column(Integer, ForeignKey('cl_base_condition_type.base_condition_type_id'))
    base_condition_type_ref = relationship("ClBaseConditionType")



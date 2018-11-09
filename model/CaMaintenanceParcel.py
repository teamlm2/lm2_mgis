__author__ = 'Ankhaa'

from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from SetRole import *
from SetSurveyor import *
from CtApplication import *

class CaMaintenanceParcel(Base):

    __tablename__ = 'ca_parcel_maintenance_case'

    parcel = Column(String, primary_key=True)
    maintenance = Column(Integer)
    case_id = Column(String)


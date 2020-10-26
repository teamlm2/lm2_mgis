__author__ = 'Ankhaa'

from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from SetRole import *
from CaLanduseMaintenanceCase import *
from StWorkflow import *

class CaLanduseMaintenanceStatus(Base):

    __tablename__ = 'ca_landuse_maintenance_status'

    id = Column(Integer, primary_key=True)
    status_date = Column(Date)
    description = Column(String)
    # foreign keys:
    case_id = Column(Integer, ForeignKey('ca_landuse_maintenance_case.id'))
    case_ref = relationship("CaLanduseMaintenanceCase")

    status_id = Column(Integer, ForeignKey('cl_landuse_movement_status.code'))
    status_ref = relationship("ClLanduseMovementStatus")

    officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    officer_in_charge_ref = relationship("SdUser", foreign_keys=[officer_in_charge], cascade="save-update")

    next_officer_in_charge = Column(Integer, ForeignKey('sd_user.user_id'))
    next_officer_in_charge_ref = relationship("SdUser", foreign_keys=[next_officer_in_charge], cascade="save-update")


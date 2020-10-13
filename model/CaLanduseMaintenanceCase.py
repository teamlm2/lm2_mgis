__author__ = 'Ankhaa'

from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from SetRole import *
from SetSurveyor import *
from CtApplication import *

parcel_table = Table('ca_landuse_parcel_maintenance_case', Base.metadata,
                        Column('case_id', Integer, ForeignKey('ca_landuse_maintenance_case.id')),
                        Column('landuse_parcel', String, ForeignKey('ca_landuse_type_tbl.parcel_id'))
                    )


class CaLanduseMaintenanceCase(Base):

    __tablename__ = 'ca_landuse_maintenance_case'

    id = Column(Integer, primary_key=True)
    creation_date = Column(Date)
    completion_date = Column(Date)
    # foreign keys:
    workflow_id = Column(Integer, ForeignKey('data_landuse.st_workflow'))
    workflow_ref = relationship("SetWorkflow")

    completed_by = Column(Integer, ForeignKey('sd_user.user_id'))
    created_by = Column(Integer, ForeignKey('sd_user.user_id'))
    updated_by = Column(Integer, ForeignKey('sd_user.user_id'))
    # created_by_ref = relationship("SetRole")

    created_at = Column(Date)
    updated_at = Column(Date)

    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")


__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class SetOrgTypeSpaTypeLanduse(Base):

    __tablename__ = 'set_org_type_spa_type_landuse'

    org_type = Column(Integer, ForeignKey('sd_organization.id'), primary_key=True)
    org_type_ref = relationship("SdOrganization")

    spa_type = Column(String, ForeignKey('cl_spa_type.code'), primary_key=True)
    spa_type_ref = relationship("ClSpaType")

    landuse = Column(String, ForeignKey('cl_landuse_type.code'), primary_key=True)
    landuse_ref = relationship("ClLanduseType")
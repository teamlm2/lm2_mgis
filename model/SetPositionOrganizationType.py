__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class SetPositionOrganizationType(Base):
    __tablename__ = 'set_position_organization_type'
    position = Column(String, ForeignKey('cl_position_type.code'), primary_key=True)
    position_ref = relationship("ClPositionType")

    organization = Column(Integer, ForeignKey('cl_organization_type.code'), primary_key=True)
    organization_ref = relationship("ClOrganizationType")
__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class SetApplicationTypeParcelType(Base):

    __tablename__ = 'set_application_type_parcel_type'

    app_type = Column(String, ForeignKey('cl_application_type.code'), primary_key=True)
    app_type_ref = relationship("ClApplicationType")

    parcel_type = Column(Integer, ForeignKey('cl_parcel_type.code'), primary_key=True)
    parcel_type_ref = relationship("ClParcelType")
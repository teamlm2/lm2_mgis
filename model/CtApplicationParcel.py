__author__ = 'B.Ankhbold'
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from Base import *


class CtApplicationParcel(Base):

    __tablename__ = 'ct_application_parcel'

    app_id = Column(String, ForeignKey('ct_application.app_id'), primary_key=True)
    parcel_id = Column(String)

    parcel_type = Column(Integer, ForeignKey('cl_parcel_type.code'), primary_key=True)
    parcel_type_ref = relationship("ClParcelType")
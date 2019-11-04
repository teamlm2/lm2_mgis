__author__ = 'B.Ankhbold'
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from Base import *


class PlProjectParcelRefPastureParcel(Base):

    __tablename__ = 'pl_project_parcel_ref_pasture_parcel'

    id = Column(Integer, primary_key=True)
    parcel_id = Column(Integer, ForeignKey('pl_project_parcel.parcel_id'))
    ref_parcel_id = Column(Integer, ForeignKey('pl_project_parcel.parcel_id'))
    pasture_parcel_id = Column(String, ForeignKey('ca_pasture_parcel_tbl.parcel_id'))

    is_cadastre = Column(Boolean)

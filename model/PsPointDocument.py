__author__ = 'B.Ankhbold'
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class PsPointDocument(Base):

    __tablename__ = 'ps_point_document'

    point_detail_id = Column(String, ForeignKey('ps_point_detail.point_detail_id'), primary_key=True)
    document_id = Column(Integer, ForeignKey('ct_document.id'), primary_key=True)
    role = Column(String)
    monitoring_year = Column(Integer)
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from Base import *


class CtApplicationDocument(Base):

    __tablename__ = 'ct_application_document'

    application_id = Column(String, ForeignKey('ct_application.app_id'), primary_key=True)
    document_id = Column(Integer, ForeignKey('ct_document.id'), primary_key=True)
    role = Column(Integer, ForeignKey('cl_document_role.code'))
    is_send = Column(Boolean)
    # person = Column(Integer, ForeignKey('bs_person.person_id'))
    # app_no = Column(String)

    document_ref = relationship("CtDocument", backref="applications", cascade="all")
    # person_ref = relationship("BsPerson", backref="application_documents")
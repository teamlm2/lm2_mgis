__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Sequence, Binary, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class PlDocument(Base):

    __tablename__ = 'pl_document'

    document_id = Column(Integer, Sequence('ct_document_id_seq'), primary_key=True)
    name = Column(String)
    file_url = Column(String)
    description = Column(String)
    ftp_id = Column(Integer)

    created_at = Column(DateTime)
    created_by = Column(Integer)
    updated_at = Column(DateTime)
    updated_by = Column(Integer)

    document_type_id = Column(Integer, ForeignKey('cl_document_type.document_type_id'))
    document_type_ref = relationship("ClDocumentType")


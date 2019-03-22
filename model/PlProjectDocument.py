__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from Base import *


class PlProjectDocument(Base):

    __tablename__ = 'pl_project_document'

    document_id = Column(String, ForeignKey('pl_document.document_id'), primary_key=True)
    document_ref = relationship("PlDocument")

    project_id = Column(Integer, ForeignKey('pl_project.project_id'), primary_key=True)
    project_ref = relationship("PlProject")

    created_at = Column(DateTime)
    created_by = Column(Integer)
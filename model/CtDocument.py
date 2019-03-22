__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Sequence, Binary, DateTime
from Base import *


class CtDocument(Base):

    __tablename__ = 'ct_document'

    id = Column(Integer, Sequence('ct_document_id_seq'), primary_key=True)
    name = Column(String)
    created_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    file_url = Column(String)
    ftp_id = Column(Integer)


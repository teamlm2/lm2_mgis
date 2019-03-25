__author__ = 'B.Ankhbold'

from sqlalchemy import Column, String, Integer, Boolean
from Base import *


class ClDocumentRole(Base):

    __tablename__ = 'cl_document_role'

    code = Column(Integer, primary_key=True)
    description = Column(String)
    description_en = Column(String)

    is_required = Column(Boolean)
    is_ubeg_required = Column(Boolean)
    is_ubeg_after_required = Column(Boolean)

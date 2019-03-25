__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Sequence, Boolean
from sqlalchemy.orm import relationship, backref
from Base import *


class SetCertificate(Base):

    __tablename__ = 'set_certificate'

    id = Column(Integer, Sequence('set_certificate_id_seq'), primary_key=True)
    description = Column(String)
    range_first_no = Column(Integer)
    range_last_no = Column(Integer)
    current_no = Column(Integer)
    begin_date = Column(Date)
    end_date = Column(Date)
    is_valid = Column(Boolean)

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    certificate_type = Column(Integer, ForeignKey('cl_certificate_type.code'))
    certificate_type_ref = relationship("ClCertificateType")

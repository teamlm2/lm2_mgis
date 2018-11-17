__author__ = 'Ankhbold'

from sqlalchemy import Column, String, Integer, Date,DateTime, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from ClEmployeeType import *
from ClUserCancelReason import *
from Base import *


class SdFtpPermission(Base):

    __tablename__ = 'sd_ftp_permission'

    ftp_perm_id = Column(Integer, primary_key=True)
    ftp_id = Column(String)
    aimag_code = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
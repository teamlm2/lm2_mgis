__author__ = 'Ankhbold'

from sqlalchemy import Column, String, Integer, Date,DateTime, Boolean, ForeignKey, Sequence
from sqlalchemy.orm import relationship
from ClEmployeeType import *
from ClUserCancelReason import *
from Base import *


class SdFtpConnection(Base):

    __tablename__ = 'sd_ftp_connection'

    ftp_id = Column(Integer, primary_key=True)
    host = Column(String)
    username = Column(String)
    password = Column(String)
    root_dir = Column(String)
    port = Column(String)
    passive = Column(String)
    ssl = Column(String)
    timeout = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
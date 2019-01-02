__author__ = 'B.Ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError
import shutil
import os
import subprocess
from ..utils.DatabaseUtils import *
import sys
# import chilkat

class FtpConnection():

    def __init__(self):
        self.session = SessionHandler().session_instance()

    @staticmethod
    def chdir(ftp_path, ftp_conn):
        dirs = [d for d in ftp_path.split('/') if d != '']
        for p in dirs:
            FtpConnection.check_dir(p, ftp_conn)

    @staticmethod
    def check_dir(dir, ftp_conn):

        filelist = []
        ftp_conn.retrlines('LIST', filelist.append)
        found = False

        for f in filelist:
            if f.split()[-1] == dir and f.lower().startswith('d'):
                found = True

        if not found:
            ftp_conn.mkd(dir)
        ftp_conn.cwd(dir)

    @staticmethod
    def upload_app_ftp_file(file, file_name, ftp):

        file = open(file, 'rb')  # file to send
        file_b = 'STOR ' + file_name
        ftp.storbinary(file_b, file)

    # @staticmethod
    # def move_app_ftp_file(ftp):
    #
    #     # ftp.rename('mgis/test/dir0', 'mgis/test/parcel')
    #
    #     ftp = chilkat.CkFtp2()
    #
    #     #  Any string unlocks the component for the 1st 30-days.
    #     success = ftp.UnlockComponent("Anything for 30-day trial")
    #     # if (success != True):
    #     #     print(ftp.lastErrorText())
    #         # sys.exit()
    #
    #     ftp.put_Hostname("192.168.15.249")
    #     ftp.put_Username("alagacftp")
    #     ftp.put_Password("12gazar!@")
    #
    #     success = ftp.Connect()
    #     print success
    #
    #     # Rename the remote file (or directory)
    #     existingFilepath = "mgis/test/app1"
    #     newFilepath = "mgis/test/parcel"
    #     success = ftp.RenameRemoteFile(existingFilepath, newFilepath)
    #     # success = ftp.
    #     if (success != True):
    #         print(ftp.lastErrorText())
    #         # sys.exit()
    #
    #     success = ftp.Disconnect()
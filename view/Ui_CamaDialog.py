# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\CamaDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_CamaDialog(object):
    def setupUi(self, CamaDialog):
        CamaDialog.setObjectName(_fromUtf8("CamaDialog"))
        CamaDialog.resize(415, 726)
        CamaDialog.setMinimumSize(QtCore.QSize(415, 700))
        CamaDialog.setMaximumSize(QtCore.QSize(415, 790))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setGeometry(QtCore.QRect(2, 0, 411, 681))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 600))
        self.scrollArea.setMaximumSize(QtCore.QSize(435, 800))
        self.scrollArea.setMouseTracking(False)
        self.scrollArea.setAcceptDrops(False)
        self.scrollArea.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.scrollArea.setAutoFillBackground(False)
        self.scrollArea.setFrameShape(QtGui.QFrame.StyledPanel)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Sunken)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 409, 739))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.error_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.error_label.setGeometry(QtCore.QRect(20, 715, 361, 17))
        self.error_label.setText(_fromUtf8(""))
        self.error_label.setObjectName(_fromUtf8("error_label"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        CamaDialog.setWidget(self.dockWidgetContents)

        self.retranslateUi(CamaDialog)
        QtCore.QMetaObject.connectSlotsByName(CamaDialog)

    def retranslateUi(self, CamaDialog):
        CamaDialog.setWindowTitle(_translate("CamaDialog", "UB Parcel Information", None))


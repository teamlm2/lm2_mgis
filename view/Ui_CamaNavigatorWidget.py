# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\CamaNavigatorWidget.ui'
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

class Ui_CamaNavigatorWidget(object):
    def setupUi(self, CamaNavigatorWidget):
        CamaNavigatorWidget.setObjectName(_fromUtf8("CamaNavigatorWidget"))
        CamaNavigatorWidget.resize(415, 712)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CamaNavigatorWidget.sizePolicy().hasHeightForWidth())
        CamaNavigatorWidget.setSizePolicy(sizePolicy)
        CamaNavigatorWidget.setMinimumSize(QtCore.QSize(415, 620))
        CamaNavigatorWidget.setMaximumSize(QtCore.QSize(415, 524287))
        CamaNavigatorWidget.setBaseSize(QtCore.QSize(440, 665))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 418, 650))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 600))
        self.scrollArea.setMaximumSize(QtCore.QSize(435, 650))
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 419, 664))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.working_l1_cbox = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.working_l1_cbox.setGeometry(QtCore.QRect(11, 3, 170, 22))
        self.working_l1_cbox.setObjectName(_fromUtf8("working_l1_cbox"))
        self.working_l2_cbox = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.working_l2_cbox.setGeometry(QtCore.QRect(210, 3, 170, 22))
        self.working_l2_cbox.setObjectName(_fromUtf8("working_l2_cbox"))
        self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setGeometry(QtCore.QRect(10, 30, 381, 171))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.parcel_price_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.parcel_price_button.setGeometry(QtCore.QRect(10, 220, 161, 23))
        self.parcel_price_button.setObjectName(_fromUtf8("parcel_price_button"))
        self.distinct_analys_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.distinct_analys_button.setGeometry(QtCore.QRect(10, 250, 161, 23))
        self.distinct_analys_button.setObjectName(_fromUtf8("distinct_analys_button"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        CamaNavigatorWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(CamaNavigatorWidget)
        QtCore.QMetaObject.connectSlotsByName(CamaNavigatorWidget)

    def retranslateUi(self, CamaNavigatorWidget):
        CamaNavigatorWidget.setWindowTitle(_translate("CamaNavigatorWidget", "Selection / Filter", None))
        self.groupBox.setTitle(_translate("CamaNavigatorWidget", "Parcel Information", None))
        self.parcel_price_button.setText(_translate("CamaNavigatorWidget", "Зах зээлийн үнийн мэдээлэл", None))
        self.distinct_analys_button.setText(_translate("CamaNavigatorWidget", "Зайн анализ", None))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\NavigatorMainWidget.ui'
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

class Ui_NavigatorMainWidget(object):
    def setupUi(self, NavigatorMainWidget):
        NavigatorMainWidget.setObjectName(_fromUtf8("NavigatorMainWidget"))
        NavigatorMainWidget.resize(415, 712)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NavigatorMainWidget.sizePolicy().hasHeightForWidth())
        NavigatorMainWidget.setSizePolicy(sizePolicy)
        NavigatorMainWidget.setMinimumSize(QtCore.QSize(415, 620))
        NavigatorMainWidget.setMaximumSize(QtCore.QSize(415, 524287))
        NavigatorMainWidget.setBaseSize(QtCore.QSize(440, 665))
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
        self.error_label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.error_label.setGeometry(QtCore.QRect(20, 576, 374, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Helvetica"))
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.error_label.setFont(font)
        self.error_label.setStyleSheet(_fromUtf8("QLabel {color : red;}\n"
"font: 75 14pt \"Helvetica\";"))
        self.error_label.setText(_fromUtf8(""))
        self.error_label.setWordWrap(True)
        self.error_label.setObjectName(_fromUtf8("error_label"))
        self.cadastre_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.cadastre_button.setGeometry(QtCore.QRect(10, 10, 131, 50))
        self.cadastre_button.setObjectName(_fromUtf8("cadastre_button"))
        self.pasture_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.pasture_button.setGeometry(QtCore.QRect(10, 70, 131, 50))
        self.pasture_button.setObjectName(_fromUtf8("pasture_button"))
        self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_2.setGeometry(QtCore.QRect(70, 290, 192, 321))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setStyleSheet(_fromUtf8("QGroupBox {\n"
"     background-color: #f5f5ef; border: 1px solid black;\n"
"     border-radius: 3px;\n"
"}"))
        self.groupBox_2.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.au_level3_button = QtGui.QPushButton(self.groupBox_2)
        self.au_level3_button.setGeometry(QtCore.QRect(16, 65, 161, 23))
        self.au_level3_button.setObjectName(_fromUtf8("au_level3_button"))
        self.plan_button = QtGui.QPushButton(self.groupBox_2)
        self.plan_button.setGeometry(QtCore.QRect(16, 165, 161, 23))
        self.plan_button.setStyleSheet(_fromUtf8(""))
        self.plan_button.setObjectName(_fromUtf8("plan_button"))
        self.fee_tax_zone_button = QtGui.QPushButton(self.groupBox_2)
        self.fee_tax_zone_button.setGeometry(QtCore.QRect(16, 190, 161, 23))
        self.fee_tax_zone_button.setObjectName(_fromUtf8("fee_tax_zone_button"))
        self.au_level2_button = QtGui.QPushButton(self.groupBox_2)
        self.au_level2_button.setGeometry(QtCore.QRect(16, 40, 161, 23))
        self.au_level2_button.setObjectName(_fromUtf8("au_level2_button"))
        self.mpa_zone_button = QtGui.QPushButton(self.groupBox_2)
        self.mpa_zone_button.setGeometry(QtCore.QRect(16, 115, 161, 23))
        self.mpa_zone_button.setObjectName(_fromUtf8("mpa_zone_button"))
        self.sec_zone_button = QtGui.QPushButton(self.groupBox_2)
        self.sec_zone_button.setGeometry(QtCore.QRect(16, 140, 161, 23))
        self.sec_zone_button.setObjectName(_fromUtf8("sec_zone_button"))
        self.au_level1_button = QtGui.QPushButton(self.groupBox_2)
        self.au_level1_button.setGeometry(QtCore.QRect(16, 15, 161, 23))
        self.au_level1_button.setObjectName(_fromUtf8("au_level1_button"))
        self.free_zone_button = QtGui.QPushButton(self.groupBox_2)
        self.free_zone_button.setGeometry(QtCore.QRect(16, 90, 161, 23))
        self.free_zone_button.setObjectName(_fromUtf8("free_zone_button"))
        self.valuation_zone_button = QtGui.QPushButton(self.groupBox_2)
        self.valuation_zone_button.setGeometry(QtCore.QRect(16, 215, 161, 23))
        self.valuation_zone_button.setObjectName(_fromUtf8("valuation_zone_button"))
        self.test_button_2 = QtGui.QPushButton(self.groupBox_2)
        self.test_button_2.setGeometry(QtCore.QRect(16, 290, 161, 23))
        self.test_button_2.setObjectName(_fromUtf8("test_button_2"))
        self.ub_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.ub_button.setGeometry(QtCore.QRect(150, 10, 131, 50))
        self.ub_button.setObjectName(_fromUtf8("ub_button"))
        self.mpa_button = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.mpa_button.setGeometry(QtCore.QRect(150, 70, 131, 50))
        self.mpa_button.setObjectName(_fromUtf8("mpa_button"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        NavigatorMainWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(NavigatorMainWidget)
        QtCore.QMetaObject.connectSlotsByName(NavigatorMainWidget)

    def retranslateUi(self, NavigatorMainWidget):
        NavigatorMainWidget.setWindowTitle(_translate("NavigatorMainWidget", "Selection / Filter", None))
        self.cadastre_button.setText(_translate("NavigatorMainWidget", "Cadastre", None))
        self.pasture_button.setText(_translate("NavigatorMainWidget", "Pasture", None))
        self.groupBox_2.setTitle(_translate("NavigatorMainWidget", "Давхарга", None))
        self.au_level3_button.setText(_translate("NavigatorMainWidget", "Баг/Хорооны хил", None))
        self.plan_button.setText(_translate("NavigatorMainWidget", "ГЗБТөлөвгөгөө", None))
        self.fee_tax_zone_button.setText(_translate("NavigatorMainWidget", "Төлбөр, Татварын бүс", None))
        self.au_level2_button.setText(_translate("NavigatorMainWidget", "Сум/Дүүргийн хил", None))
        self.mpa_zone_button.setText(_translate("NavigatorMainWidget", "Тусгай хамгаалалтай газар", None))
        self.sec_zone_button.setText(_translate("NavigatorMainWidget", "Хамгаалалтын зурвас", None))
        self.au_level1_button.setText(_translate("NavigatorMainWidget", "Аймаг/Нийслэлийн хил", None))
        self.free_zone_button.setText(_translate("NavigatorMainWidget", "Чөлөөт бүс", None))
        self.valuation_zone_button.setText(_translate("NavigatorMainWidget", "Үнэлгээний бүс", None))
        self.test_button_2.setText(_translate("NavigatorMainWidget", "TEST", None))
        self.ub_button.setText(_translate("NavigatorMainWidget", "UB Parcel Editor", None))
        self.mpa_button.setText(_translate("NavigatorMainWidget", "MPA", None))


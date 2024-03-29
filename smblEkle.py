# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'smblEkle.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(581, 631)
        font = QtGui.QFont()
        font.setPointSize(12)
        Form.setFont(font)
        Form.setWindowOpacity(28.0)
        Form.setStyleSheet("background-color: rgb(242, 237, 221);")
        self.gridLayoutWidget = QtWidgets.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(90, 100, 396, 461))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(4, 4, 4, 4)
        self.gridLayout.setObjectName("gridLayout")
        self.almmktr = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.almmktr.setFont(font)
        self.almmktr.setStyleSheet("color: rgb(41, 86, 170);")
        self.almmktr.setObjectName("almmktr")
        self.gridLayout.addWidget(self.almmktr, 6, 0, 1, 1)
        self.lineEdit_sembol = QtWidgets.QLineEdit(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_sembol.setFont(font)
        self.lineEdit_sembol.setStyleSheet("")
        self.lineEdit_sembol.setMaxLength(5)
        self.lineEdit_sembol.setObjectName("lineEdit_sembol")
        self.gridLayout.addWidget(self.lineEdit_sembol, 0, 2, 1, 1)
        self.lineEdit_bistx = QtWidgets.QLineEdit(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_bistx.setFont(font)
        self.lineEdit_bistx.setStyleSheet("")
        self.lineEdit_bistx.setText("")
        self.lineEdit_bistx.setObjectName("lineEdit_bistx")
        self.gridLayout.addWidget(self.lineEdit_bistx, 3, 2, 1, 1)
        self.textEdit_sembolAciklama = QtWidgets.QTextEdit(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.textEdit_sembolAciklama.setFont(font)
        self.textEdit_sembolAciklama.setStyleSheet("border-color: rgb(32, 16, 255);\n"
"")
        self.textEdit_sembolAciklama.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_sembolAciklama.setObjectName("textEdit_sembolAciklama")
        self.gridLayout.addWidget(self.textEdit_sembolAciklama, 1, 2, 1, 1)
        self.lineEdit_alimFiyati = QtWidgets.QLineEdit(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_alimFiyati.setFont(font)
        self.lineEdit_alimFiyati.setTabletTracking(False)
        self.lineEdit_alimFiyati.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lineEdit_alimFiyati.setStyleSheet("")
        self.lineEdit_alimFiyati.setInputMask("")
        self.lineEdit_alimFiyati.setMaxLength(8)
        self.lineEdit_alimFiyati.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_alimFiyati.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.lineEdit_alimFiyati.setObjectName("lineEdit_alimFiyati")
        self.gridLayout.addWidget(self.lineEdit_alimFiyati, 6, 2, 1, 1)
        self.lineEdit_sektor = QtWidgets.QLineEdit(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_sektor.setFont(font)
        self.lineEdit_sektor.setStyleSheet("border-color: rgb(234, 234, 255);")
        self.lineEdit_sektor.setText("")
        self.lineEdit_sektor.setMaxLength(36)
        self.lineEdit_sektor.setObjectName("lineEdit_sektor")
        self.gridLayout.addWidget(self.lineEdit_sektor, 2, 2, 1, 1)
        self.ltmktr = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ltmktr.setFont(font)
        self.ltmktr.setStyleSheet("color: rgb(41, 86, 170);")
        self.ltmktr.setObjectName("ltmktr")
        self.gridLayout.addWidget(self.ltmktr, 5, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.smbl = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.smbl.setFont(font)
        self.smbl.setStyleSheet("color: rgb(41, 86, 170);")
        self.smbl.setObjectName("smbl")
        self.gridLayout.addWidget(self.smbl, 0, 0, 1, 1)
        self.checkBox_arz = QtWidgets.QCheckBox(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.checkBox_arz.setFont(font)
        self.checkBox_arz.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBox_arz.setStyleSheet("")
        self.checkBox_arz.setObjectName("checkBox_arz")
        self.gridLayout.addWidget(self.checkBox_arz, 4, 2, 1, 1)
        self.trh = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.trh.setFont(font)
        self.trh.setStyleSheet("color: rgb(41, 86, 170);")
        self.trh.setObjectName("trh")
        self.gridLayout.addWidget(self.trh, 7, 0, 1, 1)
        self.sktr = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.sktr.setFont(font)
        self.sktr.setStyleSheet("color: rgb(41, 86, 170);")
        self.sktr.setObjectName("sktr")
        self.gridLayout.addWidget(self.sktr, 2, 0, 1, 1)
        self.bstx = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.bstx.setFont(font)
        self.bstx.setStyleSheet("color: rgb(41, 86, 170);")
        self.bstx.setObjectName("bstx")
        self.gridLayout.addWidget(self.bstx, 3, 0, 1, 1)
        self.lineEdit_alinanLot = QtWidgets.QLineEdit(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_alinanLot.setFont(font)
        self.lineEdit_alinanLot.setTabletTracking(False)
        self.lineEdit_alinanLot.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.lineEdit_alinanLot.setStyleSheet("")
        self.lineEdit_alinanLot.setText("")
        self.lineEdit_alinanLot.setMaxLength(6)
        self.lineEdit_alinanLot.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.lineEdit_alinanLot.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_alinanLot.setObjectName("lineEdit_alinanLot")
        self.gridLayout.addWidget(self.lineEdit_alinanLot, 5, 2, 1, 1)
        self.smblacklm = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.smblacklm.setFont(font)
        self.smblacklm.setStyleSheet("color: rgb(41, 86, 170);")
        self.smblacklm.setObjectName("smblacklm")
        self.gridLayout.addWidget(self.smblacklm, 1, 0, 1, 1)
        self.arzmi = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.arzmi.setFont(font)
        self.arzmi.setStyleSheet("color: rgb(41, 86, 170);\n"
"")
        self.arzmi.setObjectName("arzmi")
        self.gridLayout.addWidget(self.arzmi, 4, 0, 1, 1)
        self.dateEdit_tarih = QtWidgets.QDateEdit(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.dateEdit_tarih.setFont(font)
        self.dateEdit_tarih.setAlignment(QtCore.Qt.AlignCenter)
        self.dateEdit_tarih.setTime(QtCore.QTime(0, 0, 0))
        self.dateEdit_tarih.setMaximumDate(QtCore.QDate(2032, 12, 31))
        self.dateEdit_tarih.setMinimumDate(QtCore.QDate(2022, 10, 14))
        self.dateEdit_tarih.setCalendarPopup(True)
        self.dateEdit_tarih.setDate(QtCore.QDate(2023, 4, 4))
        self.dateEdit_tarih.setObjectName("dateEdit_tarih")
        self.gridLayout.addWidget(self.dateEdit_tarih, 7, 2, 1, 1)
        self.pushButton_ekle = QtWidgets.QPushButton(Form)
        self.pushButton_ekle.setGeometry(QtCore.QRect(160, 20, 251, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_ekle.setFont(font)
        self.pushButton_ekle.setStyleSheet("background-color: rgb(238, 212, 189);")
        self.pushButton_ekle.setObjectName("pushButton_ekle")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Arz Girişi"))
        self.almmktr.setText(_translate("Form", "Alım Fyatı :"))
        self.lineEdit_bistx.setPlaceholderText(_translate("Form", "mi ?"))
        self.textEdit_sembolAciklama.setPlaceholderText(_translate("Form", "Sembol Açıklama"))
        self.lineEdit_sektor.setPlaceholderText(_translate("Form", "Hassektör ?"))
        self.ltmktr.setText(_translate("Form", "Alınan Lot :"))
        self.smbl.setText(_translate("Form", "Sembol:"))
        self.checkBox_arz.setText(_translate("Form", "Evet"))
        self.trh.setText(_translate("Form", "Tarih"))
        self.sktr.setText(_translate("Form", "Sektör :"))
        self.bstx.setText(_translate("Form", "Bist X :"))
        self.lineEdit_alinanLot.setInputMask(_translate("Form", "999999"))
        self.smblacklm.setText(_translate("Form", "Sembol Açıklama:"))
        self.arzmi.setText(_translate("Form", "Halka Arz mı ?"))
        self.pushButton_ekle.setText(_translate("Form", "Ekle"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

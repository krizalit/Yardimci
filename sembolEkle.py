
import sys
import mysql.connector

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QBrush, QColor
from smblEkle import *
#from vt import *



Uygulama=QApplication(sys.argv)
eklePencere = QMainWindow()
ekleArayuz = Ui_Form()
ekleArayuz.setupUi(eklePencere)

baglanti = mysql.connector.connect(
  host="localhost",
  user="firat",
  password="eben",
  database="yatirim"
)
vtimlec = baglanti.cursor()


def ekleme():

  sembol = ekleArayuz.lineEdit_sembol.text()
  sembolAciklama = ekleArayuz.textEdit_sembolAciklama.toPlainText()
  sektor = ekleArayuz.lineEdit_sektor.text()
  bistx = ekleArayuz.lineEdit_bistx.text()
  if ekleArayuz.checkBox_arz.isChecked():
    arzMi = "E"
  else:
    arzMi = "H"
  alimLot = float(ekleArayuz.lineEdit_alinanLot.text())
  alimFiyati = float(ekleArayuz.lineEdit_alimFiyati.text())
  tarih = ekleArayuz.dateEdit_tarih.date().toPyDate()
  hacim = alimLot * alimFiyati
  vtimlec.execute(f"INSERT INTO `semboller`(`sembol`, `sembolaciklama`, `sektor`, `bistx`, `arz`) VALUES ('{sembol}','{sembolAciklama}','{sektor}','{bistx}','{arzMi}')")
  vtimlec.execute(f"INSERT INTO `emirlerim`(`sembol`, `alsat`, `fiyat`, `gerceklesen`, `hacim`,  `gun`) VALUES ('{sembol}','A','{alimFiyati}','{alimLot}','{hacim}','{tarih}')")




  print(sembol, sembolAciklama, sektor, bistx, arzMi, alimLot, alimFiyati, tarih, hacim)



ekleArayuz.pushButton_ekle.clicked.connect(ekleme)

eklePencere.show()
sys.exit(Uygulama.exec_())

""""
INSERT INTO `emirlerim`(`sembol`, `alsat`, `fiyat`, `gerceklesen`, `hacim`,  `gun`) VALUES ('','','','','','')
SELECT * FROM `semboller` WHERE `sembol` = 'KOPOL'
DELETE FROM semboller WHERE `semboller`.`sembol_id` = 176" 
INSERT INTO `semboller`(`sembol`, `sembolaciklama`, `sektor`, `bistx`, `arz`) VALUES ('[value-1]','[value-2]','[value-3]','[value-4]','[value-5]')


"""
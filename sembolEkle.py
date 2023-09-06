
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
  alimLot = int(ekleArayuz.lineEdit_alinanLot.text())
  alimFiyati = float(ekleArayuz.lineEdit_alimFiyati.text().replace(",", "."))

  if not all((sembol, sembolAciklama, alimLot, alimFiyati)):
    print("Lütfen tüm girdi alanlarını doldurun.")
  else:
    sektor = ekleArayuz.lineEdit_sektor.text()
    bistx = ekleArayuz.lineEdit_bistx.text()
    if ekleArayuz.checkBox_arz.isChecked():
      arzMi = "E"
    else:
      arzMi = "H"
    tarih = ekleArayuz.dateEdit_tarih.date().toPyDate()

    hacim = alimLot * alimFiyati
    vtimlec.execute(f"SELECT * FROM `semboller` WHERE `sembol` = '{sembol}'")
    varmiSorgusu = vtimlec.fetchall()
    varMi = len(varmiSorgusu)
    if varMi == 0:
      print("yok")
      vtimlec.execute(f"INSERT INTO `semboller`(`sembol`, `sembolaciklama`, `sektor`, `bistx`, `arz`) VALUES ('{sembol}','{sembolAciklama}','{sektor}','{bistx}','{arzMi}')")
      vtimlec.execute(f"INSERT INTO `emirlerim`(`sembol`, `alsat`, `fiyat`, `gerceklesen`, `hacim`,  `gun`) VALUES ('{sembol}','A','{alimFiyati}','{alimLot}','{hacim}','{tarih}')")
      baglanti.commit()

    else:
      vtimlec.execute(f"INSERT INTO `emirlerim`(`sembol`, `alsat`, `fiyat`, `gerceklesen`, `hacim`,  `gun`) VALUES ('{sembol}','A','{alimFiyati}','{alimLot}','{hacim}','{tarih}')")
      baglanti.commit()
      print("var")

    print(sembol, sembolAciklama, sektor, bistx, arzMi, alimLot, alimFiyati, tarih, hacim)





ekleArayuz.pushButton_ekle.clicked.connect(ekleme)

eklePencere.show()
sys.exit(Uygulama.exec_())

#--------------------------Kütüphane----------------------#
#---------------------------------------------------------#
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from kzmodul import *

Uygulama = QApplication(sys.argv)
kzmodulAnaPencere = QMainWindow()
kzarayuz = Ui_Form()
kzarayuz.setupUi(kzmodulAnaPencere)


#----------------------Veritabanı-------------------------#
import mysql.connector

baglanti = mysql.connector.connect(
  host="localhost",
  user="firat",
  password="eben",
  database="yatirim"
)
vtimlec = baglanti.cursor()

#sembol = 'ASELS'
alimlariCek = "SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = 'ASELS' AND `alsat` = 'A'"
satimlariCek = "SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = 'ASELS' AND `alsat` = 'S'"

#----------------------Tanımlamalar-------------------------#
#sembol = "ASELS"
toplamAdet = 0

def listele_alim():

  alimAdet = 0
  alimHacim = 0
  vtimlec.execute(alimlariCek)
  alimlar = vtimlec.fetchall()
  alimlarSatirSayisi = vtimlec.rowcount
  print(alimlarSatirSayisi)
  for  a, b, c, d in alimlar:
    alimAdet += b
    alimHacim += d

  kzarayuz.tableWidget_alim.clear()
  kzarayuz.tableWidget_alim.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Eder'])
  kzarayuz.tableWidget_alim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  kzarayuz.tableWidget_alim.setRowCount(alimlarSatirSayisi)

  for satirIndeks, satirVeri in enumerate(alimlar):
    for sutunIndeks, sutunVeri in enumerate(satirVeri):

      hucre = QTableWidgetItem(str(sutunVeri))
      if isinstance(sutunVeri, float):
        hucre.setData(Qt.EditRole, '{:,.2f}'.format(sutunVeri))

      if sutunIndeks > 0:
        hucre.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

      kzarayuz.tableWidget_alim.setItem(satirIndeks,sutunIndeks,hucre)

  print("Toplam Alınan Adet:"+ str(alimAdet))
  alimOrtalamasi = alimHacim / alimAdet
  alimOrtalamasiSade = "{:.2f}".format(alimOrtalamasi)
  print("Alım Ortalaması:"+ str(alimOrtalamasiSade))
  kzarayuz.label_alimOrtalama.clear()
  kzarayuz.label_alimOrtalama.setText(str(alimOrtalamasiSade))
  global toplamAdet
  toplamAdet += alimAdet


def listele_satim():
  satimAdet = 0
  satimHacim = 0

  vtimlec.execute(satimlariCek)
  satimlar = vtimlec.fetchall()
  satimlarSatirSayisi = vtimlec.rowcount
  for  a, b, c, d in satimlar:
    satimAdet += a
    satimHacim += c
  print(satimlarSatirSayisi)
  kzarayuz.tableWidget_satim.clear()
  kzarayuz.tableWidget_satim.setHorizontalHeaderLabels(('Adet', 'Fiyat', 'Eder', 'Tarih'))
  kzarayuz.tableWidget_satim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  kzarayuz.tableWidget_satim.setRowCount(satimlarSatirSayisi)
  for satirIndeks, satirVeri in enumerate(satimlar):
    for sutunIndeks, sutunVeri in enumerate(satirVeri):
      print(satirVeri[2])
      kzarayuz.tableWidget_satim.setItem(satirIndeks,sutunIndeks,QTableWidgetItem(str(sutunVeri)))
  print("Toplam Satılan Adet:" + str(satimAdet))
  satimOrtalamasi = satimHacim / satimAdet
  satimOrtalamasiSade = "{:.2f}".format(satimOrtalamasi)
  print("Satım Ortalaması:" + str(satimOrtalamasiSade))
  kzarayuz.label_satimOrtalama.clear()
  kzarayuz.label_satimOrtalama.setText(str(satimOrtalamasiSade))
  global toplamAdet
  toplamAdet -= satimAdet

def adetYerlestir():
  global toplamAdet
  kzarayuz.label_toplamAdet.setText(str(toplamAdet))

#------------------------Uygulama Oluştur-----------------#
#---------------------------------------------------------#



kzmodulAnaPencere.show()
listele_alim()
listele_satim()
adetYerlestir()
print(toplamAdet)

#print(sembol)
sys.exit(Uygulama.exec_())

#--------------------------Kütüphane----------------------#
#---------------------------------------------------------#
import sys
from PyQt5 import QtWidgets
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
alimlaricek = "SELECT * FROM `emirlerim` WHERE `sembol` = 'DOHOL' AND `alsat` = 'A'"
satimlaricek = "SELECT * FROM `emirlerim` WHERE `sembol` = 'ASELS' AND `alsat` = 'S'"
#vtimlec.execute(satimlaricek)
#satimlar = vtimlec.fetchall()

#----------------------Tanımlamalar-------------------------#
#sembol = "ASELS"


def listele_alim():
  kzarayuz.tableWidget_alim.clear()
  kzarayuz.tableWidget_alim.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Eder'])
  kzarayuz.tableWidget_alim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  #alimlaricek = "SELECT * FROM `emirlerim` WHERE `sembol` = 'ASELS' AND `alsat` = 'A'"
  vtimlec.execute(alimlaricek)
  alimlar = vtimlec.fetchall()
  for alimdongu in alimlar:
    tarih = alimdongu[7].strftime("%d")+" "+alimdongu[7].strftime("%m")+" "+alimdongu[7].strftime("%Y")
    alimHacim = float(alimdongu[5])*1.002
    print(alimdongu[7], alimdongu[4], alimdongu[3]), alimHacim
    #print(alimdongu[1])
    print(tarih)

    #kzarayuz.tableWidget_alim.setItem(tarih, alimdongu[4], alimdongu[3], alimdongu[5], QTableWidgetItem )
  #for satirIndeks, satirVeri in enumerate(vtimlec):
    #for sutunIndeks, sutunVeri in enumerate(satirVeri):
      #print(sutunVeri)
      #print(satirVeri)
      #kzarayuz.tableWidget_alim.setItem(satirIndeks,sutunIndeks,QTableWidgetItem(str(value)))
#listele_alim()
print(alimlaricek)
print(satimlaricek)
def listele_satim():
  kzarayuz.tableWidget_satim.clear()
  kzarayuz.tableWidget_satim.setHorizontalHeaderLabels(('Adet','Fiyat','Eder','Tarih'))
  kzarayuz.tableWidget_satim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

#------------------------Uygulama Oluştur-----------------#
#---------------------------------------------------------#



kzmodulAnaPencere.show()
listele_alim()
listele_satim()
#print(sembol)
sys.exit(Uygulama.exec_())

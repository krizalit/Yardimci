#--------------------------Kütüphane----------------------#
#---------------------------------------------------------#
import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QBrush, QColor
from kzmodul2 import *

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

sembol = ""

#alimlariCek = f"SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'A'"
#satimlariCek = f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'S'"
sembolleriCek = "SELECT `sembol` FROM `semboller` ORDER BY `semboller`.`sembol` ASC "
#----------------------Tanımlamalar-------------------------#

toplamAdet = 0
toplamAlimAdet = 0
toplamSatimAdet = 0


def sembolleriYerlestir():
  vtimlec.execute(sembolleriCek)
  sembolGelenler = vtimlec.fetchall()

  # QListWidget nesnesine sembolleri ekle
  kzarayuz.listWidget_semboller.clear()
  for smbl in sembolGelenler:
    kzarayuz.listWidget_semboller.addItem(smbl[0])

  # QListWidget nesnesindeki herhangi bir öğe tıklandığında seciliSembolDegistir fonksiyonunu çağır
  kzarayuz.listWidget_semboller.itemClicked.connect(seciliSembolDegistir)
  global sembol
  kzarayuz.lineEdit_sembol.setText(str(sembol))

def seciliSembolDegistir(item):
  global toplamAdet
  toplamAdet = 0

  global sembol
  sembol = item.text()
  kzarayuz.lineEdit_sembol.setText(sembol)
  alimVerisiIsleme()
  satimVerisiIsleme()
  adetYerlestir()



def sembolGonder():
  kzarayuz.pushButton_sembolGonder.clicked()

def alimVerisiIsleme():
  alimAdet = 0
  alimHacim = 0

  # MySQL sorgusunu çalıştır
  vtimlec.execute(f"SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'A'")
  islemIcinGelenAlimlar = vtimlec.fetchall()
  if len(islemIcinGelenAlimlar) == 0:

    kzarayuz.tableWidget_alim.clear()
    kzarayuz.tableWidget_alim.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Eder'])
    kzarayuz.tableWidget_alim.setRowCount(0)
    kzarayuz.label_alimAdet.setText("0")
    kzarayuz.label_satimAdet.setText("0")
    kzarayuz.label_alimOrtalama.setText("0")
    kzarayuz.label_satimOrtalama.setText("0")
  else:

    # Verileri işleme
    alimVerisiDizeye = []
    for satir in islemIcinGelenAlimlar:

      # Toplam alım ve hacimi hesaplama - Dizeye ekleme esnasında yan işlem
      alimAdet += satir[1]
      hacim = satir[3] / 1000 * 1002
      alimHacim += hacim

      # Tarih verisini dd mm yyyy formatına çevir
      tarih = satir[0].strftime("%d %m %Y")
      # adet verisi tanımıyla gerceklenenleri adete çevir
      adet = satir[1]

      # Fiyat verisini binlik ayraçlı sayı formatına çevir ve virgülden sonra 2 basamak göster
      fiyat = '{:,.2f}'.format(satir[2]).replace(",", "X").replace(".", ",").replace("X", ".")

      # Eder verisini binlik ayraçlı sayı formatına çevir ve virgülden sonra 2 basamak göster
      eder = '{:,.2f}'.format(hacim).replace(",", "X").replace(".", ",").replace("X", ".")

      # Düzenlenmiş veriyi listeye ekle
      alimVerisiDizeye.append([tarih, adet, fiyat, eder])

    # QTableWidget nesnesine veriyi yerleştir
    kzarayuz.tableWidget_alim.clear()
    kzarayuz.tableWidget_alim.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Eder'])
    kzarayuz.tableWidget_alim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    kzarayuz.tableWidget_alim.setRowCount(len(islemIcinGelenAlimlar))
    for satirIndeks, satirVeri in enumerate(alimVerisiDizeye):
      for sutunIndeks, sutunVeri in enumerate(satirVeri):
        hucre = QTableWidgetItem(str(sutunVeri))
        if sutunIndeks == 1:

          #Ortala
          hucre.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:

          # Sağa yasla
          hucre.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if sutunIndeks == 0:
          hucre.setBackground(QBrush(QColor(242, 237, 221)))
        # Hücreyi tabloya yerleştir
        kzarayuz.tableWidget_alim.setItem(satirIndeks, sutunIndeks, hucre)

    #Saydadaki diğer işlemlerde kullanılacak değişken değerlerinin oluşması ve yerleşmesi
    print("Toplam Alınan Adet:" + str(alimAdet))
    alimOrtalamasi = alimHacim / alimAdet
    alimOrtalamasiSade = "{:.2f}".format(alimOrtalamasi)
    print("Alım Ortalaması:" + str(alimOrtalamasiSade))
    kzarayuz.label_alimOrtalama.clear()
    kzarayuz.label_alimOrtalama.setText(str(alimOrtalamasiSade))
    global toplamAdet
    toplamAdet += alimAdet
    global toplamAlimAdet
    toplamAlimAdet += alimAdet
    kzarayuz.label_alimAdet.setText(str(alimAdet))


def satimVerisiIsleme():
  satimAdet = 0
  satimHacim = 0

  # MySQL sorgusunu çalıştır
  vtimlec.execute(f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'S'")
  islemIcinGelenSatimlar = vtimlec.fetchall()
  if len(islemIcinGelenSatimlar) == 0:
    kzarayuz.tableWidget_satim.clear()
    kzarayuz.tableWidget_satim.setHorizontalHeaderLabels(['Adet', 'Fiyat', 'Eder', 'Tarih'])
    kzarayuz.tableWidget_satim.setRowCount(0)
  else:

    # Verileri işleme
    satimVerisiDizeye = []
    for satir in islemIcinGelenSatimlar:
      # Toplam alım ve hacimi hesaplama - Dizeye ekleme esnasında yan işlem
      satimAdet += satir[0]
      hacim = satir[2] / 1000 * 998
      satimHacim += hacim

      # Tarih verisini dd mm yyyy formatına çevir
      tarih = satir[3].strftime("%d %m %Y")
      # adet verisi tanımıyla gerceklenenleri adete çevir
      adet = satir[0]

      # Fiyat verisini binlik ayraçlı sayı formatına çevir ve virgülden sonra 2 basamak göster
      fiyat = '{:,.2f}'.format(satir[1]).replace(",", "X").replace(".", ",").replace("X", ".")

      # Eder verisini binlik ayraçlı sayı formatına çevir ve virgülden sonra 2 basamak göster
      eder = '{:,.2f}'.format(hacim).replace(",", "X").replace(".", ",").replace("X", ".")

      # Düzenlenmiş veriyi listeye ekle
      satimVerisiDizeye.append([adet, fiyat, eder, tarih])

    # QTableWidget nesnesine veriyi yerleştir
    kzarayuz.tableWidget_satim.clear()
    kzarayuz.tableWidget_satim.setHorizontalHeaderLabels([ 'Adet', 'Fiyat', 'Eder', 'Tarih'])
    kzarayuz.tableWidget_satim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    kzarayuz.tableWidget_satim.setRowCount(len(islemIcinGelenSatimlar))
    for satirIndeks, satirVeri in enumerate(satimVerisiDizeye):
      for sutunIndeks, sutunVeri in enumerate(satirVeri):
        hucre = QTableWidgetItem(str(sutunVeri))
        if sutunIndeks == 0:
          # Ortala
          hucre.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        else:
          # Sağa yasla
          hucre.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if sutunIndeks == 3:
          hucre.setBackground(QBrush(QColor(242, 237, 221)))
        # Hücreyi tabloya yerleştir
        kzarayuz.tableWidget_satim.setItem(satirIndeks, sutunIndeks, hucre)

    # SayFadaki diğer işlemlerde kullanılacak değişken değerlerinin oluşması ve yerleşmesi
    print("Toplam Satılan Adet:" + str(satimAdet))
    satimOrtalamasi = satimHacim / satimAdet
    satimOrtalamasiSade = "{:.2f}".format(satimOrtalamasi)
    print("Satım Ortalaması:" + str(satimOrtalamasiSade))
    kzarayuz.label_satimOrtalama.clear()
    kzarayuz.label_satimOrtalama.setText(str(satimOrtalamasiSade))
    global toplamAdet
    toplamAdet -= satimAdet
    global toplamSatimAdet
    toplamSatimAdet += satimAdet
    kzarayuz.label_satimAdet.setText(str(satimAdet))

def alimAdediYerlestir():
  kzarayuz.label_alimAdet.setText(str(toplamAlimAdet))
  kzarayuz.label_satimAdet.setText(str(toplamSatimAdet))



def adetYerlestir():
  global toplamAdet
  kzarayuz.label_toplamAdet.setText(str(toplamAdet))

#------------------------Uygulama Oluştur-----------------#
#---------------------------------------------------------#



kzmodulAnaPencere.show()

#alimVerisiIsleme()
#satimVerisiIsleme()
sembolleriYerlestir()

#adetYerlestir()
#alimAdediYerlestir()
print(toplamAdet)
#print(satimlariCek)
sys.exit(Uygulama.exec_())

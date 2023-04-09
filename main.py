#--------------------------Kütüphane----------------------#
#---------------------------------------------------------#

import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QBrush, QColor
from kzmodul2 import *
from decimal import Decimal
import xlrd
import decimal

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

#----------------------Global Değişken Tanımlamaları-------------------------#

sembol = "SELAM"
toplamAdet = 0

toplamAlimAdet = 0
alimOrtalamasi = 0.00
toplamAlimHacim = 0.00

toplamSatimAdet = 0
satimOrtalamasi = 0.00
toplamSatimHacim = 0.00

gunsonuFiyat = {}
#pozFytBilgileri = [["", 0.00]]
sembolFiyat = 0.00
sembolVarlik = 0.00
gerceklenen = 0.00
cikis = 0.00
karZararYuzdesi = 0

#-----------Veritabanından çekimlerin tanımlamaları--------------------#

#alimlariCek = f"SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'A'"
#satimlariCek = f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'S'"
sembolleriCek = "SELECT `sembol` FROM `semboller` ORDER BY `semboller`.`sembol` ASC "



"""
hebe = 3586.86
hube = 72
zzz = hebe / hube
zzz2 = hebe / 1000 * 998
print("z2 : ", zzz2)
yyy = decimal.Decimal(zzz2)
xxx = yyy.quantize(Decimal('0.01'))
print("decimal olmuş hali :", yyy)
print("z2", zzz2)
print("quantize olmuş hali :", xxx)
"""

def acilisEkranTemizle():
  kzarayuz.label_cikis.setText("Sembol Seçin")




"""
def pozisyonlariOku():
  global pozFytBilgileri
  pozFytBilgileri = ""
  workbook = xlrd.open_workbook("../../Pozisyonlarım.xlsx")
  worksheet = workbook.sheet_by_index(0)


  strSayisi =(worksheet.nrows)
  #print("pozisyonlarım sembol sayısı", strSayisi)
  #print(worksheet.cell_value(18, 0), worksheet.cell_value(18, 3))

  gunlukFiyatDizesi = []
  for i in range(1, strSayisi):
    smbl = worksheet.cell_value(i, 0)
    fyt = worksheet.cell_value(i, 3)
    gunlukFiyatDizesi.append([smbl, fyt])
    #print("Sembol ", smbl, "Fiyat :", fyt)
  pozFytBilgileri = gunlukFiyatDizesi
"""

"""
def pozisyonFiyatBilgisiAl():
  global sembol
  global pozFytBilgileri
  global sembolFiyat

  for dongusel in pozFytBilgileri:
    smbl = dongusel[0]
    fyt = dongusel[1]
    if smbl == sembol:
      sembolFiyat = fyt
      print (smbl, fyt)
      break
    else:
      sembolFiyat = 0

  #print (str(sembolFiyat))
"""

def sembolleriYerlestir():
  vtimlec.execute(sembolleriCek)
  sembolGelenler = vtimlec.fetchall()

  # QListWidget nesnesine sembolleri ekle
  kzarayuz.listWidget_semboller.clear()
  for smbl in sembolGelenler:
    kzarayuz.listWidget_semboller.addItem(smbl[0])

  # QListWidget nesnesindeki herhangi bir öğe tıklandığında seciliSembolIslemleri fonksiyonunu çağır
  kzarayuz.listWidget_semboller.itemClicked.connect(seciliSembolIslemleri)
  global sembol
  kzarayuz.lineEdit_sembol.setText(str(sembol))

def seciliSembolIslemleri(item):
  global toplamAdet
  toplamAdet = 0

  global sembol
  sembol = item.text()
  kzarayuz.lineEdit_sembol.setText(sembol)

  alimVerisiIsleme()
  satimVerisiIsleme()
  adetYerlestir()
  sembolunFiyatiniOgren(sembol)

  global sembolVarlik
  sembolVarlik = toplamAdet * sembolFiyat
  print("toplam adetle sembol fiyatı çarptık bu çıktı", sembolVarlik)
  kzarayuz.lineEdit_guncelFiyat.setText(str(sembolFiyat))
  smblvrlk = "₺"+"{:,.2f}".format(sembolVarlik)
  kzarayuz.label_sembolVarlik.setText(smblvrlk)
  hesapKitap()
  sembolunFiyatiniOgren(sembol)

def hesapKitap():
  global toplamAdet, toplamAlimAdet, toplamSatimAdet, toplamAlimHacim, toplamSatimHacim, sembolFiyat, sembolVarlik, cikis, karZararYuzdesi, gerceklenen
  global alimOrtalamasi, satimOrtalamasi
  if toplamAlimAdet == 0:
    kzarayuz.label_cikis.setText("0")
    kzarayuz.label_sembolVarlik.setText("0")
  else:
    if toplamSatimAdet == 0:
      gerceklenen = 0
    else:
      print("Toplam Alım Adet", toplamAlimAdet, "Toplam Satım Adet", toplamSatimAdet)
      satilanmiktar = toplamAlimAdet - toplamSatimAdet
      satimAlimFarki = satimOrtalamasi - alimOrtalamasi
      print("Satılan Miktar:", satilanmiktar, "Satım Alım Farkı :", satimAlimFarki)
      grckln = satilanmiktar * satimAlimFarki
      print("gerçeklenen sadeleşmemiş", grckln)
      gerceklenen = "{:.2f}".format(satilanmiktar * satimAlimFarki)
      print("Gerçeklenen: ", gerceklenen)
      print("Sembol Varlık: ", sembolVarlik)
      print("Toplam Satım Hacim :", toplamSatimHacim)
      print("Toplam Alım Hacim: ", toplamAlimHacim)
      print("Toplam alım Adet :", toplamAlimAdet)

      smblvrlk = Decimal(sembolVarlik)
      tsh = Decimal(toplamSatimHacim)
      tah = Decimal(toplamAlimHacim)

      cikis1 = float(smblvrlk + tsh - tah )
      cikis2 = round(cikis1, 2)
      cikis = "{:,.2f}".format(cikis1)
      kzarayuz.label_cikis.setText(str(cikis))
      kzarayuz.label_gerceklenen.setText(str(gerceklenen))

      print(" hadi bakalım", cikis1)
      print("Cıkış :", cikis)
      carpionbin = cikis2 * 1000
      print("Caroı on bin :", carpionbin)

def sembolGonder():
  kzarayuz.pushButton_sembolGonder.clicked()

def alimVerisiIsleme():
  alimAdet = 0
  alimHacim = 0
  global toplamAlimHacim
  toplamAlimHacim = 0

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
    kzarayuz.label_cikis.setText("0")
    kzarayuz.label_karzarar.setText("0")
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

    almOrtlm = alimHacim / alimAdet
    print("Alım ortalaması sadeleşmeden önce", almOrtlm)
    alimOrtalamasiSade = "{:.2f}".format(almOrtlm)
    print("Alım Ortalaması sadeleştikten sonra:" + str(alimOrtalamasiSade))
    kzarayuz.label_alimOrtalama.clear()
    kzarayuz.label_alimOrtalama.setText(str(alimOrtalamasiSade))
    global toplamAdet, toplamAlimAdet, alimOrtalamasi
    toplamAdet += alimAdet

    toplamAlimAdet += alimAdet
    toplamAlimHacim += alimHacim
    alimOrtalamasi = almOrtlm
    #print("Toplam Alım hacim :", toplamAlimHacim)
    kzarayuz.label_alimAdet.setText(str(alimAdet))


def satimVerisiIsleme():
  satimAdet = 0
  satimHacim = 0
  global toplamSatimHacim
  toplamSatimHacim = 0

  # MySQL sorgusunu çalıştır
  vtimlec.execute(f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'S'")
  islemIcinGelenSatimlar = vtimlec.fetchall()
  if len(islemIcinGelenSatimlar) == 0:
    kzarayuz.tableWidget_satim.clear()
    kzarayuz.tableWidget_satim.setHorizontalHeaderLabels(['Adet', 'Fiyat', 'Eder', 'Tarih'])
    kzarayuz.tableWidget_satim.setRowCount(0)
    kzarayuz.label_satimAdet.setText("0")
    kzarayuz.label_gerceklenen.setText("Satım Yok")

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
    #print("Toplam Satılan Adet:" + str(satimAdet))
    stmOrtlm = satimHacim / satimAdet
    print("Stm ortalam sadeleşmeden önce", stmOrtlm)
    satimOrtalamasiSade = "{:.2f}".format(stmOrtlm)
    print("Satım Ortalaması sadeleşmiş:" + str(satimOrtalamasiSade))
    kzarayuz.label_satimOrtalama.clear()
    kzarayuz.label_satimOrtalama.setText(str(satimOrtalamasiSade))
    global toplamAdet, toplamSatimAdet, satimOrtalamasi
    toplamAdet -= satimAdet

    toplamSatimAdet += satimAdet
    toplamSatimHacim += satimHacim
    satimOrtalamasi = stmOrtlm
    #print("Toplam SAtım Hacim :", toplamSatimHacim)
    kzarayuz.label_satimAdet.setText(str(satimAdet))

def alimAdediYerlestir():
  kzarayuz.label_alimAdet.setText(str(toplamAlimAdet))
  kzarayuz.label_satimAdet.setText(str(toplamSatimAdet))



def adetYerlestir():
  global toplamAdet
  kzarayuz.label_toplamAdet.setText(str(toplamAdet))

#------------------------Uygulama Oluştur-----------------#
#---------------------------------------------------------#

#-------------------Fiyat oluşturma ve öğrenme bölümü------------------------#

def gunsonuFiyatlariOlustur():
  # ----- progam açılışında yereldeki dosyadan bir önceki gün fiyat bilgilerini alır, dict e ekler------#
  # ----- program boyunca kullanılacak fiyat bilgileri bu dictten okunur -------------------------------#

  workbook = xlrd.open_workbook("../../Pozisyonlarım.xlsx")
  worksheet = workbook.sheet_by_index(0)
  strSayisi =(worksheet.nrows)

  for i in range(1, strSayisi):
    smbl = worksheet.cell_value(i, 0)
    fyt = worksheet.cell_value(i, 3)
    gunsonuFiyat[smbl] = fyt    # satırın ilk elemanını anahtar, ikinci elemanını değer olarak sözlüğe ekliyoruz

  return gunsonuFiyat

def sembolunFiyatiniOgren(sembol):
  # her sembol için gunsonuFiyat dict inden fiyat bilgisini alan fonksiyon
  global sembolFiyat
  dictebak = gunsonuFiyat.get(sembol)
  if dictebak == None:
    sembolFiyat = 0
  else:
    sembolFiyat = dictebak
  #return sembolFiyat

#----------------------------------------------------------------------------#




#-------------------Program başlangıcında çalışacak fonksiyonlar-------------#

kzmodulAnaPencere.show()
# En baş en baş, ahanda gördüğün pencere bununla oluşuyor.

gunsonuFiyatlariOlustur()
# Her sembolün bir önceki gün hangi fiyattan kapandığının bilgisini oluşturmaya yarıyor

sembolleriYerlestir()
# Hani solda aşağı doğru akan liste var ya sembollerin olduğu, ahanda onu oluşturuyor.



#pozisyonlariOku()
#fiyatDizesiniYazdir()
#adetYerlestir()
#alimAdediYerlestir()
#print(toplamAdet)
#print(satimlariCek)
sys.exit(Uygulama.exec_())

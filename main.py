#--------------------------Kütüphane----------------------#

import sys
#from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QBrush, QColor
from kzModul import *
from decimal import Decimal
import xlrd
#import decimal

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
# sembole selam dedim çümkü program açıldığında daha herhangibir sembol seçilmediğinde
# yukarıda ortadaki yerde bir şey yazması gerekiyor. Boş kalmasın bari selam desin.
# zaten ilk sembol seçildiğinde bu değişkenin değeri değişecek.

toplamAdet = 0
# o sembolden elinde kaç adet olduğu, toplam alim adedinden toplam satım adedi düşülerek oluşan veri

toplamAlimAdet = 0
alimOrtalamasi = 0.00
toplamAlimHacim = 0.00
# alım işlemlerinde kaç adet alındığı, bunların yekünü (hacim) ve alım ortalaması değerleri

toplamSatimAdet = 0
satimOrtalamasi = 0.00
toplamSatimHacim = 0.00
# satım işlemlerinde kaç adet alındığı, bunların yekünü (hacim) ve alım ortalaması değerleri

gunsonuFiyat = {}
# sembolüerin bir önceki gün kaçtan kapandığı bilgisi. bunu indirlimiş excel dosyasından alıyor.
# bu bir dict verisi, içinde her sembol için fiyat bilgisi tutuyor.

sembolFiyat = 0.00
# sembole özel gün sonu kapanış fiyatı bilgisi. tek sembol için ve her sembol seçildiğinde değişiyor. adı üstünde değişken

sembolVarlik = 0.00
# sembolün varolan adedi ve fiyatının çarpımı ile oluşturulan değer. Vakıfbank değer diyor buna ben varlık diyorum.

gerceklenen = 0.00
# realizasyon dediğiniz olay, yapılmış satış işlem adedi x ( satım fiyatı -  sembol fiyat ) şeklinde hesaplanıyor.

cikis = 0.00
# Komple pozisyondan o anki fiyattan çıktığındaki durumunu gösterir. Tabi önceki yaptığın alım satımları dikkate alarak.

karZararYuzdesi = 0
# İşte bu çıkışta kar zarar durumunu yüzde olarak gösterir.

tarihAraligiBilgi = QMessageBox()

#-----------Veritabanından çekimlerin tanımlamaları--------------------#

#alimlariCek = f"SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'A'"
#satimlariCek = f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'S'"
sembolleriCek = "SELECT `sembol` FROM `semboller` ORDER BY `semboller`.`sembol` ASC "

def sembolleriYerlestir():
  # Soldaki listWidget öğesine sembolleri dizer ve buna tıklandığında sembolle ilgili işlemleri tetikler #
  vtimlec.execute(sembolleriCek)
  sembolGelenler = vtimlec.fetchall()

  # QListWidget nesnesine sembolleri ekle
  kzarayuz.listWidget_semboller.clear()
  for smbl in sembolGelenler:
    kzarayuz.listWidget_semboller.addItem(smbl[0])


  # Sembol listesinin QCompleter için bir model olarak kullanılması
  sembol_listesi = [sembol[0] for sembol in sembolGelenler]
  model = QStringListModel(sembol_listesi)
  completer = QCompleter(model)
  completer.setCaseSensitivity(Qt.CaseInsensitive)
  # Girdi alanına QCompleter eklenmesi
  kzarayuz.lineEdit_sembolArama.setCompleter(completer)


  # QListWidget nesnesindeki herhangi bir öğe tıklandığında seciliSembolIslemleri fonksiyonunu çağır
  kzarayuz.listWidget_semboller.itemClicked.connect(seciliSembolIslemleri)


def seciliSembolIslemleri(item):
  global toplamAdet, toplamAlimAdet
  toplamAdet = 0
  toplamAlimAdet = 0


  # üstteki sembol lineEditine sembol adını yaz
  global sembol
  sembol = item.text()
  kzarayuz.lineEdit_sembol.setText(sembol)

  alimVerisiIsleme()
  if toplamAlimAdet > 0:
    satimVerisiIsleme()
  else:
    satimsizSembolIslemleri()
  sembolunFiyatiniOgren(sembol)
  hesapKitap()
  adetYerlestir()

def hesapKitap():
  global toplamAdet, toplamAlimAdet, toplamSatimAdet, toplamAlimHacim, toplamSatimHacim, alimOrtalamasi, satimOrtalamasi
  global sembolFiyat, sembolVarlik, gerceklenen, cikis, karZararYuzdesi
  if toplamAlimAdet == 0:
    alimsizSembolIslemleri()
  else:
    #gerceklenen'in (realizasyon) hesaplanması
    satimAlimFarki = satimOrtalamasi - alimOrtalamasi
    gerceklenen = round(toplamSatimAdet * satimAlimFarki, 2)

    # güncel fiyata göre hissenin ederinin (varlık) hesaplanması
    sembolVarlik = round(toplamAdet * sembolFiyat, 2)

    #Çıkışın (güncel fiyattan tüm hisselerin satılması durumu) hesaplanması -
    # Unutma float ile decimal + - yapılamıyor önce hepsini devimal yapmak gerekiyor.
    smblvrlk_Decimal = Decimal(sembolVarlik)
    satimHacim_Decimal = Decimal(toplamSatimHacim)
    alimHacim_Decimal = Decimal(toplamAlimHacim)
    cikisDecimal = smblvrlk_Decimal + satimHacim_Decimal - alimHacim_Decimal
    #toplayabildikten sonra da tekrar floata döndürmek gerekiyor.
    cikis = round(float(smblvrlk_Decimal + satimHacim_Decimal - alimHacim_Decimal), 2)
    #kar zarar durumunu yüzde olarak belirtilmesi - kolay işlem ne kadar para yatırdın bu durumda çıkarsan ne kadar paran olacak
    karZararYuzdesi = round(float(cikisDecimal / alimHacim_Decimal * 100), 2)

    hesapkitapSonrasiYerlesimler(sembolVarlik, gerceklenen, cikis, karZararYuzdesi)


def alimVerisiIsleme():
  adetSay = 0
  hacimSay = 0
  global toplamAlimAdet, toplamAlimHacim, alimOrtalamasi, toplamAdet
  toplamAlimAdet = 0
  alimOrtalamasi = 0
  toplamAlimHacim = 0

  # MySQL sorgusunu çalıştır
  vtimlec.execute(f"SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'A' ORDER BY `emirlerim`.`gun` ASC")
  islemIcinGelenAlimlar = vtimlec.fetchall()
  if len(islemIcinGelenAlimlar) == 0:

    alimsizSembolIslemleri()


  else:

    # Verileri işleme - list view öğesine döngüyle yerleştirilecek dizeyi oluşturma işlemi
    # Neden dizeye ekliyorsun dersen listview eklenmesi biraz karışık işlem her sütun satır için ayrı hücre oluşturuyor
    # o yüzden vritabanından gelen veriyi direk lisviewa ekleyemiyoruz. aşağıda satirIndeks satirVeri
    # sutunIndeks sütunVeri filan işlemden anlayacaksın.

    alimVerisiDizeye = []
    for satir in islemIcinGelenAlimlar:

      # Hazır veritabanından gelen veriyi işleyen döngü varken alım toplamını  ve hacmini hesaplama -
      # Dizeye ekleme esnasında yan işlem yani.

      adetSay += satir[1]
      hacim = round(satir[3] / 1000 * 1002, 2)
      hacimSay += hacim

      tarih = trh(satir[0])
      adet = satir[1]
      fiyat = vrgnkt(satir[2])
      eder = vrgnkt(hacim)

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
    toplamAlimAdet = adetSay
    toplamAlimHacim = hacimSay
    alimOrtalamasi = round(toplamAlimHacim / toplamAlimAdet, 2)
    toplamAdet += toplamAlimAdet

    kzarayuz.label_alimOrtalama.clear()
    kzarayuz.label_alimOrtalama.setText(str(alimOrtalamasi))
    kzarayuz.label_alimAdet.setText(str(toplamAlimAdet))



def satimVerisiIsleme():
  satimAdet = 0
  satimHacim = 0
  global toplamSatimAdet, toplamSatimHacim, satimOrtalamasi, toplamAdet
  toplamSatimAdet = 0
  satimOrtalamasi = 0
  toplamSatimHacim = 0

  vtimlec.execute(f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'S' ORDER BY `emirlerim`.`gun` ASC")
  islemIcinGelenSatimlar = vtimlec.fetchall()
  if len(islemIcinGelenSatimlar) == 0:
    satimsizSembolIslemleri()
  else:

    # Verileri işleme
    satimVerisiDizeye = []
    for satir in islemIcinGelenSatimlar:
      # Toplam alım ve hacimi hesaplama - Dizeye ekleme esnasında yan işlem
      satimAdet += satir[0]
      hacim = round(satir[2] / 1000 * 998, 2)
      satimHacim += hacim

      tarih = trh(satir[3])
      adet = satir[0]
      fiyat = vrgnkt(satir[1])
      eder = vrgnkt(hacim)

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

    toplamAdet -= satimAdet

    toplamSatimAdet = satimAdet
    toplamSatimHacim = satimHacim
    satimOrtalamasi = round(satimHacim / satimAdet, 2)
    kzarayuz.label_satimAdet.clear()
    kzarayuz.label_satimAdet.setText(str(satimAdet))
    kzarayuz.label_satimOrtalama.clear()
    kzarayuz.label_satimOrtalama.setText(str(satimOrtalamasi))


def adetYerlestir():
  global toplamAdet
  toplamAdetYazisi = "Toplam Adet : " + str(toplamAdet)
  kzarayuz.label_toplamAdet.setText(toplamAdetYazisi)



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

#----------------------------------------------------------------------------#

def acilisEkranTemizle():
  kzarayuz.label_alimAdet.clear()
  kzarayuz.label_alimOrtalama.clear()
  kzarayuz.label_cikis.clear()
  kzarayuz.label_gerceklenen.clear()
  kzarayuz.label_karzarar.clear()
  kzarayuz.label_satimAdet.clear()
  kzarayuz.label_satimOrtalama.clear()
  kzarayuz.label_sembolVarlik.setText("Sembol seçin")
  kzarayuz.label_toplamAdet.clear()
  kzarayuz.lineEdit_guncelFiyat.clear()
  kzarayuz.lineEdit_sembol.setText(sembol)

def alimsizSembolIslemleri():

  global toplamAdet, toplamAlimAdet, alimOrtalamasi, toplamAlimHacim, toplamSatimAdet, satimOrtalamasi, toplamSatimHacim
  global sembolFiyat, sembolVarlik, gerceklenen, cikis, karZararYuzdesi

  toplamAdet = 0
  toplamAlimAdet = 0
  alimOrtalamasi = 0.00
  toplamAlimHacim = 0.00

  toplamSatimAdet = 0
  satimOrtalamasi = 0.00
  toplamSatimHacim = 0.00

  sembolFiyat = 0.00
  sembolVarlik = 0.00
  gerceklenen = 0.00
  cikis = 0.00
  karZararYuzdesi = 0

  # Alım ve satım tablolarını boşalt
  kzarayuz.tableWidget_alim.clear()
  kzarayuz.tableWidget_alim.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Eder'])
  kzarayuz.tableWidget_alim.setRowCount(0)
  kzarayuz.label_alimAdet.setText("0")
  kzarayuz.label_satimAdet.setText("0")
  kzarayuz.label_alimOrtalama.setText("0")
  kzarayuz.label_satimOrtalama.setText("0")
  kzarayuz.label_cikis.setText("0")
  kzarayuz.label_karzarar.setText("0")
  kzarayuz.lineEdit_guncelFiyat.setText("0")
  kzarayuz.label_sembolVarlik.setText("0")

def satimsizSembolIslemleri():

  global toplamSatimAdet, satimOrtalamasi, toplamSatimHacim, gerceklenen

  toplamSatimAdet = 0
  satimOrtalamasi = 0
  toplamSatimHacim = 0

  gerceklenen = 0

  # Alım ve satım tablolarını boşalt
  kzarayuz.tableWidget_satim.clear()
  kzarayuz.tableWidget_satim.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Eder'])
  kzarayuz.tableWidget_satim.setRowCount(0)
  kzarayuz.label_satimAdet.setText("0")
  kzarayuz.label_satimOrtalama.setText("0")
  kzarayuz.label_gerceklenen.setText("0")

def hesapkitapSonrasiYerlesimler(sembolVarlik, gerceklenen, cikis, karZararYuzdesi):

  varlik_yazisi = tl_ekle(vrgnkt(sembolVarlik))
  kzarayuz.label_sembolVarlik.setText(varlik_yazisi)

  gerceklenen_yazisi = tl_ekle(vrgnkt(gerceklenen))

  if gerceklenen < 0:
    kzarayuz.label_gerceklenen.setStyleSheet("color: red")
  else:
    kzarayuz.label_gerceklenen.setStyleSheet("color: black")
  kzarayuz.label_gerceklenen.setText(gerceklenen_yazisi)

  cikis_yazisi = tl_ekle(vrgnkt(cikis))

  if cikis < 0:
    kzarayuz.label_cikis.setStyleSheet("color: red")
  else:
    kzarayuz.label_cikis.setStyleSheet("color: black")
  kzarayuz.label_cikis.setText(cikis_yazisi)

  if karZararYuzdesi < 0:
    kzarayuz.label_karzarar.setStyleSheet("color: red")
  else:
    kzarayuz.label_karzarar.setStyleSheet("color: black")
  kzyazisi = "% " + str(karZararYuzdesi)
  kzarayuz.label_karzarar.setText(kzyazisi)
  guncelFiyatYazisi = "Güncel Fiyat : ₺" + vrgnkt(sembolFiyat)

  kzarayuz.lineEdit_guncelFiyat.setText(guncelFiyatYazisi)
  kzarayuz.lineEdit_guncelFiyat.setStyleSheet("font-weight:bold; background-color: rgb(205, 194, 159);")

def guncelle():
  gunsonuFiyat.clear()
  gunsonuFiyatlariOlustur()


def vrgnkt(gel):
  don = '{:,.2f}'.format(gel).replace(",", "X").replace(".", ",").replace("X", ".")
  return  don

def trh(gel):
  don = gel.strftime("%d.%m.%Y")
  return don

def tl_ekle(gel):
  don = "₺ " + gel
  return don
#-------------------Program başlangıcında çalışacak fonksiyonlar-------------#

kzmodulAnaPencere.show()
# En baş en baş, ahanda gördüğün pencere bununla oluşuyor.

gunsonuFiyatlariOlustur()
# Her sembolün bir önceki gün hangi fiyattan kapandığının bilgisini oluşturmaya yarıyor

sembolleriYerlestir()
# Hani solda aşağı doğru akan liste var ya sembollerin olduğu, ahanda onu oluşturuyor.

acilisEkranTemizle()
# En başta bir kere çalışacak. Ekrandaki list widget hariç herşeyi temizliyor.

#"Fiyat Güncelle" butonuna basıldığında fiyatların güncellenmesini sağlar.
kzarayuz.pushButton_fiyatGuncelle.clicked.connect(guncelle)

def tarihAraligiSecimi():
  alimUzun = 0
  satimUzun = 0
  alimBilgiMesaj = ""
  alimText = ""
  secilenAlimSatirlari = kzarayuz.tableWidget_alim.selectedItems()
  alimUzun = len(secilenAlimSatirlari)
  if alimUzun > 0:
    ilkAtarih = secilenAlimSatirlari[0].text()
    sonAtarih = secilenAlimSatirlari[alimUzun - 4].text()
    alimAdet = 0
    alimHacim = 0
    for index in range(0, alimUzun, 4):
      alimAdet += geriCevir(secilenAlimSatirlari[index + 1].text())
      alimHacim += geriCevir(secilenAlimSatirlari[index + 3].text())
    ortalamaA = round(alimHacim / alimAdet, 2)
    alimText = '<p style="font-size:14pt; color:green">' + ilkAtarih + ' - - - - - ' + sonAtarih + ' </p>\n \
                <p style="font-size:14pt; color:green; font-weight:bold">Toplam Adet : ' + str(round(alimAdet)) + '</p> \
                <p style="font-size:14pt; color:green; font-weight:bold">Alım Ortalaması : ' + str(ortalamaA) + '</p> \
                <p style="font-size:14pt; color:green; font-weight:bold">Toplam Hacim: ' + vrgnkt(alimHacim) + '</p> '
  else:

    alimText = '<p style="font-size:13pt;">Alım tarih aralığı seçmediniz.</p>'

  satimText = '<p style="font-size:14pt;">Satım tarih aralığı seçmediniz.</p>'
  secilenSatimSatirlari = kzarayuz.tableWidget_satim.selectedItems()
  satimUzun = len(secilenSatimSatirlari)
  print(satimUzun)

  if satimUzun > 0:
    ilkStarih = secilenSatimSatirlari[3].text()
    sonStarih = secilenSatimSatirlari[satimUzun-1].text()
    satimAdet = 0
    satimHacim = 0
    for index in range(0, satimUzun, 4):
      satimAdet += geriCevir(secilenSatimSatirlari[index].text())
      satimHacim += geriCevir(secilenSatimSatirlari[index + 2].text())
    ortalamaS = round(satimHacim / satimAdet, 2)
    satimText = '<p style = "font-size:14pt; color:red; font-weight:bold;" > ' + ilkStarih + ' - - - - - ' + sonStarih + ' </p>\
                <p style = "font-size:14pt; color:red; font-weight:bold;" > Toplam Adet: ' + str(round(satimAdet)) + ' </p> \
                <p style = "font-size:14pt; color:red; font-weight:bold;" > Satım Ortalaması: ' + str(ortalamaS) + ' </p> \
                <p style = "font-size:14pt; color:red; font-weight:bold;" > Toplam Hacim: ' + vrgnkt(satimHacim) + ' </p>'
  else:
    satimText = '<p style="font-size:14pt;">Satım tarih aralığı seçmediniz.</p>'

  fiyatiYaz = '<p style = "font-size:16pt; font-weight:bold;" > <center>Güncel Fiyat : ' + str(sembolFiyat) +  ' </center></p>'
  alimBilgiMesaj = alimText + fiyatiYaz + satimText

  tarihAraligiBilgi = QMessageBox.about(None, "Bilgilendirme", alimBilgiMesaj)



kzarayuz.pushButton_bas.clicked.connect(tarihAraligiSecimi)

def geriCevir(gel):
  don = float(gel.replace(".", "").replace(",", "."))
  return don



sys.exit(Uygulama.exec_())
# Valla ne yalan söyliyim, bu sys exit ne bok yer hiç bir fikrim yok. Ama gerekyior sanırım. #

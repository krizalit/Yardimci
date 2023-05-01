import sys
import mysql.connector
import xlrd
from yrdmc import *
from fonk import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QBrush, QColor
from PyQt5 import QtCore, QtGui, QtWidgets

Yardimci = QApplication(sys.argv)
yardimciAnaPencere = QtWidgets.QTabWidget()
yrmdcAryz = Ui_TabWidget()
yrmdcAryz.setupUi(yardimciAnaPencere)

baglanti = mysql.connector.connect(
  host="localhost",
  user="firat",
  password="eben",
  database="yatirim"
)
vtimlec = baglanti.cursor()

#-------------------Başlangıç Değişkenleri

gunsonuFiyat = {}
borsaDurumVerileri = {}
yuzdePay = {}
sektorel = {}
varlik = 0

def gunsonuFiyatlariOlustur():
  # ----- progam açılışında yereldeki dosyadan bir önceki gün fiyat bilgilerini alır, dict e ekler------#
  # ----- program boyunca kullanılacak fiyat bilgileri bu dictten okunur -------------------------------#
  workbook = xlrd.open_workbook("../../Pozisyonlarım.xlsx")
  worksheet = workbook.sheet_by_index(0)
  strSayisi =(worksheet.nrows)

  for i in range(1, strSayisi):
    smbl = worksheet.cell_value(i, 0)
    fyt = worksheet.cell_value(i, 3)
    gunsonuFiyat[smbl] = fyt
  return gunsonuFiyat

def sembolunFiyatiniOgren(sembol):
  # her sembol için gunsonuFiyat dict inden fiyat bilgisini alan fonksiyon
  dictebak = gunsonuFiyat.get(sembol)
  if dictebak == None:
    sembolFiyat = 0
  else:
    sembolFiyat = dictebak
  return sembolFiyat

def sembolSozluguOlustur(sembol):
  toplamAdet = 0
  global varlik
  sembolFiyat = sembolunFiyatiniOgren(sembol)

  vtimlec.execute(f"SELECT SUM(`gerceklesen`), sum(`hacim`) FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'A' ")
  islemIcinGelenAlimlar = vtimlec.fetchall()
  tplmAlmAdt, tplmAlmHcm = islemIcinGelenAlimlar[0]
  if tplmAlmAdt == None:
    pass
  else:
    toplamAlimAdet = int(tplmAlmAdt)
    toplamAlimHacim = round(tplmAlmHcm / 1000 * 1002, 2)
    alimOrtalamasi = round(toplamAlimHacim / toplamAlimAdet, 2)
    toplamAdet += toplamAlimAdet

    vtimlec.execute(f"SELECT SUM(`gerceklesen`), sum(`hacim`) FROM `emirlerim` WHERE `sembol` = '{sembol}' AND `alsat` = 'S' ")
    islemIcinGelenSatimlar = vtimlec.fetchall()
    tplmStmAdt, tplmStmHcm = islemIcinGelenSatimlar[0]
    if tplmStmAdt == None:
      toplamSatimAdet = 0
      satimOrtalamasi = 0
      toplamSatimHacim = 0
      gerceklenen = 0

    else:
      toplamSatimAdet = int(tplmStmAdt)
      toplamSatimHacim = round(tplmStmHcm / 1000 * 998, 2)
      satimOrtalamasi = round(toplamSatimHacim / toplamSatimAdet, 2)
      satimAlimFarki = satimOrtalamasi - alimOrtalamasi
      gerceklenen = round(toplamSatimAdet * satimAlimFarki, 2)

    toplamAdet -= toplamSatimAdet
    sembolVarlik = round(toplamAdet * sembolFiyat, 2)
    kz = toplamAdet * ( sembolFiyat - alimOrtalamasi )
    cikis = round(sembolVarlik + toplamSatimHacim - toplamAlimHacim, 2)
    karZararYuzdesi = round(cikis / toplamAlimHacim * 100, 2)

    borsaDurumVerileri[sembol] = {'alimadet': toplamAlimAdet, 'satimadet': toplamSatimAdet, 'toplamadet': toplamAdet, \
                                 'maliyet': alimOrtalamasi, 'fiyat': sembolFiyat, 'gerceklenen': gerceklenen, 'cikis': cikis, \
                                 'kz': vrgnkt(kz), 'deger': sembolVarlik, 'yzkz': karZararYuzdesi, 'yzpay': 0}
    yuzdePay[sembol] = {'yzpay': sembolVarlik}
    varlik += sembolVarlik

def borsaDurumSozluguOlustur():
  vtimlec.execute("SELECT `sembol` FROM `semboller` ORDER BY `semboller`.`sembol` ASC ")
  sembolGelenler = vtimlec.fetchall()
  for smbl in sembolGelenler:
    sembolSozluguOlustur(smbl[0])

def yuzdePayGuncelle():
  for anahtar in yuzdePay:
    yzpay = yuzdePay[anahtar]['yzpay']
    borsaDurumVerileri[anahtar]['yzpay'] = round(yzpay * 100 / varlik ,3)

def borsa_durum_verilerini_guncelle(tableWidget_borsaDurum, borsaDurumVerileri):
  tableWidget_borsaDurum.setRowCount(len(borsaDurumVerileri))
  tableWidget_borsaDurum.setColumnCount(12)

  for i, (sembol, veri) in enumerate(borsaDurumVerileri.items()):
    tableWidget_borsaDurum.setItem(i, 0, QtWidgets.QTableWidgetItem(sembol))
    tableWidget_borsaDurum.item(i,0).setTextAlignment(Qt.AlignCenter | Qt.AlignLeft)
    tableWidget_borsaDurum.setItem(i, 1, QtWidgets.QTableWidgetItem(str(veri['alimadet'])))
    tableWidget_borsaDurum.item(i, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_borsaDurum.setItem(i, 2, QtWidgets.QTableWidgetItem(str(veri['satimadet'])))
    tableWidget_borsaDurum.item(i, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_borsaDurum.setItem(i, 3, QtWidgets.QTableWidgetItem(str(veri['toplamadet'])))
    tableWidget_borsaDurum.item(i, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_borsaDurum.setItem(i, 4, QtWidgets.QTableWidgetItem(vrgnkt(veri['maliyet'])))
    tableWidget_borsaDurum.item(i, 4).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_borsaDurum.setItem(i, 5, QtWidgets.QTableWidgetItem(vrgnkt(veri['fiyat'])))
    tableWidget_borsaDurum.item(i, 5).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_borsaDurum.setItem(i, 6, QtWidgets.QTableWidgetItem(vrgnkt(veri['gerceklenen'])))
    tableWidget_borsaDurum.item(i, 6).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if veri['gerceklenen'] < 0:
      tableWidget_borsaDurum.item(i, 6).setForeground(QtGui.QBrush(QtGui.QColor(244, 0, 0)))
    tableWidget_borsaDurum.setItem(i, 7, QtWidgets.QTableWidgetItem(vrgnkt(veri['cikis'])))
    tableWidget_borsaDurum.item(i, 7).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if veri['cikis'] < 0:
      tableWidget_borsaDurum.item(i, 7).setForeground(QtGui.QBrush(QtGui.QColor(244, 0, 0)))
    tableWidget_borsaDurum.setItem(i, 8, QtWidgets.QTableWidgetItem(veri['kz']))
    tableWidget_borsaDurum.item(i, 8).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if geriCevir(veri['kz']) < 0:
      tableWidget_borsaDurum.item(i, 8).setForeground(QtGui.QBrush(QtGui.QColor(244, 0, 0)))
    tableWidget_borsaDurum.setItem(i, 9, QtWidgets.QTableWidgetItem(vrgnkt(veri['deger'])))
    tableWidget_borsaDurum.item(i, 9).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_borsaDurum.setItem(i, 10, QtWidgets.QTableWidgetItem('{:.2f}'.format(veri['yzkz'])))
    tableWidget_borsaDurum.item(i, 10).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if veri['yzkz'] < 0:
      tableWidget_borsaDurum.item(i, 10).setForeground(QtGui.QBrush(QtGui.QColor(244, 0, 0)))
    tableWidget_borsaDurum.setItem(i, 11, QtWidgets.QTableWidgetItem('{:.3f}'.format(veri['yzpay'])))
    tableWidget_borsaDurum.item(i, 11).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

def altnFyt ():
  global borsaDurumVerileri
  global gunsonuFiyat
  gunsonuFiyatlariOlustur()
  fiyat = float(yrmdcAryz.lineEdit_altnFyt.text().replace(",", "."))
  gunsonuFiyat['ALTIN'] = fiyat
  borsaDurumSozluguOlustur()
  yuzdePayGuncelle()
  borsa_durum_verilerini_guncelle(yrmdcAryz.tableWidget_borsaDurum, borsaDurumVerileri)

def karzararHesapla():
  kacan =  0
  for sembol, veri in borsaDurumVerileri.items():
    kacan += float(veri['cikis'])
  yrmdcAryz.label_toplamKZ.setText(vrgnkt(kacan))
  sektorsel()

def sektorsel():
  global sektorel
  vtimlec.execute("SELECT `sektor` FROM `sektorler` ORDER BY `sektorler`.`sektor` ASC ")
  sektorGelenler = vtimlec.fetchall()
  for sektor in sektorGelenler:
    vtimlec.execute(f"SELECT `sembol` FROM `semboller` WHERE `sektor` = '{sektor[0]}'")
    semboller = vtimlec.fetchall()
    deger = 0
    cikis = 0
    for sembol in semboller:
      sembol_verileri = borsaDurumVerileri.get(sembol[0])
      if sembol_verileri:
        deger += round(float(sembol_verileri['deger']), 2)
        cikis += round(float(sembol_verileri['cikis']), 2)
    sektorel[sektor[0]] = {'Varlik': deger, 'Cikis': cikis}

  print(sektorel)
  bankaCikis = sektorel['Bankacılık']['Cikis']
  bankaVarlik = sektorel['Bankacılık']['Varlik']
  yrmdcAryz.label_bankaVarlik.setText(vrgnkt(bankaVarlik))
  yrmdcAryz.label_bankaCikis.setText(vrgnkt(bankaCikis))
  if bankaCikis < 0:
    yrmdcAryz.label_bankaCikis.setStyleSheet("color: rgb(244, 0, 0);font-weight: bold")
  else:
    yrmdcAryz.label_bankaCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  dcCikis = sektorel['Demir-Çelik']['Cikis']
  dcVarlik =sektorel['Demir-Çelik']['Varlik']
  yrmdcAryz.label_dnrclkVarlik.setText(vrgnkt(dcVarlik))
  yrmdcAryz.label_dmrclkCikis.setText(vrgnkt(dcCikis))
  if dcCikis < 0:
    yrmdcAryz.label_dmrclkCikis.setStyleSheet("color: rgb(244, 0, 0);font-weight: bold")
  else:
    yrmdcAryz.label_dmrclkCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  agCikis = sektorel['AUGAG']['Cikis']
  agVarlik = sektorel['AUGAG']['Varlik']
  yrmdcAryz.label_augagCikis.setText(vrgnkt(agCikis))
  yrmdcAryz.label_augagVarlik.setText(vrgnkt(agVarlik))
  if agCikis < 0:
    yrmdcAryz.label_augagCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_endustriCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  endustriCikis = sektorel['Endüstri']['Cikis']
  endustriVarlik = sektorel['Endüstri']['Varlik']
  yrmdcAryz.label_endustriCikis.setText(vrgnkt(endustriCikis))
  yrmdcAryz.label_endustriVarlik.setText(vrgnkt(endustriVarlik))
  if endustriCikis < 0:
    yrmdcAryz.label_endustriCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_endustriCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  eneCikis = sektorel['Enerji']['Cikis']
  eneVarlik = sektorel['Enerji']['Varlik']
  yrmdcAryz.label_enerjiCikis.setText(vrgnkt(eneCikis))
  yrmdcAryz.label_enerjiVarlik.setText(vrgnkt(eneVarlik))
  if eneCikis < 0:
    yrmdcAryz.label_enerjiCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_enerjiCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  gidaCikis = sektorel['Gıda']['Cikis']
  gidaVarlik = sektorel['Gıda']['Varlik']
  yrmdcAryz.label_gidaCikis.setText(vrgnkt(gidaCikis))
  yrmdcAryz.label_gidaVarlik.setText(vrgnkt(gidaVarlik))
  if gidaCikis < 0:
    yrmdcAryz.label_gidaCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_gidaCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  girisimCikis = sektorel['Girişim']['Cikis']
  girisimVarlik = sektorel['Girişim']['Varlik']
  yrmdcAryz.label_girisimCikis.setText(vrgnkt(girisimCikis))
  yrmdcAryz.label_girisimVarlik.setText(vrgnkt(girisimVarlik))
  if girisimCikis < 0:
    yrmdcAryz.label_girisimCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_girisimCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  gmyoCikis = sektorel['GMYO']['Cikis']
  gmyoVarlik = sektorel['GMYO']['Varlik']
  yrmdcAryz.label_gmyoCikis.setText(vrgnkt(gmyoCikis))
  yrmdcAryz.label_gmyoVarlik.setText(vrgnkt(gmyoVarlik))
  if gmyoCikis < 0:
    yrmdcAryz.label_gmyoCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_gmyoCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")


  havacilikCikis = sektorel['Havacılık']['Cikis']
  havacilikVarlik = sektorel['Havacılık']['Varlik']
  yrmdcAryz.label_havacilikCikis.setText(vrgnkt(havacilikCikis))
  yrmdcAryz.label_havacilikVarlik.setText(vrgnkt(havacilikVarlik))
  if havacilikCikis < 0:
    yrmdcAryz.label_havacilikCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_havacilikCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  holdingCikis = sektorel['Holding']['Cikis']
  holdingVarlik = sektorel['Holding']['Varlik']
  yrmdcAryz.label_holdingCikis.setText(vrgnkt(holdingCikis))
  yrmdcAryz.label_holdingVarlik.setText(vrgnkt(holdingVarlik))
  if holdingCikis < 0:
    yrmdcAryz.label_holdingCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_holdingCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  insaatCikis = sektorel['İnşaat']['Cikis']
  insaatVarlik = sektorel['İnşaat']['Varlik']
  yrmdcAryz.label_insaatCikis.setText(vrgnkt(insaatCikis))
  yrmdcAryz.label_insaatVarlik.setText(vrgnkt(insaatVarlik))
  if insaatCikis < 0:
    yrmdcAryz.label_insaatCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_insaatCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  kagitCikis = sektorel['Kağıt']['Cikis']
  kagitVarlik = sektorel['Kağıt']['Varlik']
  yrmdcAryz.label_kagitCikis.setText(vrgnkt(kagitCikis))
  yrmdcAryz.label_kagitVarlik.setText(vrgnkt(kagitVarlik))
  if kagitCikis < 0:
    yrmdcAryz.label_kagitCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_kagitCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  kimyaCikis = sektorel['Kimya']['Cikis']
  kimyaVarlik = sektorel['Kimya']['Varlik']
  yrmdcAryz.label_kimyaCikis.setText(vrgnkt(kimyaCikis))
  yrmdcAryz.label_kimyaVarlik.setText(vrgnkt(kimyaVarlik))
  if kimyaCikis < 0:
    yrmdcAryz.label_kimyaCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_kimyaCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  madenCikis = sektorel['Maden']['Cikis']
  madenVarlik = sektorel['Maden']['Varlik']
  yrmdcAryz.label_madenVarlik.setText(vrgnkt(madenVarlik))
  yrmdcAryz.label_madenCikis.setText(vrgnkt(madenCikis))
  if madenCikis < 0:
    yrmdcAryz.label_madenCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_madenCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  mkyoCikis = sektorel['MKYO']['Cikis']
  mkyoVarlik = sektorel['MKYO']['Varlik']
  yrmdcAryz.label_mkyoCikis.setText(vrgnkt(mkyoCikis))
  yrmdcAryz.label_mkyoVarlik.setText(vrgnkt(mkyoVarlik))
  if mkyoCikis < 0:
    yrmdcAryz.label_mkyoCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_mkyoCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  otomotivCikis = sektorel['Otomotiv']['Cikis']
  otomotivVarlik = sektorel['Otomotiv']['Varlik']
  yrmdcAryz.label_otoCikis.setText(vrgnkt(otomotivCikis))
  yrmdcAryz.label_otoVarlik.setText(vrgnkt(otomotivVarlik))
  if otomotivCikis < 0:
    yrmdcAryz.label_otoCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_otoCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  petrokimyaCikis = sektorel['Petrokimya']['Cikis']
  petrokimyaVarlik = sektorel['Petrokimya']['Varlik']
  yrmdcAryz.label_petroCikis.setText(vrgnkt(petrokimyaCikis))
  yrmdcAryz.label_petroVarlik.setText(vrgnkt(petrokimyaVarlik))
  if petrokimyaCikis < 0:
    yrmdcAryz.label_petroCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_petroCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  saglikCikis = sektorel['Sağlık']['Cikis']
  saglikVarlik = sektorel['Sağlık']['Varlik']
  yrmdcAryz.label_saglikCikis.setText(vrgnkt(saglikCikis))
  yrmdcAryz.label_saglikVarlik.setText(vrgnkt(saglikVarlik))
  if saglikCikis < 0:
    yrmdcAryz.label_saglikCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_saglikCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  tarimCikis = sektorel['Tarım']['Cikis']
  tarimVarlik = sektorel['Tarım']['Varlik']
  yrmdcAryz.label_tarimCikis.setText(vrgnkt(tarimCikis))
  yrmdcAryz.label_tarimVarlik.setText(vrgnkt(tarimVarlik))
  if tarimCikis < 0:
    yrmdcAryz.label_tarimCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_tarimCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  tasimacilikCikis = sektorel['Taşımacılık']['Cikis']
  tasimacilikVarlik = sektorel['Taşımacılık']['Varlik']
  yrmdcAryz.label_tasimaCikis.setText(vrgnkt(tasimacilikCikis))
  yrmdcAryz.label_tasimaVarlik.setText(vrgnkt(tasimacilikVarlik))
  if tasimacilikCikis < 0:
    yrmdcAryz.label_tasimaCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_tasimaCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  teknolojiCikis = sektorel['Teknoloji']['Cikis']
  teknolojiVarlik = sektorel['Teknoloji']['Varlik']
  yrmdcAryz.label_teknoCikis.setText(vrgnkt(teknolojiCikis))
  yrmdcAryz.label_teknoVarlik.setText(vrgnkt(teknolojiVarlik))
  if teknolojiCikis < 0:
    yrmdcAryz.label_teknoCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_teknoCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")

  tekstilCikis = sektorel['Tekstil']['Cikis']
  tekstilVarlik = sektorel['Tekstil']['Varlik']
  yrmdcAryz.label_tekstilCikis.setText(vrgnkt(tekstilCikis))
  yrmdcAryz.label_tekstilVarlik.setText(vrgnkt(tekstilVarlik))
  if tekstilCikis < 0:
    yrmdcAryz.label_tekstilCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans'")
  else:
    yrmdcAryz.label_tekstilCikis.setStyleSheet("color: rgb(0, 0, 0);font-weight: bold")



yrmdcAryz.pushButton_altnFytGnclle.clicked.connect(altnFyt)
yrmdcAryz.pushButton_toplamKZ.clicked.connect(karzararHesapla)

yardimciAnaPencere.show()
sys.exit(Yardimci.exec_())
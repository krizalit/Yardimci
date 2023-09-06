import sys
import os
import datetime
import mysql.connector
import xlrd
import xlwt
from xlwt import Workbook
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

#-------------------Başlangıç Değişkenleri
baglanti = mysql.connector.connect(
  host="localhost",
  user="firat",
  password="eben",
  database="yatirim"
)
vtimlec = baglanti.cursor()
#-------- Borsa durum değişkenleri
gunsonuFiyat = {}
guniciFiyat = {}
borsaDurumVerileri = {}
guniciFiyatVerileri = {}
yuzdePay = {}
sektorel = {}
cikilmisKagitlar = {}
guniciAlimEmirlerim = {}
guniciSatimEmirlerim = {}
varlik = 0
cikilmisVarlik = 0
#-------- kzModul değikenleri

#-------- Borsa Durum işlevleri

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
  global cikilmisVarlik
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
    if toplamAdet == 0:
      cikis = gerceklenen
      karZararYuzdesi = round(cikis / toplamAlimHacim * 100, 2)
      cikilmisKagitlar[sembol] = {'alimadet': toplamAlimAdet, 'satimadet': toplamSatimAdet, \
                                  'maliyet': alimOrtalamasi, 'satimortalamasi': satimOrtalamasi, \
                                  'cikis': cikis, 'yzkz': karZararYuzdesi, }

      yrmdcAryz.listWidget_cikilmisSemboller.addItem(sembol)
      cikilmisVarlik += cikis

    else:
      cikis = round(sembolVarlik + toplamSatimHacim - toplamAlimHacim, 2)
      karZararYuzdesi = round(cikis / toplamAlimHacim * 100, 2)

      borsaDurumVerileri[sembol] = {'alimadet': toplamAlimAdet, 'satimadet': toplamSatimAdet, 'toplamadet': toplamAdet, \
                                 'maliyet': alimOrtalamasi, 'satimortalamasi': satimOrtalamasi, 'fiyat': sembolFiyat, 'gerceklenen': gerceklenen, 'cikis': cikis, \
                                 'kz': vrgnkt(kz), 'deger': sembolVarlik, 'yzkz': karZararYuzdesi, 'yzpay': 0}
      yuzdePay[sembol] = {'yzpay': sembolVarlik}
      varlik += sembolVarlik

      yrmdcAryz.listWidget_semboller.addItem(sembol)

def borsaDurumSozluguOlustur():
  yrmdcAryz.listWidget_semboller.clear()
  vtimlec.execute("SELECT `sembol` FROM `semboller` ORDER BY `semboller`.`sembol` ASC ")
  sembolGelenler = vtimlec.fetchall()
  for smbl in sembolGelenler:
    sembolSozluguOlustur(smbl[0])
  yrmdcAryz.label_cikilmisToplam.setText(vrgnkt(cikilmisVarlik))

def yuzdePayGuncelle():
  for anahtar in yuzdePay:
    yzpay = yuzdePay[anahtar]['yzpay']
    borsaDurumVerileri[anahtar]['yzpay'] = round(yzpay * 100 / varlik ,3)

def borsa_durum_tablosu_olustur(tableWidget_borsaDurum, borsaDurumVerileri):
  tableWidget_borsaDurum.clear()
  tableWidget_borsaDurum.setRowCount(len(borsaDurumVerileri))
  tableWidget_borsaDurum.setColumnCount(12)
  tableWidget_borsaDurum.setHorizontalHeaderLabels(['Sembol', 'Alım Adet', 'Satım Adet', 'Adet', 'Maliyet', 'Günc. Fiyat', 'Satım Ort.', 'Gerçeklenen', 'Çıkış', 'Değer', '% K / Z', '% Pay'])

  for i, (sembol, veri) in enumerate(borsaDurumVerileri.items()):
    tableWidget_borsaDurum.setItem(i, 0, QtWidgets.QTableWidgetItem(sembol))
    tableWidget_borsaDurum.item(i,0).setTextAlignment(Qt.AlignCenter | Qt.AlignLeft)
    tableWidget_borsaDurum.setItem(i, 1, QtWidgets.QTableWidgetItem(str(binliknokta(veri['alimadet']))))
    tableWidget_borsaDurum.item(i, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_borsaDurum.setItem(i, 2, QtWidgets.QTableWidgetItem(str(binliknokta(veri['satimadet']))))
    tableWidget_borsaDurum.item(i, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_borsaDurum.setItem(i, 3, QtWidgets.QTableWidgetItem(str(binliknokta(veri['toplamadet']))))
    tableWidget_borsaDurum.item(i, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_borsaDurum.setItem(i, 4, QtWidgets.QTableWidgetItem(vrgnkt(veri['maliyet'])))
    tableWidget_borsaDurum.item(i, 4).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_borsaDurum.setItem(i, 5, QtWidgets.QTableWidgetItem(vrgnkt(veri['fiyat'])))
    tableWidget_borsaDurum.item(i, 5).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_borsaDurum.setItem(i, 6, QtWidgets.QTableWidgetItem(str(vrgnkt(veri['satimortalamasi']))))
    tableWidget_borsaDurum.item(i, 6).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_borsaDurum.setItem(i, 7, QtWidgets.QTableWidgetItem(vrgnkt(veri['gerceklenen'])))
    tableWidget_borsaDurum.item(i, 7).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if veri['gerceklenen'] < 0:
      tableWidget_borsaDurum.item(i, 7).setForeground(QtGui.QBrush(QtGui.QColor(214, 1, 1)))
    tableWidget_borsaDurum.setItem(i, 8, QtWidgets.QTableWidgetItem(vrgnkt(veri['cikis'])))
    tableWidget_borsaDurum.item(i, 8).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if veri['cikis'] < 0:
      tableWidget_borsaDurum.item(i, 8).setForeground(QtGui.QBrush(QtGui.QColor(214, 1, 1)))
    tableWidget_borsaDurum.setItem(i, 9, QtWidgets.QTableWidgetItem(vrgnkt(veri['deger'])))
    tableWidget_borsaDurum.item(i, 9).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_borsaDurum.setItem(i, 10, QtWidgets.QTableWidgetItem(vrgnkt(round(veri['yzkz'], 2))))
    tableWidget_borsaDurum.item(i, 10).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if veri['yzkz'] < 0:
      tableWidget_borsaDurum.item(i, 10).setForeground(QtGui.QBrush(QtGui.QColor(214, 1, 1)))
    tableWidget_borsaDurum.setItem(i, 11, QtWidgets.QTableWidgetItem(vrgnkt2(round(veri['yzpay'], 3))))
    tableWidget_borsaDurum.item(i, 11).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    print()

def borsa_cikilmislarTablosuOlustur(tableWidget_cikilmisDurum, cikilmisKagitlar):
  tableWidget_cikilmisDurum.clear()
  tableWidget_cikilmisDurum.setRowCount(len(cikilmisKagitlar))
  tableWidget_cikilmisDurum.setColumnCount(7)
  tableWidget_cikilmisDurum.setHorizontalHeaderLabels(['Sembol', 'Alım Adet', 'Satım Adet', 'Alım Ort.', 'Satım Ort.', 'Çıkış', '% K / Z'])
  for i, (sembol, veri) in enumerate(cikilmisKagitlar.items()):
    tableWidget_cikilmisDurum.setItem(i, 0, QtWidgets.QTableWidgetItem(sembol))
    tableWidget_cikilmisDurum.item(i,0).setTextAlignment(Qt.AlignCenter | Qt.AlignLeft)
    tableWidget_cikilmisDurum.setItem(i, 1, QtWidgets.QTableWidgetItem(str(veri['alimadet'])))
    tableWidget_cikilmisDurum.item(i, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_cikilmisDurum.setItem(i, 2, QtWidgets.QTableWidgetItem(str(veri['satimadet'])))
    tableWidget_cikilmisDurum.item(i, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    tableWidget_cikilmisDurum.setItem(i, 3, QtWidgets.QTableWidgetItem(vrgnkt(veri['maliyet'])))
    tableWidget_cikilmisDurum.item(i, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_cikilmisDurum.setItem(i, 4, QtWidgets.QTableWidgetItem(vrgnkt(veri['satimortalamasi'])))
    tableWidget_cikilmisDurum.item(i, 4).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    tableWidget_cikilmisDurum.setItem(i, 5, QtWidgets.QTableWidgetItem(vrgnkt(veri['cikis'])))
    tableWidget_cikilmisDurum.item(i, 5).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
    if veri['cikis'] < 0:
      tableWidget_cikilmisDurum.item(i, 5).setForeground(QtGui.QBrush(QtGui.QColor(214, 1, 1)))
    tableWidget_cikilmisDurum.setItem(i, 6, QtWidgets.QTableWidgetItem('{:.2f}'.format(veri['yzkz'])))
    tableWidget_cikilmisDurum.item(i, 6).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)
    if veri['yzkz'] < 0:
      tableWidget_cikilmisDurum.item(i, 6).setForeground(QtGui.QBrush(QtGui.QColor(214, 1, 1)))

def yeniOlustur():
  global borsaDurumVerileri
  global gunsonuFiyat
  gunsonuFiyat = {}
  borsaDurumVerileri = {}
  gunsonuFiyatlariOlustur()
  fiyat = float(yrmdcAryz.lineEdit_altnFyt.text().replace(",", "."))
  gunsonuFiyat['ALTIN'] = fiyat
  borsaDurumSozluguOlustur()
  yuzdePayGuncelle()
  borsa_durum_tablosu_olustur(yrmdcAryz.tableWidget_borsaDurum, borsaDurumVerileri)
  borsa_cikilmislarTablosuOlustur(yrmdcAryz.tableWidget_cikilmisDurum, cikilmisKagitlar)

def altnFyt ():
  global borsaDurumVerileri
  global gunsonuFiyat
  gunsonuFiyatlariOlustur()
  fiyat = float(yrmdcAryz.lineEdit_altnFyt.text().replace(",", "."))
  gunsonuFiyat['ALTIN'] = fiyat
  borsaDurumSozluguOlustur()
  yuzdePayGuncelle()
  borsa_durum_tablosu_olustur(yrmdcAryz.tableWidget_borsaDurum, borsaDurumVerileri)
  borsa_cikilmislarTablosuOlustur(yrmdcAryz.tableWidget_cikilmisDurum, cikilmisKagitlar)

def karzararHesapla():
  varlik = 0
  kacan =  0
  for sembol, veri in borsaDurumVerileri.items():
    kacan += float(veri['cikis'])
    varlik += float(veri['deger'])
  yrmdcAryz.label_toplamKZ.setText(vrgnkt(kacan))
  if kacan < 0:
    yrmdcAryz.label_toplamKZ.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_toplamKZ.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  yrmdcAryz.label_varlik.setText(vrgnkt(varlik))
  yrmdcAryz.label_varlik.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
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
      sembol_verileri_cikilmislar = cikilmisKagitlar.get(sembol[0])
      if sembol_verileri_cikilmislar:
        #deger += round(float(sembol_verileri_cikilmislar['deger']), 2)
        cikis += round(float(sembol_verileri_cikilmislar['cikis']), 2)

    sektorel[sektor[0]] = {'Varlik': deger, 'Cikis': cikis}

  vtimlec.execute("SELECT `sembol` FROM `semboller` WHERE `arz` = 'E'")
  arzGelenler = vtimlec.fetchall()
  arzdeger = 0
  arzcikis = 0
  for arzsmbl in arzGelenler:
    arz =  borsaDurumVerileri.get(arzsmbl[0])
    if arz:
      arzdeger += round(float(arz['deger']), 2)
      arzcikis += round(float(arz['cikis']), 2)

  yrmdcAryz.label_arzVarlik.setText(vrgnkt(arzdeger))
  yrmdcAryz.label_arzCikis.setText(vrgnkt(arzcikis))
  if arzcikis < 0:
    yrmdcAryz.label_arzCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_arzCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  bankaCikis = sektorel['Bankacılık']['Cikis']
  bankaVarlik = sektorel['Bankacılık']['Varlik']
  yrmdcAryz.label_bankaVarlik.setText(vrgnkt(bankaVarlik))
  yrmdcAryz.label_bankaCikis.setText(vrgnkt(bankaCikis))
  if bankaCikis < 0:
    yrmdcAryz.label_bankaCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_bankaCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  dcCikis = sektorel['Demir-Çelik']['Cikis']
  dcVarlik =sektorel['Demir-Çelik']['Varlik']
  yrmdcAryz.label_dnrclkVarlik.setText(vrgnkt(dcVarlik))
  yrmdcAryz.label_dmrclkCikis.setText(vrgnkt(dcCikis))
  if dcCikis < 0:
    yrmdcAryz.label_dmrclkCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_dmrclkCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  agCikis = sektorel['AUGAG']['Cikis']
  agVarlik = sektorel['AUGAG']['Varlik']
  yrmdcAryz.label_augagCikis.setText(vrgnkt(agCikis))
  yrmdcAryz.label_augagVarlik.setText(vrgnkt(agVarlik))
  if agCikis < 0:
    yrmdcAryz.label_augagCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_augagCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  endustriCikis = sektorel['Endüstri']['Cikis']
  endustriVarlik = sektorel['Endüstri']['Varlik']
  yrmdcAryz.label_endustriCikis.setText(vrgnkt(endustriCikis))
  yrmdcAryz.label_endustriVarlik.setText(vrgnkt(endustriVarlik))
  if endustriCikis < 0:
    yrmdcAryz.label_endustriCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_endustriCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  enerjiCikis = sektorel['Enerji']['Cikis']
  enerjiVarlik = sektorel['Enerji']['Varlik']
  yrmdcAryz.label_enerjiCikis.setText(vrgnkt(enerjiCikis))
  yrmdcAryz.label_enerjiVarlik.setText(vrgnkt(enerjiVarlik))
  if enerjiCikis < 0:
    yrmdcAryz.label_enerjiCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_enerjiCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  gidaCikis = sektorel['Gıda']['Cikis']
  gidaVarlik = sektorel['Gıda']['Varlik']
  yrmdcAryz.label_gidaCikis.setText(vrgnkt(gidaCikis))
  yrmdcAryz.label_gidaVarlik.setText(vrgnkt(gidaVarlik))
  if gidaCikis < 0:
    yrmdcAryz.label_gidaCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_gidaCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  girisimCikis = sektorel['Girişim']['Cikis']
  girisimVarlik = sektorel['Girişim']['Varlik']
  yrmdcAryz.label_girisimCikis.setText(vrgnkt(girisimCikis))
  yrmdcAryz.label_girisimVarlik.setText(vrgnkt(girisimVarlik))
  if girisimCikis < 0:
    yrmdcAryz.label_girisimCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_girisimCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  gmyoCikis = sektorel['GMYO']['Cikis']
  gmyoVarlik = sektorel['GMYO']['Varlik']
  yrmdcAryz.label_gmyoCikis.setText(vrgnkt(gmyoCikis))
  yrmdcAryz.label_gmyoVarlik.setText(vrgnkt(gmyoVarlik))
  if gmyoCikis < 0:
    yrmdcAryz.label_gmyoCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_gmyoCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  havacilikCikis = sektorel['Havacılık']['Cikis']
  havacilikVarlik = sektorel['Havacılık']['Varlik']
  yrmdcAryz.label_havacilikCikis.setText(vrgnkt(havacilikCikis))
  yrmdcAryz.label_havacilikVarlik.setText(vrgnkt(havacilikVarlik))
  if havacilikCikis < 0:
    yrmdcAryz.label_havacilikCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_havacilikCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  holdingCikis = sektorel['Holding']['Cikis']
  holdingVarlik = sektorel['Holding']['Varlik']
  yrmdcAryz.label_holdingCikis.setText(vrgnkt(holdingCikis))
  yrmdcAryz.label_holdingVarlik.setText(vrgnkt(holdingVarlik))
  if holdingCikis < 0:
    yrmdcAryz.label_holdingCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_holdingCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  insaatCikis = sektorel['İnşaat']['Cikis']
  insaatVarlik = sektorel['İnşaat']['Varlik']
  yrmdcAryz.label_insaatCikis.setText(vrgnkt(insaatCikis))
  yrmdcAryz.label_insaatVarlik.setText(vrgnkt(insaatVarlik))
  if insaatCikis < 0:
    yrmdcAryz.label_insaatCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_insaatCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  kagitCikis = sektorel['Kağıt']['Cikis']
  kagitVarlik = sektorel['Kağıt']['Varlik']
  yrmdcAryz.label_kagitCikis.setText(vrgnkt(kagitCikis))
  yrmdcAryz.label_kagitVarlik.setText(vrgnkt(kagitVarlik))
  if kagitCikis < 0:
    yrmdcAryz.label_kagitCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_kagitCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  kimyaCikis = sektorel['Kimya']['Cikis']
  kimyaVarlik = sektorel['Kimya']['Varlik']
  yrmdcAryz.label_kimyaCikis.setText(vrgnkt(kimyaCikis))
  yrmdcAryz.label_kimyaVarlik.setText(vrgnkt(kimyaVarlik))
  if kimyaCikis < 0:
    yrmdcAryz.label_kimyaCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_kimyaCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  madenCikis = sektorel['Maden']['Cikis']
  madenVarlik = sektorel['Maden']['Varlik']
  yrmdcAryz.label_madenVarlik.setText(vrgnkt(madenVarlik))
  yrmdcAryz.label_madenCikis.setText(vrgnkt(madenCikis))
  if madenCikis < 0:
    yrmdcAryz.label_madenCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_madenCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  mkyoCikis = sektorel['MKYO']['Cikis']
  mkyoVarlik = sektorel['MKYO']['Varlik']
  yrmdcAryz.label_mkyoCikis.setText(vrgnkt(mkyoCikis))
  yrmdcAryz.label_mkyoVarlik.setText(vrgnkt(mkyoVarlik))
  if mkyoCikis < 0:
    yrmdcAryz.label_mkyoCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_mkyoCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  otomotivCikis = sektorel['Otomotiv']['Cikis']
  otomotivVarlik = sektorel['Otomotiv']['Varlik']
  yrmdcAryz.label_otoCikis.setText(vrgnkt(otomotivCikis))
  yrmdcAryz.label_otoVarlik.setText(vrgnkt(otomotivVarlik))
  if otomotivCikis < 0:
    yrmdcAryz.label_otoCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_otoCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  petrokimyaCikis = sektorel['Petrokimya']['Cikis']
  petrokimyaVarlik = sektorel['Petrokimya']['Varlik']
  yrmdcAryz.label_petroCikis.setText(vrgnkt(petrokimyaCikis))
  yrmdcAryz.label_petroVarlik.setText(vrgnkt(petrokimyaVarlik))
  if petrokimyaCikis < 0:
    yrmdcAryz.label_petroCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_petroCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  saglikCikis = sektorel['Sağlık']['Cikis']
  saglikVarlik = sektorel['Sağlık']['Varlik']
  yrmdcAryz.label_saglikCikis.setText(vrgnkt(saglikCikis))
  yrmdcAryz.label_saglikVarlik.setText(vrgnkt(saglikVarlik))
  if saglikCikis < 0:
    yrmdcAryz.label_saglikCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_saglikCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  tarimCikis = sektorel['Tarım']['Cikis']
  tarimVarlik = sektorel['Tarım']['Varlik']
  yrmdcAryz.label_tarimCikis.setText(vrgnkt(tarimCikis))
  yrmdcAryz.label_tarimVarlik.setText(vrgnkt(tarimVarlik))
  if tarimCikis < 0:
    yrmdcAryz.label_tarimCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_tarimCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  tasimacilikCikis = sektorel['Taşımacılık']['Cikis']
  tasimacilikVarlik = sektorel['Taşımacılık']['Varlik']
  yrmdcAryz.label_tasimaCikis.setText(vrgnkt(tasimacilikCikis))
  yrmdcAryz.label_tasimaVarlik.setText(vrgnkt(tasimacilikVarlik))
  if tasimacilikCikis < 0:
    yrmdcAryz.label_tasimaCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_tasimaCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  teknolojiCikis = sektorel['Teknoloji']['Cikis']
  teknolojiVarlik = sektorel['Teknoloji']['Varlik']
  yrmdcAryz.label_teknoCikis.setText(vrgnkt(teknolojiCikis))
  yrmdcAryz.label_teknoVarlik.setText(vrgnkt(teknolojiVarlik))
  if teknolojiCikis < 0:
    yrmdcAryz.label_teknoCikis.setStyleSheet("color: rgb(244, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_teknoCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

  tekstilCikis = sektorel['Tekstil']['Cikis']
  tekstilVarlik = sektorel['Tekstil']['Varlik']
  yrmdcAryz.label_tekstilCikis.setText(vrgnkt(tekstilCikis))
  yrmdcAryz.label_tekstilVarlik.setText(vrgnkt(tekstilVarlik))
  if tekstilCikis < 0:
    yrmdcAryz.label_tekstilCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_tekstilCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

#----------   Güniçi Fiyatlar işlevleri

def guniciFiyatlaraGoreDegerleriOlustur():
  global guniciFiyatVerileri
  guniciFiyatVerileri = {}

  # --- Dosyadan oku, güniçindeki fiyatları öğrenirken gerekli işlemleri yap ve "guniciFiyatVerileri" sözlüğünü oluştur.
  workbook = xlrd.open_workbook("../../Güniçi.xlsx")
  worksheet = workbook.sheet_by_index(0)
  strSayisi = (worksheet.nrows)
  for i in range(1, strSayisi):
    islenenSembol = worksheet.cell_value(i, 0)
    sembolGunIciFiyat = worksheet.cell_value(i, 3)
    if islenenSembol == "ALTINS1":
      islenenSembol = "ALTIN"

    vtimlec.execute(f"SELECT SUM(`gerceklesen`), sum(`hacim`) FROM `emirlerim` WHERE `sembol` = '{islenenSembol}' AND `alsat` = 'A' ")
    islemIcinGelenAlimlar = vtimlec.fetchall()
    tplmAlmAdt, tplmAlmHcm = islemIcinGelenAlimlar[0]

    toplamAdet = 0
    toplamAlimAdet = int(tplmAlmAdt)
    toplamAlimHacim = round(tplmAlmHcm / 1000 * 1002, 2)
    toplamAdet += toplamAlimAdet

    vtimlec.execute(f"SELECT SUM(`gerceklesen`), sum(`hacim`) FROM `emirlerim` WHERE `sembol` = '{islenenSembol}' AND `alsat` = 'S' ")
    islemIcinGelenSatimlar = vtimlec.fetchall()
    tplmStmAdt, tplmStmHcm = islemIcinGelenSatimlar[0]
    if tplmStmAdt == None:
      toplamSatimAdet = 0
      toplamSatimHacim = 0
    else:
      toplamSatimAdet = int(tplmStmAdt)
      toplamSatimHacim = round(tplmStmHcm / 1000 * 998, 2)

    toplamAdet -= toplamSatimAdet
    sembolVarlik = round(toplamAdet * sembolGunIciFiyat, 2)
    cikis = round(sembolVarlik + toplamSatimHacim - toplamAlimHacim, 2)
    karZararYuzdesi = round(cikis / toplamAlimHacim * 100, 2)

    guniciFiyatVerileri[islenenSembol] = {'sembolGunIciFiyat': sembolGunIciFiyat, 'cikis': cikis, 'sembolVarlik': sembolVarlik, 'karZararYuzdesi': karZararYuzdesi}
  alt = gunsonuFiyat.get("ALTIN")
  print(guniciFiyatVerileri)
  gncSmbl = yrmdcAryz.label_sembol.text()
  if gncSmbl in ("SELAM", "ALTIN"):
    pass
  else:
    gncfyt = guniciFiyatVerileri[gncSmbl]['sembolGunIciFiyat']
    gncfytYazi = "( " + str(gncfyt) + " )"
    yrmdcAryz.lineEdit_guniciFiyat.setText(gncfytYazi)
    gnccks = guniciFiyatVerileri[gncSmbl]['cikis']
    gnccksYazi = "( " + tl_ekle(vrgnkt(gnccks)) + " )"
    yrmdcAryz.label_guniciCikis.setText(gnccksYazi)
    gncvrlk = guniciFiyatVerileri[gncSmbl]['sembolVarlik']
    gncvrlkYazi = "( " + tl_ekle(vrgnkt(gncvrlk)) + " )"
    yrmdcAryz.label_gunici_SembolVarlik.setText(gncvrlkYazi)
    gnckrzrryzds = guniciFiyatVerileri[gncSmbl]['karZararYuzdesi']
    gnckrzrryzdsYazi = "( %" + str(gnckrzrryzds) + " )"
    yrmdcAryz.label_guniciKarzarar.setText(gnckrzrryzdsYazi)

def guniciFiyatTemizle():
  yrmdcAryz.label_gunici_SembolVarlik.clear()
  yrmdcAryz.label_guniciCikis.clear()
  yrmdcAryz.label_guniciKarzarar.clear()
  yrmdcAryz.lineEdit_guniciFiyat.clear()

#----------  Arz katılımında sembolleri dizme ve alış ekleme fonksiyonları

def ilkSembolGirisi():
  sembol = yrmdcAryz.lineEdit_sembol.text()
  sembolAciklama = yrmdcAryz.textEdit_sembolAciklama.toPlainText()
  sektor = yrmdcAryz.comboBox_sektor.currentText()
  bistx = yrmdcAryz.lineEdit_bistx.text()
  alLot = yrmdcAryz.lineEdit_alinanLot.text()
  alFyt = yrmdcAryz.lineEdit_alimFiyati.text()
  tarih = yrmdcAryz.dateEdit_tarih.date().toPyDate()

  if yrmdcAryz.checkBox_arz.isChecked():
    # Arz mı bölümü tıklı
    if not all((sembol, sembolAciklama, alLot, alFyt)):
      yrmdcAryz.label_eksikalan.setText("Eksik alanları doldurun")
    else:
      alimLot = int(alLot)
      alimFiyati = float(alFyt.replace(",", "."))
      hacim = alimLot * alimFiyati
      vtimlec.execute(f"SELECT * FROM `semboller` WHERE `sembol` = '{sembol}'")
      varmiSorgusu = vtimlec.fetchall()
      varMi = len(varmiSorgusu)
      if varMi == 0:
        try:
          # veritabanına veri ekleme işlemi
          vtimlec.execute(f"INSERT INTO `semboller`(`sembol`, `sembolaciklama`, `sektor`, `bistx`, `arz`) VALUES ('{sembol}','{sembolAciklama}','{sektor}','{bistx}','E')")
          vtimlec.execute(f"INSERT INTO `emirlerim`(`sembol`, `alsat`, `fiyat`, `gerceklesen`, `hacim`, `gun`) VALUES ('{sembol}','A','{alimFiyati}','{alimLot}','{hacim}','{tarih}')")
          baglanti.commit()
          hatayazisi = str(vtimlec.rowcount) + "kayıt girildi."
          yrmdcAryz.label_mysqlhata.setText(hatayazisi)
        except mysql.connector.Error as error:
          # hata durumunda hata mesajını yazdırma
          print("Tabloya eklenemedi {}".format(error))
        baglanti.commit()

      else:
        yrmdcAryz.label_mysqlhata.setText("Sembol zaten oluşturulmuş.")

      print("değişkenler tam")
  else:
    print("Arz Değil")
    if not all((sembol, sembolAciklama)):
      yrmdcAryz.label_eksikalan.setText("Eksik alanları doldurun")
    else:
      vtimlec.execute(f"INSERT INTO `semboller`(`sembol`, `sembolaciklama`, `sektor`, `bistx`, `arz`) VALUES ('{sembol}','{sembolAciklama}','{sektor}','{bistx}','H')")
      baglanti.commit()

def arzYadaDegil(state):

  yrmdcAryz.lineEdit_alinanLot.setReadOnly(state != QtCore.Qt.Checked)
  yrmdcAryz.lineEdit_alimFiyati.setReadOnly(state != QtCore.Qt.Checked)

yrmdcAryz.checkBox_arz.stateChanged.connect(arzYadaDegil)

def komboyaSektorleriDiz():

  vtimlec.execute("SELECT `sektor` FROM `sektorler` ORDER BY `sektorler`.`sektor` ASC ")
  sektorGelenler = vtimlec.fetchall()
  #print(sektorGelenler)
  for sm in sektorGelenler:
    yrmdcAryz.comboBox_sektor.addItem(sm[0])

#----------   kzModul işlevleri

def seciliSembolIslemleri(item):

  sembol = item.text()
  # -- labelların doldurulması.........
  yrmdcAryz.label_sembol.setText(sembol)
  toplamAlimAdet = borsaDurumVerileri[sembol]['alimadet']
  yrmdcAryz.label_alimAdet.setText(str(toplamAlimAdet))
  satimAdet = borsaDurumVerileri[sembol]['satimadet']
  yrmdcAryz.label_satimAdet.setText(str(satimAdet))
  toplamAdet = borsaDurumVerileri[sembol]['toplamadet']
  toplamAdetYazisi = 'Toplam Adet : <b>' + str(toplamAdet) + '</b>'
  yrmdcAryz.label_toplamAdet.setText(toplamAdetYazisi)
  alimOrtalamasi = borsaDurumVerileri[sembol]['maliyet']
  yrmdcAryz.label_alimOrtalama.setText(str(alimOrtalamasi))
  satimOrtalamasi = borsaDurumVerileri[sembol]['satimortalamasi']
  yrmdcAryz.label_satimOrtalama.setText(str(satimOrtalamasi))
  fiyat = borsaDurumVerileri[sembol]['fiyat']
  yrmdcAryz.lineEdit_guncelFiyat.setText(vrgnkt(fiyat))
  gerceklenen = borsaDurumVerileri[sembol]['gerceklenen']
  cikis = borsaDurumVerileri[sembol]['cikis']
  sembolVarlik = borsaDurumVerileri[sembol]['deger']
  karZararYuzdesi = borsaDurumVerileri[sembol]['yzkz']

  alimVerisiIsleme(sembol)
  satimVerisiIsleme(sembol)

  varlik_yazisi = tl_ekle(vrgnkt(sembolVarlik))
  yrmdcAryz.label_sembolVarlik.setText(varlik_yazisi)

  gerceklenen_yazisi = tl_ekle(vrgnkt(gerceklenen))

  if gerceklenen < 0:
    yrmdcAryz.label_gerceklenen.setStyleSheet("color: rgb(244, 0, 0)")
  else:
    yrmdcAryz.label_gerceklenen.setStyleSheet("color: black")
  yrmdcAryz.label_gerceklenen.setText(gerceklenen_yazisi)

  cikis_yazisi = tl_ekle(vrgnkt(cikis))

  if cikis < 0:
    yrmdcAryz.label_cikis.setStyleSheet("color: rgb(244, 0, 0)")
  else:
    yrmdcAryz.label_cikis.setStyleSheet("color: black")
  yrmdcAryz.label_cikis.setText(cikis_yazisi)

  if karZararYuzdesi < 0:
    yrmdcAryz.label_karzarar.setStyleSheet("color: rgb(244, 0, 0)")
  else:
    yrmdcAryz.label_karzarar.setStyleSheet("color: black")
  kzyazisi = '% <b>' + str(karZararYuzdesi) + '</b>'
  yrmdcAryz.label_karzarar.setText(kzyazisi)
  yrmdcAryz.lineEdit_guncelFiyat.setStyleSheet("font-weight:bold; background-color: rgb(205, 194, 159);")
  yrmdcAryz.gnclfyt.setText("Güncel Fiyat :")

  if guniciFiyatVerileri:

    if sembol == "ALTIN":
      yrmdcAryz.lineEdit_guniciFiyat.clear()
      yrmdcAryz.label_guniciCikis.clear()
      yrmdcAryz.label_gunici_SembolVarlik.clear()
      yrmdcAryz.label_guniciKarzarar.clear()
    else:
      gncfyt = guniciFiyatVerileri[sembol]['sembolGunIciFiyat']
      gncfytYazi = "( " + str(gncfyt) + " )"
      yrmdcAryz.lineEdit_guniciFiyat.setText(gncfytYazi)
      gnccks = guniciFiyatVerileri[sembol]['cikis']
      gnccksYazi = "( " + tl_ekle(vrgnkt(gnccks)) + " )"
      yrmdcAryz.label_guniciCikis.setText(gnccksYazi)
      gncvrlk = guniciFiyatVerileri[sembol]['sembolVarlik']
      gncvrlkYazi = "( " + tl_ekle(vrgnkt(gncvrlk)) + " )"
      yrmdcAryz.label_gunici_SembolVarlik.setText(gncvrlkYazi)
      gnckrzrryzds = guniciFiyatVerileri[sembol]['karZararYuzdesi']
      gnckrzrryzdsYazi = "( %" + str(gnckrzrryzds) + " )"
      yrmdcAryz.label_guniciKarzarar.setText(gnckrzrryzdsYazi)

def alimVerisiIsleme(gel):
  vtimlec.execute(f"SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = '{gel}' AND `alsat` = 'A' ORDER BY `emirlerim`.`gun` ASC")
  islemIcinGelenAlimlar = vtimlec.fetchall()

  alimVerisiDizeye = []
  for satir in islemIcinGelenAlimlar:
    hacim = round(satir[3] / 1000 * 1002, 2)
    tarih = trh(satir[0])
    adet = int(satir[1])
    fiyat = vrgnkt(satir[2])
    eder = vrgnkt(hacim)
    # Düzenlenmiş veriyi listeye ekle
    alimVerisiDizeye.append([tarih, adet, fiyat, eder])
  # QTableWidget nesnesine veriyi yerleştir
  yrmdcAryz.tableWidget_alim.clear()
  yrmdcAryz.tableWidget_alim.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Hacim'])
  yrmdcAryz.tableWidget_alim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  yrmdcAryz.tableWidget_alim.horizontalHeader().setStyleSheet("font-weight: bold;")
  yrmdcAryz.tableWidget_alim.setRowCount(len(islemIcinGelenAlimlar))
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
      yrmdcAryz.tableWidget_alim.setItem(satirIndeks, sutunIndeks, hucre)

def satimVerisiIsleme(gel):
  vtimlec.execute(f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{gel}' AND `alsat` = 'S' ORDER BY `emirlerim`.`gun` ASC")
  islemIcinGelenSatimlar = vtimlec.fetchall()
  if len(islemIcinGelenSatimlar) == 0:
    satimsizSembolIslemleri()
  else:
    # Verileri işleme
    satimVerisiDizeye = []
    for satir in islemIcinGelenSatimlar:
      # Toplam alım ve hacimi hesaplama - Dizeye ekleme esnasında yan işlem

      hacim = round(satir[2] / 1000 * 998, 2)
      tarih = trh(satir[3])
      adet = int(satir[0])
      fiyat = vrgnkt(satir[1])
      eder = vrgnkt(hacim)

      # Düzenlenmiş veriyi listeye ekle
      satimVerisiDizeye.append([adet, fiyat, eder, tarih])

    # QTableWidget nesnesine veriyi yerleştir
    yrmdcAryz.tableWidget_satim.clear()
    yrmdcAryz.tableWidget_satim.setHorizontalHeaderLabels(['Adet', 'Fiyat', 'Hacim', 'Tarih'])
    yrmdcAryz.tableWidget_satim.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    yrmdcAryz.tableWidget_satim.horizontalHeader().setStyleSheet("font-weight: bold;")
    yrmdcAryz.tableWidget_satim.setRowCount(len(islemIcinGelenSatimlar))
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
        yrmdcAryz.tableWidget_satim.setItem(satirIndeks, sutunIndeks, hucre)

def kzEkranTemizle():
  yrmdcAryz.label_alimAdet.clear()
  yrmdcAryz.label_alimOrtalama.clear()
  yrmdcAryz.label_cikis.clear()
  yrmdcAryz.label_gerceklenen.clear()
  yrmdcAryz.label_karzarar.clear()
  yrmdcAryz.label_satimAdet.clear()
  yrmdcAryz.label_satimOrtalama.clear()
  yrmdcAryz.label_sembolVarlik.setText("Sembol seçin")
  yrmdcAryz.label_toplamAdet.clear()
  yrmdcAryz.lineEdit_guncelFiyat.clear()
  yrmdcAryz.lineEdit_sembol.setText("Selam")
  yrmdcAryz.gnclfyt.clear()

def satimsizSembolIslemleri():

  # Alım ve satım tablolarını boşalt
  yrmdcAryz.tableWidget_satim.clear()
  yrmdcAryz.tableWidget_satim.setHorizontalHeaderLabels(['Adet', 'Fiyat', 'Eder', 'Tarih'])
  yrmdcAryz.tableWidget_satim.setRowCount(0)
  yrmdcAryz.label_satimAdet.setText("0")
  yrmdcAryz.label_satimOrtalama.setText("0")
  yrmdcAryz.label_gerceklenen.setText("0")

def tarihAraligiSecimi():
  alimUzun = 0
  satimUzun = 0
  alimBilgiMesaj = ""
  alimText = ""
  secilenAlimSatirlari = yrmdcAryz.tableWidget_alim.selectedItems()
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
                <p style="font-size:14pt; color:green;">Toplam Adet : <b>' + str(round(alimAdet)) + '</b></p> \
                <p style="font-size:14pt; color:green;">Alım Ortalaması : <b>' + str(ortalamaA) + '</b></p> \
                <p style="font-size:14pt; color:green;">Toplam Hacim: <b>' + vrgnkt(alimHacim) + '</b></p> '
  else:
    alimText = '<p style="font-size:13pt;">Alım tarih aralığı seçmediniz.</p>'

  satimText = '<p style="font-size:14pt;">Satım tarih aralığı seçmediniz.</p>'
  secilenSatimSatirlari = yrmdcAryz.tableWidget_satim.selectedItems()
  satimUzun = len(secilenSatimSatirlari)

  if satimUzun > 0:
    ilkStarih = secilenSatimSatirlari[3].text()
    sonStarih = secilenSatimSatirlari[satimUzun-1].text()
    satimAdet = 0
    satimHacim = 0
    for index in range(0, satimUzun, 4):
      satimAdet += geriCevir(secilenSatimSatirlari[index].text())
      satimHacim += geriCevir(secilenSatimSatirlari[index + 2].text())
    ortalamaS = round(satimHacim / satimAdet, 2)
    satimText = '<p style = "font-size:14pt; color:red;" > ' + ilkStarih + ' - - - - - ' + sonStarih + ' </p>\
                <p style = "font-size:14pt; color:red;" > Toplam Adet: <b>' + str(round(satimAdet)) + '</b> </p> \
                <p style = "font-size:14pt; color:red;" > Satım Ortalaması: <b>' + str(ortalamaS) + '</b> </p> \
                <p style = "font-size:14pt; color:red;" > Toplam Hacim: <b>' + vrgnkt(satimHacim) + '</b> </p>'
  else:
    satimText = '<p style="font-size:13pt;">Satım tarih aralığı seçmediniz.</p>'
  sembolFiyat = yrmdcAryz.lineEdit_guncelFiyat.text()
  fiyatiYaz = '<p style = "font-size:16pt; font-weight:bold;" > <center>Güncel Fiyat : ' + str(sembolFiyat) +  ' </center></p>'
  alimBilgiMesaj = alimText + fiyatiYaz + satimText

  sembol = yrmdcAryz.label_sembol.text()
  tarihAraligiBilgi = QMessageBox()
  tarihAraligiBilgi.setWindowTitle(sembol)
  tarihAraligiBilgi.setText(alimBilgiMesaj)

  tarihAraligiBilgi.setStandardButtons(QMessageBox.Save |QMessageBox.Ok)

  save_button = tarihAraligiBilgi.button(QMessageBox.Save)
  save_button.setText("Ekle")
  save_button.clicked.connect(ekle)

  tarihAraligiBilgi.exec_()

yrmdcAryz.pushButton_bas.clicked.connect(tarihAraligiSecimi)

def ekle():
  print("ekle")

#----------   Gün içi al-sat hesaplayıcı İşlevleri

# emirlerimi okuyacak. alım satımları dizecek, alım satım hesaplamaları yaparak fikir vericek....

def emirleriOku():
  global guniciAlimEmirlerim
  guniciAlimEmirlerim = {}
  emirlerim = xlrd.open_workbook("../../Emirlerim.xlsx")
  worksheet = emirlerim.sheet_by_index(0)
  satirsayisi = (worksheet.nrows)

  for i in range(1, satirsayisi):
    sql = "INSERT INTO emirlerim (sembol, alsat, fiyat, gerceklesen, hacim, saat) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (
    worksheet.cell_value(i, 0), worksheet.cell_value(i, 1), worksheet.cell_value(i, 2), worksheet.cell_value(i, 4),
    worksheet.cell_value(i, 6), worksheet.cell_value(i, 7))
    vtimlec.execute(sql, val)
  try:
    baglanti.commit()
    emirhatasiz = str(vtimlec.rowcount) + "kayıt eklendi."
    yrmdcAryz.label_ekleEmirMesaj.setText(emirhatasiz)
  except mysql.connector.Error as error:
    emirhata = "Tabloya eklenemedi {}".format(error)
    yrmdcAryz.label_ekleEmirMesaj.setText(emirhata)
    print("Tabloya eklenemedi {}".format(error))

def emirleriDiz():
  print("hebe")

def ortalamaBul():
  print("hebe")

#----------   Borsa Çıkılmışlar İşlevleri

def cikilmisSembolIslemleri(item):
  sembol = item.text()
  cikilmisAlimIsleme(sembol)
  cikilmisSatimIsleme(sembol)
  cikilmisDegerleriYaz(sembol)

def cikilmisDegerleriYaz(gel):
  yrmdcAryz.label_cikilmisSembol.clear()
  yrmdcAryz.label_cikilmisCikis.clear()
  yrmdcAryz.label_cikilmisKZ.clear()
  yrmdcAryz.label_cikilmisSembol.setText(gel)
  cikis = cikilmisKagitlar[gel]['cikis']
  cikisYazisi = "Çıkış : " + str(cikis)
  yzkz = cikilmisKagitlar[gel]['yzkz']
  yzkzYazisi = "% " + str(yzkz)
  yrmdcAryz.label_cikilmisCikis.setText(cikisYazisi)
  if cikis < 0:
    yrmdcAryz.label_cikilmisCikis.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_cikilmisCikis.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")
  yrmdcAryz.label_cikilmisKZ.setText(yzkzYazisi)
  if yzkz < 0:
    yrmdcAryz.label_cikilmisKZ.setStyleSheet("color: rgb(214, 1, 1);font: 12pt 'Noto Sans';font-weight: bold")
  else:
    yrmdcAryz.label_cikilmisKZ.setStyleSheet("color: rgb(0, 0, 0);font: 12pt 'Noto Sans';font-weight: bold")

def cikilmisAlimIsleme(gel):
  vtimlec.execute(f"SELECT `gun`, `gerceklesen`, `fiyat`, `hacim` FROM `emirlerim` WHERE `sembol` = '{gel}' AND `alsat` = 'A' ORDER BY `emirlerim`.`gun` ASC")
  islemIcinGelenAlimlar = vtimlec.fetchall()

  alimVerisiDizeye = []
  for satir in islemIcinGelenAlimlar:
    hacim = round(satir[3] / 1000 * 1002, 2)
    tarih = trh(satir[0])
    adet = int(satir[1])
    fiyat = vrgnkt(satir[2])
    eder = vrgnkt(hacim)
    # Düzenlenmiş veriyi listeye ekle
    alimVerisiDizeye.append([tarih, adet, fiyat, eder])
  # QTableWidget nesnesine veriyi yerleştir
  yrmdcAryz.tableWidget_alim_cikilmis.clear()
  yrmdcAryz.tableWidget_alim_cikilmis.setHorizontalHeaderLabels(['Tarih', 'Adet', 'Fiyat', 'Hacim'])
  yrmdcAryz.tableWidget_alim_cikilmis.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
  yrmdcAryz.tableWidget_alim_cikilmis.horizontalHeader().setStyleSheet("font-weight: bold;")
  yrmdcAryz.tableWidget_alim_cikilmis.setRowCount(len(islemIcinGelenAlimlar))
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
      yrmdcAryz.tableWidget_alim_cikilmis.setItem(satirIndeks, sutunIndeks, hucre)

def cikilmisSatimIsleme(gel):

  vtimlec.execute(f"SELECT `gerceklesen`, `fiyat`, `hacim`, `gun` FROM `emirlerim` WHERE `sembol` = '{gel}' AND `alsat` = 'S' ORDER BY `emirlerim`.`gun` ASC")
  islemIcinGelenSatimlar = vtimlec.fetchall()
  if len(islemIcinGelenSatimlar) == 0:
    satimsizSembolIslemleri()
  else:
    # Verileri işleme
    satimVerisiDizeye = []
    for satir in islemIcinGelenSatimlar:
      # Toplam alım ve hacimi hesaplama - Dizeye ekleme esnasında yan işlem

      hacim = round(satir[2] / 1000 * 998, 2)
      tarih = trh(satir[3])
      adet = int(satir[0])
      fiyat = vrgnkt(satir[1])
      eder = vrgnkt(hacim)

      # Düzenlenmiş veriyi listeye ekle
      satimVerisiDizeye.append([adet, fiyat, eder, tarih])

    # QTableWidget nesnesine veriyi yerleştir
    yrmdcAryz.tableWidget_satim_cikilmis.clear()
    yrmdcAryz.tableWidget_satim_cikilmis.setHorizontalHeaderLabels(['Adet', 'Fiyat', 'Hacim', 'Tarih'])
    yrmdcAryz.tableWidget_satim_cikilmis.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    yrmdcAryz.tableWidget_satim_cikilmis.horizontalHeader().setStyleSheet("font-weight: bold;")
    yrmdcAryz.tableWidget_satim_cikilmis.setRowCount(len(islemIcinGelenSatimlar))
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
        yrmdcAryz.tableWidget_satim_cikilmis.setItem(satirIndeks, sutunIndeks, hucre)

#----------   Gün Sonu emirlerim ve pozisyonlarım ekleme işlevleri

def ekleemirlerim():
  emirlerim = xlrd.open_workbook("../../Emirlerim.xlsx")
  worksheet = emirlerim.sheet_by_index(0)
  satirsayisi = (worksheet.nrows)

  for i in range(1, satirsayisi):
    sql = "INSERT INTO emirlerim (sembol, alsat, fiyat, gerceklesen, hacim, saat) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (worksheet.cell_value(i, 0), worksheet.cell_value(i, 1), worksheet.cell_value(i, 2), worksheet.cell_value(i, 4), worksheet.cell_value(i, 6), worksheet.cell_value(i, 7))
    vtimlec.execute(sql, val)
  try:
    baglanti.commit()
    emirhatasiz = str(vtimlec.rowcount) + "kayıt eklendi."
    yrmdcAryz.label_ekleEmirMesaj.setText(emirhatasiz)
  except mysql.connector.Error as error:
    emirhata = "Tabloya eklenemedi {}".format(error)
    yrmdcAryz.label_ekleEmirMesaj.setText(emirhata)
    print("Tabloya eklenemedi {}".format(error))

def eklepozisyonlarim():
  workbook = xlrd.open_workbook("../../Pozisyonlarım.xlsx")
  worksheet = workbook.sheet_by_index(0)
  satirsayisi = (worksheet.nrows)
  for i in range(1, satirsayisi):
    yuzde = ((worksheet.cell_value(i, 3) / worksheet.cell_value(i, 2)) - 1) * 100
    sql = "INSERT INTO gunluksipsak (sembol, adet, maliyet, fiyat, topkarzarar, deger, karzarar) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (worksheet.cell_value(i, 0), worksheet.cell_value(i, 1), worksheet.cell_value(i, 2), worksheet.cell_value(i, 3), worksheet.cell_value(i, 4), worksheet.cell_value(i, 5), yuzde)
    vtimlec.execute(sql, val)
  try:
    baglanti.commit()
    pozeklesayisi = str(vtimlec.rowcount) + "kayıt eklendi."
    yrmdcAryz.label_eklePzsynNesaj.setText(pozeklesayisi)
  except mysql.connector.Error as error:
    pozhata = "Tabloya eklenemedi {}".format(error)
    yrmdcAryz.label_eklePzsynNesaj.setText(pozhata)

#yrmdcAryz.pushButton_gunSonuEkle.clicked.connect(lambda: (ekleemirlerim(), eklepozisyonlarim()))
yrmdcAryz.pushButton_posizyonEkle.clicked.connect(eklepozisyonlarim)
yrmdcAryz.pushButton_emirlerimEkle.clicked.connect(ekleemirlerim)

#----------   Bedelsiz sermaye arttırımı işlemleri

def bedelsizkombosu():
  vtimlec.execute("SELECT `sembol` FROM `semboller` ORDER BY `semboller`.`sembol` ASC ")
  sembolGelenler = vtimlec.fetchall()
  for sm in sembolGelenler:
    yrmdcAryz.comboBox_bedelsiz.addItem(sm[0])

def bedelsizguncelle():
  secsembol = yrmdcAryz.comboBox_bedelsiz.currentText()
  bedelsizOran = yrmdcAryz.lineEdit_bedelsizOran.text()
  bedelsizOranDuzenle = float(bedelsizOran.replace(",", "."))
  oran = (bedelsizOranDuzenle + 100) / 100
  print(oran)

  vtimlec.execute(f"SELECT * FROM `emirlerim` WHERE `sembol` = '{secsembol}'")
  islemGelenler = vtimlec.fetchall()
  for gl in islemGelenler:
    fiyatOran = round(gl[3] / oran, 3)
    adetOran = round(gl[4] * oran, 2)
    #fiyatOran = round(gl[3] * oran, 3)
    #adetOran = round(gl[4] / oran, 2)

    print("Fiyat Oran = ", fiyatOran)

    print("Adet Oran = ", adetOran)
    vtimlec.execute(f"UPDATE `emirlerim` SET `fiyat` = '{fiyatOran}', `gerceklesen` = '{adetOran}' WHERE `emirlerim`.`emirlerimid` = {gl[0]}")
    print("id = ", gl[0])
  baglanti.commit()

yrmdcAryz.pushButton_bedelsiz.clicked.connect(bedelsizguncelle)

#----------   Borsa Durum Excele aktarma İşlevleri

def excelDosyasiOlusturma(tableWidget):
  today = datetime.datetime.now().strftime("%Y-%m-%d")
  file_path = f"/home/firat/Yatırım/BorsaDurum_{today}.xls"
  workbook = Workbook()
  worksheet = workbook.add_sheet("BorsaDurum")

  # Başlıkları ekleme
  headers = ['Sembol', 'Alım Adet', 'Satım Adet', 'Adet', 'Maliyet', 'Günc. Fiyat', 'Satım Ort.', 'Gerçeklenen',
             'Çıkış', 'Değer', '% K / Z', '% Pay']
  for col, header in enumerate(headers):
    worksheet.write(0, col, header)

  # TableWidget içeriğini ekleme
  for row in range(tableWidget.rowCount()):
    for col in range(tableWidget.columnCount()):
      item = tableWidget.item(row, col)
      if item is not None:
        text = item.text()
        if col in [4, 5, 6, 7, 8, 9]:
          text = deneyselcevir(text)
        worksheet.write(row + 1, col, text)

  try:
    workbook.save(file_path)
    print(f"Excel dosyası başarıyla oluşturuldu: {file_path}")
  except Exception as e:
    print(f"Hata oluştu: {e}")

def exceleAktar():
  excelDosyasiOlusturma(yrmdcAryz.tableWidget_borsaDurum)

yrmdcAryz.pushButton_excelAktar.clicked.connect(exceleAktar)
#----------   Borsa Durum başlangıç çalışanları
yrmdcAryz.pushButton_altnFytGnclle.clicked.connect(altnFyt)
yrmdcAryz.pushButton_toplamKZ.clicked.connect(karzararHesapla)
yrmdcAryz.pushButton_ekle.clicked.connect(ilkSembolGirisi)
komboyaSektorleriDiz()
#----------    kzModul başlangıç çalışanları
kzEkranTemizle()
yrmdcAryz.listWidget_semboller.itemClicked.connect(seciliSembolIslemleri)
yrmdcAryz.pushButton_fiyatGuncelle.clicked.connect(guniciFiyatlaraGoreDegerleriOlustur)

#----------   Güniçi Fiyatlar çalışanları
guniciFiyatTemizle()

#----------    Borsa Çıkılmışlar çalışanları

yrmdcAryz.listWidget_cikilmisSemboller.itemClicked.connect(cikilmisSembolIslemleri)

#----------    bedelsiz başlangıç çalışanları
bedelsizkombosu()

#-----------------------------------------------
yardimciAnaPencere.show()
sys.exit(Yardimci.exec_())

### yeşil
### #eff7f1
### kırmızı #ffe9e6
### sarı #fef7e2
### #d3ecf9

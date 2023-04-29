
import mysql.connector
import xlrd


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
varlik = 0

#-------------------Fonksiyon tanımlamaları

def vrgnkt(gel):
  don = '{:,.2f}'.format(gel).replace(",", "X").replace(".", ",").replace("X", ".")
  return  don

def geriCevir(gel):
  don = float(gel.replace(".", "").replace(",", "."))
  return don

def trh(gel):
  don = gel.strftime("%d.%m.%Y")
  return don

def tl_ekle(gel):
  don = "₺ " + gel
  return don

#---------------------------------------------------------------------------------

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

gunsonuFiyatlariOlustur()

def sembolunFiyatiniOgren(sembol):
  # her sembol için gunsonuFiyat dict inden fiyat bilgisini alan fonksiyon
  dictebak = gunsonuFiyat.get(sembol)
  if dictebak == None:
    sembolFiyat = 0
  else:
    sembolFiyat = dictebak
  return sembolFiyat

#--------------------------------------------------------------------------------

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
  #for sembl in sembolGelenler:
    #anahtar = sembl[0]

    #deger = yuzdePay[anahtar]['yzpay']
    #print(deger)
    #borsaDurumVerileri[sembl]['yzpay'] = deger

def yuzdePayGuncelle():
  for anahtar in yuzdePay:
    yzpay = yuzdePay[anahtar]['yzpay']
    borsaDurumVerileri[anahtar]['yzpay'] = round(yzpay * 100 / varlik ,3)


borsaDurumSozluguOlustur()
print(borsaDurumVerileri)
print(yuzdePay)
yuzdePayGuncelle()
print(vrgnkt(varlik))
print(borsaDurumVerileri)



#-------------------------Bu tabloya ekleme döngüsü için ama daha qwidget çözülmedi------------------------------

class MyTable(QWidget):
  def __init__(self, borsaDurumVerileri):
    super().__init__()
    self.title = 'Borsa Durum Verileri'
    self.left = 0
    self.top = 0
    self.width = 500
    self.height = 300
    self.borsaDurumVerileri = borsaDurumVerileri
    self.initUI()

  def initUI(self):
    self.setWindowTitle(self.title)
    self.setGeometry(self.left, self.top, self.width, self.height)
    self.createTable()

    # Add box layout, add table to box layout and add box layout to widget
    self.layout = QVBoxLayout()
    self.layout.addWidget(self.tableWidget)
    self.setLayout(self.layout)

  def createTable(self):
    # Create table
    self.tableWidget = QTableWidget()
    self.tableWidget.setRowCount(len(self.borsaDurumVerileri))
    self.tableWidget.setColumnCount(11)
    self.tableWidget.setHorizontalHeaderLabels(
      ['Alım Adet', 'Satım Adet', 'Toplam Adet', 'Maliyet', 'Fiyat', 'Gerçekleşen', 'Çıkış', 'K/Z', 'Değer', 'YZKZ',
       'YZPay'])

    # Loop through the nested dictionary and add items to the table widget
    row = 0
    for key, values in self.borsaDurumVerileri.items():
      self.tableWidget.setItem(row, 0, QTableWidgetItem(str(values['alimadet'])))
      self.tableWidget.setItem(row, 1, QTableWidgetItem(str(values['satimadet'])))
      self.tableWidget.setItem(row, 2, QTableWidgetItem(str(values['toplamadet'])))
      self.tableWidget.setItem(row, 3, QTableWidgetItem(str(values['maliyet'])))
      self.tableWidget.setItem(row, 4, QTableWidgetItem(str(values['fiyat'])))
      self.tableWidget.setItem(row, 5, QTableWidgetItem(str(values['gerceklenen'])))
      self.tableWidget.setItem(row, 6, QTableWidgetItem(str(values['cikis'])))
      self.tableWidget.setItem(row, 7, QTableWidgetItem(str(values['kz'])))
      self.tableWidget.setItem(row, 8, QTableWidgetItem(str(values['deger'])))
      self.tableWidget.setItem(row, 9, QTableWidgetItem(str(values['yzkz'])))
      self.tableWidget.setItem(row, 10, QTableWidgetItem(str(values['yzpay'])))

      row += 1











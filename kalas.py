#-------------------Başlangıç Değişkenleri

#-------------------Fonksiyon tanımlamaları
#-------------Sembol Ekleme--Arz filan




from PyQt5 import QtWidgets, QtGui, QtCore


class CustomTabWidget(Ui_TabWidget):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # burada istediğiniz değişiklikleri yapabilirsiniz
    for label in self.findChildren(QtWidgets.QLabel):
      if float(label.text()) > 0:
        label.setStyleSheet("color: red;")
      elif float(label.text()) < 0:
        label.setStyleSheet("color: black;")




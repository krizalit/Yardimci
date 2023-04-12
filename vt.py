import mysql.connector

def baglanti_olustur(self):
    self.baglanti = mysql.connector.connect(
        host="localhost",
        user="firat",
        password="eben",
        database="yatirim"
    )
    self.vtimlec = self.baglanti.cursor()
import sqlite3 #pythonda veri tabanı oluşturmak için kullanılır.

def veritabani(): #SQLite veritabanı dosyası oluşturur ve içine bir tablo tanımlar
    conn = sqlite3.connect('yuz_tanima.db') #Belirtilen dosya adını kullanarak bir veritabanına bağlanır. Eğer dosya yoksa keni oluşturur.
    c = conn.cursor() #Veritabanına sql komutları göndermek için kullanılan bir cursor (imleç) nesnesi oluşturur. c harfi nesneyi temsil eder.
    c.execute('''
        CREATE TABLE IF NOT EXISTS yuzler (
            id INTEGER PRIMARY KEY,
            isim TEXT NOT NULL,
            yuz_kodlari BLOB NOT NULL
        )
    ''')
   
    #7.satırda belirtilen kod eğer tablo varsa tablo oluşturmaz. Yoksa oluşturur
    #8.satırdaki birincil anahtar ID aynı isimdeki insanların birbirine karışmasını önler.
    #9.satırdaki kod yüz tanıma verilerini saklamak için kullanılır.BLOB genelde resim, video veya şifrelenmiş veri gibi dosyaları saklar. Boş geçilmez kısım.
    
    conn.commit() #Yapılan değişiklikleri kalıcı olarak kaydeder.
    conn.close() #veritabanı bağlantısını kapatır.

if __name__ == "__main__": #kodun doğrudan mı yoksa başka bir dosya tarafından mı çağıralacağını kontrol eder.
    veritabani() #veritabanı fonksiyonunu çalıştırır.
    print("Veritabanı oluşturuldu.")

import sqlite3 #Veritabanı için kullanılır
import pickle #Verileri binary formatına dönüştürür ve saklar.
import face_recognition # type: ignore #Yüz tanıma ve kodlama için kullanılan bir kütüphane

def yuz_ekle(isim, yuz_kodlari): #
    conn = sqlite3.connect('yuz_tanima.db') #diğer dosyadaki yuz_tanima.db adlı veri tabanına bağlanır.
    c = conn.cursor() #Veritabanına sql komutları göndermek için kullanılan bir cursor (imleç) nesnesi oluşturur. c harfi nesneyi temsil eder.
    yuz_kodlari_p = pickle.dumps(yuz_kodlari)  #yüzün sayısal özelliklerini içerir. O özellikler pickle ile binary hale getirilir.
    c.execute('INSERT INTO yuzler (isim, yuz_kodlari) VALUES (?, ?)', (isim, yuz_kodlari_p)) #SQL komutlarıyla tabloya yeni bir yüz eklenir.
    conn.commit() #Yapılan değişiklikleri veri tabanına kalıcı olarak kaydeder.
    conn.close()

def yeni_yuz_ekle(goruntu_yolu, isim):
    goruntu = face_recognition.load_image_file(goruntu_yolu) #Yüzün bulunduğu dosyanı0n tam yolunu içerir.
    yuz_kodlari = face_recognition.face_encodings(goruntu) #Yüzün sayısal özelliklerini çıkarır. Görüntüde birden fazla yüz varsa her biri için kodlama döndürür. 
    #Eğer yüz yoksa liste boş kalır.

    if yuz_kodlari:
        yuz_ekle(isim, yuz_kodlari[0]) #İlk yüz kodlaması 0 seçilir ve yuz_ekle ile veritabanına kaydedilir.
        print(f"{isim} eklendi.")
    else:
        print(f"{goruntu_yolu} dosyasında yüz bulunamadı.") #Eğer yüz bulunamazsa hata mesajı yazddırır.

if __name__ == "__main__":
    # Örnek yüz ekleme (bu kısım bir kere çalıştırılmalı ve ardından yorum satırına alınmalı)
    yeni_yuz_ekle("C:/Users/gamze/Desktop/Yüz Tanıma Gelişmiş Versiyon/Yüz Tanıma/Fotoğraflar/Gamze.jpg", "Gamze")
    yeni_yuz_ekle("C:/Users/gamze/Desktop/Yüz Tanıma Gelişmiş Versiyon/Yüz Tanıma/Fotoğraflar/Ennur.jpg", "Ennur")
    yeni_yuz_ekle("C:/Users/gamze/Desktop/Yüz Tanıma Gelişmiş Versiyon/Yüz Tanıma/Fotoğraflar/Aslan.jpg", "Aslan")
    yeni_yuz_ekle("C:/Users/gamze/Desktop/Yüz Tanıma Gelişmiş Versiyon/Yüz Tanıma/Fotoğraflar/Esat.jpg", "Esat")
    yeni_yuz_ekle("C:/Users/gamze/Desktop/Yüz Tanıma Gelişmiş Versiyon/Yüz Tanıma/Fotoğraflar/Ali Kemal.jpg", "Ali Kemal")

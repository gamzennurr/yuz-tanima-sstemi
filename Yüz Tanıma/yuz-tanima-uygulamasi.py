import sys #Uygulamanın sistemle iletişim kurmasını sağlar
import sqlite3
import pickle
import face_recognition
import cv2 #Görrüntü işleme ve kameradan veri alma için kullanılır.
import pyttsx3 #Sesli mesajlar için kullanılır.
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt #PyQt5 kullanıcı arayüzünü oluşturmak için kullanılır.

class YuzTanimlamaApp(QWidget): #Yüz tanıma uygulamasının ana penceresini oluşturur.
    def __init__(self): #Yapıcı metot
        super().__init__()
        self.setWindowTitle("Yüz Tanıma Uygulaması") #Pencerenin başlığında ne yazacağını belirtir.
        self.setGeometry(100, 100, 800, 600) #Pencerenin boyutlarını oluşturur.
        
        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 640, 480)

        self.start_button = QPushButton("Başlat", self)
        self.start_button.setGeometry(10, 500, 100, 30)
        self.start_button.clicked.connect(self.baslat)

        self.stop_button = QPushButton("Durdur", self)
        self.stop_button.setGeometry(120, 500, 100, 30)
        self.stop_button.clicked.connect(self.durdur)

        self.register_button = QPushButton("Yüz Kaydet", self)
        self.register_button.setGeometry(230, 500, 100, 30)
        self.register_button.clicked.connect(self.kayit_ekrani_ac)

        self.bilinen_yuz_kodlari, self.bilinen_yuz_isimleri = self.yuzleri_getir() #Veritabanındaki yüz kodlarını ve isimlerini yükler.

        self.video_kamerasi = cv2.VideoCapture(0)
        self.timer = QTimer(self) #yüz tanıma işleminin düzenli olarak çalışmasını sağlar.
        self.timer.timeout.connect(self.yuzleri_tani) #video akışındaki yüzleri her 30ms de tanımaya çalışır.
        self.timer.setInterval(30) #zamanlayıcının tetiklenme aralığını belirler.

        self.engine = pyttsx3.init() #py de metini sese dönüştürmek için kullanılır.
        self.son_tanimlanan_isim = None #Aynı kişi tekrar tanındığında gereksiz sesli bildirim yapmasını engllemek için kullanılır.

    def yuzleri_getir(self): #
        conn = sqlite3.connect('yuz_tanima.db') #SQL veritabanına bağlanır
        c = conn.cursor() #Veritabanıyla etkileşim kurmak için kullanılır.
        c.execute('SELECT isim, yuz_kodlari FROM yuzler') #Veritabanından tüm kayıtlı isimleri ve yüz kodlamalarını getirir.
        veriler = c.fetchall() #Select sorgusunun sonucunda dönen tüm satırları alır.
        conn.close()

        isimler = []
        yuz_kodlari = [] #Veri tabanından alınan verileri saklamak için oluşturulmuştur.

        for isim, yuz_kodlari_p in veriler: #Veriler listesindeki her bir satırı işler.
            yuz_kodlari.append(pickle.loads(yuz_kodlari_p)) #pickle ile serileştirilmiş veriyi, orijinal py nesnesine dönüştürür.
            isimler.append(isim) #Döngüde alınan her bir isim bilgisini isimler listesine ekler.

        return yuz_kodlari, isimler #Fonksiyonun sonucunu döndürür.

    def baslat(self):
        self.timer.start() #Daha önce oluşturulan QTimer nesnesini başlatır. Başlat düğmesi ile tetiklenir

    def durdur(self): #QTimer nesnesini durdurur. Durdur düğmesi ile tetiklenir.
        self.timer.stop()
        self.video_kamerasi.release() #OpenCV'nin video kamerasıyla bağlantısını serbest bırakır.
        cv2.destroyAllWindows() #OpenCV'nin görüntüleme sırasında açtığı tüm pencereleri kapatır.

    def yuzleri_tani(self): 
        ret, kare = self.video_kamerasi.read() #OpenCV kullanarak kameradan bir kare alır.
        if not ret: #Kamera görüntüsünün başarıyla okunup okunmadığını belirten bir bayraktır. true/false döner.
            return #Görüntü almazsa ret ise yani fonksiyon bir şey yapmadan sonlanır. Kontrol mekanizmasıdır.

        rgb_kare = cv2.cvtColor(kare, cv2.COLOR_BGR2RGB) #Görüntüyü rgb formatına dönüştürür.
        yuz_konumlari = face_recognition.face_locations(rgb_kare) #Görüntüdeki yüzün koordinatlarını tespit eder
        yuz_kodlari = face_recognition.face_encodings(rgb_kare, yuz_konumlari) #Yüzleri karşılaştırmak için kullanılır.

        for yuz_kodu, yuz_konumu in zip(yuz_kodlari, yuz_konumlari): #Tespit edilen tüm yüz kodları ve konumları üzerinde sırayla işlem yapar.
            ust, sag, alt, sol = yuz_konumu #Yüzün görüntüdeki tam pozisyonunu (dikdörtgen şeklinde) temsil eder.

            eslesmeler = face_recognition.compare_faces(self.bilinen_yuz_kodlari, yuz_kodu, tolerance=0.6) #İki yüzün eşleşmiş sayılması için gereken eşiği belirler.
            isim = "Bilinmeyen" #Daha düşük bir değer daha kesin eşleşme gerektirir.

            yuz_mesafeleri = face_recognition.face_distance(self.bilinen_yuz_kodlari, yuz_kodu) #algılanan yüz kodlaması ile bilinen yüz kodlamaları arasındaki mesafeleri hesaplar.
            en_iyi_eslesme_indeksi = yuz_mesafeleri.argmin() if len(yuz_mesafeleri) > 0 else None #En düşük mesafeye sahip kodlamanın indeksini döner. En iyi eşleşme arar. 

            if en_iyi_eslesme_indeksi is not None and eslesmeler[en_iyi_eslesme_indeksi]: #En iyi eşleşme bulunduysa ve eşleşme toleran sınırları içinde geçerliyse yüzün ismini veritabanındakiyle eşleştirir.
                isim = self.bilinen_yuz_isimleri[en_iyi_eslesme_indeksi]

            cv2.rectangle(kare, (sol, ust), (sag, alt), (0, 255, 0), 2) #Tespit edilen yüzün etrafında yeşil dikdörtgen çizer.
            cv2.putText(kare, isim, (sol + 6, alt - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1) #Dikdörtgenin altına yüzün ismini veya bilinmeyen metnini ekler

            if isim != "Bilinmeyen" and isim != self.son_tanimlanan_isim: #Eğer tanımlanan yüz kayıtlı değilse self kısmındaki kod ile kişi tanımlanan isimle güncellenir.
                self.son_tanimlanan_isim = isim
                self.engine.say(f"Merhaba, hoşgeldiniz {isim}") #Pyttsx3 kütüphanesi sayesinde isimi sesli mesaj olarak verir.
                self.engine.runAndWait()

        qimage = self.convert_cv_qt(kare) #convert fonksiyonu, opencv'nin görüntü formatını qrt için uygun hale getirir
        self.label.setPixmap(qimage) #QT arayüzünde görüntüyü görüntüler.

    def convert_cv_qt(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #OpenCV'den gelen görüntüyü BGR formatından RGB formatına dönüştürür.Çünkü PyQt5 görüntüyü RGB formatında ister.
        h, w, ch = rgb_image.shape #Burada görüntünün yüksekliği(h), genişliği (w) ve kanal sayısı (ch) elde edilir.
        bytes_per_line = ch * w #Bir satırdaki toplam bayt sayısını hesaplar (kanal S. * genişlik). PyQt'nin görüntü formatı için gereklidir.
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888) #rgb_image.data: görüntü verisi içindir. bytes_per_line: Her satırdaki bayt sayısı için. QImage.Format_RGB888: RGB formatını belirtir.
        p = QPixmap.fromImage(convert_to_Qt_format) #QImage, Qt'nin daha yaygın kullanılan görüntü formatı QPixmap formatına dönüştürür.
        return p.scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio) #QPixmap, arayüzdeki label'in (etiketin) boyutlarına sığdırılır.
        #Qt.KeepAspectRatio: görüntünün oranını koruyarak yeniden boyutlandırır.

    def kayit_ekrani_ac(self): #Bu fonksiyon, br yüz kaydetmek içi kullanılan yeni bir kayıt penceresi açar.
        self.kayit_penceresi = KayitPenceresi(self) #Kayıt penceresi sınıfından yeni bir pencere (instance) oluşturur. Ana pencereye (self) bağlıdır. 
        self.kayit_penceresi.show() #Yeni pencereyi kullanıcıya göstermek için show() metodu çağrılır.

class KayitPenceresi(QWidget): #Bu sınıf bir PyQt5 pencere sınıfıdır ve QWidget sınıfından türetilmiştir. Bu sınıf yeni yüz kayıdı için kullanılır.
    def __init__(self, parent=None): #
        super().__init__(parent) #Bu sınıf, bir ana pencereye (parent) bağlı olabilir. super(), üst sınıf olan QWidget'in init metodunu çağırır.
        self.setWindowTitle("Yüz Kaydet") #Pencerenin başlık çubuğunda görünün metni "Yüz Kaydet" olarak ayarlar
        self.setGeometry(100, 100, 400, 300) #Pencerenin başlangıç konumunu ayarlar.

        self.layout = QVBoxLayout() #Bu dikey bir düzen (layout) yaratır.Bu, pencere elemanlarının dikey olarak sıralanmasını sağlar.
        self.isim_label = QLabel("İsim:", self) #Bir etiket oluşturur ve üzerine "İsim:" yazısını ekler.
        self.isim_input = QLineEdit(self) #Kullanıcıdan metin (isim) girişini almak için bir metin kutusunu oluşturur.

        self.kayit_button = QPushButton("Kaydet", self) #Üzerinde "kaydet" yazan bir düğme oluşturur. 
        self.kayit_button.clicked.connect(self.yuz_kaydet) #"Kaydet" düğmesine tıklandığında, yuz_kaydet metodunun çalıştırılmasını sağlar.

        self.layout.addWidget(self.isim_label) #addwidget: Etiket, metin kutusu ve düğme sırasıyla düzen içerisine eklenir.
        self.layout.addWidget(self.isim_input) 
        self.layout.addWidget(self.kayit_button)

        self.setLayout(self.layout) #Bu düzen, pencerenin ana düzeni olarak ayarlanır.

    def yuz_kaydet(self): #Kullanıcı tarafından girilen ismi ve kameradan alının yüz verilerini veritabanına kaydeder.
        isim = self.isim_input.text() #Kullanıcının metin kutusuna girdiği isimi alır ve isim değişkenine atar.
        parent = self.parent() #Bu sınıfın bağlı olduğu üst pencereyi (parent) alır. Bu pencere, yüz tanıma uygulamasının arayüzüdür.
        ret, kare = parent.video_kamerasi.read() #Ana pencerenin video_kamerasi nesnesinden bir kare (frame) okur.
        if not ret: #Görüntü alınmazsa işlem sonlanır.
            return

        rgb_kare = cv2.cvtColor(kare, cv2.COLOR_BGR2RGB) 
        yuz_konumlari = face_recognition.face_locations(rgb_kare) #Görüntüdeki yüzlerin konumlarını (koordinatlarını bulur.)
        yuz_kodlari = face_recognition.face_encodings(rgb_kare, yuz_konumlari) #Bulunan yüzlerin benzersiz kodlarını (encodings) çıkarır.

        if yuz_kodlari: #Görüntüde yüz bulunduysa bu blok çalışır.
            conn = sqlite3.connect('yuz_tanima.db') #Yüz tanıma veritabanına bağlanır.
            c = conn.cursor() #Veritabanına sql komutları göndermek için kullanılan bir cursor (imleç) nesnesi oluşturur. c harfi nesneyi temsil eder.
            c.execute('INSERT INTO yuzler (isim, yuz_kodlari) VALUES (?, ?)', (isim, pickle.dumps(yuz_kodlari[0]))) #Bu satır, verilen isim ve seri hale getirilmiş (pickle ile) yüz kodlamasını, yuzler tablosuna ekler. 
            #? işaretleri, SQL sorgusunda parametre geçişi için kullanılır ve güvenliği arttırır.
            conn.commit() #Yapılan değişiklikleri veritabanına kayıt eder
            conn.close() #Veritabanı bağlantısını kapatır.

            parent.bilinen_yuz_kodlari, parent.bilinen_yuz_isimleri = parent.yuzleri_getir() #Yeni kaydedilen yüzü belleğe yüklemek için ana pencerenin yüz tanıma listelerini günceller.
            self.close()#Bu pencereyi kapatır.

if __name__ == "__main__": #Bu dosyanın doğrudan çalıştırıldığında kodun çalıştırılmasını sağlar.
    app = QApplication(sys.argv) #PyQt5 uygulamasını başlatır ve komut satırı argümanlarını alır. QApplication, bir PyQt5 uygulamasının ana kontrol mekanizmasıdır.
    window = YuzTanimlamaApp() #YuzTanimlamaApp sınıfından bir pencere nesnesi oluşturur
    window.show() #Uygulama penceresini ekranda görüntüler
    sys.exit(app.exec_()) #Uygulama döngüsünü başlatır (app.exec_()) ve uygulama kapatıldığında düzgün bir çıkış yapar.
    #sys.exit, uygulamanın dönüş değerini işletim sistemine iletir.

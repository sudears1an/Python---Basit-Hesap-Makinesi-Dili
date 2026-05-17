======================================================================
TEKİRDAĞ NAMIK KEMAL ÜNİVERSİTESİ - ÇORLU MÜHENDİSLİK FAKÜLTESİ
Bilgisayar Mühendisliği Bölümü
Programlama Dilleri Prensipleri Dersi Dönem Projesi
======================================================================

PROJE BİLGİLERİ:
----------------
Öğrenci Adı : Sude Arslan
Öğrenci No  : 2230656055
Ödev No     : 1
Tarih       : 17.05.2026
Proje Adı   : Değişken ve Koşul Destekli Hesap Makinesi Yorumlayıcısı

1. KULLANILAN PROGRAMLAMA DİLİ VE SÜRÜMÜ
----------------------------------------
* Dil: Python 3 (Önerilen ve test edilen en düşük sürüm: Python 3.8+)
* Geliştirme ve Test Sürümü: Python 3.11.x / 3.12.x (Anaconda Environment)

2. GEREKLİ KÜTÜPHANELER VE BAĞIMLILIKLAR (DEPENDENCIES)
------------------------------------------------------
* Standart Kütüphane: Proje, Python'ın tamamen yerleşik (built-in) mimarisi
  üzerine kurulmuştur. Dışarıdan kurulması gereken hiçbir üçüncü parti 
  kütüphaneye veya bağımlılığa (pip install paket_adi vb.) ihtiyaç duymaz.
* Grafik Arayüz (GUI): Python ile gömülü gelen 'tkinter' ve 'ttk' modülleri
  kullanılmıştır. Ekstra bir grafik motoru kurulumu gerektirmez.

3. DERLEME BİLGİSİ (COMPILATION)
--------------------------------
* Bu proje, yorumlanabilir (interpreted) bir dil olan Python ile yazılmıştır
  ve kendisi de bir Yorumlayıcı (Interpreter) projesidir. Dolayısıyla C, C++ 
  veya Java gibi dillerdeki gibi bir ön derleme (compilation/build) adımına 
  ihtiyaç duymaz. Kaynak kodlar doğrudan Python yorumlayıcısı tarafından 
  çalışma zamanında (runtime) satır satır işlenir.

4. ÇALIŞTIRMA KOMUTLARI
-----------------------
Projenin kök dizinindeyken terminal veya PowerShell üzerinden "src" klasörünün 
içine geçilerek şu komutlar koşturulabilir:

* Grafik Kullanıcı Arayüzünü (GUI / IDE) Başlatmak İçin (Önerilen):
  cd src
  python gui.py

* Alternatif Konsol / Terminal Modu Çalıştırma (Varsa):
  cd src
  python main.py

5. ÖRNEK KULLANIM VE BEKLENEN ÇIKTI
-----------------------------------
Arayüzdeki editöre şu kod bloğu girildiğinde:
  x = 10
  y = 3
  toplam = x + y * 2
  if toplam > 15 { sonuc = toplam * 2 } else { sonuc = 0 }

Beklenen Çıktı (Değişken Hafızası Durumu):
  x      = 10  (int)
  y      = 3   (int)
  toplam = 16  (int)  -> İşlem önceliğinin çalıştığının kanıtı.
  sonuc  = 32  (int)  -> if koşulunun başarıyla değerlendirildiğinin kanıtı.

6. BİLİNEN HATALAR, SINIR DURUMLAR VEYA EKSİKLER
------------------------------------------------
* Döngü Yapıları (Loops): Mevcut sürüm (Ödev 1 kapsamı gereğince) sadece 
  'if-else' koşul yapısını desteklemektedir. 'while' veya 'for' gibi döngü 
  yapıları dilin gramerinde ve Parser modülünde şu an için yer almamaktadır.
* Sürüm Farklılığı (Tkinter): Bazı çok eski Python/Tkinter sürümlerinde 
  Text bileşenindeki '-tabsize' parametresi 'TclError' verebilmektedir. 
  Mevcut 'gui.py' kodunda bu parametre, maksimum geriye dönük uyumluluk 
  sağlamak adına varsayılan ayarlara bırakılarak pasifize edilmiştir.
* Mantıksal Operatör Birleştirmeleri: Dilimiz tekil karşılaştırmaları 
  (>, <, ==) destekler; ancak 'and' veya 'or' gibi bağlaçlarla iki koşulu 
  aynı anda bağlama özelliği (Örn: if x > 5 and y < 10) bu sürümde eksiktir.

7. ZORUNLU RESMİ DİZİN VE DOSYA YAPISI
--------------------------------------
├── src/                      # Tüm kaynak kod dosyaları klasörü
│   ├── lexer.py              # Sözcüksel Analizci (Token üretimi)
│   ├── parser_ast.py         # Sözdizimsel Analizci (AST Yapısı)
│   ├── interpreter.py        # Yürütücü (Hafıza yönetimi ve hesaplama)
│   ├── gui.py                # Modern Geliştirici Arayüzü (IDE)
│   └── main.py               # Ana Giriş ve Yönetim Modülü
├── docs/                     # Açıklama ve akademik rapor dosyaları
│   ├── 2230656055_Sude_Arslan_Proje_Raporu.docx
│   └── proje_mimari.svg      # Sistem mimari akış şeması
├── tests/                    # Örnek hazır test senaryoları kodları
│   ├── test_normal_durum.txt
│   ├── test_sifira_bolme.txt
│   └── test_tanimsiz_degisken.txt
└── README.txt                # Bu bilgilendirme ve çalıştırma dökümanı
======================================================================
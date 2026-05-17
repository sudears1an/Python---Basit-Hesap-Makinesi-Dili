======================================================================
TEKİRDAĞ NAMIK KEMAL ÜNİVERSİTE Sİ - ÇORLU MÜHENDİSLİK FAKÜLTESİ
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

PROJE AÇIKLAMASI:
-----------------
Bu proje, Python dili kullanılarak Nesne Yönelimli Programlama (OOP) 
prensiplerine uygun şekilde geliştirilmiş modüler bir Interpreter (Yorumlayıcı) 
projesidir. Proje, özel olarak tasarlanmış mini bir hesap makinesi ve kontrol 
dilini karakter karakter işleyerek çalıştırır.

DİLİN DESTEKLEDİĞİ ÖZELLİKLER:
------------------------------
1. Değişken Atama ve Hafıza: (Örn: x = 10)
2. Aritmetik İşlemler ve Öncelik Yönetimi: (+, -, *, /) İşlem öncelikleri 
   Parser seviyesinde çözülmüştür (Çarpma/Bölme önceliklidir).
3. Karşılaştırma ve Koşul Blokları: (>, <, ==) Operatörleri ile küme 
   parantezli {} 'if-else' yapısı desteklenmektedir.
4. Gelişmiş Hata Raporlama: Sözcüksel (LexerHatasi), Sözdizimsel (ParserHatasi) 
   ve Çalışma Zamanı (NameError, ZeroDivisionError) hataları programı 
   çökertmeden satır numarasıyla konsola raporlanır.

DİZİN VE DOSYA YAPISI:
----------------------
2230656055_Sude_Arslan/
│
├── src/                      # Kaynak kod klasörü
│   ├── lexer.py              # Sözcüksel Analiz Modülü (Tokenization)
│   ├── parser_ast.py         # Sözdizim Analiz Modülü (AST İnşası)
│   ├── interpreter.py        # Yürütücü Modül (AST Evaluation & Environment)
│   ├── gui.py                # Tkinter Tabanlı Minimalist IDE / Arayüz Modülü
│   └── main.py               # Proje Giriş Noktası ve Pipeline Yönetimi
│
├── tests/                    # Test senaryoları klasörü
├── docs/                     # Akademik raporlar ve BNF Grameri
├── screenshots/              # Arayüz çalışma anı ekran görüntüleri
├── ornek.mini                # Örnek kaynak kod dosyası
└── README.txt                # Bu bilgilendirme dosyası

SİSTEM GEREKSİNİMLERİ VE ÇALIŞTIRMA:
------------------------------------
Proje, harici hiçbir kütüphaneye (pip install vb.) ihtiyaç duymadan, 
Python 3.8+ standart kütüphaneleriyle çalışmaktadır.

Ana klasör dizinindeyken terminal (PowerShell / CMD) üzerinden şu komutlarla çalıştırılabilir:

1. Otomatik Test Paketini Koşturmak İçin:
   python src/main.py --test

2. İnteraktif REPL Terminal Modunu Başlatmak İçin:
   python src/main.py --repl

3. Grafik Kullanıcı Arayüzünü (GUI) Başlatmak İçin:
   python src/main.py --gui

4. Bir Metin Dosyasını Doğrudan Yorumlamak İçin:
   python src/main.py ornek.mini
======================================================================
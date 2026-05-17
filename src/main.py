# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 1
# Tarih:   16.05.2026
# =========================================================
# Açıklama: Mini Interpreter'ın giriş noktası (main.py).
#            İki çalışma modu destekler:
#              1. Dosya Modu  : Komut satırı argümanıyla verilen
#                               .mini uzantılı kaynak dosyayı okur
#                               ve baştan sona çalıştırır.
#              2. REPL Modu   : Argüman verilmezse interaktif
#                               okuma-değerlendirme-yazdırma döngüsü
#                               başlatır. Kullanıcı 'çık' yazarak
#                               oturumu sonlandırabilir.
#            Ayrıca hocanın istediği 3 zorunlu test senaryosunu
#            doğrudan kod içinde koşturan hazır fonksiyonlar içerir.
# =========================================================

import sys
import os

# Modüllerin bulunduğu 'src/' dizinini Python yoluna ekle
# Bu sayede lexer, parser_ast, interpreter doğrudan import edilebilir.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer       import Lexer, LexerHatasi
from parser_ast  import Parser, ParserHatasi
from interpreter import Interpreter, CalismaSuresiHatasi


# ===========================================================================
# BORU HATTI (PIPELINE) — Kaynak Koddan Sonuca
# ===========================================================================

def kaynak_kodu_calistir(kaynak_kod: str, interpreter: Interpreter):
    """
    Verilen kaynak kodu metni üç aşamalı boru hattından geçirerek çalıştırır:
      1. Lexer  → Token listesi üretir.
      2. Parser → AST inşa eder.
      3. Interpreter → AST'yi yürütür.

    Her aşamada oluşabilecek hatalar uygun mesajla yakalanır;
    yorumlayıcı çökmez.
    """
    try:
        # --- AŞAMA 1: Sözcüksel Analiz ---
        lexer        = Lexer(kaynak_kod)
        token_listesi = lexer.tokenize()

        # --- AŞAMA 2: Sözdizimsel Analiz (AST Oluşturma) ---
        parser   = Parser(token_listesi)
        ast_koku = parser.parse()

        # --- AŞAMA 3: Yorumlama ---
        sonuc = interpreter.calistir(ast_koku)
        return sonuc

    except LexerHatasi as hata:
        print(f"[SözDizimHatası] Satır {hata.satir}: {hata}")
        return None

    except ParserHatasi as hata:
        print(f"[SözDizimHatası] Satır {hata.satir}: {hata}")
        return None

    except CalismaSuresiHatasi as hata:
        print(hata)
        return None


# ===========================================================================
# ZORUNLU TEST SENARYOLARI
# ===========================================================================

def senaryo_ayirici(baslik: str) -> None:
    print("\n" + "=" * 60)
    print(f"  TEST: {baslik}")
    print("=" * 60)


def test_normal_calisma() -> None:
    senaryo_ayirici("Normal Çalışma (Değişken, Aritmetik, if/else)")
    kaynak = """
x = 10
y = 3
toplam = x + y * 2
fark = x - y

if toplam > 15 {
    sonuc = toplam * 2
} else {
    sonuc = fark
}
"""
    interp = Interpreter()
    kaynak_kodu_calistir(kaynak, interp)

    degiskenler = interp.ortam.tum_degiskenler()
    for isim, deger in degiskenler.items():
        print(f"  {isim} = {deger}")

    assert degiskenler.get("x")      == 10,  "x yanlış!"
    assert degiskenler.get("y")      == 3,   "y yanlış!"
    assert degiskenler.get("toplam") == 16,  "toplam yanlış!"
    assert degiskenler.get("fark")   == 7,   "fark yanlış!"
    assert degiskenler.get("sonuc")  == 32,  "sonuc yanlış!"
    print("\n  [GEÇTİ] Tüm değerler beklenenle örtüşüyor.")


def test_sinir_durum_sifira_bolme() -> None:
    senaryo_ayirici("Sınır Durum — Sıfıra Bölme (ZeroDivisionError)")
    kaynak = """
pay = 100
payda = 0
sonuc = pay / payda
"""
    interp = Interpreter()
    print("  Beklenen: ZeroDivisionError mesajı")
    print("  Üretilen:", end=" ")
    kaynak_kodu_calistir(kaynak, interp)

    assert "sonuc" not in interp.ortam.tum_degiskenler(), "'sonuc' hata sonrası tanımlı olmamalı!"
    print("  [GEÇTİ] Yorumlayıcı çökmedi, 'sonuc' tanımlı değil.")


def test_hata_durumu_tanimsiz_degisken() -> None:
    senaryo_ayirici("Hata Durumu — Tanımlanmamış Değişken (NameError)")
    kaynak = """
a = 5
b = a + tanimsiz_degisken
"""
    interp = Interpreter()
    print("  Beklenen: NameError mesajı")
    print("  Üretilen:", end=" ")
    kaynak_kodu_calistir(kaynak, interp)

    degiskenler = interp.ortam.tum_degiskenler()
    assert degiskenler.get("a") == 5, "'a' doğru tanımlı olmalı!"
    assert "b" not in degiskenler,    "'b' hata nedeniyle tanımlı olmamalı!"
    print("  [GEÇTİ] Yorumlayıcı çökmedi, 'b' tanımlı değil.")


def tum_testleri_calistir() -> None:
    print("\n" + "#" * 60)
    print("  MİNİ INTERPRETER — OTOMATİK TEST PAKETİ")
    print("#" * 60)

    test_normal_calisma()
    test_sinir_durum_sifira_bolme()
    test_hata_durumu_tanimsiz_degisken()

    print("\n" + "#" * 60)
    print("  Tüm senaryolar başarıyla tamamlandı.")
    print("#" * 60 + "\n")


# ===========================================================================
# DOSYA MODU
# ===========================================================================

def dosya_modunda_calistir(dosya_yolu: str) -> None:
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            kaynak_kod = dosya.read()
    except FileNotFoundError:
        print(f"[HataError] Dosya bulunamadı: '{dosya_yolu}'")
        sys.exit(1)
    except IOError as io_hata:
        print(f"[HataError] Dosya okunamadı: {io_hata}")
        sys.exit(1)

    print(f"\n[Dosya Modu] '{dosya_yolu}' çalıştırılıyor...\n")

    interp = Interpreter()
    sonuc  = kaynak_kodu_calistir(kaynak_kod, interp)

    if sonuc is not None:
        print(f"\n=> Son ifade sonucu: {sonuc}")

    degiskenler = interp.ortam.tum_degiskenler()
    if degiskenler:
        print("\n[Değişken Ortamı]")
        for isim, deger in degiskenler.items():
            print(f"  {isim} = {deger}")


# ===========================================================================
# REPL MODU (Read-Eval-Print Loop)
# ===========================================================================

def repl_modunu_baslat() -> None:
    print("=" * 60)
    print("  Mini Interpreter — REPL Modu")
    print("  Çıkmak için: 'çık' veya 'exit' yazın.")
    print("  Çok satırlı bloklar için '{' ile satırı bitirin.")
    print("=" * 60 + "\n")

    interp = Interpreter()

    while True:
        try:
            giris = input(">>> ").strip()

            if giris.lower() in ("çık", "exit", "quit", "q"):
                print("Oturum kapatıldı.")
                break

            if not giris:
                continue

            satir_tampon = giris
            if "{" in giris:
                while "}" not in satir_tampon.split("{", 1)[-1]:
                    ek_satir = input("... ").rstrip()
                    satir_tampon += "\n" + ek_satir

            sonuc = kaynak_kodu_calistir(satir_tampon, interp)

            if sonuc is not None:
                print(f"=> {sonuc}")

        except KeyboardInterrupt:
            print("\nKlavye kesmesi algılandı. Çıkılıyor...")
            break
        except EOFError:
            break


# ===========================================================================
# GİRİŞ NOKTASI
# ===========================================================================

def main() -> None:
    argümanlar = sys.argv[1:]

    if not argümanlar:
        # Argüman yoksa hem otomatik testleri koş, hem de görsel arayüzü başlat!
        tum_testleri_calistir()
        print("\n[Sistem] Grafik kullanıcı arayüzü başlatılıyor...")
        
        # gui.py içindeki UygulamaGUI sınıfını dinamik olarak çağırıyoruz
        from gui import UygulamaGUI
        root = __import__('tkinter').Tk()
        app = UygulamaGUI(root)
        root.mainloop()
        
    elif argümanlar[0] == "--test":
        tum_testleri_calistir()
        
    elif argümanlar[0] == "--repl":
        repl_modunu_baslat()
        
    elif argümanlar[0] == "--gui":
        # Sadece arayüzü başlatmak için: python src/main.py --gui
        from gui import UygulamaGUI
        root = __import__('tkinter').Tk()
        app = UygulamaGUI(root)
        root.mainloop()
        
    else:
        dosya_modunda_calistir(argümanlar[0])


if __name__ == "__main__":
    main()
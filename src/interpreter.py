# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 142
# Tarih:   17.05.2026
# =========================================================
# Açıklama: Interpreter (Yorumlayıcı) modülü. Lexer ve
#            Parser tarafından üretilen Soyut Sözdizim Ağacını
#            (AST) Ziyaretçi Tasarım Deseni (Visitor Pattern)
#            kullanarak özyinelemeli olarak yürütür.
#            Çalışma zamanı hataları yakalanarak raporlanır.
# =========================================================

from parser_ast import (
    ProgramDugumu, SayiDugumu, DegiskenDugumu, IkiliIslemDugumu, 
    AtamaDugumu, KosulDugumu,
)

# ===========================================================================
# ÇALIŞMA ZAMANI HATA SINIFLARI (RUNTIME EXCEPTIONS)
# ===========================================================================

class CalismaSuresiHatasi(Exception):
    """
    Yorumlayıcının çalışma zamanında (runtime) karşılaşabileceği tüm
    hataların temel sınıfı. Hatayı fırlatan kodun satır numarasını taşır.
    """
    def __init__(self, hata_turu: str, mesaj: str, satir: int) -> None:
        super().__init__(mesaj)
        self.hata_turu = hata_turu   # Hatanın kategorisi (Örn: NameError)
        self.satir     = satir        # Hatanın kaynak koddaki satır numarası
        
    def __str__(self) -> str:
        # Hatanın konsola veya arayüze basılacak standart formatı
        return f"[{self.hata_turu}] Satır {self.satir}: {super().__str__()}"


class IsimHatasi(CalismaSuresiHatasi):
    """Tanımlanmamış veya hafızada bulunmayan bir değişken çağrıldığında tetiklenir."""
    def __init__(self, degisken_adi: str, satir: int) -> None:
        super().__init__("NameError", f"'{degisken_adi}' isimli değişken tanımlanmamış.", satir)


class SifiraBolmeHatasi(CalismaSuresiHatasi):
    """Matematiksel olarak bir sayı sıfıra bölünmeye çalışıldığında tetiklenir."""
    def __init__(self, satir: int) -> None:
        super().__init__("ZeroDivisionError", "Sıfıra bölme hatası: bir sayı sıfıra bölünemez.", satir)


# ===========================================================================
# BELLEK YÖNETİMİ / DEĞİŞKEN ORTAMI (ENVIRONMENT)
# ===========================================================================

class Ortam:
    """
    Çalışma zamanındaki değişkenleri ve bunlara ait değerleri saklayan
    hafıza/sembol tablosu (Symbol Table) yönetim sınıfı.
    """
    def __init__(self) -> None:
        # Değişkenleri 'ad: değer' çifti olarak tutan dinamik sözlük (Hash Map)
        self._depo: dict = {}
        
    def degisken_ata(self, isim: str, deger) -> None:
        """Yeni bir değişken tanımlar veya mevcut olanın değerini günceller."""
        self._depo[isim] = deger
        
    def degisken_oku(self, isim: str, satir: int):
        """İsmi verilen değişkenin değerini döndürür. Bulamazsa NameError fırlatır."""
        if isim not in self._depo:
            raise IsimHatasi(isim, satir)
        return self._depo[isim]
        
    def tum_degiskenler(self) -> dict:
        """Mevcut bellek durumunun kopyasını arayüz (GUI) veya testler için döndürür."""
        return dict(self._depo)


# ===========================================================================
# YORUMLAYICI ANA SINIFI (INTERPRETER)
# ===========================================================================

class Interpreter:
    """
    Soyut Sözdizim Ağacının (AST) kökünden başlayarak tüm düğümleri
    ziyaret eden ve kaynak kodu mantıksal sonuca ulaştıran ana yürütücü motor.
    """
    def __init__(self) -> None:
        self.ortam = Ortam()   # Yorumlayıcıya ait izole hafıza alanı

    def _ziyaret(self, dugum):
        """
        Gelen AST düğümünün sınıf adına göre dinamik olarak ilgili
        ziyaretçi metodunu (visitor method) tespit eder ve tetikler.
        """
        metod_adi = "_ziyaret_" + type(dugum).__name__
        ziyaretci = getattr(self, metod_adi, None)
        if ziyaretci is None:
            raise ValueError(f"Bilinmeyen AST düğüm türü: '{type(dugum).__name__}'")
        return ziyaretci(dugum)

    def _ziyaret_ProgramDugumu(self, dugum: ProgramDugumu):
        """Programın en üst kök düğümünü işler; tüm alt deyimleri sırayla yürütür."""
        son_sonuc = None
        for deyim in dugum.deyimler:
            son_sonuc = self._ziyaret(deyim)
        return son_sonuc

    def _ziyaret_SayiDugumu(self, dugum: SayiDugumu):
        """Sabit sayı düğümlerini işler; doğrudan sayısal değeri (int/float) döndürür."""
        return dugum.deger

    def _ziyaret_DegiskenDugumu(self, dugum: DegiskenDugumu):
        """Değişken çağrısı düğümlerini işler; değeri bellekten (Environment) sorgular."""
        return self.ortam.degisken_oku(dugum.isim, dugum.satir)

    def _ziyaret_AtamaDugumu(self, dugum: AtamaDugumu):
        """
        Atama işlemlerini (=) yürütür. Önce eşitliğin sağ tarafındaki 
        ifadeyi çözer (evaluate eder), ardından çıkan sonucu değişkene bağlar.
        """
        hesaplanan_deger = self._ziyaret(dugum.ifade)
        self.ortam.degisken_ata(dugum.degisken_adi, hesaplanan_deger)
        return None   # Atama deyimleri dışarıya bir değer döndürmez

    def _ziyaret_IkiliIslemDugumu(self, dugum: IkiliIslemDugumu):
        """
        Aritmetik (+, -, *, /) ve karşılaştırma (>, <, ==) düğümlerini işler.
        Sol ve sağ alt ağaçları çözerek çıkan değerler üzerinde operatörü uygular.
        """
        sol_deger = self._ziyaret(dugum.sol)
        sag_deger = self._ziyaret(dugum.sag)
        operator  = dugum.operator

        # Aritmetik Operatörlerin Yürütülmesi
        if operator == "+":    return sol_deger + sag_deger
        elif operator == "-":  return sol_deger - sag_deger
        elif operator == "*":  return sol_deger * sag_deger
        elif operator == "/":
            # Sıfıra bölme sınır durum kontrolü (Boundary Case Control)
            if sag_deger == 0:
                raise SifiraBolmeHatasi(dugum.satir)
            return sol_deger / sag_deger
            
        # Karşılaştırma / Mantıksal Operatörlerin Yürütülmesi
        elif operator == ">":  return sol_deger > sag_deger
        elif operator == "<":  return sol_deger < sag_deger
        elif operator == "==": return sol_deger == sag_deger
        else: 
            raise ValueError(f"Desteklenmeyen operatör: '{operator}'")

    def _ziyaret_KosulDugumu(self, dugum: KosulDugumu):
        """
        'if-else' bloklarının mantıksal kontrolünü yapar. Koşul ifadesi
        doğru (True) ise sadece doğru bloğunu, yanlış ise varsa else bloğunu yürütür.
        """
        kosul_sonucu = self._ziyaret(dugum.kosul_ifadesi)
        
        if kosul_sonucu:
            for deyim in dugum.dogru_blok:
                self._ziyaret(deyim)
        else:
            for deyim in dugum.yanlis_blok:
                self._ziyaret(deyim)
        return None   # Koşul blokları dışarıya doğrudan bir değer döndürmez

    def calistir(self, ast_koku: ProgramDugumu):
        """Yorumlayıcıyı dış dünyadan tetikleyen ana dış arayüz metodu."""
        return self._ziyaret(ast_koku)
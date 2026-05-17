# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 1
# Tarih:   16.05.2026
# =========================================================
# Açıklama: Interpreter (Yorumlayıcı) modülü. Lexer ve
#            Parser tarafından üretilen AST'yi yürütür.
#            Çalışma zamanı hataları yakalanarak raporlanır.
# =========================================================

from parser_ast import (
    ProgramDugumu, SayiDugumu, DegiskenDugumu, IkiliIslemDugumu, 
    AtamaDugumu, KosulDugumu,
)

class CalismaSuresiHatasi(Exception):
    def __init__(self, hata_turu: str, mesaj: str, satir: int) -> None:
        super().__init__(mesaj)
        self.hata_turu = hata_turu   
        self.satir     = satir        
    def __str__(self) -> str:
        return f"[{self.hata_turu}] Satır {self.satir}: {super().__str__()}"

class IsimHatasi(CalismaSuresiHatasi):
    def __init__(self, degisken_adi: str, satir: int) -> None:
        super().__init__("NameError", f"'{degisken_adi}' isimli değişken tanımlanmamış.", satir)

class SifiraBolmeHatasi(CalismaSuresiHatasi):
    def __init__(self, satir: int) -> None:
        super().__init__("ZeroDivisionError", "Sıfıra bölme hatası: bir sayı sıfıra bölünemez.", satir)


class Ortam:
    def __init__(self) -> None:
        self._depo: dict = {}
    def degisken_ata(self, isim: str, deger) -> None:
        self._depo[isim] = deger
    def degisken_oku(self, isim: str, satir: int):
        if isim not in self._depo:
            raise IsimHatasi(isim, satir)
        return self._depo[isim]
    def tum_degiskenler(self) -> dict:
        return dict(self._depo)


class Interpreter:
    def __init__(self) -> None:
        self.ortam = Ortam()   

    def _ziyaret(self, dugum):
        metod_adi = "_ziyaret_" + type(dugum).__name__
        ziyaretci = getattr(self, metod_adi, None)
        if ziyaretci is None:
            raise ValueError(f"Bilinmeyen AST düğüm türü: '{type(dugum).__name__}'")
        return ziyaretci(dugum)

    def _ziyaret_ProgramDugumu(self, dugum: ProgramDugumu):
        son_sonuc = None
        for deyim in dugum.deyimler:
            son_sonuc = self._ziyaret(deyim)
        return son_sonuc

    def _ziyaret_SayiDugumu(self, dugum: SayiDugumu):
        return dugum.deger

    def _ziyaret_DegiskenDugumu(self, dugum: DegiskenDugumu):
        return self.ortam.degisken_oku(dugum.isim, dugum.satir)

    def _ziyaret_AtamaDugumu(self, dugum: AtamaDugumu):
        hesaplanan_deger = self._ziyaret(dugum.ifade)
        self.ortam.degisken_ata(dugum.degisken_adi, hesaplanan_deger)
        return None   

    def _ziyaret_IkiliIslemDugumu(self, dugum: IkiliIslemDugumu):
        sol_deger = self._ziyaret(dugum.sol)
        sag_deger = self._ziyaret(dugum.sag)
        operator  = dugum.operator

        if operator == "+": return sol_deger + sag_deger
        elif operator == "-": return sol_deger - sag_deger
        elif operator == "*": return sol_deger * sag_deger
        elif operator == "/":
            if sag_deger == 0:
                raise SifiraBolmeHatasi(dugum.satir)
            return sol_deger / sag_deger
        elif operator == ">": return sol_deger > sag_deger
        elif operator == "<": return sol_deger < sag_deger
        elif operator == "==": return sol_deger == sag_deger
        else: raise ValueError(f"Desteklenmeyen operatör: '{operator}'")

    def _ziyaret_KosulDugumu(self, dugum: KosulDugumu):
        kosul_sonucu = self._ziyaret(dugum.kosul_ifadesi)
        if kosul_sonucu:
            for deyim in dugum.dogru_blok:
                self._ziyaret(deyim)
        else:
            for deyim in dugum.yanlis_blok:
                self._ziyaret(deyim)
        return None   

    def calistir(self, ast_koku: ProgramDugumu):
        return self._ziyaret(ast_koku)
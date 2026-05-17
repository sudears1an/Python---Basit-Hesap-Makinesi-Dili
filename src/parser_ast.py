# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 1
# Tarih:   16.05.2026
# =========================================================
# Açıklama: AST (Soyut Sözdizim Ağacı) düğüm sınıfları ve
#            Parser (Sözdizimsel Analizci) modülü. Parser,
#            Lexer'dan gelen token listesini tüketerek dilin
#            gramerine uygun bir ağaç yapısı (AST) inşa eder.
# =========================================================

from lexer import (
    Token, TOKEN_SAYI, TOKEN_DEGISKEN, TOKEN_ARTI, TOKEN_EKSI, 
    TOKEN_CARP, TOKEN_BOL, TOKEN_ESIT, TOKEN_ATAMA, TOKEN_BUYUK, 
    TOKEN_KUCUK, TOKEN_IF, TOKEN_ELSE, TOKEN_LBRACE, TOKEN_RBRACE,
    TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_EOF,
)

class SayiDugumu:
    def __init__(self, deger, satir: int) -> None:
        self.deger = deger
        self.satir = satir
    def __repr__(self) -> str: return f"SayiDugumu({self.deger})"

class DegiskenDugumu:
    def __init__(self, isim: str, satir: int) -> None:
        self.isim  = isim
        self.satir = satir
    def __repr__(self) -> str: return f"DegiskenDugumu({self.isim})"

class IkiliIslemDugumu:
    def __init__(self, sol, operator: str, sag, satir: int) -> None:
        self.sol      = sol
        self.operator = operator
        self.sag      = sag
        self.satir    = satir
    def __repr__(self) -> str: return f"IkiliIslemDugumu({self.sol} {self.operator} {self.sag})"

class AtamaDugumu:
    def __init__(self, degisken_adi: str, ifade, satir: int) -> None:
        self.degisken_adi = degisken_adi
        self.ifade        = ifade
        self.satir        = satir
    def __repr__(self) -> str: return f"AtamaDugumu({self.degisken_adi} = {self.ifade})"

class KosulDugumu:
    def __init__(self, kosul_ifadesi, dogru_blok: list, yanlis_blok: list, satir: int) -> None:
        self.kosul_ifadesi = kosul_ifadesi
        self.dogru_blok    = dogru_blok    
        self.yanlis_blok   = yanlis_blok   
        self.satir         = satir
    def __repr__(self) -> str: return f"KosulDugumu(kosul={self.kosul_ifadesi}, dogru={self.dogru_blok}, yanlis={self.yanlis_blok})"

class ProgramDugumu:
    def __init__(self, deyimler: list) -> None:
        self.deyimler = deyimler
    def __repr__(self) -> str: return f"ProgramDugumu({self.deyimler})"


class ParserHatasi(Exception):
    def __init__(self, mesaj: str, satir: int) -> None:
        super().__init__(mesaj)
        self.satir = satir


class Parser:
    def __init__(self, token_listesi: list) -> None:
        self.token_listesi = token_listesi
        self.konum         = 0   

    def _mevcut_token(self) -> Token:
        return self.token_listesi[self.konum]

    def _ilerle(self) -> Token:
        token = self.token_listesi[self.konum]
        if self.konum < len(self.token_listesi) - 1:
            self.konum += 1
        return token

    def _tüket(self, beklenen_tur: str) -> Token:
        token = self._mevcut_token()
        if token.tur != beklenen_tur:
            raise ParserHatasi(f"Beklenen token '{beklenen_tur}', ancak '{token.tur}' bulundu.", token.satir)
        return self._ilerle()

    def parse(self) -> ProgramDugumu:
        deyim_listesi = []
        while self._mevcut_token().tur != TOKEN_EOF:
            deyim_listesi.append(self._deyim())
        return ProgramDugumu(deyim_listesi)

    def _deyim(self):
        token = self._mevcut_token()
        if (token.tur == TOKEN_DEGISKEN and self.konum + 1 < len(self.token_listesi) 
                and self.token_listesi[self.konum + 1].tur == TOKEN_ATAMA):
            return self._atama_deyimi()
        if token.tur == TOKEN_IF:
            return self._kosul_deyimi()
        return self._ifade()

    def _atama_deyimi(self) -> AtamaDugumu:
        degisken_token = self._tüket(TOKEN_DEGISKEN)
        atama_token    = self._tüket(TOKEN_ATAMA)
        ifade_dugumu   = self._ifade()
        return AtamaDugumu(degisken_token.deger, ifade_dugumu, atama_token.satir)

    def _kosul_deyimi(self) -> KosulDugumu:
        if_token = self._tüket(TOKEN_IF)
        kosul    = self._ifade()            
        self._tüket(TOKEN_LBRACE)
        dogru_blok = self._blok()
        self._tüket(TOKEN_RBRACE)

        yanlis_blok = []
        if self._mevcut_token().tur == TOKEN_ELSE:
            self._ilerle()                  
            self._tüket(TOKEN_LBRACE)
            yanlis_blok = self._blok()
            self._tüket(TOKEN_RBRACE)
        return KosulDugumu(kosul, dogru_blok, yanlis_blok, if_token.satir)

    def _blok(self) -> list:
        deyim_listesi = []
        while self._mevcut_token().tur not in (TOKEN_RBRACE, TOKEN_EOF):
            deyim_listesi.append(self._deyim())
        return deyim_listesi

    def _ifade(self):
        sol = self._toplam()
        while self._mevcut_token().tur in (TOKEN_BUYUK, TOKEN_KUCUK, TOKEN_ESIT):
            operator_token = self._ilerle()
            sag = self._toplam()
            sol = IkiliIslemDugumu(sol, operator_token.deger, sag, operator_token.satir)
        return sol

    def _toplam(self):
        sol = self._carpim()
        while self._mevcut_token().tur in (TOKEN_ARTI, TOKEN_EKSI):
            operator_token = self._ilerle()
            sag = self._carpim()
            sol = IkiliIslemDugumu(sol, operator_token.deger, sag, operator_token.satir)
        return sol

    def _carpim(self):
        sol = self._birincil()
        while self._mevcut_token().tur in (TOKEN_CARP, TOKEN_BOL):
            operator_token = self._ilerle()
            sag = self._birincil()
            sol = IkiliIslemDugumu(sol, operator_token.deger, sag, operator_token.satir)
        return sol

    def _birincil(self):
        token = self._mevcut_token()
        if token.tur == TOKEN_SAYI:
            self._ilerle()
            return SayiDugumu(token.deger, token.satir)
        if token.tur == TOKEN_DEGISKEN:
            self._ilerle()
            return DegiskenDugumu(token.deger, token.satir)
        if token.tur == TOKEN_LPAREN:
            self._tüket(TOKEN_LPAREN)
            ic_ifade = self._ifade()
            self._tüket(TOKEN_RPAREN)
            return ic_ifade
        raise ParserHatasi(f"Beklenmeyen token: '{token.deger}'", token.satir)
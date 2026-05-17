# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 142
# Tarih:   17.05.2026
# =========================================================
# Açıklama: AST (Soyut Sözdizim Ağacı) düğüm sınıfları ve
#            Parser (Sözdizimsel Analizci) modülü. Parser,
#            Lexer'dan gelen token listesini özyinelemeli iniş
#            (Recursive Descent) algoritmasıyla tüketerek dilin
#            gramerine uygun hiyerarşik bir ağaç yapısı inşa eder.
# =========================================================

from lexer import (
    Token, TOKEN_SAYI, TOKEN_DEGISKEN, TOKEN_ARTI, TOKEN_EKSI, 
    TOKEN_CARP, TOKEN_BOL, TOKEN_ESIT, TOKEN_ATAMA, TOKEN_BUYUK, 
    TOKEN_KUCUK, TOKEN_IF, TOKEN_ELSE, TOKEN_LBRACE, TOKEN_RBRACE,
    TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_EOF,
)

# ===========================================================================
# SOYUT SÖZDİZİM AĞACI (AST) DÜĞÜM TANIMLAMALARI
# ===========================================================================

class SayiDugumu:
    """Ağaçtaki sabit sayısal (int/float) değerleri temsil eden yaprak düğüm."""
    def __init__(self, deger, satir: int) -> None:
        self.deger = deger
        self.satir = satir
    def __repr__(self) -> str: return f"SayiDugumu({self.deger})"


class DegiskenDugumu:
    """Ağaçtaki tanımlayıcıları/değişken isimlerini temsil eden yaprak düğüm."""
    def __init__(self, isim: str, satir: int) -> None:
        self.isim  = isim
        self.satir = satir
    def __repr__(self) -> str: return f"DegiskenDugumu({self.isim})"


class IkiliIslemDugumu:
    """Aritmetik ve mantıksal tüm ikili (binary) işlemleri (+, -, *, /, >, <, ==) temsil eden düğüm."""
    def __init__(self, sol, operator: str, sag, satir: int) -> None:
        self.sol      = sol       # İşlemin sol tarafındaki alt ağaç
        self.operator = operator  # Uygulanacak işlem sembolü
        self.sag      = sag       # İşlemin sağ tarafındaki alt ağaç
        self.satir    = satir
    def __repr__(self) -> str: return f"IkiliIslemDugumu({self.sol} {self.operator} {self.sag})"


class AtamaDugumu:
    """Değişken değer atama işlemlerini (=) temsil eden yapısal düğüm."""
    def __init__(self, degisken_adi: str, ifade, satir: int) -> None:
        self.degisken_adi = degisken_adi  # Atama yapılacak hedef değişkenin adı
        self.ifade        = ifade         # Değişkene atanacak ifadenin AST kökü
        self.satir        = satir
    def __repr__(self) -> str: return f"AtamaDugumu({self.degisken_adi} = {self.ifade})"


class KosulDugumu:
    """'if-else' kontrol bloklarını ve dallanma mantığını temsil eden karmaşık düğüm."""
    def __init__(self, kosul_ifadesi, dogru_blok: list, yanlis_blok: list, satir: int) -> None:
        self.kosul_ifadesi = kosul_ifadesi  # Doğruluğu kontrol edilecek mantıksal ifade
        self.dogru_blok    = dogru_blok     # Koşul True ise yürütülecek deyim listesi
        self.yanlis_blok   = yanlis_blok    # Koşul False ise yürütülecek (else) deyim listesi
        self.satir         = satir
    def __repr__(self) -> str: return f"KosulDugumu(kosul={self.kosul_ifadesi}, dogru={self.dogru_blok}, yanlis={self.yanlis_blok})"


class ProgramDugumu:
    """Oluşturulan tüm AST'nin en tepesindeki ana kök düğüm (Root Node)."""
    def __init__(self, deyimler: list) -> None:
        self.deyimler = deyimler  # Programı oluşturan sıralı deyimler/satırlar listesi
    def __repr__(self) -> str: return f"ProgramDugumu({self.deyimler})"


# ===========================================================================
# SÖZDİZİM HATA SINIFI (PARSER ERROR)
# ===========================================================================

class ParserHatasi(Exception):
    """Sözdizim kurallarına uyulmadığında (Grammar Violation) fırlatılan hata sınıfı."""
    def __init__(self, mesaj: str, satir: int) -> None:
        super().__init__(mesaj)
        self.satir = satir


# ===========================================================================
# SÖZDİZİM ANALİZCİSİ (PARSER ENGINE)
# ===========================================================================

class Parser:
    """Token listesini dilin BNF kurallarına göre analiz ederek hiyerarşik AST'ye dönüştüren sınıf."""
    def __init__(self, token_listesi: list) -> None:
        self.token_listesi = token_listesi
        self.konum         = 0   # Token listesindeki anlık okuma indeksi

    def _mevcut_token(self) -> Token:
        """Şu an incelenmekte olan güncel Token nesnesini döndürür."""
        return self.token_listesi[self.konum]

    def _ilerle(self) -> Token:
        """Token indeksini bir adım ileri taşır ve bir önceki token'ı döndürür."""
        token = self.token_listesi[self.konum]
        if self.konum < len(self.token_listesi) - 1:
            self.konum += 1
        return token

    def _tüket(self, beklenen_tur: str) -> Token:
        """
        Sözdizimsel doğrulamadır. Mevcut token beklenen türdeyse listeyi ilerletir,
        aksi takdirde katı bir ParserHatasi (Syntax Error) fırlatır.
        """
        token = self._mevcut_token()
        if token.tur != beklenen_tur:
            raise ParserHatasi(f"Beklenen token '{beklenen_tur}', ancak '{token.tur}' bulundu.", token.satir)
        return self._ilerle()

    def parse(self) -> ProgramDugumu:
        """Ayrıştırma işlemini başlatan dış arayüz. EOF görene kadar deyimleri toplar."""
        deyim_listesi = []
        while self._mevcut_token().tur != TOKEN_EOF:
            deyim_listesi.append(self._deyim())
        return ProgramDugumu(deyim_listesi)

    def _deyim(self):
        """Dilin en tepesindeki deyim (statement) kurallarını dallandırır (Atama, Koşul veya İfade)."""
        token = self._mevcut_token()
        
        # İleriye Bakış (Lookahead): Mevcut token değişken ve bir sonrası '=' ise bu bir atama deyimidir.
        if (token.tur == TOKEN_DEGISKEN and self.konum + 1 < len(self.token_listesi) 
                and self.token_listesi[self.konum + 1].tur == TOKEN_ATAMA):
            return self._atama_deyimi()
            
        # 'if' anahtar kelimesi ile başlayan blok yapıları
        if token.tur == TOKEN_IF:
            return self._kosul_deyimi()
            
        # Hiçbir yapıya uymuyorsa yalın bir matematiksel/mantıksal ifadedir
        return self._ifade()

    def _atama_deyimi(self) -> AtamaDugumu:
        """Gramer: <atama_deyimi> ::= DEGISKEN ATAMA <ifade> yapısını ayrıştırır."""
        degisken_token = self._tüket(TOKEN_DEGISKEN)
        atama_token    = self._tüket(TOKEN_ATAMA)
        ifade_dugumu   = self._ifade()
        return AtamaDugumu(degisken_token.deger, ifade_dugumu, atama_token.satir)

    def _kosul_deyimi(self) -> KosulDugumu:
        """Gramer: <kosul_deyimi> ::= IF <ifade> LBRACE <blok> RBRACE [ELSE LBRACE <blok> RBRACE]"""
        if_token = self._tüket(TOKEN_IF)
        kosul    = self._ifade()            # Koşulun mantıksal ifadesi çözülür
        
        # Doğru (True) ise çalışacak gövdenin küme parantezleri içi ayrıştırılır
        self._tüket(TOKEN_LBRACE)
        dogru_blok = self._blok()
        self._tüket(TOKEN_RBRACE)

        # İsteğe bağlı (Optional) Else bloğunun kontrolü
        yanlis_blok = []
        if self._mevcut_token().tur == TOKEN_ELSE:
            self._ilerle()                  # 'else' token'ı geçilir
            self._tüket(TOKEN_LBRACE)
            yanlis_blok = self._blok()
            self._tüket(TOKEN_RBRACE)
            
        return KosulDugumu(kosul, dogru_blok, yanlis_blok, if_token.satir)

    def _blok(self) -> list:
        """Küme parantezleri içerisindeki çoklu kod satırlarını/deyimleri yutan yardımcı kural."""
        deyim_listesi = []
        while self._mevcut_token().tur not in (TOKEN_RBRACE, TOKEN_EOF):
            deyim_listesi.append(self._deyim())
        return deyim_listesi

    # -----------------------------------------------------------------------
# İŞLEM ÖNCELİĞİ HİYERARŞİSİ (OPERATOR PRECEDENCE)
# Hiyerarşi (Düşükten Yükseğe): _ifade (>, <, ==) -> _toplam (+, -) -> _carpim (*, /) -> _birincil
# -----------------------------------------------------------------------

    def _ifade(self):
        """En düşük öncelikli karşılaştırma operatörlerini (>, <, ==) yöneten katman."""
        sol = self._toplam()
        while self._mevcut_token().tur in (TOKEN_BUYUK, TOKEN_KUCUK, TOKEN_ESIT):
            operator_token = self._ilerle()
            sag = self._toplam()
            sol = IkiliIslemDugumu(sol, operator_token.deger, sag, operator_token.satir)
        return sol

    def _toplam(self):
        """Orta öncelikli toplama ve çıkarma (+, -) işlemlerini yöneten katman."""
        sol = self._carpim()
        while self._mevcut_token().tur in (TOKEN_ARTI, TOKEN_EKSI):
            operator_token = self._ilerle()
            sag = self._carpim()
            sol = IkiliIslemDugumu(sol, operator_token.deger, sag, operator_token.satir)
        return sol

    def _carpim(self):
        """Yüksek öncelikli çarpma ve bölme (*, /) işlemlerini yöneten katman."""
        sol = self._birincil()
        while self._mevcut_token().tur in (TOKEN_CARP, TOKEN_BOL):
            operator_token = self._ilerle()
            sag = self._birincil()
            sol = IkiliIslemDugumu(sol, operator_token.deger, sag, operator_token.satir)
        return sol

    def _birincil(self):
        """
        En yüksek öncelikli temel yapı taşlarını ayrıştırır (Sayı, Değişken çağrısı veya parantez).
        Parantez içi ifadeleri tekrar en üst kurala (_ifade) yönlendirerek hiyerarşiyi sıfırlar.
        """
        token = self._mevcut_token()
        
        if token.tur == TOKEN_SAYI:
            self._ilerle()
            return SayiDugumu(token.deger, token.satir)
            
        if token.tur == TOKEN_DEGISKEN:
            self._ilerle()
            return DegiskenDugumu(token.deger, token.satir)
            
        if token.tur == TOKEN_LPAREN:
            self._tüket(TOKEN_LPAREN)
            ic_ifade = self._ifade()  # Parantez içi en yüksek öncelikle yeniden işlenir
            self._tüket(TOKEN_RPAREN)
            return ic_ifade
            
        # Dilin gramer yapısına uymayan geçersiz ifade durumu (Parser Error Case)
        raise ParserHatasi(f"Beklenmeyen token: '{token.deger}'", token.satir)
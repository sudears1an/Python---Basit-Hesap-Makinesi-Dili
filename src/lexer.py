# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 1
# Tarih:   16.05.2026
# =========================================================
# Açıklama: Lexer (Sözcüksel Analizci) modülü. Kaynak kodu
#            karakter karakter tarayarak anlamlı token dizisi
#            üretir. Her token bir tür etiketi ve değer çifti
#            ile temsil edilir. Bilinmeyen karakterler için
#            LexerHatasi fırlatır.
# =========================================================

# ---------------------------------------------------------------------------
# TOKEN TÜRLERİ — Dilin tanıdığı tüm sembolik birimlerin sabit etiketleri
# ---------------------------------------------------------------------------
TOKEN_SAYI       = "SAYI"        # Tam ya da ondalıklı sayı sabiti
TOKEN_DEGISKEN   = "DEGISKEN"    # Harf ile başlayan tanımlayıcı
TOKEN_ARTI       = "ARTI"        # + operatörü
TOKEN_EKSI       = "EKSI"        # - operatörü
TOKEN_CARP       = "CARP"        # * operatörü
TOKEN_BOL        = "BOL"         # / operatörü
TOKEN_ESIT       = "ESIT"        # == karşılaştırma operatörü
TOKEN_ATAMA      = "ATAMA"       # = atama operatörü
TOKEN_BUYUK      = "BUYUK"       # > karşılaştırma operatörü
TOKEN_KUCUK      = "KUCUK"       # < karşılaştırma operatörü
TOKEN_IF         = "IF"          # 'if' anahtar kelimesi
TOKEN_ELSE       = "ELSE"        # 'else' anahtar kelimesi
TOKEN_LBRACE     = "LBRACE"      # { sol küme parantezi
TOKEN_RBRACE     = "RBRACE"      # } sağ küme parantezi
TOKEN_LPAREN     = "LPAREN"      # ( sol yuvarlak parantez
TOKEN_RPAREN     = "RPAREN"      # ) sağ yuvarlak parantez
TOKEN_EOF        = "EOF"         # Kaynak metninin sonu

# Dil tarafından ayrılmış anahtar kelimeler sözlüğü.
# Bir tanımlayıcı bu tabloda bulunursa token türü değiştirilir.
ANAHTAR_KELIMELER = {
    "if":   TOKEN_IF,
    "else": TOKEN_ELSE,
}


class LexerHatasi(Exception):
    """Sözcüksel analiz sırasında karşılaşılan hataları temsil eder."""
    def __init__(self, mesaj: str, satir: int) -> None:
        super().__init__(mesaj)
        self.satir = satir


class Token:
    """Tek bir sözcüksel birimi (token) temsil eden veri nesnesi."""
    def __init__(self, tur: str, deger, satir: int) -> None:
        self.tur   = tur
        self.deger = deger
        self.satir = satir

    def __repr__(self) -> str:
        return f"Token({self.tur}, {self.deger!r}, satir={self.satir})"


class Lexer:
    """Kaynak kodu karakter karakter tarayan sözcüksel analizci."""
    def __init__(self, kaynak_kod: str) -> None:
        self.kaynak_kod    = kaynak_kod
        self.konum         = 0          
        self.satir         = 1          
        self.token_listesi = []         

    def _mevcut_karakter(self):
        if self.konum < len(self.kaynak_kod):
            return self.kaynak_kod[self.konum]
        return None

    def _sonraki_karakter(self):
        sonraki_konum = self.konum + 1
        if sonraki_konum < len(self.kaynak_kod):
            return self.kaynak_kod[sonraki_konum]
        return None

    def _ilerle(self):
        if self.konum < len(self.kaynak_kod):
            if self.kaynak_kod[self.konum] == "\n":
                self.satir += 1
            self.konum += 1

    def _bosluk_atla(self):
        while self._mevcut_karakter() is not None and self._mevcut_karakter() in " \t\r\n":
            self._ilerle()

    def _sayi_oku(self) -> Token:
        baslangic_satir = self.satir
        tampon = ""
        nokta_sayisi = 0

        while self._mevcut_karakter() is not None and (
            self._mevcut_karakter().isdigit() or self._mevcut_karakter() == "."
        ):
            if self._mevcut_karakter() == ".":
                nokta_sayisi += 1
                if nokta_sayisi > 1:
                    break
            tampon += self._mevcut_karakter()
            self._ilerle()

        sayisal_deger = float(tampon) if "." in tampon else int(tampon)
        return Token(TOKEN_SAYI, sayisal_deger, baslangic_satir)

    def _tanimlayici_oku(self) -> Token:
        baslangic_satir = self.satir
        tampon = ""

        while self._mevcut_karakter() is not None and (
            self._mevcut_karakter().isalnum() or self._mevcut_karakter() == "_"
        ):
            tampon += self._mevcut_karakter()
            self._ilerle()

        token_turu = ANAHTAR_KELIMELER.get(tampon, TOKEN_DEGISKEN)
        return Token(token_turu, tampon, baslangic_satir)

    def tokenize(self) -> list:
        while self._mevcut_karakter() is not None:
            if self._mevcut_karakter() in " \t\r\n":
                self._bosluk_atla()
                continue

            mevcut = self._mevcut_karakter()
            satir  = self.satir

            if mevcut.isdigit():
                self.token_listesi.append(self._sayi_oku())
                continue

            if mevcut.isalpha() or mevcut == "_":
                self.token_listesi.append(self._tanimlayici_oku())
                continue

            if mevcut == "+":
                self.token_listesi.append(Token(TOKEN_ARTI, "+", satir))
                self._ilerle()
            elif mevcut == "-":
                self.token_listesi.append(Token(TOKEN_EKSI, "-", satir))
                self._ilerle()
            elif mevcut == "*":
                self.token_listesi.append(Token(TOKEN_CARP, "*", satir))
                self._ilerle()
            elif mevcut == "/":
                self.token_listesi.append(Token(TOKEN_BOL, "/", satir))
                self._ilerle()
            elif mevcut == "=":
                if self._sonraki_karakter() == "=":
                    self.token_listesi.append(Token(TOKEN_ESIT, "==", satir))
                    self._ilerle()
                    self._ilerle()
                else:
                    self.token_listesi.append(Token(TOKEN_ATAMA, "=", satir))
                    self._ilerle()
            elif mevcut == ">":
                self.token_listesi.append(Token(TOKEN_BUYUK, ">", satir))
                self._ilerle()
            elif mevcut == "<":
                self.token_listesi.append(Token(TOKEN_KUCUK, "<", satir))
                self._ilerle()
            elif mevcut == "{":
                self.token_listesi.append(Token(TOKEN_LBRACE, "{", satir))
                self._ilerle()
            elif mevcut == "}":
                self.token_listesi.append(Token(TOKEN_RBRACE, "}", satir))
                self._ilerle()
            elif mevcut == "(":
                self.token_listesi.append(Token(TOKEN_LPAREN, "(", satir))
                self._ilerle()
            elif mevcut == ")":
                self.token_listesi.append(Token(TOKEN_RPAREN, ")", satir))
                self._ilerle()
            else:
                raise LexerHatasi(f"Bilinmeyen karakter: '{mevcut}'", satir)

        self.token_listesi.append(Token(TOKEN_EOF, None, self.satir))
        return self.token_listesi
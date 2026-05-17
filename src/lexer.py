# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 1
# Tarih:   17.05.2026
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
TOKEN_SAYI       = "SAYI"        # Tam ya da ondalıklı sayı sabitleri (Örn: 5, 3.14)
TOKEN_DEGISKEN   = "DEGISKEN"    # Harf veya alt tire ile başlayan kullanıcı tanımlayıcıları
TOKEN_ARTI       = "ARTI"        # + toplama operatörü
TOKEN_EKSI       = "EKSI"        # - çıkarma operatörü
TOKEN_CARP       = "CARP"        # * çarpma operatörü
TOKEN_BOL        = "BOL"         # / bölme operatörü
TOKEN_ESIT       = "ESIT"        # == karşılaştırma operatörü
TOKEN_ATAMA      = "ATAMA"       # = değer atama operatörü
TOKEN_BUYUK      = "BUYUK"       # > büyük mü karşılaştırma operatörü
TOKEN_KUCUK      = "KUCUK"       # < küçük mü karşılaştırma operatörü
TOKEN_IF         = "IF"          # 'if' koşul anahtar kelimesi
TOKEN_ELSE       = "ELSE"        # 'else' dallanma anahtar kelimesi
TOKEN_LBRACE     = "LBRACE"      # { sol küme parantezi (Blok başlangıcı)
TOKEN_RBRACE     = "RBRACE"      # } sağ küme parantezi (Blok bitişi)
TOKEN_LPAREN     = "LPAREN"      # ( sol yuvarlak parantez (İşlem önceliği/koşul)
TOKEN_RPAREN     = "RPAREN"      # ) sağ yuvarlak parantez (İşlem önceliği/koşul)
TOKEN_EOF        = "EOF"         # End of File - Kaynak metninin sonunu belirten sanal token

# Dil tarafından ayrılmış (reserved) anahtar kelimeler sözlüğü.
# Genel tanımlayıcıların (DEGISKEN) dilin anahtar kelimeleriyle çakışmasını önler.
ANAHTAR_KELIMELER = {
    "if":   TOKEN_IF,
    "else": TOKEN_ELSE,
}


class LexerHatasi(Exception):
    """Sözcüksel analiz sırasında (tanımlanamayan karakterler vb.) karşılaşılan hatalar."""
    def __init__(self, mesaj: str, satir: int) -> None:
        super().__init__(mesaj)
        self.satir = satir


class Token:
    """Anlamlı hale getirilmiş her bir sözcüksel birimi temsil eden veri yapısı."""
    def __init__(self, tur: str, deger, satir: int) -> None:
        self.tur   = tur        # Token türü (Örn: TOKEN_SAYI)
        self.deger = deger      # Kaynak koddaki orijinal veya dönüştürülmüş değer
        self.satir = satir      # Token'ın tespit edildiği satır numarası

    def __repr__(self) -> str:
        return f"Token({self.tur}, {self.deger!r}, satir={self.satir})"


class Lexer:
    """Kaynak kod metnini girdi olarak alıp token listesine dönüştüren tarayıcı engine."""
    def __init__(self, kaynak_kod: str) -> None:
        self.kaynak_kod    = kaynak_kod
        self.konum         = 0           # Kaynak kod içindeki anlık karakter indeksi
        self.satir         = 1           # Hata raporlama için anlık satır takibi
        self.token_listesi = []          # Analiz sonucu üretilen token'ların sırayla tutulduğu liste

    def _mevcut_karakter(self):
        """İmlecin şu an üzerinde bulunduğu karakteri döndürür. Kod bittiyse None verir."""
        if self.konum < len(self.kaynak_kod):
            return self.kaynak_kod[self.konum]
        return None

    def _sonraki_karakter(self):
        """İmleci ilerletmeden bir sonraki karakteri kontrol eder (Lookahead - Örn: == tespiti için)."""
        sonraki_konum = self.konum + 1
        if sonraki_konum < len(self.kaynak_kod):
            return self.kaynak_kod[sonraki_konum]
        return None

    def _ilerle(self):
        """İmleci bir karakter ileri taşır. Yeni satır karakterinde satır sayacını artırır."""
        if self.konum < len(self.kaynak_kod):
            if self.kaynak_kod[self.konum] == "\n":
                self.satir += 1
            self.konum += 1

    def _bosluk_atla(self):
        """Kodun yürütülmesini etkilemeyen boşluk, tab ve satır başı karakterlerini yutar."""
        while self._mevcut_karakter() is not None and self._mevcut_karakter() in " \t\r\n":
            self._ilerle()

    def _sayi_oku(self) -> Token:
        """Karakterleri tarayarak tam (int) veya ondalıklı (float) sayı sabitlerini inşa eder."""
        baslangic_satir = self.satir
        tampon = ""
        nokta_sayisi = 0

        while self._mevcut_karakter() is not None and (
            self._mevcut_karakter().isdigit() or self._mevcut_karakter() == "."
        ):
            if self._mevcut_karakter() == ".":
                nokta_sayisi += 1
                if nokta_sayisi > 1:  # Birden fazla nokta içeren hatalı sayı yazımını durdurur
                    break
            tampon += self._mevcut_karakter()
            self._ilerle()

        # Sayı biçimine göre uygun Python tipine dönüştürme yapılır
        sayisal_deger = float(tampon) if "." in tampon else int(tampon)
        return Token(TOKEN_SAYI, sayisal_deger, baslangic_satir)

    def _tanimlayici_oku(self) -> Token:
        """Değişken adlarını ve 'if/else' gibi dille bütünleşik anahtar kelimeleri okur."""
        baslangic_satir = self.satir
        tampon = ""

        # Değişkenlerin alfanümerik veya alt tire olabileceğini doğrular
        while self._mevcut_karakter() is not None and (
            self._mevcut_karakter().isalnum() or self._mevcut_karakter() == "_"
        ):
            tampon += self._mevcut_karakter()
            self._ilerle()

        # Okunan kelime anahtar kelimeler tablosunda var mı kontrolü (Reserved Word Check)
        token_turu = ANAHTAR_KELIMELER.get(tampon, TOKEN_DEGISKEN)
        return Token(token_turu, tampon, baslangic_satir)

    def tokenize(self) -> list:
        """Tüm kaynak kodu baştan sona tarayarak nihai Token Listesini üreten ana döngü."""
        while self._mevcut_karakter() is not None:
            # Boşlukların temizlenmesi
            if self._mevcut_karakter() in " \t\r\n":
                self._bosluk_atla()
                continue

            mevcut = self._mevcut_karakter()
            satir  = self.satir

            # Sayısal sabit kontrolü
            if mevcut.isdigit():
                self.token_listesi.append(self._sayi_oku())
                continue

            # Tanımlayıcı veya anahtar kelime kontrolü (Harf veya _ ile başlamalı)
            if mevcut.isalpha() or mevcut == "_":
                self.token_listesi.append(self._tanimlayici_oku())
                continue

            # Tekil ve Çoklu Karakterli Operatörlerin/Sembollerin Ayırt Edilmesi
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
                # İleriye Bakış (Lookahead): Değer atama (=) mı, Karşılaştırma (==) mı?
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
                # Dilin gramerinde tanımlanmamış illegal karakter durumu (Lexer Error Case)
                raise LexerHatasi(f"Bilinmeyen karakter: '{mevcut}'", satir)

        # Ağacın düzgün sonlanması için dosya sonu belirtecinin eklenmesi
        self.token_listesi.append(Token(TOKEN_EOF, None, self.satir))
        return self.token_listesi
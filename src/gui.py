# =========================================================
# Ders: Programlama Dilleri Prensipleri
# Öğrenci: Sude Arslan
# Numara:  2230656055
# Ödev No: 1
# Tarih:   16.05.2026
# =========================================================
# Açıklama: Projenin Tkinter tabanlı Grafik Kullanıcı Arayüzü.
#            Kullanıcının kod yazmasını, hesap makinesi butonlarını
#            kullanmasını ve değişken ortamını görsel olarak
#            izlemesini sağlar.
#            Tasarım referansı: VS Code Dark+ teması.
#            Renk paleti tek bir merkezi sözlükte tutulur;
#            tüm widget'lar bu sözlükten beslenir.
# =========================================================

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Modüllerin bulunduğu src/ dizinini import yoluna ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer       import Lexer,       LexerHatasi
from parser_ast  import Parser,      ParserHatasi
from interpreter import Interpreter, CalismaSuresiHatasi


# ===========================================================================
# RENK PALETİ  —  VS Code Dark+ referanslı minimal dark mode
# Tüm arayüz bu tablodan beslenir; renk değiştirmek için tek yer burasıdır.
# ===========================================================================
PALET = {
    # Zemin katmanları (en koyu -> en açık)
    "zemin_0"        : "#1e1e1e",   # Ana pencere zemini  (VS Code Activity Bar)
    "zemin_1"        : "#252526",   # Panel arkaplanı     (VS Code Side Bar)
    "zemin_2"        : "#2d2d2d",   # Editör arkaplanı    (VS Code Editor)
    "zemin_3"        : "#3c3c3c",   # Hover / seçim zemini
    "zemin_4"        : "#464646",   # İkincil hover

    # Yazı renkleri
    "yazi_birincil"  : "#d4d4d4",   # Genel metin
    "yazi_ikincil"   : "#858585",   # Soluk yardımcı metin
    "yazi_ucuncul"   : "#5a5a5a",   # Satır numaraları, devre dışı öğeler
    "yazi_baslik"    : "#cccccc",   # Panel başlıkları

    # Aksan renkleri (yalnızca 2 ton)
    "aksan_mavi"     : "#007acc",   # VS Code mavi — birincil eylem
    "aksan_mavi_a"   : "#005f9e",   # Mavi buton hover
    "aksan_yesil"    : "#4ec9b0",   # VS Code teal — başarı / değişken vurgusu
    "aksan_yesil_a"  : "#3aab97",   # Teal hover

    # Konsol renkleri
    "konsol_bilgi"   : "#858585",   # Gri — yardımcı mesajlar
    "konsol_basari"  : "#4ec9b0",   # Teal — başarılı çalışma
    "konsol_hata"    : "#ce9178",   # Pastel turuncu — hata (VS Code string rengi)
    "konsol_vurgu"   : "#9cdcfe",   # Açık mavi — önemli bilgi
    "konsol_degisken": "#dcdcaa",   # Sarımsı — değişken listesi (VS Code func rengi)

    # Kenarlık ve ayraçlar
    "kenar"          : "#3e3e3e",   # Panel ayırıcı çizgiler
    "kenar_ince"     : "#2a2a2a",   # Satır numarası / editör arası

    # İmleç
    "imlec"          : "#aeafad",   # Metin imleci (blok imleci hissi)
}

# Monospace yazı tipi — platforma göre sıraya konmuş tercih listesi.
MONO_FONT_ADI = "Consolas"   # Tkinter Label/Button yazı tipi adı
MONO_FONT_YEK = "Courier New"  # Fallback


# ===========================================================================
# UygulamaGUI  —  Ana uygulama sınıfı
# ===========================================================================

class UygulamaGUI:
    """
    Mini Interpreter'ın VS Code tarzı Tkinter GUI'si.

    Düzen:
        Üst başlık çubuğu (tek satır, tam genişlik)
        ──────────────────────────────────────────
        Sol Panel (editör)    |  Sağ Panel (tuşlar)
        ──────────────────────────────────────────
        Alt Panel: [Değişken Tablosu] | [Konsol]

    Özellikler:
        kok         : Tkinter kök penceresi
        interpreter : Oturumlar arası değişken ortamını koruyan nesne
    """

    def __init__(self, kok: tk.Tk) -> None:
        self.kok         = kok
        # Aynı interpreter nesnesi tüm çalıştırmalar boyunca yaşar;
        # değişkenler birikimli olarak saklanır.
        self.interpreter = Interpreter()

        self._pencereyi_yapilandir()
        self._ust_cubugu_olustur()
        self._icerik_duzeni_olustur()   # PanedWindow'ları kurar
        self._sol_paneli_olustur()
        self._sag_paneli_olustur()
        self._alt_paneli_olustur()
        self._treeview_stilini_ayarla()
        self._klavye_kisayollarini_baglat()
        self._baslangic_icerigini_yukle()

    # ======================================================================
    # 1 - PENCERE & CERCEVE KURULUMU
    # ======================================================================

    def _pencereyi_yapilandir(self) -> None:
        """
        Pencere başlığı, boyutu, arka plan rengi ve minimum boyut kısıtlaması.
        Pencere ekran merkezine konumlanır.
        """
        self.kok.title("Mini Interpreter  |  Programlama Dilleri Prensipleri")
        self.kok.configure(bg=PALET["zemin_0"])
        self.kok.minsize(1080, 660)

        # Ekran merkezine konumla
        ekran_g = self.kok.winfo_screenwidth()
        ekran_y = self.kok.winfo_screenheight()
        gen, yuk = 1260, 800
        ox = (ekran_g - gen) // 2
        oy = (ekran_y - yuk) // 2
        self.kok.geometry(f"{gen}x{yuk}+{ox}+{oy}")

        # Kapatma onayı
        self.kok.protocol("WM_DELETE_WINDOW", self._kapatma_onay)
        try:
            self.kok.iconbitmap(default="")
        except Exception:
            pass

    def _ust_cubugu_olustur(self) -> None:
        """
        Tek satırlık başlık çubuğu.
        Sol: uygulama adı  /  Sağ: ders bilgisi + öğrenci kimliği.
        İnce alt kenar çizgisi ile içerik alanından ayrılır.
        """
        bar = tk.Frame(self.kok, bg=PALET["zemin_1"], height=40)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        # Sol: uygulama adı
        tk.Label(
            bar,
            text="  </> Mini Interpreter",
            font=(MONO_FONT_ADI, 11, "bold"),
            bg=PALET["zemin_1"],
            fg=PALET["yazi_birincil"],
            anchor="w",
        ).pack(side="left", padx=(4, 0), fill="y")

        # Sağ: öğrenci kimliği
        tk.Label(
            bar,
            text="Sude Arslan  |  2230656055  ",
            font=(MONO_FONT_ADI, 9),
            bg=PALET["zemin_1"],
            fg=PALET["yazi_ikincil"],
            anchor="e",
        ).pack(side="right", fill="y")

        # Sağ: ders bilgisi
        tk.Label(
            bar,
            text="Programlama Dilleri Prensipleri  |  Odev 1     ",
            font=(MONO_FONT_ADI, 9),
            bg=PALET["zemin_1"],
            fg=PALET["yazi_ucuncul"],
            anchor="e",
        ).pack(side="right", fill="y")

        # Alt ayraç
        tk.Frame(self.kok, bg=PALET["kenar"], height=1).pack(fill="x", side="top")

    def _icerik_duzeni_olustur(self) -> None:
        """
        Iki kademeli PanedWindow yapisi kurar.
        yatay_bolme: sol (editor) | sag (tus takimi)
        dikey_bolme: ust (editor+tus) | alt (konsol+tablo)
        """
        # Ust bolge — editoru barindiran yatay bolme
        self.yatay_bolme = tk.PanedWindow(
            self.kok,
            orient="horizontal",
            bg=PALET["kenar"],
            sashwidth=1,
            sashrelief="flat",
            bd=0,
        )
        self.yatay_bolme.pack(fill="both", expand=True)

        # Alt bolge — konsol + degisken tablosunu barindiran dikey bolme
        self.dikey_bolme = tk.PanedWindow(
            self.kok,
            orient="vertical",
            bg=PALET["kenar"],
            sashwidth=1,
            sashrelief="flat",
            bd=0,
        )
        self.dikey_bolme.pack(fill="x", side="bottom")

    # ======================================================================
    # 2 - SOL PANEL — KOD EDITORU
    # ======================================================================

    def _sol_paneli_olustur(self) -> None:
        """
        Sol panel; satir numarali monospace kod editoru ve
        islem butonlarindan olusur.
        """
        self.sol_cerceve = tk.Frame(self.yatay_bolme, bg=PALET["zemin_1"])
        self.yatay_bolme.add(self.sol_cerceve, minsize=420, width=720)

        # Panel baslik cubuğu
        self._panel_baslik(self.sol_cerceve, "EDITOR", "Ctrl+Enter = Calistir")

        # Editoru olustur
        self._editoru_olustur()

        # Eylem butonlari seridi
        self._eylem_butonlarini_olustur()

    def _panel_baslik(
        self,
        ebeveyn: tk.Widget,
        sol_metin: str,
        sag_metin: str = "",
    ) -> tk.Frame:
        """
        Her panelin ustune ince, mat bir baslik cubuğu ekler.
        Sol: bolum adi / Sag: kisayol ipucu.
        Dondurecek: Olusturulan Frame (gerekirse dis kaynak eklenebilir).
        """
        cerceve = tk.Frame(ebeveyn, bg=PALET["zemin_0"], height=26)
        cerceve.pack(fill="x")
        cerceve.pack_propagate(False)

        tk.Label(
            cerceve,
            text=f"  {sol_metin}",
            font=(MONO_FONT_ADI, 8),
            bg=PALET["zemin_0"],
            fg=PALET["yazi_ucuncul"],
            anchor="w",
        ).pack(side="left", fill="y")

        if sag_metin:
            tk.Label(
                cerceve,
                text=f"{sag_metin}  ",
                font=(MONO_FONT_ADI, 8),
                bg=PALET["zemin_0"],
                fg=PALET["yazi_ucuncul"],
                anchor="e",
            ).pack(side="right", fill="y")

        # Baslik alti 1 px ayrac
        tk.Frame(ebeveyn, bg=PALET["kenar"], height=1).pack(fill="x")
        return cerceve

    def _editoru_olustur(self) -> None:
        """
        Satir numarali kod editoru.

        Bilesenler:
            satir_canvas  — sabit genislikte, satir numaralarini cizer
            kod_alani     — asil Text widget; monospace, undo destekli
            kaydirma      — dikey + yatay Scrollbar
        """
        kapsayici = tk.Frame(self.sol_cerceve, bg=PALET["zemin_2"])
        kapsayici.pack(fill="both", expand=True)

        # Satir numarasi seridi
        self.satir_canvas = tk.Canvas(
            kapsayici,
            width=46,
            bg=PALET["zemin_2"],
            highlightthickness=0,
            bd=0,
        )
        self.satir_canvas.pack(side="left", fill="y")

        # Satir numarasi ile editör arasinda 1 px cizgi
        tk.Frame(kapsayici, bg=PALET["kenar_ince"], width=1).pack(
            side="left", fill="y"
        )

        # Kaydirma cubuklari
        dik_kaydir = tk.Scrollbar(
            kapsayici, orient="vertical", width=10,
            bg=PALET["zemin_3"], troughcolor=PALET["zemin_1"],
        )
        yat_kaydir = tk.Scrollbar(
            kapsayici, orient="horizontal", width=10,
            bg=PALET["zemin_3"], troughcolor=PALET["zemin_1"],
        )
        dik_kaydir.pack(side="right",  fill="y")
        yat_kaydir.pack(side="bottom", fill="x")

        # Ana kod editoru Text widget'i
        self.kod_alani = tk.Text(
            kapsayici,
            font=(MONO_FONT_ADI, 12),
            bg=PALET["zemin_2"],
            fg=PALET["yazi_birincil"],
            insertbackground=PALET["imlec"],
            selectbackground=PALET["aksan_mavi"],
            selectforeground="#ffffff",
            relief="flat",
            bd=0,
            wrap="none",
            undo=True,
            maxundo=50,
            padx=10,
            pady=8,
            insertwidth=2,
            yscrollcommand=dik_kaydir.set,
            xscrollcommand=yat_kaydir.set,
        )
        self.kod_alani.pack(side="left", fill="both", expand=True)

        # Kaydirma cubuklerini editore ve satir canvas'ina baglantila
        dik_kaydir.config(command=self._dikey_kaydir)
        yat_kaydir.config(command=self.kod_alani.xview)

        # Editör olaylarini dinle — satir numaralarini guncelle
        for olay in ("<<Modified>>", "<KeyRelease>", "<ButtonRelease>", "<Configure>"):
            self.kod_alani.bind(olay, self._satir_numaralarini_guncelle)
        self.kod_alani.bind(
            "<MouseWheel>",
            lambda e: self.kok.after(5, self._satir_numaralarini_guncelle),
        )

        # Ilk çizim — pencere tamamen olusunca yapilmali
        self.kok.after(80, self._satir_numaralarini_guncelle)

    def _dikey_kaydir(self, *arglar) -> None:
        """Kaydirma cubuğu hareketi: editörü ve satir canvas'ini esit kaydirma."""
        self.kod_alani.yview(*arglar)
        self.kok.after(5, self._satir_numaralarini_guncelle)

    def _satir_numaralarini_guncelle(self, _olay=None) -> None:
        """
        Satir numarasi Canvas'ini yeniden cizer.
        Gorunen satir araligini dlineinfo() ile ogrenip
        yalnizca ekrandaki satirlari isleme alir (performans icin).
        """
        self.satir_canvas.delete("all")

        ilk   = self.kod_alani.index("@0,0")
        son   = self.kod_alani.index(f"@0,{self.kod_alani.winfo_height()}")
        ilk_s = int(ilk.split(".")[0])
        son_s = int(son.split(".")[0])

        for satir_no in range(ilk_s, son_s + 1):
            bilgi = self.kod_alani.dlineinfo(f"{satir_no}.0")
            if bilgi is None:
                continue
            # bilgi[1] = satirin piksel y ust kenari
            y = bilgi[1] + 8   # Editörün pady=8 dolgusuyla hizala
            self.satir_canvas.create_text(
                38, y,
                text=str(satir_no),
                anchor="ne",
                fill=PALET["yazi_ucuncul"],
                font=(MONO_FONT_ADI, 10),
            )

    def _eylem_butonlarini_olustur(self) -> None:
        """
        Editörün altindaki islem seridi.
        Uc buton: [Calistir (mavi, ana eylem)]  [Editörü Temizle]  [Ortami Sifirla]
        """
        # Ince ust ayrac
        tk.Frame(self.sol_cerceve, bg=PALET["kenar"], height=1).pack(fill="x")

        serit = tk.Frame(self.sol_cerceve, bg=PALET["zemin_1"], height=46)
        serit.pack(fill="x")
        serit.pack_propagate(False)

        ic = tk.Frame(serit, bg=PALET["zemin_1"])
        ic.pack(side="left", padx=12, pady=8)

        # Birincil buton: Calistir (aksan mavi)
        self.btn_calistir = self._buton_olustur(
            ic,
            metin="  Run  Kodu Calistir",
            normal_bg=PALET["aksan_mavi"],
            hover_bg=PALET["aksan_mavi_a"],
            komut=self._kodu_calistir,
            genislik=20,
            kalin=True,
        )
        self.btn_calistir.pack(side="left", padx=(0, 6))

        # Ikincil buton: Temizle
        self.btn_temizle = self._buton_olustur(
            ic,
            metin="  Editörü Temizle",
            normal_bg=PALET["zemin_3"],
            hover_bg=PALET["zemin_4"],
            komut=self._editoru_temizle,
        )
        self.btn_temizle.pack(side="left", padx=(0, 6))

        # Ikincil buton: Sifirla
        self.btn_sifirla = self._buton_olustur(
            ic,
            metin="  Ortami Sifirla",
            normal_bg=PALET["zemin_3"],
            hover_bg=PALET["zemin_4"],
            komut=self._ortami_sifirla,
        )
        self.btn_sifirla.pack(side="left")

    def _buton_olustur(
        self,
        ebeveyn: tk.Widget,
        metin: str,
        normal_bg: str,
        hover_bg: str,
        komut,
        genislik: int = 18,
        kalin: bool = False,
    ) -> tk.Button:
        """
        Tek tip buton fabrikasi. Tum butonlar ayni yukseklik ve relief'e sahip;
        yalnizca renk ve etiket degisir. Hover efektini otomatik baglar.

        Parametreler:
            ebeveyn   : Butonun yerlestirilecegi widget
            metin     : Buton etiketi
            normal_bg : Varsayilan arkaplan rengi
            hover_bg  : Fare uzerinde arkaplan rengi
            komut     : Tiklama komutu
            genislik  : Karakter cinsinden genislik
            kalin     : True ise yazi kalin (bold)

        Dondurecek: Yapilandirilmis tk.Button nesnesi
        """
        agirlik = "bold" if kalin else "normal"
        btn = tk.Button(
            ebeveyn,
            text=metin,
            font=(MONO_FONT_ADI, 10, agirlik),
            bg=normal_bg,
            fg=PALET["yazi_birincil"],
            activebackground=hover_bg,
            activeforeground=PALET["yazi_birincil"],
            relief="flat",
            bd=0,
            padx=14,
            pady=5,
            width=genislik,
            cursor="hand2",
            command=komut,
        )
        btn.bind("<Enter>", lambda e, b=btn, r=hover_bg:  b.configure(bg=r))
        btn.bind("<Leave>", lambda e, b=btn, r=normal_bg: b.configure(bg=r))
        return btn

    # ======================================================================
    # 3 - SAG PANEL — MINIMALIST TUS TAKIMI
    # ======================================================================

    def _sag_paneli_olustur(self) -> None:
        """
        Sag panel; minimalist, mat tonlu tus takimini barindirir.

        Tus gruplamalari:
            Dil anahtar kelimeleri — if / else / {} / = / ==
            Karsılastırma         — > / <
            Rakamlar + aritmetik  — 7-9/div  4-6/mul  1-3/sub  ()0./+
            Kontrol               — backspace / yeni satir / temizle
        """
        self.sag_cerceve = tk.Frame(self.yatay_bolme, bg=PALET["zemin_1"])
        self.yatay_bolme.add(self.sag_cerceve, minsize=240, width=295)

        # Panel baslik cubuğu
        self._panel_baslik(self.sag_cerceve, "KEYPAD")

        # Tus takimi ic kapsayicisi
        ic = tk.Frame(self.sag_cerceve, bg=PALET["zemin_1"])
        ic.pack(fill="both", expand=True, padx=12, pady=10)

        # ---- Tus tanimi matrisi ----------------------------------------
        # Formati: (etiket, editore_yazilacak_metin, renk_grubu)
        # Renk gruplari:
        #   n = normal (gri zemin)
        #   o = operator (teal yazi)
        #   k = keyword (acik mavi yazi)
        #   s = sil / geri al (pastel kirmizi)
        #   x = gorulmez doldurucu
        satirlar = [
            [("if",   "if ",      "k"), ("else",  " else ", "k"),
             ("{ }",  " {\n    ", "k"), ("  =  ", " = ",    "k")],

            [(" == ", " == ",     "k"), ("  >  ", " > ",    "k"),
             ("  <  "," < ",      "k"), ("  (  ", "(",      "n")],

            [("7",    "7",        "n"), ("8",     "8",      "n"),
             ("9",    "9",        "n"), (" / ",   " / ",    "o")],

            [("4",    "4",        "n"), ("5",     "5",      "n"),
             ("6",    "6",        "n"), (" * ",   " * ",    "o")],

            [("1",    "1",        "n"), ("2",     "2",      "n"),
             ("3",    "3",        "n"), (" - ",   " - ",    "o")],

            [("  )  ",")",        "n"), ("0",     "0",      "n"),
             (".",    ".",        "n"), (" + ",   " + ",    "o")],

            [(" <- ", "__geri_al__", "s"), (" CR ", "\n", "n"),
             ("  C  ","__temizle__", "s"), ("    ", "",   "x")],
        ]

        # Renk grubu eşleme tablosu:
        # grup -> (normal_arkaplan, hover_arkaplan, yazi_rengi)
        renk_tablosu = {
            "n": (PALET["zemin_3"],  PALET["zemin_4"],  PALET["yazi_birincil"]),
            "o": (PALET["zemin_1"],  PALET["zemin_3"],  PALET["aksan_yesil"]),
            "k": (PALET["zemin_0"],  PALET["zemin_3"],  PALET["konsol_vurgu"]),
            "s": (PALET["zemin_0"],  "#4a3030",         "#c97a72"),
            "x": (PALET["zemin_1"],  PALET["zemin_1"],  PALET["zemin_1"]),
        }

        # Izgara olusturma dongusu — her satir, her tus
        for satir in satirlar:
            satir_f = tk.Frame(ic, bg=PALET["zemin_1"])
            satir_f.pack(fill="x", pady=2)

            for etiket, metin, grup in satir:
                n_bg, h_bg, yazi = renk_tablosu[grup]

                # Gorulmez doldurucu alan
                if grup == "x":
                    tk.Frame(satir_f, bg=PALET["zemin_1"], width=48).pack(
                        side="left", padx=2, expand=True, fill="x"
                    )
                    continue

                btn = tk.Button(
                    satir_f,
                    text=etiket,
                    font=(MONO_FONT_ADI, 10),
                    bg=n_bg,
                    fg=yazi,
                    activebackground=h_bg,
                    activeforeground=yazi,
                    relief="flat",
                    bd=0,
                    pady=7,
                    cursor="hand2",
                    command=lambda m=metin: self._tusa_basildi(m),
                )
                btn.pack(side="left", padx=2, expand=True, fill="x")
                btn.bind("<Enter>", lambda e, b=btn, r=h_bg: b.configure(bg=r))
                btn.bind("<Leave>", lambda e, b=btn, r=n_bg: b.configure(bg=r))

    def _tusa_basildi(self, metin: str) -> None:
        """
        Tus takimindaki bir tusa basildiginda calisir.
        Ozel komutlari (geri al, temizle) ele alir;
        diger durumlarda metni imlecin konumuna ekler.

        Parametreler:
            metin : Editore eklenecek metin veya ozel komut etiketi
        """
        if metin == "__temizle__":
            self._editoru_temizle()
        elif metin == "__geri_al__":
            try:
                self.kod_alani.delete("insert-1c", "insert")
            except tk.TclError:
                pass
        elif metin:
            self.kod_alani.insert("insert", metin)
            self._satir_numaralarini_guncelle()

        # Odagi editore geri ver — yazmaya devam edilebilsin
        self.kod_alani.focus_set()

    # ======================================================================
    # 4 - ALT PANEL — KONSOL + DEGISKEN TABLOSU
    # ======================================================================

    def _alt_paneli_olustur(self) -> None:
        """
        Alt panel; yan yana iki esit bolumden olusur:
            Sol — Degisken Hafizasi (Treeview)
            Sag — Konsol / Hata Ciktisi (Text)

        Sabit yuksekligi 220 pikseldir.
        """
        alt_f = tk.Frame(self.dikey_bolme, bg=PALET["zemin_1"])
        self.dikey_bolme.add(alt_f, minsize=180, height=220)

        # Ince ust ayrac
        tk.Frame(alt_f, bg=PALET["kenar"], height=1).pack(fill="x")

        # Baslik cubuğu — Konsolu Temizle butonu saga yasli
        bar = tk.Frame(alt_f, bg=PALET["zemin_0"], height=26)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar,
            text="  OUTPUT PANEL",
            font=(MONO_FONT_ADI, 8),
            bg=PALET["zemin_0"],
            fg=PALET["yazi_ucuncul"],
        ).pack(side="left", fill="y")

        tk.Button(
            bar,
            text="Konsolu Temizle  ",
            font=(MONO_FONT_ADI, 8),
            bg=PALET["zemin_0"],
            fg=PALET["yazi_ucuncul"],
            activebackground=PALET["zemin_3"],
            activeforeground=PALET["yazi_birincil"],
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._konsolu_temizle,
        ).pack(side="right", fill="y")

        tk.Frame(alt_f, bg=PALET["kenar"], height=1).pack(fill="x")

        # Icerik alani — sol tablo, sag konsol
        icerik = tk.Frame(alt_f, bg=PALET["zemin_1"])
        icerik.pack(fill="both", expand=True)

        self._degisken_panelini_olustur(icerik)
        tk.Frame(icerik, bg=PALET["kenar"], width=1).pack(side="left", fill="y")
        self._konsol_panelini_olustur(icerik)

    def _degisken_panelini_olustur(self, ebeveyn: tk.Widget) -> None:
        """
        Sol alt bolum: Degisken Hafizasi.
        ttk.Treeview ile ad | deger | tur sutunlari gosterilir.
        """
        f = tk.Frame(ebeveyn, bg=PALET["zemin_1"])
        f.pack(side="left", fill="both", expand=True)

        # Alt baslik
        baslik_f = tk.Frame(f, bg=PALET["zemin_1"])
        baslik_f.pack(fill="x", padx=10, pady=(6, 3))
        tk.Label(
            baslik_f,
            text="Degisken Hafizasi  (Environment)",
            font=(MONO_FONT_ADI, 9, "bold"),
            bg=PALET["zemin_1"],
            fg=PALET["aksan_yesil"],
        ).pack(side="left")

        # Treeview kapsayicisi
        tablo_f = tk.Frame(f, bg=PALET["zemin_1"])
        tablo_f.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        kaydir = ttk.Scrollbar(tablo_f, orient="vertical")
        kaydir.pack(side="right", fill="y")

        self.degisken_tablosu = ttk.Treeview(
            tablo_f,
            columns=("ad", "deger", "tur"),
            show="headings",
            yscrollcommand=kaydir.set,
            style="Mini.Treeview",
        )
        kaydir.config(command=self.degisken_tablosu.yview)

        # Sutun baslik ve genislik ayarlari
        for stn, baslik, gen, hiza in [
            ("ad",    "Degisken Adi",  120, "w"),
            ("deger", "Deger",         110, "center"),
            ("tur",   "Tur",            80, "center"),
        ]:
            self.degisken_tablosu.heading(stn, text=baslik)
            self.degisken_tablosu.column(stn, width=gen, anchor=hiza, minwidth=50)

        self.degisken_tablosu.pack(side="left", fill="both", expand=True)

    def _treeview_stilini_ayarla(self) -> None:
        """
        ttk.Treeview icin "Mini.Treeview" adli ozel stili tanimlar.
        Bu metot __init__'te widget'lar olusturulduktan sonra cagirilir.
        """
        stil = ttk.Style()
        stil.theme_use("default")

        stil.configure(
            "Mini.Treeview",
            background=PALET["zemin_2"],
            foreground=PALET["yazi_birincil"],
            fieldbackground=PALET["zemin_2"],
            font=(MONO_FONT_ADI, 10),
            rowheight=22,
            borderwidth=0,
        )
        stil.configure(
            "Mini.Treeview.Heading",
            background=PALET["zemin_0"],
            foreground=PALET["yazi_ikincil"],
            font=(MONO_FONT_ADI, 8),
            relief="flat",
            padding=(6, 3),
        )
        stil.map(
            "Mini.Treeview",
            background=[("selected", PALET["aksan_mavi"])],
            foreground=[("selected", "#ffffff")],
        )
        # Treeview cerceve kenarligi kaldir
        stil.layout("Mini.Treeview", [
            ("Mini.Treeview.treearea", {"sticky": "nswe"})
        ])

    def _konsol_panelini_olustur(self, ebeveyn: tk.Widget) -> None:
        """
        Sag alt bolum: Konsol / Hata Ciktisi.
        Kullanici duzenleyemez (state=disabled); renkli etiketler
        ile basari/hata/bilgi mesajlari ayristirilir.
        """
        f = tk.Frame(ebeveyn, bg=PALET["zemin_1"])
        f.pack(side="left", fill="both", expand=True)

        baslik_f = tk.Frame(f, bg=PALET["zemin_1"])
        baslik_f.pack(fill="x", padx=10, pady=(6, 3))
        tk.Label(
            baslik_f,
            text="Konsol  /  Hata Ciktisi",
            font=(MONO_FONT_ADI, 9, "bold"),
            bg=PALET["zemin_1"],
            fg=PALET["aksan_mavi"],
        ).pack(side="left")

        konsol_f = tk.Frame(f, bg=PALET["zemin_2"])
        konsol_f.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        kaydir = tk.Scrollbar(
            konsol_f, orient="vertical", width=10,
            bg=PALET["zemin_3"], troughcolor=PALET["zemin_1"],
        )
        kaydir.pack(side="right", fill="y")

        self.konsol_alani = tk.Text(
            konsol_f,
            font=(MONO_FONT_ADI, 10),
            bg=PALET["zemin_2"],
            fg=PALET["konsol_bilgi"],
            insertbackground=PALET["imlec"],
            relief="flat",
            bd=0,
            wrap="word",
            state="disabled",
            padx=10,
            pady=6,
            yscrollcommand=kaydir.set,
        )
        self.konsol_alani.pack(side="left", fill="both", expand=True)
        kaydir.config(command=self.konsol_alani.yview)

        # Renk etiketi tanimlari
        self.konsol_alani.tag_configure("bilgi",    foreground=PALET["konsol_bilgi"])
        self.konsol_alani.tag_configure("basari",   foreground=PALET["konsol_basari"])
        self.konsol_alani.tag_configure("hata",     foreground=PALET["konsol_hata"])
        self.konsol_alani.tag_configure("vurgu",    foreground=PALET["konsol_vurgu"])
        self.konsol_alani.tag_configure("degisken", foreground=PALET["konsol_degisken"])

    # ======================================================================
    # 5 - BORU HATTI ENTEGRASYONU — Calistirma Mantigi
    # ======================================================================

    def _kodu_calistir(self) -> None:
        """
        "Kodu Calistir" butonu ve Ctrl+Enter ile tetiklenir.

        Akis:
            1. Editorun kaynak kodunu al.
            2. Lexer -> Parser -> Interpreter boru hattindan gecir.
            3. Basaridaki degisken tablosunu guncelle.
            4. Hata turune gore konsolda renkli mesaj yaz.
        """
        kaynak = self.kod_alani.get("1.0", "end-1c").strip()

        if not kaynak:
            self._konsola_yaz("  Editor bos — calistirilacak kod yok.\n", "bilgi")
            return

        # Calistirma baslangic ayiracisi
        self._konsola_yaz("─" * 48 + "\n", "bilgi")
        self._konsola_yaz("  Calistiriliyor...\n", "vurgu")

        try:
            # ASAMA 1 — Sozcuksel analiz
            tokenler = Lexer(kaynak).tokenize()

            # ASAMA 2 — Sozdizimsel analiz / AST olusturma
            ast = Parser(tokenler).parse()

            # ASAMA 3 — Yorumlama
            sonuc = self.interpreter.calistir(ast)

            self._konsola_yaz("  Basariyla tamamlandi.\n", "basari")

            if sonuc is not None:
                self._konsola_yaz(f"   Son deger:  {sonuc}\n", "basari")

            self._degisken_tablosunu_guncelle()

        except LexerHatasi as hata:
            self._konsola_yaz(
                f"  [SozDizimHatasi]  Satir {hata.satir}:  {hata}\n", "hata"
            )
        except ParserHatasi as hata:
            self._konsola_yaz(
                f"  [SozDizimHatasi]  Satir {hata.satir}:  {hata}\n", "hata"
            )
        except CalismaSuresiHatasi as hata:
            self._konsola_yaz(f"  {hata}\n", "hata")
        except Exception as beklenmeyen:
            self._konsola_yaz(
                f"  [BeklenmeyenHata]:  {beklenmeyen}\n", "hata"
            )

    def _degisken_tablosunu_guncelle(self) -> None:
        """
        Interpreter ortamindaki degiskenleri okuyarak Treeview tablosunu
        sifirdan doldurur. Bos ortamda bilgi satiri eklenir.
        Degisken sayisini konsolda yazar.
        """
        for satir in self.degisken_tablosu.get_children():
            self.degisken_tablosu.delete(satir)

        degiskenler = self.interpreter.ortam.tum_degiskenler()

        if not degiskenler:
            self.degisken_tablosu.insert("", "end", values=("—", "—", "bos"))
            return

        for isim, deger in sorted(degiskenler.items()):
            tur = type(deger).__name__
            # Ondalik sayilarda 6 basamak siniri
            deger_str = f"{deger:.6g}" if isinstance(deger, float) else str(deger)
            self.degisken_tablosu.insert("", "end", values=(isim, deger_str, tur))

        # Konsola ozet yaz
        self._konsola_yaz(
            "   Ortam:  " + ",  ".join(
                f"{k} = {v}" for k, v in sorted(degiskenler.items())
            ) + "\n",
            "degisken",
        )

    # ======================================================================
    # 6 - YARDIMCI EYLEM METOTLARI
    # ======================================================================

    def _editoru_temizle(self) -> None:
        """Kod editorunu tamamen siler; satir numaralarini gunceller."""
        self.kod_alani.delete("1.0", "end")
        self._satir_numaralarini_guncelle()
        self._konsola_yaz("  Editor temizlendi.\n", "bilgi")

    def _ortami_sifirla(self) -> None:
        """
        Interpreter nesnesini yeniden olusturur; degisken deposunu sifirlar.
        Treeview tablosunu temizler ve konsola bilgi mesaji yazar.
        """
        self.interpreter = Interpreter()
        for satir in self.degisken_tablosu.get_children():
            self.degisken_tablosu.delete(satir)
        self._konsola_yaz("  Degisken ortami sifirlandi.\n", "bilgi")

    def _konsolu_temizle(self) -> None:
        """Konsol metin alanini tamamen siler."""
        self.konsol_alani.configure(state="normal")
        self.konsol_alani.delete("1.0", "end")
        self.konsol_alani.configure(state="disabled")

    def _konsola_yaz(self, metin: str, etiket: str = "bilgi") -> None:
        """
        Konsol alanina renkli metin ekler ve otomatik kaydirir.
        Widget salt okunur modda oldugundan gecici olarak normal moda alinir.

        Parametreler:
            metin  : Eklenecek metin satiri
            etiket : Renk etiketi  bilgi | basari | hata | vurgu | degisken
        """
        self.konsol_alani.configure(state="normal")
        self.konsol_alani.insert("end", metin, etiket)
        self.konsol_alani.see("end")
        self.konsol_alani.configure(state="disabled")

    def _baslangic_icerigini_yukle(self) -> None:
        """
        Uygulama basladiginda konsolda kisa kullanim kilavuzu yazar
        ve editore hazir ornek kaynak kod yukler.
        """
        # Konsol karsilama mesajlari
        self._konsola_yaz("Mini Interpreter  |  GUI Modu\n", "vurgu")
        self._konsola_yaz("─" * 48 + "\n", "bilgi")
        self._konsola_yaz("  Ctrl+Enter  Kodu calistir\n",   "bilgi")
        self._konsola_yaz("  Ctrl+L      Editoru temizle\n", "bilgi")
        self._konsola_yaz("  Ctrl+R      Ortami sifirla\n",  "bilgi")
        self._konsola_yaz("  Ctrl+K      Konsolu temizle\n", "bilgi")
        self._konsola_yaz("─" * 48 + "\n", "bilgi")

        # Editore hazir ornek kaynak kod
        ornek = (
            "x = 10\n"
            "y = 3\n"
            "toplam = x + y * 2\n"
            "\n"
            "if toplam > 15 {\n"
            "    sonuc = toplam * 2\n"
            "} else {\n"
            "    sonuc = toplam - y\n"
            "}\n"
            "\n"
            "oran = sonuc / y\n"
        )
        self.kod_alani.insert("1.0", ornek)
        self.kok.after(80, self._satir_numaralarini_guncelle)

    # ======================================================================
    # 7 - KLAVYE KISAYOLLARI & PENCERE YONETIMI
    # ======================================================================

    def _klavye_kisayollarini_baglat(self) -> None:
        """
        Uygulama genelinde aktif klavye kisayollari:
            Ctrl+Enter  Kodu calistir
            Ctrl+L      Editoru temizle
            Ctrl+R      Ortami sifirla
            Ctrl+K      Konsolu temizle
        """
        self.kok.bind("<Control-Return>", lambda e: self._kodu_calistir())
        self.kok.bind("<Control-l>",      lambda e: self._editoru_temizle())
        self.kok.bind("<Control-L>",      lambda e: self._editoru_temizle())
        self.kok.bind("<Control-r>",      lambda e: self._ortami_sifirla())
        self.kok.bind("<Control-R>",      lambda e: self._ortami_sifirla())
        self.kok.bind("<Control-k>",      lambda e: self._konsolu_temizle())
        self.kok.bind("<Control-K>",      lambda e: self._konsolu_temizle())

    def _kapatma_onay(self) -> None:
        """Pencere kapatilmadan once kullanicidan onay alir."""
        if messagebox.askokcancel(
            "Cikis",
            "Mini Interpreter'dan cikmak istediginize emin misiniz?",
        ):
            self.kok.destroy()


# ===========================================================================
# GIRIS NOKTASI
# ===========================================================================

def main() -> None:
    """
    Tkinter kok penceresini olusturur, UygulamaGUI sinifini baslatir
    ve olay dongusunu (mainloop) calistirir.
    Pencere kapatilana kadar dongu devam eder.
    """
    kok = tk.Tk()

    # Windows'ta yuksek DPI farkindaliigi — metin bulanikligini onler
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass   # Windows disi sistemlerde bu cagri basarisiz olur — sorunsuz devam

    UygulamaGUI(kok)
    kok.mainloop()


if __name__ == "__main__":
    main()
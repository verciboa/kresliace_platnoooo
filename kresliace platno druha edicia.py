import tkinter as tk

# Globálne premenné na ukladanie stavu kreslenia
aktualna_farba = "#1e293b"
nazov_aktualnej_farby = "Čierna"
farba_pozadia = "#ffffff"
rezim_gumy = False
velkost_stetca = 4
posledne_x = None
posledne_y = None
vsetky_tahy = []       # Zoznam akcií (ťahy alebo zmena pozadia) pre funkciu Ctrl+Z
aktualny_tah = []      # Zoznam čiar tvoriacich jeden súvislý ťah myšou

# Farebná paleta aplikácie
POZADIE_OKNA = "#f4f6f9"
POZADIE_KARTY = "#ffffff"
TEXT_HLAVNY = "#1e293b"
TEXT_JEMNY = "#64748b"
OKRAJ_JEMNY = "#cbd5e1"
POZADIE_STAVU = "#e2e8f0"


def aktualny_nastroj_text():
    return "Guma" if rezim_gumy else "Štetec"


def ziskaj_farbu_kreslenia():
    return farba_pozadia if rezim_gumy else aktualna_farba


# 1. CALLBACK FUNKCIA: Reaguje na stlačenie ľavého tlačidla myši (<Button-1>)
def zaciatok_kreslenia(event):
    global posledne_x, posledne_y, aktualny_tah
    # Uloženie počiatočných súradníc kliknutia (event.x, event.y)
    posledne_x = event.x
    posledne_y = event.y
    aktualny_tah = []

    # Nakreslenie bodky pri obyčajnom kliknutí bez ťahu
    farba_tahu = ziskaj_farbu_kreslenia()
    polomer = velkost_stetca / 2
    bodka = platno.create_oval(
        event.x - polomer, event.y - polomer,
        event.x + polomer, event.y + polomer,
        fill=farba_tahu, outline=farba_tahu
    )
    aktualny_tah.append(bodka)

    label_stav.config(
        text=f"{aktualny_nastroj_text()} od [{event.x}, {event.y}]  •  Farba: {nazov_aktualnej_farby}  •  Hrúbka: {velkost_stetca}px"
    )


# 2. CALLBACK FUNKCIA: Reaguje na pohyb myši so stlačeným tlačidlom (<B1-Motion>)
def kreslenie(event):
    global posledne_x, posledne_y
    if posledne_x is not None and posledne_y is not None:
        farba_tahu = ziskaj_farbu_kreslenia()
        # Nakreslenie čiary z predchádzajúceho bodu do aktuálnej pozície myši
        ciara = platno.create_line(
            posledne_x, posledne_y, event.x, event.y,
            fill=farba_tahu, width=velkost_stetca, capstyle=tk.ROUND, smooth=True
        )
        aktualny_tah.append(ciara)
        posledne_x = event.x
        posledne_y = event.y
        label_stav.config(
            text=f"{aktualny_nastroj_text()} na [{event.x}, {event.y}]  •  Farba: {nazov_aktualnej_farby}  •  Hrúbka: {velkost_stetca}px"
        )


# 3. CALLBACK FUNKCIA: Reaguje na pustenie ľavého tlačidla myši (<ButtonRelease-1>)
def koniec_kreslenia(event):
    global posledne_x, posledne_y, aktualny_tah
    if aktualny_tah:
        # Uloženie dokončeného ťahu ako akcie do histórie (pre krok späť)
        vsetky_tahy.append(("tah", aktualny_tah))
    posledne_x = None
    posledne_y = None
    label_stav.config(
        text=f"Ťah uložený  •  Nástroj: {aktualny_nastroj_text()}  •  Farba: {nazov_aktualnej_farby}"
    )


# 4. CALLBACK FUNKCIA: Reaguje na zmenu farby (z klávesnice alebo cez tlačidlo s lambda)
def zmena_farby(farba, nazov_farby):
    global aktualna_farba, nazov_aktualnej_farby, rezim_gumy
    aktualna_farba = farba
    nazov_aktualnej_farby = nazov_farby
    rezim_gumy = False
    indikator_farby.config(bg=farba)
    aktualizuj_tlacidla_nastrojov()
    label_stav.config(text=f"Zvolená farba: {nazov_farby}  •  Nástroj: Štetec")


# 5. CALLBACK FUNKCIA: Reaguje na skratku Ctrl+Z (<Control-z> / <Control-Z>)
def krok_spat(event=None):
    global farba_pozadia
    if vsetky_tahy:
        typ_akcie, data = vsetky_tahy.pop()
        if typ_akcie == "tah":
            for objekt_id in data:
                platno.delete(objekt_id)
        elif typ_akcie == "pozadie":
            predchadzajuca_farba = data
            farba_pozadia = predchadzajuca_farba
            platno.config(bg=farba_pozadia)
            ram_platna.config(bg=farba_pozadia)
        label_stav.config(text=f"Vrátený posledný krok (Ctrl+Z)  •  Zostáva krokov: {len(vsetky_tahy)}")
    else:
        label_stav.config(text="Nie je čo vrátiť späť.")


# 6. CALLBACK FUNKCIA: Reaguje na kliknutie na tlačidlo "Vymazať všetko" (command=)
def vymazat_platno():
    global farba_pozadia
    platno.delete("all")
    vsetky_tahy.clear()
    farba_pozadia = "#ffffff"
    platno.config(bg=farba_pozadia)
    ram_platna.config(bg=farba_pozadia)
    label_stav.config(text="Plátno bolo úplne vyčistené.")


# 7. CALLBACK FUNKCIA: Reaguje na stlačenie klávesov a číta event.keysym
def spracuj_klaves(event):
    klaves = event.keysym.lower()
    if klaves == "r":
        zmena_farby("#ef4444", "Červená (R)")
    elif klaves == "g":
        zmena_farby("#22c55e", "Zelená (G)")
    elif klaves == "b":
        zmena_farby("#3b82f6", "Modrá (B)")
    elif klaves == "c":
        zmena_farby("#1e293b", "Čierna (C)")
    elif klaves == "e":
        prepni_gumu()


# 8. CALLBACK FUNKCIA: Vyplní celú stranu aktuálnou farbou (Bucket)
def vyplnit_stranu():
    global farba_pozadia
    stara_farba = farba_pozadia
    farba_pozadia = aktualna_farba
    platno.config(bg=farba_pozadia)
    ram_platna.config(bg=farba_pozadia)
    vsetky_tahy.append(("pozadie", stara_farba))
    label_stav.config(text=f"Celá strana vyplnená farbou: {nazov_aktualnej_farby}")


# 9. CALLBACK FUNKCIA: Prepne medzi štetcom a gumou
def prepni_gumu():
    global rezim_gumy
    rezim_gumy = not rezim_gumy
    aktualizuj_tlacidla_nastrojov()
    label_stav.config(
        text=f"Aktívny nástroj: {aktualny_nastroj_text()}  •  Hrúbka: {velkost_stetca}px"
    )


# 10. CALLBACK FUNKCIA: Reaguje na posuvník veľkosti štetca / gumy
def zmen_velkost_stetca(hodnota):
    global velkost_stetca
    velkost_stetca = int(hodnota)
    label_stav.config(
        text=f"Hrúbka nástroja nastavená na {velkost_stetca}px  •  Nástroj: {aktualny_nastroj_text()}"
    )


def aktualizuj_tlacidla_nastrojov():
    if rezim_gumy:
        btn_guma.config(bg="#fef08a", fg="#854d0e", relief=tk.SUNKEN)
        platno.config(cursor="dotbox")
    else:
        btn_guma.config(bg="#e2e8f0", fg="#1e293b", relief=tk.FLAT)
        platno.config(cursor="pencil")


# --- VYTVORENIE HLAVNÉHO OKNA ---
okno = tk.Tk()
okno.title("Kresliace plátno")
okno.configure(bg=POZADIE_OKNA)
okno.resizable(False, False)

# Horná lišta s nadpisom a návodom (Požiadavka 1)
hlavicka = tk.Frame(okno, bg=POZADIE_OKNA, padx=16, pady=10)
hlavicka.pack(fill=tk.X)

label_nadpis = tk.Label(
    hlavicka,
    text="Kresliace plátno",
    font=("Segoe UI", 16, "bold"),
    bg=POZADIE_OKNA,
    fg=TEXT_HLAVNY,
    anchor="w"
)
label_nadpis.pack(fill=tk.X)

label_navod = tk.Label(
    hlavicka,
    text="Ťahaj myšou pre kreslenie  •  R / G / B / C menia farbu  •  E prepne gumu  •  Ctrl+Z vráti krok späť",
    font=("Segoe UI", 9),
    bg=POZADIE_OKNA,
    fg=TEXT_JEMNY,
    anchor="w"
)
label_navod.pack(fill=tk.X, pady=(2, 0))

# Rámček okolo plátna
ram_platna = tk.Frame(
    okno,
    bg=POZADIE_KARTY,
    highlightbackground=OKRAJ_JEMNY,
    highlightthickness=1,
    padx=4,
    pady=4
)
ram_platna.pack(padx=16, pady=(0, 8))

platno = tk.Canvas(
    ram_platna,
    width=740,
    height=430,
    bg=farba_pozadia,
    cursor="pencil",
    highlightthickness=0
)
platno.pack()

# Panel s farbami, nástrojmi a veľkosťou štetca
panel_nastrojov = tk.Frame(okno, bg=POZADIE_OKNA, padx=16, pady=4)
panel_nastrojov.pack(fill=tk.X)

styl_tlacidla = {
    "font": ("Segoe UI", 9, "bold"),
    "relief": tk.FLAT,
    "padx": 10,
    "pady": 6,
    "cursor": "hand2",
    "bd": 0
}

# Tlačidlá farieb s parametrom cez lambda (Požiadavka 4)
btn_cervena = tk.Button(
    panel_nastrojov, text="● Červená (R)", fg="#dc2626", bg="#fee2e2",
    activebackground="#fecaca", activeforeground="#991b1b",
    command=lambda: zmena_farby("#ef4444", "Červená (R)"), **styl_tlacidla
)
btn_cervena.pack(side=tk.LEFT, padx=(0, 6))

btn_zelena = tk.Button(
    panel_nastrojov, text="● Zelená (G)", fg="#16a34a", bg="#dcfce7",
    activebackground="#bbf7d0", activeforeground="#166534",
    command=lambda: zmena_farby("#22c55e", "Zelená (G)"), **styl_tlacidla
)
btn_zelena.pack(side=tk.LEFT, padx=(0, 6))

btn_modra = tk.Button(
    panel_nastrojov, text="● Modrá (B)", fg="#2563eb", bg="#dbeafe",
    activebackground="#bfdbfe", activeforeground="#1e40af",
    command=lambda: zmena_farby("#3b82f6", "Modrá (B)"), **styl_tlacidla
)
btn_modra.pack(side=tk.LEFT, padx=(0, 6))

btn_cierna = tk.Button(
    panel_nastrojov, text="● Čierna (C)", fg="#1e293b", bg="#e2e8f0",
    activebackground="#cbd5e1", activeforeground="#0f172a",
    command=lambda: zmena_farby("#1e293b", "Čierna (C)"), **styl_tlacidla
)
btn_cierna.pack(side=tk.LEFT, padx=(0, 12))

# Guma a Bucket (vyplnenie celej strany)
btn_guma = tk.Button(
    panel_nastrojov, text="Guma (E)", fg="#1e293b", bg="#e2e8f0",
    activebackground="#cbd5e1",
    command=prepni_gumu, **styl_tlacidla
)
btn_guma.pack(side=tk.LEFT, padx=(0, 6))

btn_bucket = tk.Button(
    panel_nastrojov, text="Vyplniť stranu", fg="#1d4ed8", bg="#e0e7ff",
    activebackground="#c7d2fe", activeforeground="#1e3a8a",
    command=vyplnit_stranu, **styl_tlacidla
)
btn_bucket.pack(side=tk.LEFT, padx=(0, 6))

# Tlačidlo s command= BEZ zátvoriek (Požiadavka 3)
btn_vymazat = tk.Button(
    panel_nastrojov, text="Vymazať všetko", fg="#991b1b", bg="#fee2e2",
    activebackground="#fecaca", activeforeground="#7f1d1d",
    command=vymazat_platno, **styl_tlacidla
)
btn_vymazat.pack(side=tk.RIGHT)

# Druhý riadok pre nastavenie hrúbky štetca / gumy
panel_velkosti = tk.Frame(okno, bg=POZADIE_OKNA, padx=16, pady=4)
panel_velkosti.pack(fill=tk.X)

label_velkost = tk.Label(
    panel_velkosti,
    text="Hrúbka štetca / gumy:",
    font=("Segoe UI", 9, "bold"),
    bg=POZADIE_OKNA,
    fg=TEXT_HLAVNY
)
label_velkost.pack(side=tk.LEFT, padx=(0, 8))

posuvnik_velkosti = tk.Scale(
    panel_velkosti,
    from_=1,
    to=30,
    orient=tk.HORIZONTAL,
    length=220,
    bg=POZADIE_OKNA,
    fg=TEXT_HLAVNY,
    highlightthickness=0,
    troughcolor="#cbd5e1",
    activebackground="#3b82f6",
    command=zmen_velkost_stetca
)
posuvnik_velkosti.set(velkost_stetca)
posuvnik_velkosti.pack(side=tk.LEFT)

# Stavový riadok v spodnej časti okna
stavovy_riadok = tk.Frame(okno, bg=POZADIE_STAVU, padx=12, pady=6)
stavovy_riadok.pack(fill=tk.X, side=tk.BOTTOM, pady=(6, 0))

indikator_farby = tk.Label(
    stavovy_riadok,
    text="",
    width=2,
    bg=aktualna_farba,
    relief=tk.SOLID,
    bd=1
)
indikator_farby.pack(side=tk.LEFT, padx=(0, 8))

label_stav = tk.Label(
    stavovy_riadok,
    text=f"Pripravený na kreslenie  •  Farba: {nazov_aktualnej_farby}  •  Hrúbka: {velkost_stetca}px",
    font=("Segoe UI", 9),
    bg=POZADIE_STAVU,
    fg=TEXT_HLAVNY,
    anchor="w"
)
label_stav.pack(side=tk.LEFT, fill=tk.X)

# --- PREPOJENIE UDALOSTÍ CEZ BIND (Požiadavka 5 a 6) ---
platno.bind("<Button-1>", zaciatok_kreslenia)
platno.bind("<B1-Motion>", kreslenie)
platno.bind("<ButtonRelease-1>", koniec_kreslenia)

okno.bind("<KeyPress>", spracuj_klaves)
okno.bind("<Control-z>", krok_spat)
okno.bind("<Control-Z>", krok_spat)

okno.mainloop()

# Sťahovač videí z archívu Národnej Rady Slovenskej Republiky

Tento skript sťahuje video z archívu TV NRSR. Funguje na Windows aj Linuxe.

## Predpoklady

### 1. Nainštalujte `ffmpeg`

#### Pre Linux:

`ffmpeg` môžete nainštalovať cez vášho správcu balíkov (napr. `apt` pre Ubuntu):

```bash
sudo apt update
sudo apt install ffmpeg
```

#### Pre Windows:

Stiahnite si spustiteľný súbor `ffmpeg.exe` z [ffmpeg.org](https://ffmpeg.org/download.html) alebo priamo z [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).

- Rozbaľte archív `ffmpeg` a umiestnite `ffmpeg.exe` do koreňového adresára tohto skriptu (tam, kde je súbor `downloader.py`).
- Nemusíte pridávať `ffmpeg` do systémovej premennej PATH, ak sa nachádza v rovnakom adresári ako skript.

## Použitie

### 1. Nainštalujte závislosti pre Python

Uistite sa, že máte nainštalované potrebné Python knižnice. Môžete ich nainštalovať pomocou `pip`:

```bash
pip install requests
pip install argparse
```

### 2. Spustite skript

Skript vyžaduje URL na webovú stránku obsahujúcu video, následne stiahne všetky časti videa, spojí ich a vytvorí jeden výstupný súbor `.mp4`.

#### Príklad:

python3 downloader.py https://tv.nrsr.sk/archiv/odkaz_na_pozadovane_video

```bash
python3 downloader.py https://tv.nrsr.sk/archiv/schodza/9/21
```

### Poznámka:

- Skript automaticky rieši konverziu URL pre Windows a Linux, aby bola zaistená kompatibilita.
- Na Windows, ak je `ffmpeg.exe` v rovnakom adresári ako skript, nemusíte upravovať systémovú premennú PATH.

### 3. Ak nemáte nainštalovaný python (len pre Windows užívateľov)

Stiahnite si nrsr_tv_downloader.exe a použite ho následovne v príkazovom riadku

nrsr_tv_downloader.exe https://tv.nrsr.sk/archiv/odkaz_na_pozadovane_video

```bash
nrsr_tv_downloader.exe https://tv.nrsr.sk/archiv/schodza/9/21
```

## Riešenie problémov

- **`ffmpeg` nebol nájdený**: Skontrolujte, či je `ffmpeg` nainštalovaný a správne umiestnený v adresári (pre Windows) alebo nainštalovaný cez správca balíkov (pre Linux).



# Audio App Router 🎧

[Italiano](#italiano) | [English](#english)

---

## Italiano

**Audio App Router** è un'applicazione Windows moderna, scalabile e performante che consente di indirizzare l'audio di specifiche applicazioni (es. Spotify, Chrome, Discord) verso dispositivi di riproduzione diversi (es. Cuffie, Altoparlanti, Virtual Audio Cable).

L'interfaccia grafica è stata costruita con **PySide6 (Qt6)** per garantire scalabilità DPI automatica, una reattività eccezionale e un design scuro professionale e moderno.

### ✨ Funzionalità
- **Interfaccia Moderna (Qt6)**: Tema scuro elegante con scrollbar personalizzate, layout flessibile e angoli arrotondati.
- **DPI Scaling & Splitter**: Layout scalabile con divisore centrale trascinabile per adattarsi a qualsiasi schermo.
- **Icone App in Tempo Reale**: Mostra le icone reali dei processi in esecuzione e i relativi PID.
- **Filtro di Ricerca Rapido**: Barra di ricerca per filtrare all'istante le applicazioni attive.
- **Badge Dispositivo Predefinito**: Evidenzia il dispositivo audio predefinito del sistema.
- **Aggiornamento Automatico**: Rileva apertura/chiusura delle app audio ogni secondo, preservando la selezione.
- **Doppio Motore di Routing**:
  - COM nativo di Windows (`IPolicyConfig`) — funziona senza dipendenze esterne.
  - **SoundVolumeView** di NirSoft (opzionale, per maggiore stabilità su alcune configurazioni).

---

### ⬇️ Download rapido (EXE precompilato)

Vai alla sezione [**Releases**](https://github.com/zuc7/Audio_router/releases) e scarica `AudioRouter.exe`.

> ⚠️ Windows potrebbe mostrare un avviso SmartScreen. Clicca **Ulteriori informazioni → Esegui comunque**.

---

### 📋 Requisiti
- Windows 10 / 11 (64-bit)
- Python 3.8+ *(solo se esegui da sorgente)*

### 🚀 Installazione (da sorgente)

1. Clona la repository:
   ```bash
   git clone https://github.com/zuc7/Audio_router.git
   cd Audio_router
   ```
2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
3. **(Opzionale ma raccomandato)** Scarica **SoundVolumeView** da NirSoft:
   - Link: https://www.nirsoft.net/utils/sound_volume_view.html
   - Estrai `SoundVolumeView.exe` in `tools/soundvolumeview/SoundVolumeView.exe`

### 💻 Utilizzo
```bash
python audio_router_gui.py
```
1. Seleziona l'app dall'elenco a sinistra (usa la barra di ricerca per filtrare).
2. Seleziona il dispositivo di riproduzione a destra.
3. Clicca **Applica Collegamento**.
4. Per ripristinare il predefinito, clicca **Ripristina Predefinito**.

---

## English

**Audio App Router** is a modern, scalable, lightweight Windows application to route audio output of specific running apps (e.g. Spotify, Chrome, Discord) to different playback devices (e.g. Headphones, Speakers, Virtual Audio Cable).

The GUI is built with **PySide6 (Qt6)** for automatic DPI scaling, fluid interactions, and a clean professional dark theme.

### ✨ Features
- **Modern Interface (Qt6)**: Sleek dark theme with custom scrollbars, flexible layout and rounded corners.
- **Scalable Splitter Layout**: Drag-resizable center divider for any screen size.
- **Real-Time App Icons**: Extracts and shows running process icons and PIDs.
- **Instant Search/Filter**: Filter active apps instantly.
- **Default Device Badge**: Highlights the current system default audio device.
- **Auto-Refresh**: Detects audio sessions opening/closing every second, preserving selection.
- **Dual Routing Backend**:
  - Native Windows COM (`IPolicyConfig`) — no external dependencies needed.
  - **SoundVolumeView** by NirSoft (optional, for better stability on some setups).

---

### ⬇️ Quick Download (prebuilt EXE)

Go to [**Releases**](https://github.com/zuc7/Audio_router/releases) and download `AudioRouter.exe`.

> ⚠️ Windows may show a SmartScreen warning. Click **More info → Run anyway**.

---

### 📋 Requirements
- Windows 10 / 11 (64-bit)
- Python 3.8+ *(only if running from source)*

### 🚀 Installation (from source)

1. Clone the repository:
   ```bash
   git clone https://github.com/zuc7/Audio_router.git
   cd Audio_router
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **(Optional but recommended)** Download **SoundVolumeView** from NirSoft:
   - URL: https://www.nirsoft.net/utils/sound_volume_view.html
   - Extract `SoundVolumeView.exe` into `tools/soundvolumeview/SoundVolumeView.exe`

### 💻 Usage
```bash
python audio_router_gui.py
```
1. Select your target app from the left list (use the search bar to filter).
2. Select your target playback device from the right list.
3. Click **Applica Collegamento** (Apply Route).
4. To reset to the system default, click **Ripristina Predefinito** (Reset Default).

---

### 📄 License
This project is licensed under the MIT License. Feel free to use, modify, and distribute.

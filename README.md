# Audio App Router 🎧

[Italiano](#italiano) | [English](#english)

---

## Italiano

**Audio App Router** è un'applicazione Windows moderna, scalabile e performante che consente di indirizzare l'audio di specifiche applicazioni (es. Spotify, Chrome, Discord) verso dispositivi di riproduzione diversi (es. Cuffie, Altoparlanti, Virtual Audio Cable).

L'interfaccia grafica è stata riscritta utilizzando **PySide6 (Qt6)** per garantire scalabilità DPI automatica, una reattività eccezionale e un design scuro professionale e moderno.

### ✨ Funzionalità
- **Interfaccia Moderna (Qt6)**: Tema scuro elegante e coerente con scrollbar personalizzate, layout flessibili e angoli arrotondati.
- **DPI Scaling & Splitter**: Layout scalabile con divisore centrale trascinabile (`QSplitter`) per adattarsi a schermi di qualsiasi dimensione.
- **Riconoscimento App**: Mostra le icone reali delle applicazioni e i relativi PID.
- **Filtro di Ricerca Rapido**: Barra di ricerca per filtrare all'istante le applicazioni in esecuzione (utilissimo con molte app aperte).
- **Evidenziazione Dispositivo Predefinito**: Mostra un badge verde "Predefinito" sul dispositivo di sistema principale.
- **Aggiornamento Automatico**: Rileva l'apertura o chiusura delle applicazioni audio ogni secondo, mantenendo la selezione corrente senza sfarfallio.
- **Doppio Motore di Routing**:
  - Utilizza l'interfaccia COM di Windows (`IPolicyConfig`) nativa.
  - Supporta opzionalmente **SoundVolumeView** di NirSoft (se inserito in `tools/soundvolumeview/`) per una maggiore stabilità.

### 📋 Requisiti
- Windows 10 o Windows 11
- Python 3.8+

### 🚀 Installazione
1. Clona la repository:
   ```bash
   git clone https://github.com/tuo-username/audio_router.git
   cd audio_router
   ```
2. Installa le dipendenze necessarie:
   ```bash
   pip install -r requirements.txt
   ```

### 💻 Utilizzo
Avvia l'applicazione eseguendo:
```bash
python audio_router_gui.py
```

1. Seleziona l'applicazione desiderata dall'elenco a sinistra (puoi usare la barra di ricerca in alto).
2. Seleziona il dispositivo di riproduzione desiderato dall'elenco a destra.
3. Clicca su **Applica Collegamento**.
4. Per ripristinare il comportamento predefinito di un'applicazione, selezionala e clicca su **Ripristina Predefinito**.

---

## English

**Audio App Router** is a modern, scalable, and lightweight Windows application that lets you route the audio output of specific running applications (e.g., Spotify, Chrome, Discord) to different playback devices (e.g., Headphones, Speakers, Virtual Audio Cable).

The GUI has been written using **PySide6 (Qt6)** to provide automatic DPI scaling, fluid interactions, and a clean professional dark theme.

### ✨ Features
- **Modern Interface (Qt6)**: Sleek dark stylesheet with custom scrollbars, flexible grid spacing, and rounded corners.
- **Scalable Splitter Layout**: Drag-resizable center divider (`QSplitter`) ensuring perfect visibility on any screen size.
- **App Icon & PID Extraction**: Real-time extraction of running process icons and PIDs.
- **Instant Search/Filter**: Search bar to instantly filter running processes, highly useful when managing many background tasks.
- **Default Device Indicator**: Renders a clean green "Default" badge next to the current system default audio device.
- **Auto-Refresh Loop**: Detects audio sessions opening/closing every second, preserving your current selection seamlessly.
- **Dual Routing Backend**:
  - Standard native Windows COM interfaces (`IPolicyConfig`).
  - Fallback integration with NirSoft's **SoundVolumeView** (if placed inside `tools/soundvolumeview/`).

### 📋 Requirements
- Windows 10 or Windows 11
- Python 3.8+

### 🚀 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/audio_router.git
   cd audio_router
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 💻 Usage
Run the application using:
```bash
python audio_router_gui.py
```

1. Select your target app from the left list (use the top search bar to filter).
2. Select your target audio playback device from the right list.
3. Click **Applica Collegamento** (Apply Route).
4. To reset an app back to your system default playback device, select the app and click **Ripristina Predefinito** (Reset Default).

---

### 📄 License
This project is licensed under the MIT License. Feel free to use, modify, and distribute.

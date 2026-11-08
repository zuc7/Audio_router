import json
import os
import warnings
import csv
import sys
import subprocess
import time
import psutil
import comtypes
from comtypes import CLSCTX_ALL, GUID, COMMETHOD, IUnknown
from ctypes import HRESULT
from ctypes.wintypes import DWORD, LPCWSTR
from pycaw.utils import AudioUtilities
from pycaw.constants import EDataFlow, ERole, DEVICE_STATE
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import ctypes

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QStatusBar, QMessageBox, QFrame, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QPixmap, QImage

CLSID_PolicyConfigClient = GUID("{870af99c-171d-4f9e-af0d-e63df40c2bc9}")
IID_IPolicyConfig10 = GUID("{CA286FC3-91FD-42C3-8E9B-CAAFA66242E3}")


class IPolicyConfig10(IUnknown):
    _iid_ = IID_IPolicyConfig10
    _methods_ = (
        COMMETHOD([], HRESULT, "GetMixFormat"),
        COMMETHOD([], HRESULT, "GetDeviceFormat"),
        COMMETHOD([], HRESULT, "ResetDeviceFormat"),
        COMMETHOD([], HRESULT, "SetDeviceFormat"),
        COMMETHOD([], HRESULT, "GetProcessingPeriod"),
        COMMETHOD([], HRESULT, "SetProcessingPeriod"),
        COMMETHOD([], HRESULT, "GetShareMode"),
        COMMETHOD([], HRESULT, "SetShareMode"),
        COMMETHOD([], HRESULT, "GetPropertyValue"),
        COMMETHOD([], HRESULT, "SetPropertyValue"),
        COMMETHOD([], HRESULT, "SetDefaultEndpoint", (["in"], LPCWSTR, "device_id"), (["in"], DWORD, "role")),
        COMMETHOD([], HRESULT, "SetEndpointVisibility"),
        COMMETHOD(
            [],
            HRESULT,
            "SetPersistedDefaultAudioEndpoint",
            (["in"], DWORD, "process_id"),
            (["in"], DWORD, "data_flow"),
            (["in"], DWORD, "role"),
            (["in"], LPCWSTR, "device_id"),
        ),
        COMMETHOD([], HRESULT, "GetPersistedDefaultAudioEndpoint"),
        COMMETHOD([], HRESULT, "ClearAllPersistedApplicationDefaultEndpoints"),
    )


class IPolicyConfigVista(IPolicyConfig10):
    _iid_ = GUID("{568b9108-44bf-40b4-9006-86afe5b5a620}")


APP_TITLE = "Audio App Router"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):
    DATA_DIR = os.path.dirname(sys.executable)
else:
    DATA_DIR = BASE_DIR

SETTINGS_FILE = os.path.join(DATA_DIR, "audio_router_settings.json")
SVV_EXE = os.path.join(BASE_DIR, "tools", "soundvolumeview", "SoundVolumeView.exe")
LOCK_FILE = os.path.join(DATA_DIR, "audio_router.lock")

warnings.filterwarnings("ignore", category=UserWarning, module="pycaw.utils")
ROLE_LIST = [ERole.eConsole, ERole.eMultimedia, ERole.eCommunications]


def _get_policy_config():
    try:
        return comtypes.CoCreateInstance(
            CLSID_PolicyConfigClient, IPolicyConfig10, CLSCTX_ALL
        )
    except Exception:
        return None


def get_default_device_id():
    device = AudioUtilities.GetSpeakers()
    return device.id


def set_app_endpoint(pid, device_id):
    policy = _get_policy_config()
    if policy is None:
        raise RuntimeError("Interfaccia PolicyConfig non supportata su questo sistema.")
    for role in ROLE_LIST:
        policy.SetPersistedDefaultAudioEndpoint(pid, EDataFlow.eRender.value, role.value, device_id)


def get_render_devices():
    try:
        return AudioUtilities.GetAllDevices(EDataFlow.eRender.value, DEVICE_STATE.ACTIVE.value)
    except Exception:
        return []


def svv_available():
    return os.path.exists(SVV_EXE)


def svv_export_rows():
    if not svv_available():
        return []
    out_csv = os.path.join(BASE_DIR, "svv_rows.csv")
    try:
        subprocess.run([SVV_EXE, "/scomma", out_csv], check=True, capture_output=True)
    except Exception:
        return []
    rows = []
    try:
        with open(out_csv, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    except Exception:
        pass
    try:
        os.remove(out_csv)
    except Exception:
        pass
    return rows


def svv_list_render_devices(rows=None):
    if rows is None:
        rows = svv_export_rows()
    render = []
    for row in rows:
        item_type = (row.get("Type") or "").lower()
        direction = (row.get("Direction") or "").lower()
        state = (row.get("Device State") or row.get("State") or "").lower()
        if item_type != "device":
            continue
        if "render" not in direction:
            continue
        if state and "active" not in state:
            continue
        name = row.get("Name") or ""
        if str(name).strip().lower() in ("", "none"):
            name = ""
        device_name = row.get("Device Name") or ""
        item_name = row.get("Item Name") or ""
        display = name or device_name or item_name
        if not name:
            cli = row.get("Command-Line Friendly ID") or row.get("Item ID") or ""
            if "\\Device\\" in cli and "\\Render" in cli:
                mid = cli.split("\\Device\\", 1)[1]
                mid = mid.rsplit("\\Render", 1)[0]
                if mid:
                    display = mid
        if not display:
            continue
        if name and device_name and name != device_name:
            display = f"{name} — {device_name}"
        render.append((display, row))
    return render


def svv_list_app_sessions(rows=None):
    if rows is None:
        rows = svv_export_rows()
    apps = []
    seen = set()
    for row in rows:
        item_type = (row.get("Type") or "").lower()
        pid = row.get("Process ID") or ""
        if item_type == "device":
            continue
        if not pid.strip():
            continue
        try:
            pid_int = int(pid)
        except Exception:
            continue
        if pid_int in seen:
            continue
        seen.add(pid_int)
        name = row.get("Name") or ""
        if not name:
            path = row.get("Process Path") or ""
            name = os.path.basename(path) if path else f"PID {pid_int}"
        apps.append((pid_int, name))
    return apps


def svv_set_app_default(device_row, pid):
    if not svv_available():
        raise RuntimeError("SoundVolumeView non disponibile.")
    device_id = device_row.get("Command-Line Friendly ID") or device_row.get("Item ID") or device_row.get("Device Name")
    if not device_id:
        raise RuntimeError("ID dispositivo non valido.")
    for role in (0, 1, 2):
        subprocess.run(
            [SVV_EXE, "/SetAppDefault", device_id, str(role), str(pid)],
            check=True,
            capture_output=True,
        )


def svv_reset_app_default(pid):
    if not svv_available():
        raise RuntimeError("SoundVolumeView non disponibile.")
    subprocess.run(
        [SVV_EXE, "/SetAppDefault", "DefaultRenderDevice", "all", str(pid)],
        check=True,
        capture_output=True,
    )


def svv_get_default_render_row(rows=None):
    for name, row in svv_list_render_devices(rows):
        if (row.get("Default Multimedia") or "").lower() == "yes":
            return row
        if (row.get("Default") or "").lower() == "yes":
            return row
    return None


def get_sessions():
    if svv_available():
        rows = svv_export_rows()
        return svv_list_app_sessions(rows), rows
    sessions = []
    try:
        comtypes.CoInitialize()
    except Exception:
        pass
    for session in AudioUtilities.GetAllSessions():
        if session.Process is None:
            continue
        try:
            pid = session.ProcessId
            proc = psutil.Process(pid)
            name = proc.name()
            sessions.append((pid, name))
        except Exception:
            continue
    try:
        comtypes.CoUninitialize()
    except Exception:
        pass
    return sessions, None


def _force_clean_lock():
    if not os.path.exists(LOCK_FILE):
        return
    try:
        with open(LOCK_FILE, "r", encoding="utf-8") as f:
            pid = int(f.read().strip() or "0")
        if pid and psutil.pid_exists(pid):
            try:
                proc = psutil.Process(pid)
                cmdline = " ".join(proc.cmdline()).lower()
                if "audio_router" in cmdline or "audio router" in cmdline:
                    return
            except Exception:
                pass
    except Exception:
        pass
    try:
        os.remove(LOCK_FILE)
    except Exception:
        pass


def _acquire_lock():
    _force_clean_lock()
    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        return True
    except FileExistsError:
        return False
    except Exception:
        return False


class AudioRouterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            comtypes.CoInitialize()
        except Exception:
            pass

        self.setWindowTitle(APP_TITLE)
        self.resize(920, 600)
        self.setMinimumSize(760, 520)

        self.apps = []
        self.devices = []
        self.app_icons = {}
        
        # Populate initial list and set self._last_session_ids
        self._setup_style()
        self._set_app_user_model_id()
        self._build_ui()
        self.refresh_lists()
        
        self._last_session_ids = {pid for pid, _ in self.apps}
        
        self._load_window_state()
        self._set_app_icon()

        # Polling for changes
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._check_restart_on_change)
        self.poll_timer.start(1000)

    def _setup_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #141415;
            }
            QFrame.CardFrame {
                background-color: #19191b;
                border: 1px solid #303034;
                border-radius: 12px;
            }
            QLabel {
                color: #ededed;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                background-color: #232325;
                color: #ededed;
                border: 1px solid #303034;
                border-radius: 8px;
                padding: 0 12px;
                min-height: 40px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3288b8;
            }
            QListWidget {
                background-color: #141415;
                border: 1px solid #303034;
                border-radius: 8px;
                outline: 0;
                padding: 4px;
            }
            QListWidget:focus { border-color: #3288b8; }
            QListWidget::item {
                color: #d8d8dc;
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 4px;
                font-size: 14px;
            }
            QListWidget::item:hover {
                background-color: #232325;
                color: #ededed;
            }
            QListWidget::item:selected {
                background-color: #18577d;
                color: #ffffff;
            }
            QPushButton {
                background-color: #232325;
                color: #ededed;
                border: 1px solid #38383d;
                border-radius: 8px;
                padding: 0 16px;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2b2b2e;
                border-color: #4a4a50;
            }
            QPushButton:pressed {
                background-color: #1c1c1e;
            }
            QPushButton#primaryBtn {
                background-color: #e5e9ed;
                color: #171719;
                border-color: #e5e9ed;
            }
            QPushButton#primaryBtn:hover {
                background-color: #ffffff;
            }
            QPushButton#primaryBtn:pressed {
                background-color: #d2d6da;
            }
            QScrollBar:vertical {
                border: none;
                background: #141415;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #45454a;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QStatusBar {
                background-color: #141415;
                color: #a1a1a6;
                border-top: 1px solid #303034;
            }
            QSplitter::handle {
                background-color: #303034;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
        """)

    def _build_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 16)
        main_layout.setSpacing(16)

        # Header area
        header_layout = QHBoxLayout()
        title_container = QVBoxLayout()
        title_container.setSpacing(4)
        
        self.title_lbl = QLabel(APP_TITLE)
        self.title_lbl.setStyleSheet("font-size: 22px; font-weight: 600; color: #ededed;")
        
        self.subtitle_lbl = QLabel("Assegna a ogni app il dispositivo di uscita audio")
        self.subtitle_lbl.setStyleSheet("font-size: 13px; color: #a1a1a6;")
        
        title_container.addWidget(self.title_lbl)
        title_container.addWidget(self.subtitle_lbl)
        header_layout.addLayout(title_container)
        header_layout.addStretch()

        self.refresh_btn = QPushButton("Aggiorna")
        self.refresh_btn.setFixedWidth(104)
        self.refresh_btn.clicked.connect(self.refresh_lists)
        header_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(header_layout)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cerca app")
        self.search_bar.textChanged.connect(self.filter_apps)
        main_layout.addWidget(self.search_bar)

        # Splitter for apps and devices
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left card (apps)
        app_frame = QFrame()
        app_frame.setObjectName("cardFrame")
        app_frame.setProperty("class", "CardFrame")
        app_layout = QVBoxLayout(app_frame)
        app_layout.setContentsMargins(16, 16, 16, 16)
        app_layout.setSpacing(8)
        
        app_title = QLabel("Applicazioni attive")
        app_title.setStyleSheet("font-size: 14px; font-weight: 500; color: #ededed;")
        app_layout.addWidget(app_title)
        
        self.app_list = QListWidget()
        self.app_list.setIconSize(QSize(24, 24))
        app_layout.addWidget(self.app_list)
        splitter.addWidget(app_frame)

        # Right card (devices)
        dev_frame = QFrame()
        dev_frame.setObjectName("cardFrame")
        dev_frame.setProperty("class", "CardFrame")
        dev_layout = QVBoxLayout(dev_frame)
        dev_layout.setContentsMargins(16, 16, 16, 16)
        dev_layout.setSpacing(8)
        
        dev_title = QLabel("Dispositivi di riproduzione")
        dev_title.setStyleSheet("font-size: 14px; font-weight: 500; color: #ededed;")
        dev_layout.addWidget(dev_title)
        
        self.dev_list = QListWidget()
        self.dev_list.setIconSize(QSize(24, 24))
        dev_layout.addWidget(self.dev_list)
        splitter.addWidget(dev_frame)

        main_layout.addWidget(splitter, 1)

        # Actions buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        actions_layout.addStretch()
        
        self.reset_btn = QPushButton("Usa predefinito")
        self.reset_btn.clicked.connect(self.reset_route)
        actions_layout.addWidget(self.reset_btn)
        
        self.apply_btn = QPushButton("Applica uscita")
        self.apply_btn.setObjectName("primaryBtn")
        self.apply_btn.clicked.connect(self.apply_route)
        actions_layout.addWidget(self.apply_btn)
        
        main_layout.addLayout(actions_layout)

        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")

    def filter_apps(self, text):
        search_text = text.lower().strip()
        for row in range(self.app_list.count()):
            item = self.app_list.item(row)
            pid = item.data(Qt.ItemDataRole.UserRole)
            name = item.data(Qt.ItemDataRole.UserRole + 1)
            matches = (search_text in name.lower()) or (search_text in str(pid))
            self.app_list.setRowHidden(row, not matches)

    def refresh_lists(self):
        # 1. Save current selections
        selected_pid = None
        selected_device_id = None
        
        selected_app_items = self.app_list.selectedItems()
        if selected_app_items:
            selected_pid = selected_app_items[0].data(Qt.ItemDataRole.UserRole)
                
        selected_dev_items = self.dev_list.selectedItems()
        if selected_dev_items:
            dev_data = selected_dev_items[0].data(Qt.ItemDataRole.UserRole)
            if dev_data:
                if svv_available():
                    selected_device_id = dev_data.get("Command-Line Friendly ID") or dev_data.get("Item ID")
                else:
                    selected_device_id = getattr(dev_data, "id", None)

        # 2. Clear lists
        self.app_list.clear()
        self.dev_list.clear()

        # 3. Fetch applications
        self.apps, shared_rows = get_sessions()
        for pid, name in self.apps:
            if not name:
                continue
            item = QListWidgetItem(self.app_list)
            item.setText(f"{name}  (PID: {pid})")
            
            icon_pixmap = self._get_app_icon(pid)
            if icon_pixmap:
                item.setIcon(QIcon(icon_pixmap))
            else:
                fallback = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_TitleBarMenuButton)
                item.setIcon(fallback)
            
            # Store data inside Item UserRoles
            item.setData(Qt.ItemDataRole.UserRole, pid)
            item.setData(Qt.ItemDataRole.UserRole + 1, name)

        # 4. Fetch devices
        devices_data = self._get_devices_list(shared_rows)
        for item_data, label, is_default in devices_data:
            item = QListWidgetItem(self.dev_list)
            display_text = f"{label}  [Predefinito]" if is_default else label
            item.setText(display_text)
            
            icon = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_MediaVolume)
            item.setIcon(icon)
            
            # Store data inside Item UserRoles
            item.setData(Qt.ItemDataRole.UserRole, item_data)
            item.setData(Qt.ItemDataRole.UserRole + 1, label)

        # 5. Restore application selection
        if selected_pid is not None:
            found_app = False
            for row in range(self.app_list.count()):
                item = self.app_list.item(row)
                pid = item.data(Qt.ItemDataRole.UserRole)
                if pid == selected_pid:
                    self.app_list.setCurrentItem(item)
                    found_app = True
                    break
            if not found_app and self.app_list.count() > 0:
                self.app_list.setCurrentRow(0)
        else:
            if self.app_list.count() > 0:
                self.app_list.setCurrentRow(0)

        # 6. Restore device selection
        if selected_device_id is not None:
            found_dev = False
            for row in range(self.dev_list.count()):
                item = self.dev_list.item(row)
                dev_data = item.data(Qt.ItemDataRole.UserRole)
                if dev_data:
                    dev_id = None
                    if svv_available():
                        dev_id = dev_data.get("Command-Line Friendly ID") or dev_data.get("Item ID")
                    else:
                        dev_id = getattr(dev_data, "id", None)
                    if dev_id == selected_device_id:
                        self.dev_list.setCurrentItem(item)
                        found_dev = True
                        break
            if not found_dev and self.dev_list.count() > 0:
                self.dev_list.setCurrentRow(0)
        else:
            if self.dev_list.count() > 0:
                self.dev_list.setCurrentRow(0)

        # 7. Re-apply search filter
        self.filter_apps(self.search_bar.text())

    def _get_devices_list(self, shared_rows):
        devices = []
        dev_labels = []
        
        if svv_available():
            default_row = svv_get_default_render_row(shared_rows)
            default_id = None
            if default_row:
                default_id = default_row.get("Command-Line Friendly ID") or default_row.get("Item ID")
                
            for name, row in svv_list_render_devices(shared_rows):
                label = name
                if label in dev_labels:
                    label = f"{label} (dup)"
                dev_labels.append(label)
                
                row_id = row.get("Command-Line Friendly ID") or row.get("Item ID")
                is_default = (row_id == default_id) if (default_id and row_id) else False
                devices.append((row, label, is_default))
        else:
            raw_devices = get_render_devices()
            seen_ids = set()
            try:
                default_id = get_default_device_id()
            except Exception:
                default_id = None
                
            for d in raw_devices:
                dev_id = getattr(d, "id", None)
                if not dev_id or dev_id in seen_ids:
                    continue
                name = getattr(d, "FriendlyName", None)
                if not name or str(name).strip().lower() == "none":
                    continue
                seen_ids.add(dev_id)
                label = name
                if label in dev_labels:
                    short_id = dev_id.split("{")[-1].split("}")[0][:6]
                    label = f"{label} ({short_id})"
                dev_labels.append(label)
                
                is_default = (dev_id == default_id) if default_id else False
                devices.append((d, label, is_default))
                
        return devices

    def _check_restart_on_change(self):
        try:
            current_sessions, _ = get_sessions()
            current = {pid for pid, _ in current_sessions}
            if current != self._last_session_ids:
                self._last_session_ids = current
                self.refresh_lists()
        except Exception:
            pass

    def _set_app_icon(self):
        icon_path = os.path.join(BASE_DIR, "app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _set_app_user_model_id(self):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AudioRouter.App")
        except Exception:
            pass

    def _load_window_state(self):
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            width = data.get("width", 800)
            height = data.get("height", 520)
            x = data.get("x")
            y = data.get("y")
            self.resize(width, height)
            if x is not None and y is not None:
                self.move(x, y)
        except Exception:
            pass

    def _save_window_state(self):
        try:
            rect = self.geometry()
            data = {
                "width": rect.width(),
                "height": rect.height(),
                "x": rect.x(),
                "y": rect.y()
            }
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _get_selected_app(self):
        selected_items = self.app_list.selectedItems()
        if not selected_items:
            return None
        item = selected_items[0]
        pid = item.data(Qt.ItemDataRole.UserRole)
        name = item.data(Qt.ItemDataRole.UserRole + 1)
        return (pid, name)

    def _get_selected_device(self):
        selected_items = self.dev_list.selectedItems()
        if not selected_items:
            return None
        item = selected_items[0]
        return item.data(Qt.ItemDataRole.UserRole)

    def _get_app_icon(self, pid):
        try:
            proc = psutil.Process(pid)
            exe = proc.exe()
        except Exception:
            return None
        if exe in self.app_icons:
            return self.app_icons[exe]
        try:
            large, small = win32gui.ExtractIconEx(exe, 0, 1)
            hicon = large[0] if large else (small[0] if small else None)
            if not hicon:
                for h in large: win32gui.DestroyIcon(h)
                for h in small: win32gui.DestroyIcon(h)
                return None
            
            icon_info = win32gui.GetIconInfo(hicon)
            hbm = icon_info[4]
            bmp = win32ui.CreateBitmapFromHandle(hbm)
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
            img = Image.frombuffer(
                "RGBA",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                bmpstr,
                "raw",
                "BGRA",
                0,
                1,
            )
            img = img.resize((24, 24), Image.Resampling.LANCZOS)
            
            for h in large: win32gui.DestroyIcon(h)
            for h in small: win32gui.DestroyIcon(h)
            win32gui.DeleteObject(icon_info[3])
            win32gui.DeleteObject(icon_info[4])
            
            img_rgba = img.convert("RGBA")
            data = img_rgba.tobytes("raw", "RGBA")
            qimage = QImage(data, img_rgba.size[0], img_rgba.size[1], QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            
            self.app_icons[exe] = pixmap
            return pixmap
        except Exception:
            return None

    def apply_route(self):
        app = self._get_selected_app()
        dev = self._get_selected_device()
        if not app or dev is None:
            QMessageBox.warning(self, APP_TITLE, "Seleziona un'applicazione e un dispositivo di riproduzione.")
            return
        pid, name = app
        try:
            if svv_available():
                device_name = dev.get("Device Name") or dev.get("Name")
                if not device_name:
                    raise RuntimeError("Nome dispositivo non valido.")
                svv_set_app_default(dev, pid)
                self.statusBar().showMessage(f"Instradamento: {name} → {device_name}", 6000)
            else:
                set_app_endpoint(pid, dev.id)
                self.statusBar().showMessage(f"Instradamento: {name} → {getattr(dev, 'FriendlyName', dev.id)}", 6000)
        except Exception as e:
            QMessageBox.critical(self, APP_TITLE, f"Errore durante il collegamento audio: {e}")

    def reset_route(self):
        app = self._get_selected_app()
        if not app:
            QMessageBox.warning(self, APP_TITLE, "Seleziona un'applicazione.")
            return
        pid, name = app
        try:
            if svv_available():
                svv_reset_app_default(pid)
                self.statusBar().showMessage(f"Predefinito di sistema: {name}", 6000)
            else:
                default_id = get_default_device_id()
                set_app_endpoint(pid, default_id)
                self.statusBar().showMessage(f"Impostato sul predefinito attuale: {name}", 6000)
        except Exception as e:
            QMessageBox.critical(self, APP_TITLE, f"Errore durante il ripristino predefinito: {e}")

    def closeEvent(self, event):
        self._save_window_state()
        try:
            comtypes.CoUninitialize()
        except Exception:
            pass
        try:
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)
        except Exception:
            pass
        event.accept()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        sys.exit(0)
    if not _acquire_lock():
        sys.exit(0)
        
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    gui = AudioRouterGUI()
    gui.show()
    
    sys.exit(app.exec())

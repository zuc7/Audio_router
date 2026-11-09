import unittest
from unittest.mock import patch

import audio_router_gui as router


class SessionFallbackTests(unittest.TestCase):
    @patch.object(router, "svv_available", return_value=True)
    @patch.object(router, "svv_export_rows", return_value=None)
    @patch.object(router.comtypes, "CoInitialize")
    @patch.object(router.comtypes, "CoUninitialize")
    @patch.object(router.psutil, "Process")
    @patch.object(router.AudioUtilities, "GetAllSessions")
    def test_failed_svv_export_falls_back_to_com(self, sessions, process, uninit, init, export, available):
        sessions.return_value = [type("Session", (), {"Process": object(), "ProcessId": 42})()]
        process.return_value.name.return_value = "player.exe"

        result, rows = router.get_sessions()

        self.assertEqual(result, [(42, "player.exe")])
        self.assertIsNone(rows)
        init.assert_called_once()
        uninit.assert_called_once()

    @patch.object(router.AudioUtilities, "GetAllDevices")
    def test_render_devices_come_from_com(self, get_devices):
        devices = [object()]
        get_devices.return_value = devices

        self.assertEqual(router.get_render_devices(), devices)
        get_devices.assert_called_once()

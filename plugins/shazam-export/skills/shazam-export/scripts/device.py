"""Selected-device ADB reads and recoverable USB display setting."""
import hashlib
import json
import re
import subprocess

from core import Paused, save_json


def fingerprint(device):
    return hashlib.sha256(device.encode()).hexdigest()


class Android:
    def __init__(self, adb, device):
        if not re.fullmatch(r'[A-Za-z0-9._:-]+', device):
            raise ValueError('Invalid device identifier')
        self.adb, self.device = adb, device
        result = subprocess.run([adb, 'devices'], capture_output=True, text=True, check=True, timeout=15)
        states = [line.split() for line in result.stdout.splitlines() if line.strip()]
        if [device, 'device'] not in states:
            raise Paused('selected_device_not_authorized')

    def shell(self, *args):
        return subprocess.run([self.adb, '-s', self.device, 'shell', *args],
            capture_output=True, text=True, check=True, timeout=20).stdout.strip()

    def reference_date(self):
        value = self.shell('date', '+%Y-%m-%d')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            raise Paused('device_date_unavailable')
        return value

    def version(self):
        match = re.search(r'\bversionName=([^\s]+)', self.shell('dumpsys', 'package', 'com.shazam.android'))
        if not match:
            raise Paused('shazam_not_installed')
        return match.group(1)


class Awake:
    def __init__(self, android, directory):
        self.android = android
        self.path = directory / 'screen-state.json'

    def restore(self):
        if not self.path.exists():
            return
        saved = json.loads(self.path.read_text())
        if saved['device_sha256'] != fingerprint(self.android.device):
            raise Paused('display_journal_device_mismatch')
        if saved.get('restored'):
            return
        old = saved['original']
        if old != 'null' and not re.fullmatch(r'\d+', old):
            raise Paused('invalid_display_journal')
        current = self.android.shell('settings', 'get', 'global', 'stay_on_while_plugged_in')
        if current not in ('2', old):
            raise Paused('display_setting_changed_independently')
        if old == 'null':
            self.android.shell('settings', 'delete', 'global', 'stay_on_while_plugged_in')
        else:
            self.android.shell('settings', 'put', 'global', 'stay_on_while_plugged_in', old)
        if self.android.shell('settings', 'get', 'global', 'stay_on_while_plugged_in') != old:
            raise Paused('display_restore_failed')
        saved['restored'] = True
        save_json(self.path, saved)

    def enable(self):
        self.restore()  # Recover a previous interrupted run before taking a new baseline.
        original = self.android.shell('settings', 'get', 'global', 'stay_on_while_plugged_in')
        save_json(self.path, {'device_sha256': fingerprint(self.android.device),
                              'original': original, 'restored': False})
        self.android.shell('svc', 'power', 'stayon', 'usb')
        if self.android.shell('settings', 'get', 'global', 'stay_on_while_plugged_in') != '2':
            raise Paused('display_wake_setting_failed')
        # This wakes the display; unlocking remains the user's action.
        self.android.shell('input', 'keyevent', '224')

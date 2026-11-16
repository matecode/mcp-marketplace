"""Configurable stdio MCP connection; no client settings are modified."""
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time

from core import Paused


def launch_config(path):
    entry = json.loads(Path(path).read_text())
    if not isinstance(entry.get('command'), str) or not entry['command']:
        raise ValueError('MCP launch config requires a command')
    args = entry.get('args', [])
    env = entry.get('env', {})
    if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
        raise ValueError('MCP args must be a string array')
    if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items()):
        raise ValueError('MCP env must contain strings')
    return entry


class Mobile:
    def __init__(self, config, directory):
        self.sequence, self.responses = 0, queue.Queue()
        self.log = (directory / 'mobile-stderr.log').open('ab')
        try:
            self.proc = subprocess.Popen([config['command'], *config.get('args', [])],
                cwd=config.get('cwd'), env={**os.environ, **config.get('env', {}),
                    'MOBILEMCP_DISABLE_TELEMETRY': '1', 'MOBILEWRIGHT_DISABLE_TELEMETRY': '1'},
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log,
                text=True, bufsize=1)
        except BaseException:
            self.log.close()
            raise
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()
        try:
            self.info = self.request('initialize', {'protocolVersion': '2025-03-26',
                'capabilities': {}, 'clientInfo': {'name': 'shazam-export-skill', 'version': '0.1.0'}})
            self.proc.stdin.write(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}) + '\n')
            self.proc.stdin.flush()
        except BaseException:
            self.close()
            raise

    def _read(self):
        for line in self.proc.stdout:
            try:
                self.responses.put(json.loads(line))
            except json.JSONDecodeError:
                continue
        self.responses.put(None)

    def request(self, method, params):
        self.sequence += 1
        self.proc.stdin.write(json.dumps({'jsonrpc': '2.0', 'id': self.sequence,
                                          'method': method, 'params': params}) + '\n')
        self.proc.stdin.flush()
        deadline = time.monotonic() + 45
        while True:
            try:
                item = self.responses.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty:
                raise Paused('mcp_timeout') from None
            if item is None:
                raise Paused('mcp_server_exited')
            if item.get('id') == self.sequence:
                if 'error' in item:
                    raise Paused('mcp_rpc_error')
                return item['result']

    def call(self, name, arguments):
        result = self.request('tools/call', {'name': name, 'arguments': arguments})
        if result.get('isError'):
            raise Paused('mobile_tool_failed')
        return result

    def devices(self):
        result = self.call('mobile_list_available_devices', {})
        return json.loads(self.text(result))['devices']

    @staticmethod
    def text(result):
        try:
            return next(b['text'] for b in result['content'] if b['type'] == 'text')
        except (KeyError, StopIteration):
            raise Paused('unsupported_mobile_response') from None

    def snapshot(self, device):
        text = self.text(self.call('mobile_list_elements_on_screen', {'device': device, 'format': 'json'}))
        try:
            nodes = json.loads(text[text.index('['):])
            if not isinstance(nodes, list):
                raise ValueError()
            return nodes
        except (ValueError, KeyError):
            raise Paused('unsupported_snapshot_format') from None

    def close(self):
        try:
            self.proc.stdin.close()
        except BrokenPipeError:
            pass
        try:
            self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        self.reader.join(timeout=2)
        self.proc.stdout.close()
        self.log.close()

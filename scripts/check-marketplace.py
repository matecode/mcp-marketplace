"""Offline: Katalogkonsistenz, öffentliche HTTP-Konfiguration und Skill-Pakete."""
from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "mail": "openid profile email offline_access mailbox",
    "calendar": "openid profile email offline_access mailbox",
    "obsidian": "openid profile email offline_access",
    "kleinanzeigen": "openid profile email offline_access",
    "lizu": "openid profile email offline_access lizu",
    "homeassistant": None,
    "fileee": "openid profile email offline_access fileee",
    "bandcamp": "openid profile email offline_access bandcamp",
}

def read(path):
    return json.loads((ROOT / path).read_text())

claude = read(".claude-plugin/marketplace.json")
codex = read(".agents/plugins/marketplace.json")
assert claude["name"] == codex["name"] == "mate-mcp"
expected_names = {key + "-mcp" for key in EXPECTED} | {'shazam-export'}
for catalog in (claude, codex):
    names = [entry["name"] for entry in catalog["plugins"]]
    assert len(names) == len(set(names)) == len(expected_names)
    assert set(names) == expected_names
for key, scopes in EXPECTED.items():
    name = key + "-mcp"
    relative = "./plugins/" + name
    ce = next(p for p in claude["plugins"] if p["name"] == name)
    oe = next(p for p in codex["plugins"] if p["name"] == name)
    assert ce["source"] == relative
    assert oe["source"] == {"source": "local", "path": relative}
    assert oe["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}
    folder = ROOT / relative
    assert folder.resolve().is_relative_to(ROOT.resolve())
    cm = read(relative + "/.claude-plugin/plugin.json")
    om = read(relative + "/.codex-plugin/plugin.json")
    assert cm["name"] == om["name"] == name
    assert cm["version"] == om["version"] == ce["version"]
    assert om["mcpServers"] == ("./mcp.codex.json" if key == "fileee" else "./.mcp.json")
    connection = {"type": "http", "url": f"https://mcp.bunteban.de/{key}/mcp"}
    if scopes is not None:
        connection["oauth"] = {"scopes": scopes}
    if key == "fileee":
        connection["oauth"].update(clientId="fileee-mcp", callbackPort=8767)
    assert read(relative + "/.mcp.json") == {"mcpServers": {key: connection}}
    if key == "fileee":
        assert read(relative + "/mcp.codex.json") == {
            "mcpServers": {"fileee": {
                "type": "http", "url": connection["url"],
                "oauth": {"client_id": "fileee-mcp", "callback_port": 8766, "scopes": scopes.split()},
            }},
        }
ha = ROOT / 'plugins/homeassistant-mcp'
origin = read('plugins/homeassistant-mcp/upstream-skill.json')
assert origin['repository'] == 'https://github.com/homeassistant-ai/skills'
assert origin['license'] == 'MIT' and len(origin['commit']) == 40
actual = {str(p.relative_to(ha)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in (ha / 'skills/home-assistant-best-practices').rglob('*') if p.is_file()}
assert actual == origin['files'], 'Incomplete or changed upstream skill bundle'
assert len(actual) == 17, 'Expected entrypoint, 15 references and license'
assert (ha / 'skills/home-assistant-best-practices/SKILL.md').is_file()
assert (ha / 'skills/home-assistant-best-practices/LICENSE').is_file()
relative = './plugins/shazam-export'
ce = next(p for p in claude['plugins'] if p['name'] == 'shazam-export')
oe = next(p for p in codex['plugins'] if p['name'] == 'shazam-export')
assert ce['source'] == relative
assert oe['source'] == {'source': 'local', 'path': relative}
assert oe['policy'] == {'installation': 'AVAILABLE'}
cm = read(relative + '/.claude-plugin/plugin.json')
om = read(relative + '/.codex-plugin/plugin.json')
assert cm['name'] == om['name'] == 'shazam-export'
assert cm['version'] == om['version'] == ce['version'] == '0.1.0'
assert 'mcpServers' not in cm and 'mcpServers' not in om
assert not (ROOT / relative / '.mcp.json').exists()
skill = ROOT / relative / 'skills/shazam-export'
for path in ('SKILL.md', 'agents/openai.yaml', 'references/run.md', 'references/output.md',
             'scripts/export.py', 'scripts/core.py', 'scripts/mobile.py', 'scripts/device.py'):
    assert (skill / path).resolve().is_relative_to(skill.resolve())
    assert (skill / path).is_file(), path
    assert '[TODO' not in (skill / path).read_text(), path
assert 'name: shazam-export' in (skill / 'SKILL.md').read_text()
print("Neun konsistente Plugins: acht HTTP-MCPs, ein Export-Skill; beide Kataloge und gepinnter HA-Skill geprüft.")

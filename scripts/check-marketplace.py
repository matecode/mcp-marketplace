"""Offline: Katalogkonsistenz, Pfade und ausschließlich öffentliche HTTP-Konfiguration."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "mail": "openid profile email offline_access mailbox",
    "calendar": "openid profile email offline_access mailbox",
    "obsidian": "openid profile email offline_access",
    "kleinanzeigen": "openid profile email offline_access",
    "lizu": "openid profile email offline_access lizu",
    "homeassistant": "openid profile email offline_access homeassistant",
}

def read(path):
    return json.loads((ROOT / path).read_text())

claude = read(".claude-plugin/marketplace.json")
codex = read(".agents/plugins/marketplace.json")
assert claude["name"] == codex["name"] == "mate-mcp"
expected_names = {key + "-mcp" for key in EXPECTED}
for catalog in (claude, codex):
    names = [entry["name"] for entry in catalog["plugins"]]
    assert len(names) == len(set(names)) == len(EXPECTED)
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
    assert om["mcpServers"] == "./.mcp.json"
    assert read(relative + "/.mcp.json") == {"mcpServers": {key: {
        "type": "http", "url": f"https://mcp.bunteban.de/{key}/mcp",
        "oauth": {"scopes": scopes},
    }}}
print("Sechs konsistente Plugins, zwei Kataloge; nur festgelegte öffentliche HTTP-Verbindungsdaten.")

# Mate MCP Marketplace

Öffentlicher Plugin-Katalog `matecode/mcp-marketplace`, Marketplace-ID `mate-mcp`. Deutsch.

Nur Plugin-Metadaten, MCP-Verbindungsdaten und technische Installationshinweise pflegen. Keine Secrets, Nutzdaten, Vault-Inhalte oder Serverkonfigurationen übernehmen. Repository-Zugriff und persönliche Dienstfreigabe sind unabhängig. Änderungen hier erteilen keine Freigabe für NAS-Deployments.

Claude-Katalog: `.claude-plugin/marketplace.json`; Codex-Katalog: `.agents/plugins/marketplace.json`. Gemeinsame Plugins unter `plugins/`, je Plugin Claude-/Codex-Manifest und `.mcp.json`. Namen, Versionen, Pfade und URLs konsistent halten. Keine lokale Werkzeug-Allowlist oder zusätzliche Gesprächsablage-Skills hinzufügen.

Prüfen: `python3 scripts/check-marketplace.py` und `claude plugin validate . --strict`. Client-Laden/Installation mit isolierten temporären Konfigurationsverzeichnissen prüfen, ohne persönliche Clientkonfiguration zu verändern. OAuth, Werkzeugfunktion und Refresh getrennt von Paketprüfungen dokumentieren. Keine Schreibproben an Mail, Kalender, Anzeigen oder Vault ohne konkreten Auftrag.

Übergreifendes Betriebswissen im Homelab-Vault; Infrastrukturquellen in `matecode/homelab-infra`.

Öffentliche Git-Historie mitprüfen; niemals Geheimnisse oder interne Betriebsdetails aufnehmen. Anonymes HTTPS ist der Standard-Installationsweg. Änderungen der Repository-Sichtbarkeit nur auf ausdrücklichen Nutzerauftrag.

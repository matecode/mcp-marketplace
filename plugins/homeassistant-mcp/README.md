# Home Assistant MCP

Verbindung: `https://mcp.bunteban.de/homeassistant/mcp`.

Mit Authentik anmelden; die Freigabegruppe für Home Assistant ist erforderlich. Jeder Nutzer hinterlegt seinen eigenen HA-Token im persönlichen OpenBao-Eintrag, Feld `token`. `homeassistant_connection_status` zeigt den passenden Einrichtungslink. Die OpenBao-Oberfläche ist nur im Heimnetz oder per bestehendem VPN erreichbar. Keine Tokens im Chat eingeben.

Die Werkzeuge verwenden ausschließlich den persönlichen HA-Token und dessen Rechte. Das Plugin richtet weder einen HA-Server noch ein HA-Konto ein. Alle angebotenen HA-MCP-Werkzeuge sind verfügbar, einschließlich Gerätesteuerung und administrativer Änderungen, soweit das persönliche HA-Konto sie erlaubt.

Installation, OAuth-Anmeldung, Werkzeugfunktion und Refresh sind getrennte Prüfungen. Bei bereits vorhandenem separat eingerichteten Home-Assistant-MCP zunächst doppelte Verbindungen vermeiden.

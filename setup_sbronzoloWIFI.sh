#!/bin/bash
set -e

echo "=== Avvio configurazione Hotspot Wi-Fi Standalone Sbronzolo ==="

# 1. Sblocco radio e impostazione Paese (IT)
echo "[1/6] Configurazione radio Wi-Fi e dominio Italia..."
sudo raspi-config nonint do_wifi_country IT 2>/dev/null || true
sudo rfkill unblock wifi
sudo nmcli radio wifi on

# 2. Pulizia vecchi servizi in conflitto
echo "[2/6] Disattivazione servizi in conflitto (hostapd)..."
sudo systemctl stop hostapd 2>/dev/null || true
sudo systemctl disable hostapd 2>/dev/null || true
sudo systemctl mask hostapd 2>/dev/null || true

# 3. Installazione dnsmasq
echo "[3/6] Installazione pacchetto dnsmasq..."
sudo apt update
sudo apt install -y dnsmasq

# 4. Configurazione dnsmasq (DHCP + Antidisconnessione Smartphone)
echo "[4/6] Configurazione server DHCP/DNS su wlan0..."
cat << 'EOF' | sudo tee /etc/dnsmasq.d/sbronzolo-dhcp.conf > /dev/null
# Servizio attivo ESCLUSIVAMENTE su wlan0
interface=wlan0
except-interface=eth0

# Range dinamico IP per i client Wi-Fi
dhcp-range=192.168.4.10,192.168.4.50,255.255.255.0,12h

# Gateway e DNS puntati al Raspberry Pi
dhcp-option=option:router,192.168.4.1
dhcp-option=option:dns-server,192.168.4.1

# Reindirizza tutte le richieste DNS al Raspberry Pi (riduce le disconnessioni automatiche dei telefoni)
address=/#/192.168.4.1
EOF

# 5. Creazione/Aggiornamento connessione NetworkManager (SbronzoloAP)
echo "[5/6] Configurazione connessione NetworkManager..."

# Elimina eventuale profilo vecchio corrotto per ripartire da zero
sudo nmcli con delete SbronzoloAP 2>/dev/null || true

# Ricrea l'Access Point in modalità manuale sul canale 6 (2.4 GHz)
sudo nmcli con add type wifi ifname wlan0 mode ap con-name SbronzoloAP ssid Sbronzolo_WiFi 802-11-wireless.band bg 802-11-wireless.channel 6
sudo nmcli con modify SbronzoloAP \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "sbronzolo" \
    autoconnect yes \
    ipv4.method manual \
    ipv4.addresses "192.168.4.1/24" \
    ipv4.gateway "" \
    ipv6.method disabled

# 6. Riavvio e verifica dei servizi
echo "[6/6] Riavvio servizi e attivazione Hotspot..."
sudo systemctl enable dnsmasq
sudo systemctl restart dnsmasq

sudo nmcli con down SbronzoloAP 2>/dev/null || true
sudo nmcli con up SbronzoloAP

echo ""
echo "=========================================================="
echo " Configurazione completata con successo!"
echo " SSID:             Sbronzolo_WiFi"
echo " Password:         sbronzolo"
echo " IP Raspberry Pi:  192.168.4.1"
echo " Canale Wi-Fi:     6 (2.4 GHz)"
echo "=========================================================="
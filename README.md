# TP-Link Deco for Home Assistant

[![CI](https://github.com/roquerodrigo/ha-tplink-deco/actions/workflows/ci.yml/badge.svg)](https://github.com/roquerodrigo/ha-tplink-deco/actions/workflows/ci.yml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Custom integration that connects Home Assistant to a TP-Link Deco mesh network
through the router's local web API. No cloud account required.

## Features

For each connected client device, the integration creates:

- **Device tracker** (presence: home / away)
- **Binary sensor** — connected status
- **Sensors** — IP address, MAC address, download speed, upload speed,
  connection type (2.4 GHz / 5 GHz / 6 GHz / Wired), interface (main / IoT /
  MLO)

For each Deco mesh node, the integration creates:

- **Sensors** — IP address, MAC address
- **Binary sensor** — internet connectivity (master node only)

For the master Deco node, the integration also creates:

- **Sensors** — CPU usage, memory usage, online clients counter

Each client device is linked via `via_device` to the master Deco node so the
device hierarchy in Home Assistant reflects the mesh topology. All Deco
BSSIDs (main, AP and backhaul STA) are registered as `CONNECTION_NETWORK_MAC`
so other discovery flows (DHCP, etc.) can correlate the same physical device.

## Requirements

- Home Assistant 2026.3.2 or newer
- A TP-Link Deco mesh network with the local web admin enabled
- Router credentials (username and password used in the Deco app)

## Installation

### HACS (recommended)

1. In HACS, open the menu and choose **Custom repositories**.
2. Add this repository's URL with category **Integration**.
3. Install the **TP-Link Deco** integration from the HACS list.
4. Restart Home Assistant.

### Manual

1. Download or clone this repository.
2. Copy `custom_components/tplink_deco` into your Home Assistant
   `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

After installing and restarting:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **TP-Link Deco**.
3. Enter the router IP, username and password.

The integration uses Home Assistant's UI config flow — there is no YAML
configuration. Updates are polled every 10 seconds.

## Translations

Bundled language files: English and Portuguese (Brazil). To add a new
language, copy `custom_components/tplink_deco/translations/en.json` to
`<lang>.json` and translate the values.

## Development

See [CODE_STYLE.md](CODE_STYLE.md) for project conventions and
[CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

```bash
source .venv/bin/activate
bash scripts/develop   # starts HA at http://localhost:8123
bash scripts/lint      # run formatter and linter
```

## License

MIT — see [LICENSE](LICENSE).

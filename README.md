# TP-Link Deco for Home Assistant

[![CI](https://github.com/roquerodrigo/ha-tplink-deco/actions/workflows/ci.yml/badge.svg)](https://github.com/roquerodrigo/ha-tplink-deco/actions/workflows/ci.yml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white&style=for-the-badge)](https://github.com/sponsors/roquerodrigo)

[![Open your Home Assistant instance and open the repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=roquerodrigo&repository=ha-tplink-deco&category=integration)

---

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

## Bundled Lovelace card

The integration ships a custom dashboard card that lists the clients
connected to the mesh with their connection state, address and live
throughput. The card is served by the integration itself and registered as a
Lovelace dashboard resource automatically — no manual resource setup is
required. Add it to any dashboard with:

```yaml
type: custom:tplink-deco-card
```

Optional settings: `devices` (device ids to show), `secondary_info`
(`ip` | `mac` | `connection` | `none`), `sort`
(`name` | `download` | `upload` | `connection`), `columns` (1–6) and
`show_offline`. The card also provides a visual editor in the dashboard UI
and is translated into English and Portuguese (Brazil).

## Requirements

- Home Assistant 2026.5.3 or newer
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
configuration. If the router password changes, Home Assistant prompts for
reauthentication instead of silently failing.

The same form exposes two polling settings, also editable later through
**Reconfigure**:

| Setting | Default | Range |
|---|---|---|
| Update interval | 20 s | 10–600 s |
| Request timeout | 30 s | 5–120 s |

Large networks take longer to answer: on a mesh with dozens of connected
clients, raise both values until the polls comfortably fit inside the
interval.

## Translations

Bundled language files: English and Portuguese (Brazil). To add a new
language, copy `custom_components/tplink_deco/translations/en.json` to
`<lang>.json` and translate the values.

## Development

See [CODE_STYLE.md](CODE_STYLE.md) for project conventions and
[CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

```bash
source .venv/bin/activate
bash scripts/develop                     # starts HA at http://localhost:8123
uv run ruff format .                     # format
uv run ruff check . --fix                # lint
uv run mypy custom_components/tplink_deco # type-check
```

## Support

This integration is built and maintained on personal time, on hardware bought for the purpose. If it is useful to you, consider [sponsoring the work](https://github.com/sponsors/roquerodrigo) — it keeps the devices, the testing and the releases coming.

## License

MIT — see [LICENSE](LICENSE).

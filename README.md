# TP-Link Deco

<!-- ha-marketplace:exclude-start -->
[![CI](https://github.com/roquerodrigo/ha-tplink-deco/actions/workflows/ci.yml/badge.svg)](https://github.com/roquerodrigo/ha-tplink-deco/actions/workflows/ci.yml)
[![GitHub release](https://img.shields.io/github/v/release/roquerodrigo/ha-tplink-deco)](https://github.com/roquerodrigo/ha-tplink-deco/releases/latest)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/roquerodrigo)

[![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=roquerodrigo&repository=ha-tplink-deco&category=integration)
<!-- ha-marketplace:exclude-end -->

See who is connected to your TP-Link Deco mesh, how much each device is
downloading and whether every Deco still reaches the internet. Home Assistant
talks to the main Deco on your local network, using the same login as the
Deco's web admin page, so nothing goes through TP-Link's cloud.

## Features

- Know when a phone joins or leaves the network, and use it to trigger
  automations when someone gets home.
- Follow the download and upload speed of each device, and of the whole
  network, along with the Wi-Fi band and network it uses.
- See when a Deco loses its internet connection, and keep an eye on the CPU
  and memory of the main Deco.
- Add a card to your dashboard that lists every device on the mesh, with no
  extra setup.
- On the devices page, each device appears under the main Deco.

## Requirements

- Home Assistant 2026.10.4 or newer.
- A TP-Link Deco mesh network that Home Assistant can reach.
- The IP address of the main Deco and the user name and password of its web
  admin page.

<!-- ha-marketplace:exclude-start -->
## Installation

### Home Assistant Marketplace (recommended)

1. Select the **Open your Home Assistant instance** button above, or go to
   **Settings → Marketplace**, select **Add from link** in the upper right
   corner, enter `roquerodrigo/ha-tplink-deco` and select **Add**.
2. Select **Install**.
3. Restart Home Assistant.

The Marketplace comes with Home Assistant 2026.11 and later. On older
versions, add this repository to HACS as a custom repository of type
**Integration** and install it from there.

### Manual

1. Download `tplink_deco.zip` from the
   [latest release](https://github.com/roquerodrigo/ha-tplink-deco/releases/latest).
2. Extract it into `config/custom_components/tplink_deco/`.
3. Restart Home Assistant.
<!-- ha-marketplace:exclude-end -->

## Configuration

Go to **Settings → Devices & services → Add integration**, search for
**TP-Link Deco** and fill in the form.

| Field             | What to enter                                              | Default |
|-------------------|------------------------------------------------------------|---------|
| Router IP Address | The address of the main Deco                               |         |
| Username          | The user name of the Deco's web admin page                 |         |
| Password          | The password of the Deco's web admin page                  |         |
| Update interval   | Seconds between updates, from 10 to 600                    | 20      |
| Request timeout   | Seconds to wait for each answer from the Deco, 5 to 120    | 30      |

A mesh with dozens of devices takes longer to answer. If updates start to
time out, raise both values.

To change any of these later, open the integration and select
**Reconfigure**. Leave the password empty to keep the current one. If you
change the password on the Deco, Home Assistant asks you for the new one.

## Entities

### Each connected device

| Entity          | Type           | Shows                                       |
|-----------------|----------------|---------------------------------------------|
| Device name     | Device tracker | Home or Away                                |
| Connected       | Binary sensor  | Whether it is connected right now           |
| Download Speed  | Sensor         | Download speed in kbit/s                    |
| Upload Speed    | Sensor         | Upload speed in kbit/s                      |
| Connection Type | Sensor         | 2.4 GHz, 5 GHz, 6 GHz or Wired              |
| Interface       | Sensor         | Main, IoT or Multi-Link Operation network   |
| IP Address      | Sensor         | Diagnostic                                  |
| MAC Address     | Sensor         | Diagnostic                                  |

### Each Deco

| Entity      | Type          | Shows                               |
|-------------|---------------|-------------------------------------|
| Internet    | Binary sensor | Whether this Deco reaches the internet |
| IP Address  | Sensor        | Diagnostic                          |
| MAC Address | Sensor        | Diagnostic                          |

### Main Deco

| Entity               | Type   | Shows                              |
|----------------------|--------|------------------------------------|
| CPU Usage            | Sensor | Percentage                         |
| Memory Usage         | Sensor | Percentage                         |
| Online Clients       | Sensor | Number of connected devices        |
| Total Download Speed | Sensor | Download speed of the whole network |
| Total Upload Speed   | Sensor | Upload speed of the whole network  |

Devices that connect for the first time appear on their own, without a
restart.

## Dashboard card

Search for **TP-Link Deco** in the card picker of any dashboard. The card
lists the devices on the mesh with their state, address and current speed,
and you can set it up in the visual editor. In YAML:

```yaml
type: custom:tplink-deco-card
```

| Option           | Accepts                                    | Default     |
|------------------|--------------------------------------------|-------------|
| `devices`        | A list of device IDs                       | All devices |
| `secondary_info` | `ip`, `mac`, `connection` or `none`        | `ip`        |
| `sort`           | `name`, `download`, `upload` or `connection` | `name`    |
| `columns`        | 1 to 6                                     | `2`         |
| `show_offline`   | `true` or `false`                          | `true`      |

The card is available in English and Portuguese (Brazil).

## How it works

Home Assistant asks the main Deco for the connected devices, the mesh and its
load at every update interval. Everything stays on your local network.

A device that disappears for a moment keeps its last state for up to 10
minutes. A phone that puts its Wi-Fi to sleep does not show as Away because of
it. Speeds are averaged over the last updates, so a short burst does not
dominate the graph.

CPU Usage and Memory Usage take a few seconds longer than the other entities
to show a value after Home Assistant starts, because the Deco needs about
three seconds to measure them.

## Troubleshooting

**A device I deleted came back.** You can only delete a device while it is
offline, and it comes back the next time it connects. Devices that are online
and the Decos themselves cannot be deleted.

**Updates time out.** Raise the update interval and the request timeout with
**Reconfigure**.

**Something else is wrong.** Download the diagnostics from the integration's
menu and attach them to an
[issue](https://github.com/roquerodrigo/ha-tplink-deco/issues). The password
is removed from the file.

## Known limitations

The Deco allows one login per account at a time. Signing in to the web admin
page with the same account logs Home Assistant out. Home Assistant signs in
again on its next update, which logs you out of the web admin page.

## Support

This integration is built and maintained on personal time, on hardware bought
for the purpose. If it is useful to you, consider
[sponsoring the work](https://github.com/sponsors/roquerodrigo). It keeps the
devices, the testing and the releases coming.

<!-- ha-marketplace:exclude-start -->
## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup and
workflow, and [CODE_STYLE.md](CODE_STYLE.md) for the code conventions.

## License

[MIT](LICENSE)
<!-- ha-marketplace:exclude-end -->

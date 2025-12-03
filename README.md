# Allianz BonusDrive Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration) ![GitHub Release](https://img.shields.io/github/v/release/xathon/Allianz-Bonusdrive-Homeassistant?link=https%3A%2F%2Fgithub.com%2Fxathon%2FAllianz-BonusDrive-HomeAssistant%2Freleases%2Flatest)  ![GitHub commits since latest release](https://img.shields.io/github/commits-since/xathon/Allianz-Bonusdrive-Homeassistant/latest) ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/xathon/Allianz-Bonusdrive-Homeassistant) ![GitHub Issues or Pull Requests](https://img.shields.io/github/issues-pr/xathon/Allianz-Bonusdrive-Homeassistant) ![Static Badge](https://img.shields.io/badge/badges-all_of_them-green)




A Home Assistant integration for [Allianz BonusDrive](https://www.allianz.de/auto/kfz-versicherung/telematik-versicherung/) that displays your driving scores and trip information.

## Features

### Sensors

- **Last Trip** - Overall trip score with attributes:
  - Distance, duration, average/max speed
  - Start/end times and coordinates
  - Start/end locations (requires Photon geocoding)
  - Detailed scores (speeding, braking, acceleration, cornering)

- **Daily Badge** - Current daily driving score with badge level (gold/silver/bronze/red/blue)

- **Monthly Badge** - Current monthly badge status

## Installation

### HACS (Recommended)
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=xathon&repository=Allianz-Bonusdrive-Homeassistant)

1. Add this repository as a custom repository in HACS
2. Search for "BonusDrive" and install
3. Restart Home Assistant

### Manual

1. Copy `custom_components/bonusdrive` to your `config/custom_components` directory
2. Restart Home Assistant

## Configuration

Add the integration via **Settings → Devices & Services → Add Integration → BonusDrive**.

| Option | Required | Description |
|--------|----------|-------------|
| Email | Yes | Your BonusDrive account email |
| Password | Yes | Your BonusDrive account password |
| Base URL | No | API base URL (default: `https://bonusdrive.drivesync.com`) |
| Photon URL | No | [Photon](https://photon.komoot.io/) geocoding server URL to resolve trip coordinates to addresses |

The Photon URL can also be added or changed later via **Settings → Devices & Services → Allianz BonusDrive → Configure**. If you don't have your own Photon instance, you could probably use the default instance (https://photon.komoot.io/), though I don't know how lenient their rate limits are, so I didn't want to set it as default.

## Disclaimer
- The client used for the requests pretends to be the BonusDrive app, using HTTP headers. This a) may break at any point and b) is very much not intended behavior and might be against ToS, no idea. Though I did actually check the TOS and they didn't say that automatic requests weren't allowed (which actually surprises me, lots of companies do that). Home Assistant queries every 15 minutes, which should be fine? I'm not responsible if anything happens to your account, insurance contract, Club Penguin membership, yada yada.
- I haven't yet found out how long a TGT is valid, or if it expires at any point. STs are invalidated after each use (successful or not), good job!
- LLMs have been involved in creating and debugging this program. I *mostly* know what I'm doing, so that should be fine? See above for my responsibilities.

## Credits

Uses the [Allianz BonusDrive Client](https://github.com/xathon/Allianz-BonusDrive-Client) library.


# Allianz BonusDrive Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

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

1. Add this repository as a custom repository in HACS
2. Search for "Allianz BonusDrive" and install
3. Restart Home Assistant

### Manual

1. Copy `custom_components/bonusdrive` to your `config/custom_components` directory
2. Restart Home Assistant

## Configuration

Add the integration via **Settings → Devices & Services → Add Integration → Allianz BonusDrive**.

| Option | Required | Description |
|--------|----------|-------------|
| Email | Yes | Your BonusDrive account email |
| Password | Yes | Your BonusDrive account password |
| Base URL | No | API base URL (default: `https://bonusdrive.drivesync.com`) |
| Photon URL | No | [Photon](https://photon.komoot.io/) geocoding server URL to resolve trip coordinates to addresses |

The Photon URL can also be added or changed later via **Settings → Devices & Services → Allianz BonusDrive → Configure**.

## Credits

Uses the [Allianz BonusDrive Client](https://github.com/xathon/Allianz-BonusDrive-Client) library.


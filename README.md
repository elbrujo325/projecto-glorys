# 🌊 Projecto GLORYS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE) [![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org) [![Made with Jupyter](https://img.shields.io/badge/Made%20with-Jupyter-orange.svg)](https://jupyter.org) [![Copernicus Marine](https://img.shields.io/badge/Data-GLORYS12V1-cyan.svg)](https://data.marine.copernicus.eu/)

**Oceanographic analysis of the Peruvian coastal system using GLORYS12V1 reanalysis (1993–2026)**

---

## 📝 Overview

A comprehensive climatological analysis of Sea Surface Temperature (SST), salinity, and ocean currents along the Peruvian coast (83°W–73°W, 0.5°S–19°S) using the **GLORYS12V1** global ocean reanalysis at 1/12° resolution (~8 km). The project covers 34 years of monthly data (January 1993 – 2026), with a focus on January climatology, interannual variability, and ENSO signal detection.

The analysis pipeline spans from automated data acquisition via the Copernicus Marine API to spatial dashboard generation, statistical profiling, and spectral decomposition.

---

## 🔑 Key Features

- **Automated data download** from Copernicus Marine Service (`copernicusmarine` CLI) with chunked 2-year intervals
- **Multi-panel SST dashboard** — 34 January maps (1993–2026) + climatological mean + anomaly panel with dark-themed styling
- **SST time series analysis** — interannual evolution with linear trend (°C/decade), El Niño year shading, and min/max annotations
- **Surface current speed maps** — horizontal velocity magnitude (|V| = √(u² + v²)) for all Januaries with climatological anomaly
- **Descriptive statistics** — full table with N, mean, median, std, percentiles for θ (temperature), salinity, zonal/meridional velocity, and speed
- **Vertical profile analysis** — depth-dependent distributions via histograms and vertical profile plots (0.5 m – 1942 m)
- **Latitude cross-sections** — depth–longitude sections of current speed at 2°S, 5°S, 10°S, 14°S, 18°S with logarithmic depth scale, per-year panels, and climatological comparison
- **Point time series** — SST evolution at specific coastal locations (e.g., 12°S, 77.2°W off Lima)
- **FFT spectral analysis** — amplitude spectrum of SST at coastal point, revealing the annual cycle and sub-annual harmonics in physical units (°C)

---

## 🗺️ Study Region

| Parameter | Value |
|---|---|
| **Domain** | Peruvian coast, SE Pacific |
| **Longitude** | 83.38°W – 73.26°W |
| **Latitude** | 19.30°S – 0.42°S |
| **Depth range** | 0.49 m – 1941.89 m |
| **Resolution** | 1/12° (~8 km) |
| **Time span** | Jan 1993 – 2026 (monthly) |

---

## 📊 Variables Analyzed

| Variable | GLORYS ID | Units | Description |
|---|---|---|---|
| `thetao` | Sea temperature | °C | Potential temperature (SST at depth=0) |
| `so` | Salinity | PSU | Practical salinity |
| `uo` | Eastward velocity | m/s | Zonal current component |
| `vo` | Northward velocity | m/s | Meridional current component |
| `speed` | √(uo² + vo²) | m/s | Horizontal current magnitude (derived) |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/elbrujo325/projecto-glorys.git
cd projecto-glorys

# Install dependencies
pip install numpy pandas xarray matplotlib cartopy cmocean copernicusmarine

# Download data (requires free Copernicus Marine account)
# Set your credentials: copernicusmarine login
jupyter notebook Codigos/analisis_climatologic_oceanografia.ipynb

# Or run the standalone dashboard script
python Codigos/dashboard_enero_glorys.py
```

> **Note:** NetCDF data files are not included in this repo (see `.gitignore`). Download them via the notebook's first cell or the Copernicus Marine subset API.

---

## 📁 Project Structure

```
projecto-glorys/
├── Codigos/
│   ├── analisis_climatologic_oceanografia.ipynb   ← Main analysis notebook
│   ├── dashboard_enero_glorys.py                  ← Standalone SST dashboard script
│   ├── dashboard_SST_enero_glorys12v1.png         ← Dashboard output
│   └── serie_temporal_SST_enero_glorys12v1.png    ← Time series output
├── Datos Glorys/                                  ← NetCDF data (not tracked)
└── .gitignore
```

### Notebook Contents

| Cell | Analysis |
|---|---|
| 1 | **Data download** — Copernicus Marine API with 2-year chunks |
| 2 | **Data loading** — xarray `open_mfdataset` with lazy Dask arrays |
| 3 | **SST January dashboard** — 34 panels + climatology + anomaly |
| 4 | **Surface speed maps** — |V| for all Januaries + climatology + anomaly |
| 5–6 | **Point time series** — SST and salinity at coastal point (12°S, 77.2°W) |
| 7–8 | **Descriptive statistics** — Full table + histograms + vertical profiles |
| 9–14 | **Latitude cross-sections** — Speed vs depth at 2°S, 5°S, 10°S, 14°S, 18°S |
| 15 | **Coastal SST time series** — Full-record evolution off Lima |
| 16 | **FFT spectral analysis** — Amplitude spectrum revealing annual/semi-annual cycles |

---

## 🛠️ Tech Stack

**Python** · **xarray** · **Dask** · **Cartopy** · **Matplotlib (GridSpec)** · **cmocean** · **NumPy (FFT)** · **Copernicus Marine API**

---

## 📈 Sample Outputs

### SST Dashboard — January Climatology (1993–2026)
Multi-panel map showing SST spatial patterns for every January in the 34-year record, plus the climatological mean and the anomaly of the most recent year.

### SST Time Series — Interannual Trend
Line plot of area-averaged SST each January with linear trend (°C/decade), climatological reference line, and El Niño event shading (1997/98, 2015/16, 2023).

### Latitude Cross-Sections
Depth–longitude sections of current speed at 5 latitudes along the Peruvian coast, revealing the vertical structure of the Humboldt Current system with logarithmic depth scaling.

---

## ⚙️ Dashboard Script

`dashboard_enero_glorys.py` is a standalone production-ready script that generates:

- **SST map dashboard** — Dark-themed (navy background) with `cmocean.cm.thermal` colormapping, gold-bordered climatology panel, cyan-bordered anomaly panel, and per-panel mean annotations
- **SST time series** — Area-averaged January SST with trend line, El Niño markers, and annotated extremes

```bash
# Run (edit DATA_DIR path inside the script first)
python Codigos/dashboard_enero_glorys.py
```

Outputs: `dashboard_SST_enero_glorys12v1.png` and `serie_temporal_SST_enero_glorys12v1.png`

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](./LICENSE) for details.

**Data source:** [Copernicus Marine Service](https://data.marine.copernicus.eu/) — GLORYS12V1 Reanalysis · CMEMS

---

<div align="center">

*By [Henry Paolo Alfaro Sotil](https://github.com/elbrujo325) — Physicist & Data Scientist*

</div>

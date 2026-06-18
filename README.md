# 🌊 Projecto GLORYS

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE) [![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://python.org) [![Made with Jupyter](https://img.shields.io/badge/Made%20with-Jupyter-orange.svg)](https://jupyter.org) [![Copernicus Marine](https://img.shields.io/badge/Data-GLORYS12V1-cyan.svg)](https://data.marine.copernicus.eu/)

**Oceanographic analysis of the Peruvian coastal system using GLORYS12V1 reanalysis (1993–2026)**

---

## 📝 Overview

A comprehensive climatological analysis of Sea Surface Temperature (SST), salinity, and ocean currents along the Peruvian coast (83°W–73°W, 0.5°S–19°S) using the **GLORYS12V1** global ocean reanalysis at 1/12° resolution (~8 km). The project covers 34 years of monthly data (January 1993 – 2026), with a focus on January climatology, interannual variability, ENSO signal detection, and **vertical profile dynamics** across the water column.

The analysis pipeline spans from automated data acquisition via the Copernicus Marine API to spatial dashboard generation, statistical profiling, spectral decomposition, and **monthly vertical profile dashboards** for the entire water column.

---

## 🔑 Key Features

- **Automated data download** from Copernicus Marine Service (`copernicusmarine` CLI) with chunked 2-year intervals
- **Multi-panel SST dashboard** — 34 January maps (1993–2026) + climatological mean + anomaly panel with dark-themed styling
- **SST time series analysis** — interannual evolution with linear trend (°C/decade), El Niño year shading, and min/max annotations
- **Surface current speed maps** — horizontal velocity magnitude (|V| = √(u² + v²)) for all Januaries with climatological anomaly
- **Descriptive statistics** — full table with N, mean, median, std, percentiles for θ (temperature), salinity, zonal/meridional velocity, and speed
- **Vertical profile analysis** — depth-dependent distributions via histograms and vertical profile plots (0.5 m – 1942 m)
- **Monthly vertical profile dashboards** — **12 months × 3 offshore distances (50/150/300 km) × 3 zones (Norte/Centro/Sur Perú) × 3 variables (T/S/|V|)** = 324 panels showing full water column structure with year-colored overlays and climatology
- **Fixed-interval vertical profiles** — standardized X-axis ranges per variable for direct month-to-month comparison
- **Latitude cross-sections** — depth–longitude sections of current speed at 2°S, 5°S, 10°S, 14°S, 18°S with logarithmic depth scale, per-year panels, and climatological comparison
- **Point time series** — SST evolution at specific coastal locations (e.g., 12°S, 77.2°W off Lima)
- **FFT spectral analysis** — amplitude spectrum of SST at coastal point, revealing the annual cycle and sub-annual harmonics in physical units (°C)
- **Optimized computation** — 36× `.compute()` calls reduced to 1 per zone/variable using Dask lazy evaluation

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

# Or run the standalone dashboard scripts
python Codigos/dashboard_enero_glorys.py
python Codigos/dashboard_perfiles_verticales.py
```

> **Note:** NetCDF data files are not included in this repo (see `.gitignore`). Download them via the notebook's first cell or the Copernicus Marine subset API.

---

## 📁 Project Structure

```
projecto-glorys/
├── Codigos/
│   ├── analisis_climatologic_oceanografia.ipynb   ← Main analysis notebook (all cells)
│   ├── dashboard_enero_glorys.py                  ← Standalone SST dashboard script
│   ├── dashboard_perfiles_verticales.py           ← Standalone vertical profile dashboard script
│   ├── dashboard_SST_enero_glorys12v1.png         ← SST dashboard output
│   └── serie_temporal_SST_enero_glorys12v1.png    ← Time series output
├── Graficas/                                       ← Generated visualizations
│   ├── Graficas_Perfiles/                          ← Vertical profiles (original)
│   │   ├── Norte_Perú/
│   │   ├── Centro_Perú/
│   │   └── Sur_Perú/
│   ├── Grafica_perfiles_Intervalos_Fijos/          ← Fixed-interval profiles
│   │   ├── Norte_Perú/
│   │   ├── Centro_Perú/
│   │   └── Sur_Perú/
│   ├── Cortes_Profundidad_Modulo_Velocidad/        ← Latitude cross-sections
│   │   ├── corte_-2_Latitud.png   (2°S)
│   │   ├── corte_-5_Latitud.png   (5°S)
│   │   ├── corte_-10_Latitud.png  (10°S)
│   │   ├── corte_-14_Latitud.png  (14°S)
│   │   └── corte_-18_Latitud.png  (18°S)
│   └── Graficas_Serie_de_tiempo_y_FFT/
│       ├── Temperatura_Vs_tiempo_Frente_A_Lima.png
│       └── FFT_serie_de_Tiempo.png
├── Datos Glorys/                                   ← NetCDF data (not tracked)
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
| 17–18 | **Vertical profile dashboards** — 12 months × 3 distances × 3 zones (T/S/|V|) with year-colored overlays |
| 19–20 | **Fixed-interval vertical profiles** — Standardized X-axis for month-to-month comparison |
| 21 | **Profile dashboard generation** — Produces `Graficas_Perfiles/` and `Grafica_perfiles_Intervalos_Fijos/` |

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

### Monthly Vertical Profile Dashboards
324-panel grid (12 months × 3 offshore distances × 3 zones × 3 variables) showing the full vertical structure of temperature, salinity, and current speed. Each panel overlays all years (viridis colormap) with the climatological mean in black. Fixed-interval variants provide standardized X-axis ranges for direct temporal comparison.

### Time Series & FFT
Coastal SST evolution off Lima with ENSO signatures, and FFT amplitude spectrum revealing the dominant annual cycle and sub-annual harmonics.

---

## ⚙️ Dashboard Scripts

### `dashboard_enero_glorys.py` — SST & Surface Currents
Standalone production-ready script that generates:
- **SST map dashboard** — Dark-themed (navy background) with `cmocean.cm.thermal` colormapping, gold-bordered climatology panel, cyan-bordered anomaly panel, and per-panel mean annotations
- **SST time series** — Area-averaged January SST with trend line, El Niño markers, and annotated extremes

```bash
# Run (edit DATA_DIR path inside the script first)
python Codigos/dashboard_enero_glorys.py
```

Outputs: `dashboard_SST_enero_glorys12v1.png` and `serie_temporal_SST_enero_glorys12v1.png`

### `dashboard_perfiles_verticales.py` — Vertical Profiles
Standalone script generating **9 dashboards** (3 zones × 3 variables):
- **Zones**: Norte (5°S), Centro (12°S), Sur (18°S)
- **Variables**: Temperatura (°C), Salinidad (PSU), Módulo Velocidad (m/s)
- **Layout**: 12 months (rows) × 3 offshore distances — 50 km, 150 km, 300 km (columns)
- **Features**: Year-colored overlays (viridis), climatology in black, uniform colorbar, depth-inverted Y-axis

```bash
# Run (requires 'ds' dataset loaded — copy into notebook after Cell 2, or adapt as standalone)
python Codigos/dashboard_perfiles_verticales.py
```

Outputs: Populates `Graficas/Graficas_Perfiles/` and `Graficas/Grafica_perfiles_Intervalos_Fijos/`

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](./LICENSE) for details.

**Data source:** [Copernicus Marine Service](https://data.marine.copernicus.eu/) — GLORYS12V1 Reanalysis · CMEMS

---

<div align="center">

*By [Henry Paolo Alfaro Sotil](https://github.com/elbrujo325) — Physicist & Data Scientist*

</div>
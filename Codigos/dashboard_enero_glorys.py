#!/usr/bin/env python3
"""
Dashboard de Temperatura Superficial del Mar (SST) - Enero
==========================================================
GLORYS12V1 Reanalysis (1993–2026)
Región: Costa del Perú (~83°W–73°W, ~19°S–0.5°S)

Genera un dashboard multi-panel con todos los eneros disponibles,
más un panel de climatología media y anomalía del último año.

Uso:
    python dashboard_enero_glorys.py
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
from matplotlib.colors import TwoSlopeNorm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cmocean
from pathlib import Path

# ─────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────
DATA_DIR = Path("/home/paolo/Escritorio/projecto glorys/Datos Glorys")
OUTPUT_DIR = Path("/home/paolo/Escritorio/projecto glorys/Codigos")
VARIABLE = "thetao"
DEPTH_IDX = 0  # Superficie

# Estética
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.titleweight": "bold",
    "axes.labelsize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "figure.dpi": 150,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.facecolor": "#0a0e27",
})


def load_january_data():
    """Carga todos los archivos NetCDF y extrae solo los meses de enero."""
    print("📂 Cargando datos GLORYS12V1...")
    ds = xr.open_mfdataset(
        str(DATA_DIR / "*.nc"),
        combine="by_coords",
        chunks={"time": 12}
    )
    # Filtrar solo eneros en superficie
    jan_mask = ds["time.month"] == 1
    ds_jan = ds[VARIABLE].isel(depth=DEPTH_IDX).sel(time=jan_mask)
    print(f"   ✅ {len(ds_jan.time)} eneros encontrados "
          f"({int(ds_jan.time.dt.year.min())}–{int(ds_jan.time.dt.year.max())})")
    return ds_jan.load()  # Cargar a memoria


def create_map_axes(fig, subplot_spec, projection):
    """Crea un eje de mapa con estilo consistente."""
    ax = fig.add_subplot(subplot_spec, projection=projection)
    return ax


def style_map(ax, title="", show_xlabels=False, show_ylabels=False):
    """Aplica estilo consistente a un eje de mapa."""
    # Características geográficas
    ax.add_feature(cfeature.LAND, facecolor="#1a1a2e", edgecolor="#3a3a5c",
                   linewidth=0.3, zorder=5)
    ax.add_feature(cfeature.COASTLINE, edgecolor="#7f8fa6", linewidth=0.4, zorder=6)
    ax.add_feature(cfeature.BORDERS, edgecolor="#3a3a5c", linewidth=0.2,
                   linestyle=":", zorder=6)

    # Gridlines
    gl = ax.gridlines(
        draw_labels=True, linewidth=0.15, color="#ffffff",
        alpha=0.15, linestyle="--",
        x_inline=False, y_inline=False
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.bottom_labels = show_xlabels
    gl.left_labels = show_ylabels
    gl.xlocator = mticker.FixedLocator([-82, -80, -78, -76, -74])
    gl.ylocator = mticker.FixedLocator([-18, -15, -12, -9, -6, -3, -1])
    gl.xlabel_style = {"size": 5, "color": "#b0b0b0", "rotation": 0}
    gl.ylabel_style = {"size": 5, "color": "#b0b0b0"}

    # Título
    if title:
        ax.set_title(
            title, fontsize=8, fontweight="bold", color="#e0e0e0",
            pad=3,
            path_effects=[pe.withStroke(linewidth=1.5, foreground="#0a0e27")]
        )

    # Extensión
    ax.set_extent([-83.5, -73.0, -19.5, -0.3], crs=ccrs.PlateCarree())

    return ax


def add_colorbar(fig, mappable, ax_or_axes, label="", orientation="horizontal",
                 pad=0.02, shrink=0.8, aspect=35):
    """Añade una barra de color estilizada."""
    cbar = fig.colorbar(
        mappable, ax=ax_or_axes, orientation=orientation,
        pad=pad, shrink=shrink, aspect=aspect, extend="both"
    )
    cbar.set_label(label, fontsize=7, color="#c0c0c0", labelpad=4)
    cbar.ax.tick_params(labelsize=6, colors="#b0b0b0", width=0.3, length=2)
    cbar.outline.set_edgecolor("#3a3a5c")
    cbar.outline.set_linewidth(0.4)
    return cbar


def plot_dashboard(data_jan):
    """Genera el dashboard principal con todos los eneros."""
    years = sorted(data_jan.time.dt.year.values)
    n_years = len(years)

    # Layout: calcular grid
    # 34 eneros + 2 paneles extras (climatología + anomalía) = 36 paneles
    n_panels = n_years + 2
    ncols = 6
    nrows = int(np.ceil(n_panels / ncols))

    proj = ccrs.PlateCarree()

    # Rango global de temperatura para escala consistente
    vmin = float(data_jan.min())
    vmax = float(data_jan.max())
    # Redondear a valores limpios
    vmin = np.floor(vmin)
    vmax = np.ceil(vmax)

    # Climatología media
    clim = data_jan.mean(dim="time")
    # Anomalía del último año respecto a la climatología
    last_year = years[-1]
    last_jan = data_jan.sel(time=data_jan.time.dt.year == last_year).squeeze()
    anomaly = last_jan - clim

    print(f"🌡️  Rango SST Enero: {vmin:.0f}°C – {vmax:.0f}°C")
    print(f"📊 Dashboard: {nrows} filas × {ncols} columnas = {nrows*ncols} slots")
    print(f"   Paneles de datos: {n_years} eneros + 2 resumen")

    # ─────────────────────────────────────────────────
    # FIGURA PRINCIPAL
    # ─────────────────────────────────────────────────
    fig_width = ncols * 2.8
    fig_height = nrows * 3.2 + 2.5  # Extra para título y colorbar
    fig = plt.figure(figsize=(fig_width, fig_height), facecolor="#0a0e27")

    # Título principal
    fig.suptitle(
        "🌊  GLORYS12V1 — Temperatura Superficial del Mar (SST)  •  Enero  •  1993–2026",
        fontsize=16, fontweight="bold", color="#e8e8e8",
        y=0.98, x=0.5,
        fontfamily="sans-serif"
    )
    fig.text(
        0.5, 0.965,
        "Región: Costa del Perú (83°W–73°W, 19°S–0.5°S)  •  Profundidad: Superficie (0.49 m)  •  Fuente: Copernicus Marine CMEMS",
        ha="center", fontsize=8, color="#8899aa", style="italic"
    )

    # GridSpec principal
    gs = gridspec.GridSpec(
        nrows + 1, ncols,  # +1 fila para colorbar
        figure=fig,
        hspace=0.35, wspace=0.08,
        top=0.945, bottom=0.06, left=0.03, right=0.97,
        height_ratios=[1] * nrows + [0.05]
    )

    axes_maps = []
    mappable = None

    # ─── Paneles individuales por año ───
    for i, year in enumerate(years):
        row, col = divmod(i, ncols)
        ax = create_map_axes(fig, gs[row, col], proj)

        jan_data = data_jan.sel(time=data_jan.time.dt.year == year).squeeze()

        im = jan_data.plot(
            ax=ax, transform=ccrs.PlateCarree(),
            cmap=cmocean.cm.thermal,
            vmin=vmin, vmax=vmax,
            add_colorbar=False, add_labels=False,
            rasterized=True
        )

        if mappable is None:
            mappable = im

        # Mostrar etiquetas solo en bordes
        show_y = (col == 0)
        show_x = (row == nrows - 1) or (i >= n_panels - ncols)
        style_map(ax, title=str(year), show_xlabels=show_x, show_ylabels=show_y)

        # Estadísticas en el panel
        mean_val = float(jan_data.mean())
        ax.text(
            0.97, 0.03, f"{mean_val:.1f}°C",
            transform=ax.transAxes, fontsize=5.5,
            color="#ffd700", fontweight="bold",
            ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="#0a0e27",
                      edgecolor="#ffd700", alpha=0.7, linewidth=0.3),
            zorder=10
        )

        axes_maps.append(ax)

    # ─── Panel CLIMATOLOGÍA ───
    idx_clim = n_years
    row_c, col_c = divmod(idx_clim, ncols)
    ax_clim = create_map_axes(fig, gs[row_c, col_c], proj)

    im_clim = clim.plot(
        ax=ax_clim, transform=ccrs.PlateCarree(),
        cmap=cmocean.cm.thermal,
        vmin=vmin, vmax=vmax,
        add_colorbar=False, add_labels=False,
        rasterized=True
    )

    show_y_c = (col_c == 0)
    show_x_c = (row_c == nrows - 1)
    style_map(ax_clim, title="CLIMATOLOGÍA", show_xlabels=show_x_c, show_ylabels=show_y_c)

    # Borde dorado para climatología
    for spine in ax_clim.spines.values():
        spine.set_edgecolor("#ffd700")
        spine.set_linewidth(1.5)

    ax_clim.text(
        0.97, 0.03, f"μ = {float(clim.mean()):.1f}°C",
        transform=ax_clim.transAxes, fontsize=5.5,
        color="#ffd700", fontweight="bold",
        ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.15", facecolor="#0a0e27",
                  edgecolor="#ffd700", alpha=0.7, linewidth=0.3),
        zorder=10
    )
    axes_maps.append(ax_clim)

    # ─── Panel ANOMALÍA ───
    idx_anom = n_years + 1
    row_a, col_a = divmod(idx_anom, ncols)
    ax_anom = create_map_axes(fig, gs[row_a, col_a], proj)

    # Escala divergente centrada en 0
    anom_abs_max = float(np.nanmax(np.abs(anomaly.values)))
    anom_abs_max = np.ceil(anom_abs_max * 2) / 2  # Redondear a 0.5
    anom_norm = TwoSlopeNorm(vmin=-anom_abs_max, vcenter=0, vmax=anom_abs_max)

    im_anom = anomaly.plot(
        ax=ax_anom, transform=ccrs.PlateCarree(),
        cmap=cmocean.cm.balance,
        norm=anom_norm,
        add_colorbar=False, add_labels=False,
        rasterized=True
    )

    show_y_a = (col_a == 0)
    show_x_a = True
    style_map(ax_anom, title=f"ANOMALÍA {last_year}",
              show_xlabels=show_x_a, show_ylabels=show_y_a)

    # Borde cian para anomalía
    for spine in ax_anom.spines.values():
        spine.set_edgecolor("#00d2ff")
        spine.set_linewidth(1.5)

    mean_anom = float(anomaly.mean())
    sign = "+" if mean_anom > 0 else ""
    ax_anom.text(
        0.97, 0.03, f"Δ = {sign}{mean_anom:.2f}°C",
        transform=ax_anom.transAxes, fontsize=5.5,
        color="#00d2ff", fontweight="bold",
        ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.15", facecolor="#0a0e27",
                  edgecolor="#00d2ff", alpha=0.7, linewidth=0.3),
        zorder=10
    )

    # Mini-colorbar para anomalía
    cbar_anom = fig.colorbar(
        im_anom, ax=ax_anom, orientation="horizontal",
        pad=0.08, shrink=0.85, aspect=20, extend="both"
    )
    cbar_anom.set_label("Anomalía (°C)", fontsize=5, color="#c0c0c0", labelpad=2)
    cbar_anom.ax.tick_params(labelsize=4.5, colors="#b0b0b0", width=0.3, length=1.5)
    cbar_anom.outline.set_edgecolor("#3a3a5c")
    cbar_anom.outline.set_linewidth(0.3)

    axes_maps.append(ax_anom)

    # ─── Colorbar principal (fila inferior) ───
    # Crear eje para la colorbar en toda la fila inferior
    ax_cbar = fig.add_subplot(gs[nrows, :])
    ax_cbar.set_visible(False)

    cbar = fig.colorbar(
        mappable, ax=ax_cbar, orientation="horizontal",
        fraction=1.0, pad=0.0, aspect=60, extend="both",
        anchor=(0.5, 1.0), panchor=(0.5, 0.0)
    )
    cbar.set_label(
        "Temperatura Superficial del Mar — SST (°C)",
        fontsize=10, color="#e0e0e0", labelpad=8, fontweight="bold"
    )
    cbar.ax.tick_params(labelsize=8, colors="#c0c0c0", width=0.5, length=3)
    cbar.outline.set_edgecolor("#5a5a7c")
    cbar.outline.set_linewidth(0.5)

    # ─── Guardar ───
    output_path = OUTPUT_DIR / "dashboard_SST_enero_glorys12v1.png"
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
    print(f"\n💾 Dashboard guardado en:\n   {output_path}")
    plt.close(fig)

    return output_path


def plot_timeseries(data_jan):
    """Genera una gráfica de serie temporal de SST media en enero."""
    years = data_jan.time.dt.year.values
    means = [float(data_jan.sel(time=data_jan.time.dt.year == y).mean()) for y in years]

    # Tendencia lineal
    coefs = np.polyfit(years.astype(float), means, 1)
    trend_line = np.polyval(coefs, years.astype(float))
    trend_per_decade = coefs[0] * 10

    fig, ax = plt.subplots(figsize=(14, 4.5), facecolor="#0a0e27")
    ax.set_facecolor("#0d1137")

    # Área bajo la curva
    ax.fill_between(years, means, alpha=0.15, color="#ff6b6b")

    # Línea principal
    ax.plot(years, means, color="#ff6b6b", linewidth=2, marker="o",
            markersize=5, markerfacecolor="#ff6b6b", markeredgecolor="#ffffff",
            markeredgewidth=0.5, zorder=5, label="SST media enero")

    # Tendencia
    ax.plot(years, trend_line, color="#ffd700", linewidth=1.5, linestyle="--",
            alpha=0.8, label=f"Tendencia: {trend_per_decade:+.3f} °C/década", zorder=4)

    # Climatología (media)
    clim_mean = np.mean(means)
    ax.axhline(clim_mean, color="#4ecdc4", linewidth=0.8, linestyle=":",
               alpha=0.5, label=f"Media climatológica: {clim_mean:.2f} °C")

    # Sombrear años El Niño conocidos
    nino_years = [1997, 1998, 2015, 2016, 2023]
    for ny in nino_years:
        if ny in years:
            ax.axvspan(ny - 0.4, ny + 0.4, alpha=0.08, color="#ff6348", zorder=1)

    # Estilo
    ax.set_xlabel("Año", fontsize=10, color="#c0c0c0", labelpad=8)
    ax.set_ylabel("SST Media (°C)", fontsize=10, color="#c0c0c0", labelpad=8)
    ax.set_title(
        "Serie Temporal — SST Media en Enero  •  Costa del Perú  •  GLORYS12V1",
        fontsize=13, fontweight="bold", color="#e8e8e8", pad=12
    )

    ax.tick_params(axis="both", colors="#b0b0b0", which="both")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#3a3a5c")
    ax.spines["left"].set_color("#3a3a5c")

    ax.legend(
        loc="upper left", fontsize=8, facecolor="#151a3e",
        edgecolor="#3a3a5c", labelcolor="#c0c0c0",
        framealpha=0.9
    )

    ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    ax.grid(axis="y", color="#ffffff", alpha=0.05, linewidth=0.5)
    ax.grid(axis="x", color="#ffffff", alpha=0.03, linewidth=0.3)

    # Anotar min y max
    idx_max = np.argmax(means)
    idx_min = np.argmin(means)
    ax.annotate(
        f"Máx: {means[idx_max]:.2f}°C\n({years[idx_max]})",
        xy=(years[idx_max], means[idx_max]),
        xytext=(0, 15), textcoords="offset points",
        fontsize=7, color="#ff6b6b", fontweight="bold",
        ha="center", va="bottom",
        arrowprops=dict(arrowstyle="-|>", color="#ff6b6b", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#0a0e27",
                  edgecolor="#ff6b6b", alpha=0.8, linewidth=0.5)
    )
    ax.annotate(
        f"Mín: {means[idx_min]:.2f}°C\n({years[idx_min]})",
        xy=(years[idx_min], means[idx_min]),
        xytext=(0, -20), textcoords="offset points",
        fontsize=7, color="#4ecdc4", fontweight="bold",
        ha="center", va="top",
        arrowprops=dict(arrowstyle="-|>", color="#4ecdc4", lw=0.8),
        bbox=dict(boxstyle="round,pad=0.2", facecolor="#0a0e27",
                  edgecolor="#4ecdc4", alpha=0.8, linewidth=0.5)
    )

    plt.tight_layout()

    output_path = OUTPUT_DIR / "serie_temporal_SST_enero_glorys12v1.png"
    fig.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
    print(f"💾 Serie temporal guardada en:\n   {output_path}")
    plt.close(fig)

    return output_path


# ─────────────────────────────────────────────────
# EJECUCIÓN PRINCIPAL
# ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  DASHBOARD SST ENERO — GLORYS12V1 REANALYSIS")
    print("  Costa del Perú • 1993–2026")
    print("=" * 60)
    print()

    # Cargar datos
    data_jan = load_january_data()

    # Generar dashboard de mapas
    print("\n🗺️  Generando dashboard de mapas...")
    path1 = plot_dashboard(data_jan)

    # Generar serie temporal
    print("\n📈 Generando serie temporal...")
    path2 = plot_timeseries(data_jan)

    print("\n" + "=" * 60)
    print("  ✅ DASHBOARD COMPLETO")
    print("=" * 60)

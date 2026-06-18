# =========================================================================
# DASHBOARDS DE PERFILES VERTICALES OCEANOGRÁFICOS
# Norte (-5°S), Centro (-12°S), Sur (-18°S)
# 12 meses × 3 distancias de la costa (50km, 150km, 300km)
# Variables: Temperatura, Salinidad, Módulo de Velocidad
# =========================================================================
#
# INSTRUCCIONES: Copiar este código en una nueva celda del notebook
# después de la celda que carga el dataset (Cell 1 con ds = xr.open_mfdataset).
# Requiere que 'ds' ya esté cargado en memoria.
# =========================================================================

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------------

# Zonas geográficas (nombre: latitud)
zonas = {
    'Norte': -5.0,
    'Centro': -12.0,
    'Sur': -18.0,
}

# Distancias desde la costa (en km)
distancias_km = [50, 150, 300]

# Nombres de los meses
meses_nombres = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
]

# Variables a graficar (clave interna, etiqueta para ejes)
variables_config = [
    ('thetao', 'Temperatura (°C)'),
    ('so',     'Salinidad (PSU)'),
    ('speed',  'Módulo Velocidad (m/s)'),
]

# ----------------------------------------------------------
# FUNCIONES AUXILIARES
# ----------------------------------------------------------

def encontrar_lon_costa(ds, lat_objetivo):
    """
    Encuentra la longitud más al este con datos válidos (océano)
    en la superficie, para una latitud dada.
    Esto representa el punto más cercano a la costa en la malla GLORYS.
    """
    # Tomar la primera fecha disponible, profundidad superficial
    data_sup = ds['thetao'].isel(time=0, depth=0).sel(
        latitude=lat_objetivo, method='nearest'
    )
    # Evaluar si es lazy (dask)
    if hasattr(data_sup, 'compute'):
        data_sup = data_sup.compute()

    # Buscar longitudes con datos válidos (no NaN)
    vals = data_sup.values
    lons = data_sup.longitude.values
    mask_valido = ~np.isnan(vals)

    if not np.any(mask_valido):
        raise ValueError(f"No hay datos válidos en la superficie para lat={lat_objetivo}")

    # La longitud más al este con datos válidos = más cerca de la costa peruana
    lon_costa = lons[mask_valido].max()
    return float(lon_costa)


def km_a_offset_lon(km, lat_grados):
    """
    Convierte una distancia en km a un offset en grados de longitud,
    teniendo en cuenta la latitud.
    A la latitud lat: 1° de longitud ≈ 111.32 * cos(lat) km
    """
    return km / (111.32 * np.cos(np.radians(abs(lat_grados))))


def extraer_perfil_punto(ds, var_key, lat, lon, mes_num):
    """
    Extrae el perfil vertical en un punto (lat, lon) para todos
    los años de un mes dado.

    Retorna:
        perfil: array (n_años, n_profundidades)
        years: array de años
        depth_vals: array de profundidades
    """
    # Máscara de mes
    mask_mes = ds.time.dt.month == mes_num

    if var_key == 'speed':
        # Calcular módulo de velocidad en el punto (lazy)
        uo_punto = ds['uo'].sel(latitude=lat, longitude=lon, method='nearest')
        vo_punto = ds['vo'].sel(latitude=lat, longitude=lon, method='nearest')
        da_punto = np.sqrt(uo_punto**2 + vo_punto**2)
    else:
        da_punto = ds[var_key].sel(latitude=lat, longitude=lon, method='nearest')

    # Seleccionar solo el mes deseado y computar
    da_mes = da_punto.sel(time=mask_mes)
    perfil = da_mes.compute().values  # (n_tiempos_del_mes, n_profundidades)

    years = ds.time.sel(time=mask_mes).dt.year.values
    depth_vals = ds['depth'].values

    return perfil, years, depth_vals


# ----------------------------------------------------------
# CALCULAR COORDENADAS DE LOS PUNTOS
# ----------------------------------------------------------

print("=" * 70)
print("CÁLCULO DE PUNTOS DE MUESTREO")
print("=" * 70)

puntos_info = {}

for zona_nombre, lat_obj in zonas.items():
    # Latitud real en la malla
    lat_real = float(ds.latitude.sel(latitude=lat_obj, method='nearest').values)

    # Longitud de la costa
    lon_costa = encontrar_lon_costa(ds, lat_obj)

    # Calcular longitudes offshore
    lons_offshore = []
    for km in distancias_km:
        offset = km_a_offset_lon(km, lat_real)
        lon_off = lon_costa - offset  # hacia el oeste
        lon_off_real = float(ds.longitude.sel(longitude=lon_off, method='nearest').values)
        lons_offshore.append(lon_off_real)

    puntos_info[zona_nombre] = {
        'lat': lat_real,
        'lon_costa': lon_costa,
        'lons_offshore': lons_offshore,
    }

    print(f"\n  Zona: {zona_nombre}")
    print(f"    Latitud: {lat_real:.2f}°")
    print(f"    Costa (lon): {lon_costa:.2f}°")
    for km, lon_off in zip(distancias_km, lons_offshore):
        print(f"    {km:>3d} km offshore → lon = {lon_off:.2f}°")


# ----------------------------------------------------------
# RANGO GLOBAL DE AÑOS (para colormap uniforme)
# ----------------------------------------------------------
years_global = np.unique(ds.time.dt.year.values)
cmap_yr = plt.cm.viridis
norm_yr = plt.Normalize(years_global.min(), years_global.max())

# ----------------------------------------------------------
# GENERAR LOS 9 DASHBOARDS
# ----------------------------------------------------------

print("\n" + "=" * 70)
print("GENERANDO DASHBOARDS...")
print("=" * 70)

for zona_nombre, info in puntos_info.items():
    lat = info['lat']
    lon_costa = info['lon_costa']
    lons_offshore = info['lons_offshore']

    for var_key, var_label in variables_config:

        print(f"\n  → {zona_nombre} — {var_label} ...")

        # Crear figura: 12 filas (meses) × 3 columnas (distancias)
        fig, axes = plt.subplots(
            12, 3,
            figsize=(20, 56),
            facecolor='white',
            constrained_layout=False
        )

        fig.suptitle(
            f'Perfil Vertical por Mes — Zona {zona_nombre} ({lat:.1f}°S)\n'
            f'{var_label} — Costa en {lon_costa:.2f}°',
            fontsize=16, fontweight='bold', y=0.995
        )

        for mes_idx in range(12):
            mes_num = mes_idx + 1

            for col_idx in range(3):
                ax = axes[mes_idx, col_idx]
                km = distancias_km[col_idx]
                lon_off = lons_offshore[col_idx]

                # Extraer perfil
                perfil, years_mes, depth_vals = extraer_perfil_punto(
                    ds, var_key, lat, lon_off, mes_num
                )

                # Graficar cada año con color del colormap
                for i in range(len(years_mes)):
                    color_yr = cmap_yr(norm_yr(years_mes[i]))
                    ax.plot(
                        perfil[i], -depth_vals,
                        color=color_yr, alpha=0.6, linewidth=0.9
                    )

                # Climatología (media de todos los años) en negro
                clim = np.nanmean(perfil, axis=0)
                ax.plot(
                    clim, -depth_vals,
                    color='black', linewidth=2.0, label='Climatología'
                )

                # --- Estilo idéntico al gráfico original ---
                ax.set_xlabel(var_label, fontsize=8)
                ax.set_ylabel('Profundidad (m)', fontsize=8)
                ax.legend(fontsize=6, loc='lower left')
                ax.grid(True, linestyle='--', alpha=0.4)
                ax.spines[['top', 'right']].set_visible(False)
                ax.tick_params(labelsize=7)

                # Título de columna (solo fila superior)
                if mes_idx == 0:
                    ax.set_title(
                        f'{km} km de la costa\n(lon={lon_off:.2f}°)',
                        fontsize=10, fontweight='bold'
                    )

                # Etiqueta del mes (solo columna izquierda)
                if col_idx == 0:
                    ax.annotate(
                        meses_nombres[mes_idx],
                        xy=(-0.3, 0.5),
                        xycoords='axes fraction',
                        fontsize=10, fontweight='bold',
                        ha='center', va='center',
                        rotation=90
                    )

        # --- Colorbar horizontal al fondo ---
        sm = plt.cm.ScalarMappable(cmap=cmap_yr, norm=norm_yr)
        sm.set_array([])
        cbar = fig.colorbar(
            sm,
            ax=axes.ravel().tolist(),
            orientation='horizontal',
            fraction=0.015,
            pad=0.02,
            aspect=60
        )
        cbar.set_label('Año', fontsize=10)

        plt.subplots_adjust(
            left=0.08, right=0.97,
            top=0.97, bottom=0.04,
            hspace=0.35, wspace=0.30
        )
        plt.show()

        print(f"    ✓ Dashboard generado: {zona_nombre} — {var_label}")

print("\n" + "=" * 70)
print("¡TODOS LOS DASHBOARDS GENERADOS!")
print("=" * 70)

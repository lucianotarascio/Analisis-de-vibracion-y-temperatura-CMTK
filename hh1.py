"""
07-09-2026 - Dispersor HH1
Transformación de datos de vibración y temperatura para obtención de métricas estadísticas.

"""

import pandas as pd
import numpy as np
import json

# 1. Cargar los datos
# Define el nombre del archivo en una variable
file_name = 'master2_julio.csv'
df = pd.read_csv(file_name)

# Mapeo de la arquitectura estructural de la máquina HH1
activos_maquina = {
    'port0': 'Motor izquierdo (superior)',
    'port1': 'Torreta derecha',
    'port2': 'Motor izquierdo (inferior)',
    'port3': 'Motor derecho (superior)',
    'port4': 'Torreta izquierda',
    'port5': 'Motor derecho (inferior)',
    'port6': 'Torreta central'
}

resultados_nodos = {}
ranking_criticos = []

# Iteración sobre cada puerto definido para extraer métricas locales
for puerto, descripcion in activos_maquina.items():
    # Mapeo exacto de los encabezados según el string del archivo CSV
    col_temp = f'{puerto} Contact Temperature Contact Temperature [°C]'
    col_x = f'{puerto} Vibration Velocity RMS v-RMS X [mm/s]'
    col_y = f'{puerto} Vibration Velocity RMS v-RMS Y [mm/s]'
    col_z = f'{puerto} Vibration Velocity RMS v-RMS Z [mm/s]'

    # === Métricas de Temperatura ===
    temp_prom = df[col_temp].mean()
    temp_max = df[col_temp].max()
    temp_min = df[col_temp].min()

    # === Vibración RMS Global ===
    # Se calcula la magnitud del vector espacial 3D
    rms_global_array = np.sqrt(df[col_x]**2 + df[col_y]**2 + df[col_z]**2)
    vib_prom = rms_global_array.mean()
    vib_max = rms_global_array.max()

    # === Tendencias (Deltas Temporales) ===
    # Diferencia entre el promedio del último 10% de los datos vs el primer 10%
    largo = len(df)
    ventana = max(1, int(largo * 0.1))
    tendencia_temp = df[col_temp].iloc[-ventana:].mean() - df[col_temp].iloc[:ventana].mean()
    tendencia_vib = rms_global_array.iloc[-ventana:].mean() - rms_global_array.iloc[:ventana].mean()

    # === Correlación Temperatura-Vibración ===
    # Coeficiente de correlación de Pearson (-1 a 1)
    correlacion = df[col_temp].corr(rms_global_array)

    # === Eventos Anómalos ===
    # Detección de picos fuera de 3 desviaciones estándar (Regla empírica 99.7%)
    limite_temp = temp_prom + (3 * df[col_temp].std())
    limite_vib = vib_prom + (3 * rms_global_array.std())
    anomalias = int((df[col_temp] > limite_temp).sum() + (rms_global_array > limite_vib).sum())

    # Almacenamiento de datos del nodo
    resultados_nodos[descripcion] = {
        "Temperatura (C)": {
            "Promedio": round(temp_prom, 2),
            "Max": round(temp_max, 2),
            "Min": round(temp_min, 2),
            "Tendencia": round(tendencia_temp, 2)
        },
        "Vibracion RMS (mm/s)": {
            "Promedio": round(vib_prom, 2),
            "Max": round(vib_max, 2),
            "Tendencia": round(tendencia_vib, 2)
        },
        "Correlacion": round(correlacion, 3),
        "Alertas_Anomalas": anomalias
    }

    # Se usa la vibración máxima como peso para el ranking de criticidad
    ranking_criticos.append({"Activo": descripcion, "Vib_Max": vib_max})

# === Resumen General de la Máquina ===
# Ordenamiento descendente para obtener los activos que sufrieron más estrés
ranking_criticos.sort(key=lambda x: x["Vib_Max"], reverse=True)
lista_ranking = [item["Activo"] for item in ranking_criticos]

estado_salud_HH1 = {
    "Maquina": "Dispersora HH1",
    "Ranking_Criticidad_Desgaste": lista_ranking,
    "Nodos_Sensores": resultados_nodos
}

# Impresión del output formateado para ser consumido por un LLM
print(json.dumps(estado_salud_HH1, indent=4, ensure_ascii=False))

"""Analiza el siguiente reporte de estado de salud de la máquina Dispersora HH1 y proporciona las siguientes conclusiones:

1. Identifica los 3 componentes con mayor criticidad de desgaste basándote en el 'Ranking_Criticidad_Desgaste' y explica brevemente por qué son críticos.
2. Para cada uno de esos 3 componentes críticos, resume sus métricas clave (Temperatura, Vibración RMS, Correlación y Alertas Anómalas).
3. Proporciona una recomendación de alto nivel para la máquina en general, basándote en los datos proporcionados.

Aquí está el reporte en formato JSON:

```json

[OUTPUT]

```


"""

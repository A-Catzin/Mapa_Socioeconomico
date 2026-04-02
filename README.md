# Observatorio de Indicadores de Pobreza · México
**Tecnológico Universitario Playacar · 2026**

## ¿Qué incluye esta app?

- **Mapa Multi-capa Interactivo** con 4 capas activables:
  - Pobreza Multidimensional (CONEVAL)
  - Salarios Mínimos Regionales (CONASAMI) — Zona Frontera Norte vs. Resto
  - Densidad Escolar por municipio (Censo 2020)
  - Zonas Industriales (DENUE 2024)

- **Dashboard Lateral** con filtros por:
  - Estado
  - Decil de ingreso (1–10)
  - Clasificación AMAI 2024

- **Algoritmo de Correlación Espacial de Pearson** entre densidad industrial y rezago educativo, con fórmula matemática visible en la interfaz.

- **Visualizaciones adicionales:**
  - Distribución AMAI 2024
  - Histograma por decil de ingreso
  - Comparativo salarios Frontera Norte vs. Resto

## Cómo correr la app

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar
```bash
streamlit run app.py
```

La app se abrirá en: http://localhost:8501

## Cómo conectar datos reales

Cuando tengan los CSVs del INEGI, reemplazar `municipios.csv` con datos reales. El archivo debe tener estas columnas:

| Columna | Descripción |
|---|---|
| municipio | Nombre del municipio |
| estado | Nombre del estado |
| lat / lon | Coordenadas (limpias del DENUE/Censo) |
| densidad_industrial | Unidades económicas / km² (DENUE 2024) |
| rezago_educativo | % rezago (CONEVAL) |
| pobreza_multidim | % pobreza multidimensional (CONEVAL) |
| densidad_escolar | Escuelas / 10,000 hab (Censo 2020) |
| salario_minimo | Salario efectivo en pesos/día (CONASAMI) |
| decil_ingreso | Decil 1–10 (ENIGH 2022/2024) |
| amai_2024 | A/B, C+, C, D+, D, E (Regla AMAI 2024) |
| poblacion | Población total (Censo 2020) |
| zona_frontera | True/False (Zona Libre Frontera Norte) |

## Equipo
- **Líder:** Ever López Panti (7335)
- Christopher Joan Traconis Puc (7310)
- Giovanni David Butanda Chávez (7066)
- Carlos Alberto Toscano Zepeta (7124)
- Cristian Alejandro Hoil Reyes (7243)
- Ángel Ricardo Teh Catzín (7433)
- Alejandro Ramírez Pérez (7507)
- Jesús Juárez Martínez (7190)

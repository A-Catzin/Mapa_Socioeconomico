import pandas as pd
import numpy as np

np.random.seed(42)

ESTADOS = {
    "Jalisco": {"lat": 20.6, "lon": -103.3, "n": 12},
    "Nuevo León": {"lat": 25.7, "lon": -100.3, "n": 10},
    "CDMX": {"lat": 19.43, "lon": -99.13, "n": 8},
    "Oaxaca": {"lat": 17.06, "lon": -96.7, "n": 15},
    "Chiapas": {"lat": 16.75, "lon": -93.1, "n": 14},
    "Sonora": {"lat": 29.0, "lon": -110.9, "n": 10},
    "Veracruz": {"lat": 19.17, "lon": -96.13, "n": 13},
    "Guanajuato": {"lat": 21.02, "lon": -101.26, "n": 11},
    "Puebla": {"lat": 19.04, "lon": -98.2, "n": 12},
    "Yucatán": {"lat": 20.97, "lon": -89.62, "n": 9},
    "Tamaulipas": {"lat": 24.0, "lon": -98.8, "n": 9},
    "Baja California": {"lat": 30.8, "lon": -115.5, "n": 6},
    "Coahuila": {"lat": 27.0, "lon": -101.7, "n": 8},
    "Sinaloa": {"lat": 25.0, "lon": -107.4, "n": 9},
    "Michoacán": {"lat": 19.7, "lon": -101.2, "n": 11},
}

MUNICIPIOS_NOMBRES = [
    "Centro", "Norte", "Sur", "Oriente", "Poniente",
    "San José", "Santa Cruz", "Villa", "Pueblo Nuevo", "Tlaltizapán",
    "Tepito", "Xochitepec", "Cuautla", "Tlacolula", "Zacatelco",
    "Metepec", "Tolcayuca", "Ixmiquilpan", "Huejutla", "Teziutlán"
]

def generate_data():
    rows = []
    mun_id = 1
    
    for estado, cfg in ESTADOS.items():
        n = cfg["n"]
        
        # Zona Norte tiene salario diferenciado
        es_frontera = estado in ["Baja California", "Sonora", "Tamaulipas", "Coahuila", "Nuevo León"]
        
        for i in range(n):
            lat = cfg["lat"] + np.random.uniform(-1.5, 1.5)
            lon = cfg["lon"] + np.random.uniform(-1.5, 1.5)
            
            nombre = np.random.choice(MUNICIPIOS_NOMBRES)
            
            # Densidad industrial (unidades económicas por km²)
            densidad_industrial = np.random.beta(2, 5) * 80
            if estado in ["CDMX", "Nuevo León", "Jalisco", "Guanajuato"]:
                densidad_industrial *= 2.5
            
            # Rezago educativo correlacionado negativamente con industria
            rezago_educativo = max(0, min(100,
                70 - densidad_industrial * 0.6 + np.random.normal(0, 12)
            ))
            if estado in ["Oaxaca", "Chiapas", "Veracruz", "Guerrero"]:
                rezago_educativo = min(100, rezago_educativo + 20)
            
            # Pobreza multidimensional correlacionada con rezago
            pobreza = max(0, min(100,
                rezago_educativo * 0.55 + np.random.normal(10, 10)
            ))
            
            # Densidad escolar (escuelas por 10k hab)
            densidad_escolar = max(1, np.random.normal(8, 3) - pobreza * 0.04)
            
            # Salario mínimo
            salario = 278.80 if es_frontera else 212.55
            salario_efectivo = salario * np.random.uniform(0.85, 1.3)
            
            # Decil de ingreso (1=más pobre, 10=más rico)
            decil = max(1, min(10, int(10 - pobreza / 12 + np.random.normal(0, 1))))
            
            # Clasificación AMAI 2024 (A/B, C+, C, D+, D, E)
            if decil >= 9:
                amai = "A/B"
            elif decil >= 7:
                amai = "C+"
            elif decil >= 5:
                amai = "C"
            elif decil >= 3:
                amai = "D+"
            elif decil >= 2:
                amai = "D"
            else:
                amai = "E"
            
            # Población
            poblacion = int(np.random.lognormal(10.5, 1.2))
            
            rows.append({
                "mun_id": mun_id,
                "municipio": f"{nombre} ({estado[:3]}.)",
                "estado": estado,
                "lat": lat,
                "lon": lon,
                "densidad_industrial": round(densidad_industrial, 2),
                "rezago_educativo": round(rezago_educativo, 2),
                "pobreza_multidim": round(pobreza, 2),
                "densidad_escolar": round(densidad_escolar, 2),
                "salario_minimo": round(salario_efectivo, 2),
                "decil_ingreso": decil,
                "amai_2024": amai,
                "poblacion": poblacion,
                "zona_frontera": es_frontera,
            })
            mun_id += 1
    
    df = pd.DataFrame(rows)
    df.to_csv("/home/claude/observatorio/municipios.csv", index=False)
    return df

if __name__ == "__main__":
    df = generate_data()
    print(f"Generados {len(df)} municipios")
    print(df.head())

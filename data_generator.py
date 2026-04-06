import pandas as pd
import numpy as np
import os

np.random.seed(42)

# ─── Municipios reales con coordenadas verificadas ────────────────────────────
# Cada estado tiene una lista de (nombre_municipio, lat, lon)
ESTADOS = {
    "Jalisco": {
        "frontera": False,
        "municipios": [
            ("Guadalajara", 20.6597, -103.3496),
            ("Zapopan", 20.7214, -103.3882),
            ("Tlaquepaque", 20.6411, -103.3134),
            ("Tonalá", 20.6248, -103.2346),
            ("Puerto Vallarta", 20.6534, -105.2253),
            ("Lagos de Moreno", 21.3546, -101.9316),
            ("Tepatitlán de Morelos", 20.8156, -102.7633),
            ("Chapala", 20.2928, -103.1908),
            ("Ocotlán", 20.3484, -102.7731),
            ("Ciudad Guzmán", 19.7034, -103.4618),
            ("Tequila", 20.8829, -103.8362),
            ("Autlán de Navarro", 19.7709, -104.3652),
        ],
    },
    "Nuevo León": {
        "frontera": True,
        "municipios": [
            ("Monterrey", 25.6866, -100.3161),
            ("San Pedro Garza García", 25.6600, -100.4020),
            ("San Nicolás de los Garza", 25.7431, -100.2887),
            ("Apodaca", 25.7817, -100.1882),
            ("Guadalupe", 25.6935, -100.2598),
            ("Santa Catarina", 25.6734, -100.4581),
            ("General Escobedo", 25.7893, -100.3241),
            ("Cadereyta Jiménez", 25.5864, -99.9818),
            ("Linares", 24.8601, -99.5667),
            ("Montemorelos", 25.1866, -99.8269),
        ],
    },
    "CDMX": {
        "frontera": False,
        "municipios": [
            ("Coyoacán", 19.3463, -99.1580),
            ("Gustavo A. Madero", 19.4827, -99.1133),
            ("Iztapalapa", 19.3588, -99.0518),
            ("Tlalpan", 19.2847, -99.1683),
            ("Álvaro Obregón", 19.3569, -99.2247),
            ("Cuauhtémoc", 19.4326, -99.1332),
            ("Miguel Hidalgo", 19.4134, -99.1914),
            ("Xochimilco", 19.2628, -99.1069),
        ],
    },
    "Oaxaca": {
        "frontera": False,
        "municipios": [
            ("Oaxaca de Juárez", 17.0732, -96.7266),
            ("Juchitán de Zaragoza", 16.4356, -95.0198),
            ("Salina Cruz", 16.1830, -95.1975),
            ("San Juan Bautista Tuxtepec", 18.0962, -96.1222),
            ("Huajuapan de León", 17.8050, -97.7745),
            ("Pinotepa Nacional", 16.3455, -98.0536),
            ("Tlaxiaco", 17.2747, -97.6792),
            ("Matías Romero", 16.8790, -95.0359),
            ("Puerto Escondido", 15.8618, -97.0726),
            ("Miahuatlán de Porfirio Díaz", 16.3270, -96.5939),
            ("Ocotlán de Morelos", 16.7926, -96.6720),
            ("Tehuantepec", 16.3245, -95.2386),
            ("Pochutla", 15.7413, -96.4671),
            ("Nochixtlán", 17.4613, -97.2257),
            ("Ixtlán de Juárez", 17.3293, -96.4893),
        ],
    },
    "Chiapas": {
        "frontera": False,
        "municipios": [
            ("Tuxtla Gutiérrez", 16.7528, -93.1152),
            ("San Cristóbal de las Casas", 16.7370, -92.6376),
            ("Tapachula", 14.9065, -92.2563),
            ("Comitán de Domínguez", 16.2490, -92.1338),
            ("Palenque", 17.5091, -91.9826),
            ("Chiapa de Corzo", 16.7081, -93.0138),
            ("Tonalá", 16.0892, -93.7527),
            ("Ocosingo", 16.9067, -92.0964),
            ("Villaflores", 16.2348, -93.2687),
            ("Pichucalco", 17.5088, -93.1168),
            ("Cintalapa", 16.6912, -93.7159),
            ("Las Margaritas", 16.3119, -91.9816),
            ("Motozintla", 15.3614, -92.2505),
            ("Arriaga", 16.2364, -93.8958),
        ],
    },
    "Sonora": {
        "frontera": True,
        "municipios": [
            ("Hermosillo", 29.0729, -110.9559),
            ("Ciudad Obregón", 27.4863, -109.9408),
            ("Nogales", 31.3122, -110.9460),
            ("Guaymas", 27.9218, -110.8981),
            ("Navojoa", 27.0877, -109.4422),
            ("San Luis Río Colorado", 32.4561, -114.7717),
            ("Caborca", 30.7164, -112.1586),
            ("Puerto Peñasco", 31.3165, -113.5352),
            ("Agua Prieta", 31.3268, -109.5493),
            ("Empalme", 27.9596, -110.8113),
        ],
    },
    "Veracruz": {
        "frontera": False,
        "municipios": [
            ("Veracruz", 19.1738, -96.1342),
            ("Xalapa", 19.5438, -96.9102),
            ("Coatzacoalcos", 18.1342, -94.4591),
            ("Poza Rica", 20.5331, -97.4596),
            ("Córdoba", 18.8846, -96.9342),
            ("Orizaba", 18.8496, -97.1003),
            ("Minatitlán", 17.9930, -94.5553),
            ("Tuxpan", 20.9572, -97.4014),
            ("Papantla", 20.4502, -97.3200),
            ("Martínez de la Torre", 20.0688, -97.0559),
            ("San Andrés Tuxtla", 18.4496, -95.2133),
            ("Tierra Blanca", 18.4514, -96.3469),
            ("Tantoyuca", 21.3503, -98.2317),
        ],
    },
    "Guanajuato": {
        "frontera": False,
        "municipios": [
            ("León", 21.1221, -101.6821),
            ("Irapuato", 20.6766, -101.3555),
            ("Celaya", 20.5234, -100.8157),
            ("Salamanca", 20.5737, -101.1952),
            ("Guanajuato", 21.0190, -101.2574),
            ("San Miguel de Allende", 20.9144, -100.7452),
            ("Silao", 20.9477, -101.4282),
            ("Dolores Hidalgo", 21.1567, -100.9317),
            ("San Francisco del Rincón", 21.0156, -101.8613),
            ("Pénjamo", 20.4312, -101.7225),
            ("Acámbaro", 20.0291, -100.7242),
        ],
    },
    "Puebla": {
        "frontera": False,
        "municipios": [
            ("Puebla", 19.0414, -98.2063),
            ("Tehuacán", 18.4617, -97.3928),
            ("San Martín Texmelucan", 19.2842, -98.4386),
            ("Atlixco", 18.9070, -98.4385),
            ("Cholula", 19.0634, -98.3062),
            ("Huauchinango", 20.1766, -98.0524),
            ("Teziutlán", 19.8188, -97.3573),
            ("Izúcar de Matamoros", 18.6003, -98.4666),
            ("Zacatlán", 19.9319, -97.9594),
            ("Acatlán de Osorio", 18.2053, -98.0500),
            ("Ajalpan", 18.3612, -97.1365),
            ("San Pedro Cholula", 19.0576, -98.3077),
        ],
    },
    "Yucatán": {
        "frontera": False,
        "municipios": [
            ("Mérida", 20.9674, -89.5926),
            ("Valladolid", 20.6893, -88.2015),
            ("Tizimín", 21.1427, -88.1529),
            ("Progreso", 21.2822, -89.6638),
            ("Ticul", 20.3935, -89.5320),
            ("Umán", 20.8847, -89.7575),
            ("Tekax", 20.2034, -89.2855),
            ("Motul", 21.0966, -89.2839),
            ("Izamal", 20.9328, -89.0193),
        ],
    },
    "Tamaulipas": {
        "frontera": True,
        "municipios": [
            ("Reynosa", 26.0922, -98.2778),
            ("Matamoros", 25.8790, -97.5044),
            ("Nuevo Laredo", 27.4768, -99.5165),
            ("Tampico", 22.2170, -97.8508),
            ("Ciudad Victoria", 23.7369, -99.1411),
            ("Ciudad Madero", 22.2755, -97.8365),
            ("Altamira", 22.3930, -97.9350),
            ("Río Bravo", 25.9864, -98.0889),
            ("El Mante", 22.7424, -98.9738),
        ],
    },
    "Baja California": {
        "frontera": True,
        "municipios": [
            ("Tijuana", 32.5149, -117.0382),
            ("Mexicali", 32.6245, -115.4523),
            ("Ensenada", 31.8667, -116.5964),
            ("Tecate", 32.5725, -116.6264),
            ("Rosarito", 32.3663, -117.0581),
            ("San Quintín", 30.5554, -115.9363),
        ],
    },
    "Coahuila": {
        "frontera": True,
        "municipios": [
            ("Saltillo", 25.4233, -100.9923),
            ("Torreón", 25.5428, -103.4068),
            ("Monclova", 26.9067, -101.4214),
            ("Piedras Negras", 28.7000, -100.5233),
            ("Sabinas", 27.8486, -101.1194),
            ("Acuña", 29.3231, -100.9304),
            ("Ramos Arizpe", 25.5433, -100.9481),
            ("Frontera", 26.9300, -101.4500),
        ],
    },
    "Sinaloa": {
        "frontera": False,
        "municipios": [
            ("Culiacán", 24.7994, -107.3940),
            ("Mazatlán", 23.2494, -106.4111),
            ("Los Mochis", 25.7907, -108.9860),
            ("Guasave", 25.5723, -108.4697),
            ("Guamúchil", 25.4614, -108.0781),
            ("Navolato", 24.7651, -107.7019),
            ("Escuinapa", 22.8526, -105.7830),
            ("El Rosario", 22.9932, -105.8571),
            ("Cosalá", 24.4126, -106.6883),
        ],
    },
    "Michoacán": {
        "frontera": False,
        "municipios": [
            ("Morelia", 19.7060, -101.1950),
            ("Uruapan", 19.4183, -102.0634),
            ("Zamora", 19.9809, -102.2837),
            ("Lázaro Cárdenas", 17.9577, -102.2005),
            ("Apatzingán", 19.0887, -102.3510),
            ("Zitácuaro", 19.4363, -100.3554),
            ("Pátzcuaro", 19.5139, -101.6092),
            ("La Piedad", 20.3440, -102.0325),
            ("Sahuayo", 20.0595, -102.7548),
            ("Hidalgo", 19.6938, -100.5568),
            ("Maravatío", 19.8908, -100.4448),
        ],
    },
}


def generate_data():
    rows = []
    mun_id = 1

    for estado, cfg in ESTADOS.items():
        municipios = cfg["municipios"]
        es_frontera = cfg["frontera"]

        for nombre, lat, lon in municipios:
            # Pequeño jitter para que no estén exactamente en el centro
            lat += np.random.uniform(-0.03, 0.03)
            lon += np.random.uniform(-0.03, 0.03)

            # Densidad industrial (unidades económicas por km²)
            densidad_industrial = np.random.beta(2, 5) * 80
            if estado in ["CDMX", "Nuevo León", "Jalisco", "Guanajuato"]:
                densidad_industrial *= 2.5

            # Rezago educativo correlacionado negativamente con industria
            rezago_educativo = max(0, min(100,
                70 - densidad_industrial * 0.6 + np.random.normal(0, 12)
            ))
            if estado in ["Oaxaca", "Chiapas", "Veracruz"]:
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
                "municipio": nombre,
                "estado": estado,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
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
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "municipios.csv")
    df.to_csv(csv_path, index=False)
    return df


if __name__ == "__main__":
    df = generate_data()
    print(f"Generados {len(df)} municipios")
    print(df.head())

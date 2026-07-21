import requests
import builtins
from bs4 import BeautifulSoup
import sqlite3
import time
import random
from datetime import datetime
from fake_useragent import UserAgent

# Diccionario de rubros de Mexx
CATEGORIAS = {
    "motherboards": "Motherboards",
    "procesadores": "Procesadores",
    "memorias-ram": "Memorias Ram",
    "almacenamiento": "Almacenamiento",
    "placas-de-video": "Placas de Video",
    "fuentes-de-poder": "Fuentes de Poder",
    "gabinetes": "Gabinetes",
    "refrigeracion-pc": "Refrigeración PC",
    "combos-actualizacion-pc": "Combos Actualización",
    "teclados,-mouses-y-pads": "Teclados y Mouses",
    "auriculares-y-microfonos-": "Audio y Microfonos",
    "parlantes-y-audio": "Audio y Microfonos",
    "monitores": "Monitores"
}


def actualizar_precios_lista():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contador = 0
    ua = UserAgent()
    session = requests.Session()

    conexion = sqlite3.connect("mexxlista.db")
    cursor = conexion.cursor()

    cursor.execute("DROP TABLE IF EXISTS precios_lista")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS precios_lista (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            precio REAL,
            marca TEXT,
            fecha TEXT,
            categoria TEXT
        )
    """)
    conexion.commit()

    # Bucle principal por categoría
    for rubro, nombre_cat in CATEGORIAS.items():
        print(f"\n=== Iniciando la extracción de la categoría: {nombre_cat} ===")
        num_pagina = 1

        while True:
            url_completa = f"https://www.mexx.com.ar/productos-rubro/{rubro}/?pagina={num_pagina}"
            print(f"Extrayendo información de {url_completa}...")

            # User Agents dinámicos para que no nos bloqueen el acceso
            headers = {
                "User-Agent": ua.random,
                "Accept-Language": "es-ES,es;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }

            try:
                respuesta = session.get(url_completa, headers=headers, timeout=10)

                if respuesta.status_code == 200:
                    # lmxl es mas rápido que html.parser. En vez de una hora, tardo 5 o 6 min como mucho.
                    soup = BeautifulSoup(respuesta.text, "lxml")
                    productos_lista = soup.select("div[class*='card-ecommerce']")

                    if not productos_lista:
                        print(f"No se encontraron más productos en {nombre_cat}. Pasando a la siguiente categoría.")
                        break

                    for prod in productos_lista:
                        tag_name = prod.find("h4") or prod.find(class_=lambda x: x and 'title' in x)
                        tag_price = prod.find("h3") or prod.find(class_=lambda x: x and 'price' in x)

                        if tag_name and tag_price:
                            # Asignación por defecto
                            marca_detectada = "Genérica"

                            nombre = tag_name.text.strip()
                            precio_real = tag_price.text.replace("$", "").replace(".", "").replace(",", ".").strip()

                            try:
                                precio = builtins.float(precio_real)
                            except ValueError:
                                precio = 0.0

                            # --- EXTRACTOR DE MARCA 2.0 ---
                            nombre_lower = nombre.lower()
                            marca_detectada = None

                            # Fabricantes
                            fabricantes_map = {
                                "asus": "Asus",
                                "gigabyte": "Gigabyte",
                                "aorus": "Gigabyte",
                                "msi": "MSI",
                                "asrock": "Asrock",
                                "redragon": "Redragon",
                                "logitech": "Logitech",
                                "razer": "Razer",
                                "corsair": "Corsair",
                                "hyperx": "HyperX",
                                "kingston": "Kingston",
                                "patriot": "Patriot",
                                "crucial": "Crucial",
                                "adata": "Adata / XPG",
                                "xpg": "Adata / XPG",
                                "vsg": "VSG",
                                "viewsonic": "ViewSonic",
                                "samsung": "Samsung",
                                "lg": "LG"
                            }

                            for clave, nombre_oficial in fabricantes_map.items():
                                if clave in nombre_lower:
                                    marca_detectada = nombre_oficial
                                    break

                            # Procesadores y Placas de video (Chipsets)
                            if not marca_detectada:
                                if "intel" in nombre_lower:
                                    marca_detectada = "Intel"
                                elif "amd" in nombre_lower:
                                    marca_detectada = "AMD"
                                elif "nvidia" in nombre_lower:
                                    marca_detectada = "Nvidia"
                                else:
                                    marca_detectada = "Genérica"

                            marca = marca_detectada
                            # Todo este proceso para que no mezcle las marcas de Mothers y Procesadores principalmente 

                            cursor.execute(
                                "INSERT INTO precios_lista (nombre, precio, marca, fecha, categoria) VALUES (?, ?, ?, ?, ?)",
                                (nombre, precio, marca, fecha_hoy, nombre_cat)
                            )
                            contador += 1
                            print(f"Guardado {nombre[:40]}... | ${precio} [{nombre_cat}]")

                    conexion.commit()

                    # Pausa optimizada, utilizando sólo una vez, en vez de las dos veces de antes
                    tiempo_espera = random.uniform(2.5, 4.0)
                    time.sleep(tiempo_espera)

                elif respuesta.status_code == 403:
                    print("El servidor rechazó la conexión (403 Forbidden).")
                    conexion.close()
                    return False
                elif respuesta.status_code == 404:
                    print("Servidor no encontrado (404).")
                    break
                else:
                    print(f"Error de conexión con el servidor. Código de estado: {respuesta.status_code}")
                    conexion.close()
                    return False

            except Exception as e:
                print(f"Error en el Backend: {e}")
                conexion.close()
                return False

            num_pagina += 1

    conexion.close()
    print(f"\n¡Se actualizaron {contador} productos de Mexx en la base de datos!")
    return True


if __name__ == '__main__':
    print("Iniciando el script manualmente...")
    actualizar_precios_lista()
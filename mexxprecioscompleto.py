import requests, builtins
from bs4 import BeautifulSoup
import sqlite3
import time
import random
from datetime import datetime

# Diccionario con los rubros a trackear y sus nombres limpios para la base de datos
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
    "auriculares-y-microfonos": "Audio y Microfonos",
    "monitores": "Monitores"
}

def actualizar_precios_lista():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contador = 0
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
    
    cursor.execute("DELETE FROM precios_lista")
    conexion.commit()
    
    # Bucle principal que va a recorrer cada rubro del diccionario
    for rubro, nombre_cat in CATEGORIAS.items():
        print(f"\n=== Iniciando la extracción de la categoría: {nombre_cat} ===")
        num_pagina = 1
        
        while True:
            url_completa = f"https://www.mexx.com.ar/productos-rubro/{rubro}/?pagina={num_pagina}"
            print(f"Extrayendo información de {url_completa}...")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            try:
                respuesta = requests.get(url_completa, headers=headers)
                tiempo_espera = random.uniform(3.0, 5.0)
                print(f"Intentando extraer informacion de Mexx...")
                time.sleep(tiempo_espera)
                
                if respuesta.status_code == 200:
                    soup = BeautifulSoup(respuesta.text, "html.parser")
                    productos_lista = soup.select("div[class*='card-ecommerce']")
                    
                    if not productos_lista:
                        print(f"No se encontraron más productos en {nombre_cat}. Pasando a la siguiente categoría.")
                        break
                        
                    for prod in productos_lista:
                        tag_name = prod.find("h4") or prod.find(class_=lambda x: x and 'title' in x)
                        tag_price = prod.find("h3") or prod.find(class_=lambda x: x and 'price' in x)
                        
                        if tag_name and tag_price:
                            nombre = tag_name.text.strip()
                            precio_real = tag_price.text.replace("$", "").replace(".", "").replace(",", ".").strip()
                            
                            try:
                                precio = builtins.float(precio_real)
                            except ValueError:
                                precio = 0.0
                                
                            marca = "AMD" if "amd" in nombre.lower() else ("Intel" if "intel" in nombre.lower() else "Genérica")
                            
                            cursor.execute(
                                "INSERT INTO precios_lista (nombre, precio, marca, fecha, categoria) VALUES (?, ?, ?, ?, ?)",
                                (nombre, precio, marca, fecha_hoy, nombre_cat)
                            )
                            time.sleep(random.uniform(0.5, 0.8))
                            print(f"Guardado {nombre[:40]}... | ${precio} [{nombre_cat}]")
                            contador += 1
                            
                    conexion.commit()
                    
                elif respuesta.status_code == 403:
                    print("El servidor rechazó la conexión. Respuesta: ")
                    print(respuesta.text[:500])
                    conexion.close()
                    return False
                elif respuesta.status_code == 404:
                    print("Servidor no encontrado. Error 404.")
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
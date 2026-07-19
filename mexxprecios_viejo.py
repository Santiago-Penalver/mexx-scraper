import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
from datetime import datetime
def actualizar_precios_lista():
    url = "https://www.mexx.com.ar/productos-rubro/procesadores/"
    headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        respuesta = requests.get(url, headers=headers)
        tiempo_espera = random.uniform(3.0, 5.0)
        print("Intentando extraer informacion de Mexx...")
        time.sleep(tiempo_espera)
    
        if respuesta.status_code == 200:
            
            soup = BeautifulSoup(respuesta.text, "html.parser")

            productos_lista = soup.select("div[class*='card-ecommerce']")

            if not productos_lista:
                print("No se encontró la lista de productos")
                return False
            conexion = sqlite3.connect("mexxlista.db")
            cursor = conexion.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS precios_lista (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               nombre TEXT,
               precio REAL,
               marca TEXT,
               fecha TEXT
            )
            """)
            cursor.execute("DELETE FROM precios_lista")

            fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            contador = 0
            for prod in productos_lista:
                tag_name = prod.find("h4") or prod.find(class_=lambda x: x and 'title' in x)
                tag_price = prod.find("h3") or prod.find(class_= lambda x: x and 'price' in x)

                if tag_name and tag_price:
                    nombre = tag_name.text.strip()
                    precio_real = tag_price.text.replace ("$", "").replace(".", "").replace(",", ".").strip()

                    try:
                        precio = float(precio_real)
                    except ValueError:
                        precio = 0.0
                
                    marca = "AMD" if "amd" in nombre.lower() else ("Intel" if "intel" in nombre.lower() else "Genérica")

                    cursor.execute("INSERT INTO precios_lista (nombre, precio, marca, fecha) VALUES (?, ?, ?, ?)", (nombre, precio, marca, fecha_hoy))
                    time.sleep = random.uniform(0.5, 0.8)
                    print(f"Guardado {nombre[:40]}...| ${precio}")
                    contador += 1
            conexion.commit()
            conexion.close()
            print(f"Se actualizaron {contador} productos de Mexx en la base de datos.")
            return True
        elif respuesta.status_code == 403:
            print("El servidor rechazó la conexión. Respuesta: ")
            print(respuesta.text[:500])
            return False
        elif respuesta.status_code == 404:
            print("Servidor no encontrado. Error 404.")
            return False
        else:
            print(f"Error de conexión con el servidor. Código de estado: {respuesta.status_code}")
            return False

    except Exception as e:
        print(f"Error en el Backend: {e}")
        return False
if __name__ == '__main__':
    print("Iniciando el script manualmente...")
    actualizar_precios_lista()
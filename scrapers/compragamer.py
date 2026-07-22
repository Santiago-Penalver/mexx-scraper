import builtins
from datetime import datetime
import sqlite3
import requests
from utils import es_producto_valido

# Mapa de fabricantes para normalización de marca
FABRICANTES_MAP = {
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
    "lg": "LG",
}


def detectar_marca(nombre_producto):
    """Detecta la marca del producto analizando las palabras del nombre."""
    nombre_lower = nombre_producto.lower()

    for clave, nombre_oficial in FABRICANTES_MAP.items():
        if clave in nombre_lower:
            return nombre_oficial

    if "intel" in nombre_lower:
        return "Intel"
    elif "amd" in nombre_lower:
        return "AMD"
    elif "nvidia" in nombre_lower:
        return "Nvidia"

    return "Genérica"


def actualizar_compragamer():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contador = 0

    url_api = "https://static.compragamer.com/productos"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://compragamer.com/",
    }

    print("=== Iniciando la extracción filtrada de Compra Gamer ===")

    try:
        respuesta = requests.get(url_api, headers=headers, timeout=15)

        if respuesta.status_code == 200:
            productos = respuesta.json()

            conexion = sqlite3.connect("hardware_tracker.db")
            cursor = conexion.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS precios_lista (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    precio REAL,
                    marca TEXT,
                    fecha TEXT,
                    categoria TEXT,
                    tienda TEXT
                )
            """)

            cursor.execute("DELETE FROM precios_lista WHERE tienda = 'Compra Gamer'")

            for prod in productos:
                nombre = prod.get("nombre", "").strip()

                if not nombre:
                    continue

                precio_raw = prod.get("precioEspecial") or prod.get("precioLista") or 0
                try:
                    precio = builtins.float(precio_raw)
                except (ValueError, TypeError):
                    precio = 0.0

                # --- APLICAMOS EL FILTRO PRECISO ---
                if not es_producto_valido(nombre, precio):
                    continue

                categoria = prod.get("categoria", "General")
                marca = detectar_marca(nombre)

                if not es_producto_valido(nombre, precio):
                    continue

                cursor.execute(
                    """
                    INSERT INTO precios_lista (nombre, precio, marca, fecha, categoria, tienda)
                    VALUES (?, ?, ?, ?, ?, 'Compra Gamer')
                    """,
                    (nombre, precio, marca, fecha_hoy, categoria),
                )

                contador += 1
                print(f"Guardado {nombre[:40]}... | ${precio} [Compra Gamer]")

            conexion.commit()
            conexion.close()

            print(
                f"\n=== Se actualizaron {contador} productos reales de Compra Gamer en la base de datos! ==="
            )
            return True

        elif respuesta.status_code == 403:
            print("El servidor rechazó la conexión (403 Forbidden).")
            return False
        else:
            print(f"Error de conexión. Código HTTP: {respuesta.status_code}")
            return False

    except Exception as e:
        print(f"Error en el Backend de Compra Gamer: {e}")
        return False


if __name__ == "__main__":
    actualizar_compragamer()
# Hardware Tracker - Mexx Scraper

Panel de monitoreo interno y web scraping automatizado para registrar stock y precios de hardware en tiempo real. La aplicación extrae de forma dinámica la información de los productos y la almacena en una base de datos local para su visualización a través de una interfaz web fluida y moderna.

## Tecnologías Utilizadas

* **Backend:** Python con Flask
* **Web Scraping:** BeautifulSoup4 y Requests
* **Base de Datos:** SQLite3 (Persistencia de datos en `mexxlista.db`)
* **Frontend:** HTML5, Tailwind CSS (con configuración personalizada de temas) y Font Awesome para la iconografía.
* **Interactividad Dinámica:** HTMX (implementado para el filtrado por marcas en tiempo real y la carga asíncrona de la vista de detalles individuales sin recargar la página).

## Características Principales

* Extracción automática de nombres, precios de lista/tarjeta, marcas y marcas de tiempo del stock de la tienda.
* Dashboard principal con contadores dinámicos que calculan la cantidad de procesadores listados en total, cuántos pertenecen a la línea AMD Ryzen y cuántos a Intel Core.
* Filtros rápidos por marca que inyectan el contenido de forma limpia mediante componentes.
* Formateo local de precios y fechas integrado directamente en las plantillas.

## Cómo Ejecutar el Proyecto

Para correr este proyecto de forma local en tu computadora, seguí estos pasos:

### 1. Clonar el repositorio
```bash
    git clone https://github.com/Santiago-Penalver/mexx-scraper.git
```
### 2. Instalar las dependencias
```bash
    pip install -r requirements.txt
```
### 3. Iniciar la app
```bash
        python app.py
```
### 4. Ingresá a la web que muestra en la terminal

* http://127.0.0.1:5000

Desarrollado por Santiago Peñalver - 2026
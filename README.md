<div align="center">
  <img src="assets/logo_white.png" alt="Logo" width="200">
  <h1>Sistema de Gestión Empresarial</h1>
  <p>Una aplicación de escritorio completa para la gestión empresarial desarrollada con PySide6 y MongoDB</p>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-6.5.0+-red.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 🚀 Características Principales

- **Dashboard Interactivo**
  - Métricas en tiempo real
  - Gráficos de ventas e inventario
  - Resumen financiero

- **Gestión de Inventario**
  - Control de stock
  - Alertas de inventario bajo
  - Categorización de productos

- **Módulo de Ventas**
  - Registro de ventas
  - Gestión de clientes
  - Facturación

- **CRM de Clientes**
  - Base de datos de clientes
  - Historial de compras
  - Segmentación

- **Contabilidad**
  - Registro de ingresos/gastos
  - Reportes financieros
  - Gestión de facturas

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- MongoDB 4.4 o superior
- pip (gestor de paquetes de Python)

## 🛠 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/tu-repositorio.git
   cd tu-repositorio
   ```

2. Crea un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura la base de datos MongoDB:
   - Asegúrate de tener MongoDB instalado y en ejecución
   - La aplicación creará automáticamente las colecciones necesarias

5. Inicia la aplicación:
   ```bash
   python main.py
   ```
   
   **Credenciales por defecto:**
   - Usuario: admin
   - Contraseña: admin

## 🖼️ Capturas de Pantalla

<div align="center">
  <img src="assets/icons/loging.png" alt="Vista previa 1" width="45%">
  <img src="assets/icons/login.png" alt="Vista previa 2" width="45%">
</div>

## 📦 Dependencias Principales

- PySide6 >= 6.5.0 - Interfaz gráfica
- pymongo >= 4.4.0 - Conexión con MongoDB
- pycryptodome >= 3.18.0 - Encriptación
- pyotp >= 2.7.0 - Autenticación de dos factores
- pyjwt >= 2.8.0 - Manejo de tokens JWT

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, lee nuestras [pautas de contribución](CONTRIBUTING.md) antes de enviar un pull request.

## 📧 Contacto

Para consultas o soporte, por favor contacta a [masso_sergio@hotmail.com](mailto:masso_sergio@hotmail.com)

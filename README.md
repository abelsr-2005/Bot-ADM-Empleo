# 🤖 Bot de Alertas de Empleo Automatizado

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-green?logo=githubactions&logoColor=white)
![JobSpy](https://img.shields.io/badge/Library-JobSpy-orange)

Este proyecto es un bot automatizado diseñado para **monitorizar, filtrar y notificar** ofertas de empleo relevantes diariamente. Ejecutado en la nube mediante **GitHub Actions**, elimina la necesidad de búsqueda manual en portales de empleo.

---

## 🚀 Funcionalidades

* **Scraping Multi-Plataforma:** Busca ofertas en **LinkedIn** e **Indeed** simultáneamente.
* **Filtro Inteligente:**
    * ✅ Busca palabras clave específicas (ej. "SysAdmin", "Técnico Sistemas").
    * ❌ Descarta ofertas con palabras no deseadas ("Beca", "Comercial", "Junior").
* **Notificaciones vía Email:** Envía un reporte diario en formato HTML limpio directamente a la bandeja de entrada.
* **100% Automatizado:** Se ejecuta automáticamente cada mañana a las 09:00 AM (hora España) mediante un cron job.
* **Zero Cost:** Funciona completamente gratis aprovechando la capa gratuita de GitHub Actions.

## 🛠️ Tecnologías Usadas

* **Python 3.10**: Lógica principal.
* **JobSpy (lib)**: Motor de scraping para portales de empleo.
* **Pandas**: Procesamiento y limpieza de datos.
* **SMTP Lib**: Gestión de envío de correos electrónicos seguros.
* **GitHub Actions**: CI/CD para la orquestación y ejecución programada.

## ⚙️ Configuración

El bot utiliza **Variables de Entorno (GitHub Secrets)** para proteger las credenciales. No se expone información sensible en el código.

### Variables Requeridas:

| Nombre del Secreto | Descripción |
| :--- | :--- |
| `EMAIL_USER` | Dirección de Gmail desde donde se envía (y recibe) el correo. |
| `EMAIL_PASSWORD` | Contraseña de aplicación de Google (no la contraseña normal). |

### Personalización (`main.py`)

Puedes ajustar los parámetros de búsqueda editando las variables al inicio del script:

```python
# Ubicación de búsqueda
LOCATION = "Huelva, Spain"

# Palabras clave para buscar
KEYWORDS = ["System Administrator", "DevOps", "Soporte TI"]

# Palabras para descartar automáticamente
PALABRAS_EXCLUIR = ["Prácticas", "Ventas", "Call Center"]

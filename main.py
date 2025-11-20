import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
LOCATION = "Huelva, Spain"

KEYWORDS = [
    "Técnico informático", "Técnico/a informático/a",
    "Administrador de sistemas", "System Administrator",
    "Técnico de sistemas y redes", "Soporte TI",
    "Helpdesk", "Service Desk",
    "Windows", "Linux", "VMware", "Virtualización",
    "Técnico de Redes", "Network Engineer", "CCNA",
    "Ingeniero de Redes", "Técnico de Comunicaciones",
    "Administrador IT", "Responsable IT"
]

# Filtros de exclusión (Actualizados con tu feedback)
# Filtros de exclusión (Refinado: Anti-PRL)
PALABRAS_EXCLUIR = [
    # Basura general
    "Beca", "Prácticas", "Comercial", "Ventas", "Sales",
    "Programador", "Developer", "Frontend", "Backend", "Junior",
    
    # Oficios y Construcción
    "Construcción", "Obra", "Peón", "Albañil", "Fontanero",
    "Mecánico", "Electromecánico", "Climatización",
    "Producción", "Operador", "Mantenimiento industrial",
    
    # Servicios
    "Domicilio", "Ayuda", "Auxiliar", "Enfermero", "Limpieza",
    "Dependiente", "Repartidor", "Mozo", "Conductor",
    "Administrativo", "Recepcionista", "Call Center",
    
    # NUEVO: Anti-PRL (Prevención de Riesgos)
    "PRL", "Riesgos", "Preventivo", "Prevención", "Salud", "Laborales"
]
# --- 2. FUNCIÓN DE ENVÍO (UN SOLO CORREO) ---
def enviar_resumen_correo(ofertas_html, cantidad):
    try:
        usuario = os.environ["EMAIL_USER"]
        password = os.environ["EMAIL_PASSWORD"]
    except KeyError:
        print("❌ Error: Faltan secretos.")
        return

    destinatario = usuario 
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['To'] = destinatario
    msg['Subject'] = f"🚀 Resumen Diario: {cantidad} Ofertas en {LOCATION} ({fecha_hoy})"

    # Plantilla HTML del correo completo
    cuerpo = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h2>Boletín de Empleo - SysAdmin</h2>
            <p>Hoy hemos encontrado <strong>{cantidad}</strong> ofertas potenciales en {LOCATION}.</p>
        </div>
        
        <div style="padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd;">
            {ofertas_html}
        </div>

        <div style="text-align: center; padding: 20px; font-size: 12px; color: #777;">
            Bot Automatizado con GitHub Actions
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(usuario, password)
        server.sendmail(usuario, destinatario, msg.as_string())
        server.quit()
        print(f"✅ Correo RESUMEN enviado con {cantidad} ofertas.")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

# --- 3. MOTOR DE BÚSQUEDA ---
def buscar_y_enviar():
    print(f"🔍 Buscando ofertas en {LOCATION}...")
    
    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=" OR ".join(KEYWORDS),
            location=LOCATION,
            results_wanted=20, # Buscamos bastantes para filtrar luego
            hours_old=24, 
            country_indeed='spain'
        )
    except Exception as e:
        print(f"Error en la búsqueda: {e}")
        return

    if jobs is None or jobs.empty:
        print("✅ No hay ofertas nuevas hoy. No se envía correo.")
        return

    print(f"🔎 Encontradas {len(jobs)} ofertas brutas. Filtrando y recopilando...")
    
    # Variable para acumular el HTML de todas las ofertas válidas
    contenido_html_acumulado = ""
    contador_validas = 0

    for index, job in jobs.iterrows():
        titulo = str(job['title']).lower()
        es_valida = True

        # Filtro Anti-Ruido
        for palabra in PALABRAS_EXCLUIR:
            if palabra.lower() in titulo:
                es_valida = False
                print(f"🗑️ Descartada: {job['title']}")
                break

        if es_valida:
            print(f"⭐ Añadida al resumen: {job['title']}")
            contador_validas += 1
            
            # Añadimos esta oferta al bloque HTML
            contenido_html_acumulado += f"""
            <div style="background: white; padding: 15px; margin-bottom: 15px; border-left: 5px solid #28a745; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #28a745;">{job['title']}</h3>
                <p><strong>🏢 Empresa:</strong> {job['company']}</p>
                <p><strong>📍 Ubicación:</strong> {job['location']}</p>
                <p style="text-align: right;">
                    <a href="{job['job_url']}" style="background-color: #28a745; color: white; padding: 8px 15px; text-decoration: none; border-radius: 3px; font-weight: bold;">
                        VER OFERTA 🔗
                    </a>
                </p>
            </div>
            <hr style="border: 0; border-top: 1px solid #eee;">
            """

    # --- MOMENTO DE LA VERDAD ---
    if contador_validas > 0:
        print(f"🚀 Enviando resumen con {contador_validas} ofertas...")
        enviar_resumen_correo(contenido_html_acumulado, contador_validas)
    else:
        print("🏁 Ninguna oferta pasó el filtro final. No se envía correo.")

if __name__ == "__main__":
    buscar_y_enviar()

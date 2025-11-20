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
    # --- TÍTULOS GENERALES ---
    "Administrador de Sistemas", "System Administrator", "SysAdmin",
    "Técnico de Sistemas", "Systems Technician", "Soporte TI",
    "Ingeniero de Sistemas", "Analista de Sistemas",
    "Administrador IT", "IT Manager", "Coordinador TI",
    "Técnico de Infraestructura", "Helpdesk", "Service Desk",
    "Técnico informático", "Técnico/a informático/a",
    
    # --- REDES ---
    "Administrador de Redes", "Network Administrator",
    "Ingeniero de Redes", "Network Engineer",
    "Técnico de Redes", "Network Technician",
    "CCNA", "Cisco", "Fortinet", "Mikrotik",
    
    # --- TECNOLOGÍAS ---
    "Windows Server", "Linux", "Active Directory",
    "Virtualización", "VMware", "Hyper-V", 
    "Office 365", "Azure", "AWS", "Cloud",
    "Técnico de Campo", "Mantenimiento Informático"
]

# Filtros (Anti-Ruido y Anti-PRL)
PALABRAS_EXCLUIR = [
    "Beca", "Prácticas", "Comercial", "Ventas", "Sales",
    "Programador", "Developer", "Frontend", "Backend", "Junior",
    "Construcción", "Obra", "Peón", "Albañil", "Fontanero",
    "Mecánico", "Electromecánico", "Climatización",
    "Producción", "Operador", "Mantenimiento industrial",
    "Domicilio", "Ayuda", "Auxiliar", "Enfermero", "Limpieza",
    "Dependiente", "Repartidor", "Mozo", "Conductor",
    "Administrativo", "Recepcionista", "Call Center",
    "PRL", "Riesgos", "Preventivo", "Prevención", "Salud", "Laborales"
]

# --- 2. FUNCIÓN DE ENVÍO ---
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
    msg['Subject'] = f"🚀 Resumen Huelva: {cantidad} Ofertas ({fecha_hoy})"

    cuerpo = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
            <h2>Boletín SysAdmin - Huelva</h2>
            <p>Hoy hemos encontrado <strong>{cantidad}</strong> ofertas potenciales.</p>
        </div>
        <div style="padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd;">
            {ofertas_html}
        </div>
        <div style="text-align: center; padding: 20px; font-size: 12px; color: #777;">
            Bot Automatizado (Fuentes: LinkedIn, Indeed, Google Jobs)
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
        # Añadido "google" para pillar InfoJobs
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "google"], 
            search_term=" OR ".join(KEYWORDS),
            location=LOCATION,
            results_wanted=20,
            hours_old=24, 
            country_indeed='spain'
        )
    except Exception as e:
        print(f"Error en la búsqueda: {e}")
        return

    if jobs is None or jobs.empty:
        print("✅ No hay ofertas nuevas hoy.")
        return

    print(f"🔎 Encontradas {len(jobs)} ofertas brutas. Filtrando...")
    
    contenido_html_acumulado = ""
    contador_validas = 0

    for index, job in jobs.iterrows():
        titulo = str(job['title']).lower()
        es_valida = True

        for palabra in PALABRAS_EXCLUIR:
            if palabra.lower() in titulo:
                es_valida = False
                print(f"🗑️ Descartada: {job['title']}")
                break

        if es_valida:
            print(f"⭐ Añadida: {job['title']}")
            contador_validas += 1
            
            # Tarjeta de Oferta HTML
            contenido_html_acumulado += f"""
            <div style="background: white; padding: 15px; margin-bottom: 15px; border-left: 5px solid #28a745; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #28a745;">{job['title']}</h3>
                <p><strong>🏢 Empresa:</strong> {job['company']}</p>
                <p><strong>📍 Ubicación:</strong> {job['location']}</p>
                <p><strong>📅 Publicado:</strong> {job['date_posted']}</p>
                <p style="text-align: right;">
                    <a href="{job['job_url']}" style="background-color: #28a745; color: white; padding: 8px 15px; text-decoration: none; border-radius: 3px; font-weight: bold;">
                        VER ENLACE 🔗
                    </a>
                </p>
            </div>
            <hr style="border: 0; border-top: 1px solid #eee;">
            """

    if contador_validas > 0:
        enviar_resumen_correo(contenido_html_acumulado, contador_validas)
    else:
        print("🏁 Ninguna oferta pasó el filtro final.")

if __name__ == "__main__":
    buscar_y_enviar()

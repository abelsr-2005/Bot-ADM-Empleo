import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jobspy import scrape_jobs
import pandas as pd

# --- CONFIGURACIÓN DE BÚSQUEDA ---
LOCATION = "Huelva, Spain"

KEYWORDS = [
    "Técnico informático",
    "Técnico/a informático/a",
    "Administrador de sistemas informáticos",
    "Administrador/a de sistemas informáticos",
    "Técnico de sistemas y redes",
    "Técnico de soporte informático",
    "Técnico de soporte microinformático",
    "Administrador de sistemas",
    "Windows",
    "Linux",
    "Técnico de Redes", 
    "Administrador de Redes", 
    "Técnico de Comunicaciones",
    "Técnico de Sistemas y Redes",
    "Ingeniero de Redes",
    "Administrador IT",
    
    # Títulos en Inglés
    "Network Engineer", 
    "Network Administrator", 
    "Network Technician",
    
    # Certificaciones/Tecnologías
    "CCNA",
    "Cisco",
    "Fortinet"
]

# Palabras que si aparecen en el título, DESCARTAN la oferta (Anti-ruido)
PALABRAS_EXCLUIR = [
    "Beca", "Prácticas", "Comercial", "Ventas", 
    "Programador Web", "Frontend", "Backend", "Junior",
    "Electricista", "Peón" # Evitamos puestos de obra pura
]

def enviar_correo(job):
    # Obtener credenciales de la caja fuerte de GitHub
    try:
        usuario = os.environ["EMAIL_USER"]
        password = os.environ["EMAIL_PASSWORD"]
    except KeyError:
        print("❌ Error: Faltan las credenciales (EMAIL_USER / EMAIL_PASSWORD).")
        return

    destinatario = usuario 

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['To'] = destinatario
    msg['Subject'] = f"🚀 Nueva Oferta: {job['title']}"

    # Cuerpo del correo en HTML
    cuerpo = f"""
    <html>
      <body>
        <h2>Nueva Oportunidad en {LOCATION}</h2>
        <p><strong>Puesto:</strong> {job['title']}</p>
        <p><strong>Empresa:</strong> {job['company']}</p>
        <p><strong>Ubicación:</strong> {job['location']}</p>
        <p><strong>Fecha:</strong> {job['date_posted']}</p>
        <br>
        <a href="{job['job_url']}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
           VER OFERTA Y APLICAR
        </a>
        <br><br>
        <p style="font-size: small; color: gray;">Bot de Empleo Automático</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo, 'html'))

    # Enviar el correo
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(usuario, password)
        server.sendmail(usuario, destinatario, msg.as_string())
        server.quit()
        print(f"📧 Correo enviado para: {job['title']}")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

def buscar_y_enviar():
    print(f"🔍 Buscando ofertas en {LOCATION}...")
    print(f"📋 Palabras clave: {len(KEYWORDS)} términos definidos.")

    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=" OR ".join(KEYWORDS),
            location=LOCATION,
            results_wanted=10,
            hours_old=24, # Solo ofertas de las últimas 24 horas
            country_indeed='spain'
        )
    except Exception as e:
        print(f"Error buscando ofertas: {e}")
        return

    if jobs is None or jobs.empty:
        print("✅ No se encontraron ofertas nuevas hoy.")
        return

    print(f"🔎 Encontradas {len(jobs)} ofertas brutas. Aplicando filtro inteligente...")
    enviadas = 0

    for index, job in jobs.iterrows():
        titulo = str(job['title']).lower()
        es_valida = True

        # Filtro de palabras prohibidas
        for palabra in PALABRAS_EXCLUIR:
            if palabra.lower() in titulo:
                es_valida = False
                print(f"🗑️ Descartada (Filtro): {job['title']}")
                break

        if es_valida:
            enviar_correo(job)
            enviadas += 1

    if enviadas == 0:
        print("Ninguna oferta pasó el filtro de exclusión.")

if __name__ == "__main__":
    buscar_y_enviar()

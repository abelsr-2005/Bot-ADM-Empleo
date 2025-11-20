import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jobspy import scrape_jobs
import pandas as pd

# --- 1. CONFIGURACIÓN ---
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
    "Windows", "Linux",
    "Técnico de Redes", "Administrador de Redes", 
    "Técnico de Comunicaciones", "Ingeniero de Redes",
    "Administrador IT", "Soporte TI",
    "Network Engineer", "Network Administrator",
    "CCNA", "Cisco", "Fortinet"
]

# Palabras para descartar basura
PALABRAS_EXCLUIR = [
    "Beca", "Prácticas", "Comercial", "Ventas", 
    "Programador Web", "Frontend", "Backend", "Junior",
    "Electricista", "Peón"
]

# --- 2. FUNCIÓN DE ENVÍO DE CORREO ---
def enviar_correo(job):
    try:
        usuario = os.environ["EMAIL_USER"]
        password = os.environ["EMAIL_PASSWORD"]
    except KeyError:
        print("❌ Error: Faltan secretos.")
        return

    destinatario = usuario 
    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['To'] = destinatario
    msg['Subject'] = f"🚀 Oferta Huelva: {job['title']}"

    cuerpo = f"""
    <html>
      <body>
        <h2>Nueva Oportunidad en {LOCATION}</h2>
        <p><strong>Puesto:</strong> {job['title']}</p>
        <p><strong>Empresa:</strong> {job['company']}</p>
        <p><strong>Ubicación:</strong> {job['location']}</p>
        <br>
        <a href="{job['job_url']}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
           VER OFERTA Y APLICAR
        </a>
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
        print(f"📧 Correo enviado: {job['title']}")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")

# --- 3. MOTOR DE BÚSQUEDA ---
def buscar_y_enviar():
    print(f"🔍 Buscando ofertas en {LOCATION}...")
    print(f"📋 Buscando {len(KEYWORDS)} perfiles diferentes...")

    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=" OR ".join(KEYWORDS),
            location=LOCATION,
            results_wanted=15,
            hours_old=24, 
            country_indeed='spain'
        )
    except Exception as e:
        print(f"Error en la búsqueda: {e}")
        return

    if jobs is None or jobs.empty:
        print("✅ No hay ofertas nuevas hoy en Huelva. ¡Hasta mañana!")
        return

    print(f"🔎 Encontradas {len(jobs)} ofertas. Filtrando...")
    enviadas = 0

    for index, job in jobs.iterrows():
        titulo = str(job['title']).lower()
        es_valida = True

        for palabra in PALABRAS_EXCLUIR:
            if palabra.lower() in titulo:
                es_valida = False
                print(f"🗑️ Descartada por filtro: {job['title']}")
                break

        if es_valida:
            enviar_correo(job)
            enviadas += 1

    if enviadas == 0:
        print("Ninguna oferta pasó el filtro final.")

if __name__ == "__main__":
    buscar_y_enviar()

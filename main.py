import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jobspy import scrape_jobs
import pandas as pd

# --- CONFIGURACIÓN ---
KEYWORDS = ["Administrador de Sistemas", "System Administrator", "Técnico Sistemas", "Informático", "Soporte TI"]
LOCATION = "Huelva, Spain"

PALABRAS_EXCLUIR = [
    "Beca", "Prácticas", "Comercial", "Ventas", 
    "Programador Web", "Frontend", "Backend", "Junior"
]

def enviar_correo(job):
    # Credenciales desde GitHub Secrets
    usuario = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASSWORD"]
    destinatario = usuario # Nos lo enviamos a nosotros mismos

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['To'] = destinatario
    msg['Subject'] = f"🚀 Nueva Oferta: {job['title']}"

    # Cuerpo del correo (HTML)
    cuerpo = f"""
    <html>
      <body>
        <h2>Nueva Oportunidad Detectada</h2>
        <p><strong>Puesto:</strong> {job['title']}</p>
        <p><strong>Empresa:</strong> {job['company']}</p>
        <p><strong>Ubicación:</strong> {job['location']}</p>
        <br>
        <a href="{job['job_url']}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
           VER OFERTA Y APLICAR
        </a>
        <br><br>
        <p style="font-size: small; color: gray;">Bot de Empleo Huelva - SysAdmin</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo, 'html'))

    # Enviar
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

    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=" OR ".join(KEYWORDS),
            location=LOCATION,
            results_wanted=10,
            hours_old=24, 
            country_indeed='es'
        )
    except Exception as e:
        print(f"Error buscando ofertas: {e}")
        return

    if jobs is None or jobs.empty:
        print("No se encontraron ofertas nuevas hoy.")
        return

    print(f"Encontradas {len(jobs)} ofertas. Filtrando...")
    enviadas = 0

    # --- AQUÍ ESTABA EL ERROR, YA CORREGIDO ---
    for index, job in jobs.iterrows():
    # ------------------------------------------
        titulo = str(job['title']).lower()
        es_valida = True

        for palabra in PALABRAS_EXCLUIR:
            if palabra.lower() in titulo:
                es_valida = False
                print(f"❌ Descartada: {job['title']} (spam)")
                break

        if es_valida:
            enviar_correo(job)
            enviadas += 1

    if enviadas == 0:
        print("Ninguna oferta pasó el filtro.")

if __name__ == "__main__":
    buscar_y_enviar()

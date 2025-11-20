import os
import requests
from jobspy import scrape_jobs
import pandas as pd

# --- CONFIGURACIÓN ---
KEYWORDS = ["Administrador de Sistemas", "System Administrator", "Técnico Sistemas", "Informático", "Soporte TI"]
LOCATION = "Huelva, Spain"

# Palabras que si aparecen en el título, DESCARTAN la oferta
PALABRAS_EXCLUIR = [
    "Beca", "Prácticas", "Comercial", "Ventas", 
    "Programador Web", "Frontend", "Backend", "Junior"
]

def buscar_y_enviar():
    print(f"🔍 Buscando ofertas en {LOCATION}...")

    try:
        # Buscamos en LinkedIn e Indeed
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=" OR ".join(KEYWORDS),
            location=LOCATION,
            results_wanted=10,
            hours_old=24, # Solo últimas 24 horas
            country_indeed='es'
        )
    except Exception as e:
        print(f"Error buscando ofertas: {e}")
        return

    if jobs is None or jobs.empty:
        print("No se encontraron ofertas nuevas hoy.")
        return

    print(f"Encontradas {len(jobs)} ofertas. Filtrando...")

    # --- AQUÍ ESTÁ LA CORRECCIÓN ---
    # Pedimos el NOMBRE de la variable, GitHub pondrá el valor mágicamente
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    # -------------------------------
    
    enviadas = 0

    for index, job in jobs.iterrows():
        titulo = str(job['title']).lower()
        es_valida = True

        # Filtro de palabras prohibidas
        for palabra in PALABRAS_EXCLUIR:
            if palabra.lower() in titulo:
                es_valida = False
                print(f"❌ Descartada: {job['title']} (Contiene '{palabra}')")
                break

        if es_valida:
            print(f"✅ Enviando: {job['title']}")
            mensaje = (
                f"🔔 **Nueva Oferta SysAdmin**\n\n"
                f"💼 **Puesto:** {job['title']}\n"
                f"🏢 **Empresa:** {job['company']}\n"
                f"📍 **Ubicación:** {job['location']}\n"
                f"🔗 [Ver Oferta]({job['job_url']})"
            )
            # Enviar a Telegram
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
            )
            enviadas += 1

    if enviadas == 0:
        print("Ninguna oferta pasó el filtro de palabras.")

if __name__ == "__main__":
    buscar_y_enviar()

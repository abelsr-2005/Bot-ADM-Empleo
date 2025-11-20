import os
import smtplib

def diagnostico_gmail():
    print("--- INICIANDO DIAGNÓSTICO DE CONEXIÓN ---")
    
    # 1. Recuperar secretos
    try:
        user = os.environ["EMAIL_USER"]
        pwd = os.environ["EMAIL_PASSWORD"]
    except KeyError:
        print("❌ ERROR CRÍTICO: GitHub no tiene los secretos guardados.")
        return

    # 2. Analizar el Usuario (EMAIL_USER)
    print(f"📧 Usuario detectado: '{user}'")
    if " " in user:
        print("   ❌ ERROR: Hay espacios en blanco en tu correo. Bórralos en GitHub Secrets.")
    if "@" not in user:
        print("   ❌ ERROR: Esto no parece un correo electrónico.")

    # 3. Analizar la Contraseña (EMAIL_PASSWORD)
    longitud = len(pwd)
    print(f"🔑 Longitud de contraseña: {longitud} caracteres")
    
    if longitud > 19: # 16 letras + posibles espacios
        print("   ⚠️ ADVERTENCIA: La contraseña parece muy larga. ¿Has copiado comillas?")
    
    # 4. Prueba de Fuego: Conexión real
    print("📡 Intentando conectar con los servidores de Google...")
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("   ✅ Conexión segura establecida.")
        
        server.login(user, pwd)
        print("   🎉 ¡ÉXITO! CREDENCIALES ACEPTADAS.")
        print("   ✅ Google ha dejado pasar al bot.")
        server.quit()
        
    except smtplib.SMTPAuthenticationError:
        print("   ❌ FALLO DE AUTENTICACIÓN (Error 535).")
        print("      Posibles causas:")
        print("      1. El correo impreso arriba ('Usuario detectado') tiene una errata.")
        print("      2. La contraseña de aplicación pertenece a OTRA cuenta de Google diferente.")
        print("      3. Has copiado un espacio en blanco al final del secreto.")
    except Exception as e:
        print(f"   ❌ Otro error: {e}")

if __name__ == "__main__":
    diagnostico_gmail()

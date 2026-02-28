"""
Script de diagnóstico para verificar credenciales de Traffilink
Prueba la conexión y autenticación directamente
"""
import requests
import json
from config import TRAFFILINK_BASE_URL, TRAFFILINK_ACCOUNT, TRAFFILINK_PASSWORD

print("=" * 70)
print("🔍 DIAGNÓSTICO DE TRAFFILINK")
print("=" * 70)

# Datos
url = f"{TRAFFILINK_BASE_URL}/getbalance"
params = {
    "account": TRAFFILINK_ACCOUNT,
    "password": TRAFFILINK_PASSWORD
}

print(f"\n📡 URL: {url}")
print(f"🔐 Account: {TRAFFILINK_ACCOUNT}")
print(f"🔑 Password: {'*' * len(TRAFFILINK_PASSWORD)}")

print("\n" + "=" * 70)
print("Intentando conectar...")
print("=" * 70 + "\n")

try:
    # Intento 1: HTTP normal
    print("1️⃣  Intentando HTTP (http://...)...")
    response = requests.get(url, params=params, timeout=10)

    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}\n")

    try:
        data = response.json()
        code = data.get('code')

        if code == 0:
            print("   ✅ ¡AUTENTICACIÓN EXITOSA!")
            print(f"   Balance: {data.get('balance')}")
            print(f"   Gift Balance: {data.get('gift_balance')}")
        elif code == -1:
            print("   ❌ Autenticación fallida (código -1)")
            print("   Las credenciales son incorrectas o han sido bloqueadas")
        else:
            print(f"   ⚠️ Código de error: {code}")
            print(f"   Respuesta: {json.dumps(data, indent=2)}")

    except json.JSONDecodeError:
        print("   ⚠️ Respuesta no es JSON válido")
        print(f"   Raw: {response.text}")

except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT - El servidor no respondió en 10 segundos")
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ ERROR DE CONEXIÓN: {str(e)}")
    print("   No se puede conectar a la IP/servidor")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("2️⃣  Intentando HTTPS (https://...)...")
print("=" * 70 + "\n")

try:
    url_https = TRAFFILINK_BASE_URL.replace("http://", "https://")
    response = requests.get(url_https, params=params, timeout=10, verify=False)

    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}\n")

    try:
        data = response.json()
        if data.get('code') == 0:
            print("   ✅ ¡HTTPS FUNCIONA!")
        else:
            print(f"   ⚠️ Código: {data.get('code')}")
    except:
        pass

except Exception as e:
    print(f"   ℹ️ HTTPS no funciona: {str(e)}")

print("\n" + "=" * 70)
print("📋 RESUMEN:")
print("=" * 70)
print("""
Si ves:
  ✅ Autenticación exitosa
    → Las credenciales funcionan. El problema es la conectividad en Render.

  ❌ Autenticación fallida (código -1)
    → Las credenciales no son válidas o fueron bloqueadas.
    → Posibles causas:
       1. Credenciales incorrectas
       2. El servidor bloqueó la IP después de fallos
       3. Credenciales expiradas o vencidas
       4. Contacta al proveedor de Traffilink

  ❌ Error de conexión
    → No se puede conectar a la IP
    → El servidor no es accesible desde tu red

  ⚠️ Error desconocido
    → Hay un problema con el formato o parámetros
""")

print("=" * 70)

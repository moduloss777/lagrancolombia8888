# 🔧 FIX: Balance Error - Instrucciones

Se encontraron 2 problemas que ya fueron arreglados:

## ❌ Problemas encontrados:
1. **"Error: Expecting value"** - JSON parse error
2. **Balance mostrando "--"** - Credenciales no conectando

## ✅ Cambios realizados:

### Archivo: `app.py`
- Mejorado endpoint `/api/balance` con mejor manejo de errores
- Agregado endpoint `/api/diagnostic` para verificar configuración
- JavaScript del dashboard ahora maneja errores correctamente

### Archivo: `traffilink_api.py`
- Mejorado `consultar_balance()` con logging detallado
- Mejor manejo de excepciones (Timeout, ConnectionError, ValueError)
- Verifica que credenciales estén configuradas

### Archivo: `templates/index.html`
- JavaScript mejorado para capturar errores correctamente
- Muestra "Error ⚠️" en lugar de "--" cuando falla
- Mejor logging en console del navegador

---

## 🚀 Subir cambios a GitHub (drag & drop)

### PASO 1: Ve a tu repositorio en GitHub
```
https://github.com/tusuario/GoleadorSmsMarketing-v2
```

### PASO 2: Actualizar 3 archivos modificados

#### Opción A: Upload files (recomendado)
1. Haz clic en **"Add file"** → **"Upload files"**
2. Selecciona ESTOS 3 archivos de tu carpeta local:
   - `app.py`
   - `traffilink_api.py`
   - `templates/index.html`
3. Arrastra a la ventana O haz clic en "choose your files"
4. Mensaje: `Fix balance error - improve error handling`
5. Haz clic en **"Commit changes"**

#### Opción B: Editar en GitHub directamente
1. Abre `app.py`
2. Haz clic en el lápiz (editar)
3. Copia todo el contenido de tu `app.py` local
4. Reemplaza en GitHub
5. Commit changes
6. Repite para `traffilink_api.py` y `templates/index.html`

---

## ⚡ Render redeploy automático

Render detectará los cambios automáticamente:
1. Render notará que GitHub fue actualizado
2. Hará redeploy automático (espera ~1 minuto)
3. Tu app se actualizará SIN hacer nada más

---

## 🔍 Verificar que funciona

Una vez que Render hace redeploy (espera 2-3 minutos):

### Test 1: Abrir Dashboard
```
https://goleador-sms-marketing.onrender.com
```
Deberías ver:
- ✅ Las tarjetas de estadísticas
- ✅ Balance mostrando un número (no "--")
- ✅ Sin errores en console

### Test 2: Verificar Diagnostic
```
https://goleador-sms-marketing.onrender.com/api/diagnostic
```
Deberías ver JSON con:
```json
{
  "timestamp": "...",
  "database": "OK",
  "traffilink": {
    "configured": true,
    "account": "0152C274",
    "password": "***",
    "url": "http://47.236.91.242:20003"
  },
  "stats": {...}
}
```

### Test 3: Verificar que credenciales están OK
Si ves `"configured": false` o `"account": "NOT SET"`, significa que:
- ❌ Las variables de entorno NO están configuradas en Render

**Solución:**
1. Ve a tu servicio en Render
2. Environment → verifica que estén:
   - TRAFFILINK_ACCOUNT = 0152C274
   - TRAFFILINK_PASSWORD = G2o0jRnm
   - TRAFFILINK_URL = http://47.236.91.242:20003
3. Si falta alguna, agrégala manualmente
4. Render hará redeploy automático

---

## 📊 Logs en Render

Si aún hay problemas:
1. Ve a tu servicio en Render
2. Haz clic en **"Logs"**
3. Busca líneas que digan:
   - "Consultando balance en..."
   - "Status: 200"
   - "Balance obtenido: X EUR"
4. Copialas y puedo ayudarte a diagnosticar

---

## 🎯 Checklist

- [ ] Subí 3 archivos a GitHub
- [ ] Render hizo redeploy (espera 2-3 min)
- [ ] Dashboard carga sin errores
- [ ] Balance muestra número (no "--")
- [ ] `/api/diagnostic` retorna "configured": true
- [ ] SMS se envían correctamente

---

**Una vez completes esto, el error desaparecerá** ✅

"""
Integración con TraffiLink API v3.4
"""

import requests
import hashlib
import logging
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

class TraffiLinkAPI:
    """Cliente para TraffiLink API"""
    
    def __init__(self):
        self.account = config.TRAFFILINK_ACCOUNT
        self.password = config.TRAFFILINK_PASSWORD
        self.url_base = config.TRAFFILINK_URL
        self.timeout = 10
        
        if not self.account or not self.password:
            logger.warning("⚠️ Credenciales de TraffiLink no configuradas")
    
    def generar_sign(self, params_str):
        """Genera firma MD5 para TraffiLink"""
        try:
            password_hash = hashlib.md5(self.password.encode()).hexdigest()
            sign_str = f"{params_str}{password_hash}"
            return hashlib.md5(sign_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generando sign: {e}")
            return None
    
    def consultar_balance(self):
        """Consulta balance disponible (EUR)"""
        try:
            if not self.account or not self.password:
                logger.error("Credenciales TraffiLink no configuradas")
                return {'exito': False, 'error': 'Credenciales no configuradas'}

            # Endpoint correcto según PDF v3.4: /getbalance
            url = f"{self.url_base}/getbalance"
            data = {'account': self.account, 'password': self.password}

            logger.info(f"Consultando balance en {url} con account {self.account}")
            response = requests.get(url, params=data, timeout=self.timeout)
            logger.info(f"Status: {response.status_code}")

            resultado = response.json()

            # Según PDF: status 0 = query success
            if resultado.get('status') == 0:
                balance = float(resultado.get('balance', 0))
                logger.info(f"Balance obtenido: {balance} EUR")
                return {'exito': True, 'balance': balance}
            else:
                error = resultado.get('message', f'Error status: {resultado.get("status")}')
                logger.warning(f"Error TraffiLink: {error}")
                return {'exito': False, 'error': error}

        except requests.exceptions.Timeout:
            logger.error("Timeout en TraffiLink")
            return {'exito': False, 'error': 'Timeout - TraffiLink no responde'}

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error conexion: {e}")
            return {'exito': False, 'error': f"Error conexion: {str(e)}"}

        except ValueError as e:
            logger.error(f"JSON invalido: {e}")
            return {'exito': False, 'error': 'Respuesta invalida de TraffiLink'}

        except Exception as e:
            logger.error(f"Error inesperado: {e}", exc_info=True)
            return {'exito': False, 'error': str(e)}
    
    def enviar_sms(self, numero, contenido, queue_id):
        """Envía SMS a través de TraffiLink (Endpoint: /sendsms según PDF v3.4)"""
        try:
            if not numero or not contenido:
                return {'exito': False, 'error': 'Número o contenido vacío'}

            # Asegurar prefijo internacional
            if not numero.startswith('57'):
                numero = '57' + numero

            logger.info(f"📤 Enviando SMS a {numero}...")

            # Endpoint correcto según PDF v3.4: /sendsms
            url = f"{self.url_base}/sendsms"

            # Parámetros según PDF v3.4
            data = {
                'account': self.account,
                'password': self.password,
                'smstype': '0',           # 0 = SMS normal
                'numbers': numero,         # Número del destinatario
                'content': contenido,      # Contenido del SMS
                'sender': 'Goleador'       # ID del remitente
            }

            # Usar POST según especificación del PDF
            response = requests.post(url, data=data, timeout=self.timeout)
            logger.info(f"Respuesta status: {response.status_code}")

            resultado = response.json()
            logger.info(f"Respuesta JSON: {resultado}")

            # Según PDF: status 0 = success
            if resultado.get('status') == 0:
                traffilink_id = resultado.get('id')
                logger.info(f"✅ SMS enviado. ID: {traffilink_id}")
                return {
                    'exito': True,
                    'traffilink_id': traffilink_id,
                    'numero': numero
                }
            else:
                error = resultado.get('message', f'Error status: {resultado.get("status")}')
                logger.error(f"❌ TraffiLink error: {error}")
                return {'exito': False, 'error': error}

        except Exception as e:
            logger.error(f"❌ Error enviando SMS: {e}", exc_info=True)
            return {'exito': False, 'error': str(e)}
    
    def consultar_estado(self, traffilink_id):
        """Consulta estado de entrega (Endpoint: /getreport según PDF v3.4)"""
        try:
            # Endpoint correcto según PDF v3.4: /getreport
            url = f"{self.url_base}/getreport"

            # Parámetros según PDF v3.4
            data = {
                'account': self.account,
                'password': self.password,
                'ids': str(traffilink_id)  # ID del SMS a consultar
            }

            response = requests.get(url, params=data, timeout=self.timeout)
            logger.info(f"Consultando estado de {traffilink_id}")
            resultado = response.json()

            # Mapeo de estados según PDF v3.4
            estado_map = {
                '0': 'delivered',    # Success
                '1': 'pending',      # Pending
                '2': 'failed',       # Failed
                '3': 'invalid',      # Invalid
                '4': 'expired'       # Expired
            }

            # Según PDF: status 0 = success
            if resultado.get('status') == 0:
                estado_codigo = str(resultado.get('deliverystatus', '1'))
                estado = estado_map.get(estado_codigo, 'unknown')
                logger.info(f"✅ Estado: {estado}")
                return {'exito': True, 'estado': estado}
            else:
                error = resultado.get('message', f'Error status: {resultado.get("status")}')
                logger.warning(f"⚠️ Error consultando estado: {error}")
                return {'exito': False, 'error': error}

        except Exception as e:
            logger.error(f"❌ Error consultando estado: {e}")
            return {'exito': False, 'error': str(e)}
    
    def procesar_webhook(self, datos):
        """Procesa webhook de TraffiLink"""
        try:
            if not datos:
                return {'exito': False, 'error': 'Datos vacíos'}
            
            traffilink_id = datos.get('id')
            estado_codigo = datos.get('deliverystatus')
            
            if not traffilink_id or estado_codigo is None:
                return {'exito': False, 'error': 'Datos incompletos'}
            
            estado_map = {
                '1': 'delivered',
                '2': 'failed',
                '3': 'pending',
                '4': 'invalid'
            }
            
            estado = estado_map.get(str(estado_codigo), 'unknown')
            logger.info(f"📬 Webhook: {traffilink_id} → {estado}")
            
            return {
                'exito': True,
                'traffilink_id': traffilink_id,
                'estado': estado
            }
        
        except Exception as e:
            logger.error(f"❌ Error procesando webhook: {e}")
            return {'exito': False, 'error': str(e)}

# Instancia global
traffilink = TraffiLinkAPI()

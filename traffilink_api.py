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
            params = f"account={self.account}"
            sign = self.generar_sign(params)
            
            url = f"{self.url_base}/queryBalance"
            data = {'account': self.account, 'sign': sign}
            
            logger.info("🔍 Consultando balance TraffiLink...")
            response = requests.get(url, params=data, timeout=self.timeout)
            resultado = response.json()
            
            if resultado.get('status') == '1':
                balance = float(resultado.get('balance', 0))
                logger.info(f"✅ Balance: {balance} EUR")
                return {'exito': True, 'balance': balance}
            else:
                error = resultado.get('message', 'Error desconocido')
                logger.warning(f"❌ Error: {error}")
                return {'exito': False, 'error': error}
        
        except Exception as e:
            logger.error(f"❌ Error consultando balance: {e}")
            return {'exito': False, 'error': str(e)}
    
    def enviar_sms(self, numero, contenido, queue_id):
        """Envía SMS a través de TraffiLink"""
        try:
            if not numero or not contenido:
                return {'exito': False, 'error': 'Número o contenido vacío'}
            
            # Asegurar prefijo internacional
            if not numero.startswith('57'):
                numero = '57' + numero
            
            logger.info(f"📤 Enviando SMS a {numero}...")
            
            # Construir parámetros y firma
            params_para_firma = f"account={self.account}&sendid={queue_id}&mobile={numero}&content={contenido}"
            sign = self.generar_sign(params_para_firma)
            
            if not sign:
                return {'exito': False, 'error': 'Error generando firma'}
            
            url = f"{self.url_base}/sendsmsV2"
            data = {
                'account': self.account,
                'sendid': queue_id,
                'mobile': numero,
                'content': contenido,
                'sign': sign
            }
            
            response = requests.post(url, data=data, timeout=self.timeout)
            resultado = response.json()
            
            if resultado.get('status') == '1':
                traffilink_id = resultado.get('id')
                logger.info(f"✅ SMS enviado. ID: {traffilink_id}")
                return {
                    'exito': True,
                    'traffilink_id': traffilink_id,
                    'numero': numero
                }
            else:
                error = resultado.get('message', 'Error desconocido')
                logger.error(f"❌ TraffiLink error: {error}")
                return {'exito': False, 'error': error}
        
        except Exception as e:
            logger.error(f"❌ Error enviando SMS: {e}")
            return {'exito': False, 'error': str(e)}
    
    def consultar_estado(self, traffilink_id):
        """Consulta estado de entrega"""
        try:
            params = f"account={self.account}&id={traffilink_id}"
            sign = self.generar_sign(params)
            
            url = f"{self.url_base}/queryReport"
            data = {'account': self.account, 'id': traffilink_id, 'sign': sign}
            
            response = requests.get(url, params=data, timeout=self.timeout)
            resultado = response.json()
            
            estado_map = {
                '1': 'delivered',
                '2': 'failed',
                '3': 'pending',
                '4': 'invalid'
            }
            
            if resultado.get('status') == '1':
                estado = estado_map.get(resultado.get('deliverystatus'), 'unknown')
                logger.info(f"✅ Estado: {estado}")
                return {'exito': True, 'estado': estado}
            else:
                error = resultado.get('message', 'Error')
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

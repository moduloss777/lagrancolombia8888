"""
Cliente de API para Traffilink HTTP API v3.4
Maneja autenticación, envío de SMS, reportes y gestión de tareas
"""
import requests
import json
import logging
from typing import Optional, List, Dict, Union
from urllib.parse import urlencode
from config import (
    TRAFFILINK_BASE_URL,
    TRAFFILINK_ACCOUNT,
    TRAFFILINK_PASSWORD,
    SMS_LIMIT_GET,
    SMS_LIMIT_POST,
    REPORT_BATCH_LIMIT,
    INCOMING_SMS_LIMIT,
    MAX_MESSAGE_LENGTH,
    ENCODING,
    CONTENT_TYPE,
    ERROR_CODES,
    TASK_TYPES,
    LOG_FILE,
    LOG_LEVEL
)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TrafficLinkAPI:
    """Cliente principal para interactuar con Traffilink API"""

    def __init__(self, account: str = None, password: str = None, base_url: str = None):
        """
        Inicializar cliente de Traffilink

        Args:
            account: Cuenta de Traffilink (usa .env si no se proporciona)
            password: Contraseña HTTP de Traffilink (usa .env si no se proporciona)
            base_url: URL base de la API (usa config si no se proporciona)
        """
        self.account = account or TRAFFILINK_ACCOUNT
        self.password = password or TRAFFILINK_PASSWORD
        self.base_url = base_url or TRAFFILINK_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': CONTENT_TYPE,
        })

        logger.info(f"TrafficLink API inicializado - Account: {self.account}")

    def _validate_credentials(self) -> bool:
        """Validar que las credenciales estén configuradas"""
        if not self.account or not self.password:
            logger.error("❌ Credenciales no configuradas en .env")
            return False
        return True

    def _parse_response(self, response: requests.Response) -> Dict:
        """
        Parsear respuesta JSON y manejar errores

        Args:
            response: Respuesta de requests

        Returns:
            Dict con datos parseados o error
        """
        try:
            # Log detallado para debugging (VISIBLE EN RENDER.COM)
            logger.info(f"📥 Status Code: {response.status_code}")
            logger.info(f"📥 Response Text: {response.text[:500]}")  # Primeros 500 caracteres

            data = response.json()

            # Verificar si hay código de error
            if isinstance(data, dict) and 'code' in data:
                code = data['code']
                error_msg = ERROR_CODES.get(code, f"Error desconocido: {code}")

                if code != 0:
                    logger.warning(f"⚠️ API Error ({code}): {error_msg}")
                    logger.warning(f"📋 Respuesta completa: {data}")
                    data['error_message'] = error_msg
                else:
                    logger.info(f"✅ Respuesta exitosa")

            return data
        except json.JSONDecodeError:
            logger.error(f"Error decodificando JSON: {response.text}")
            return {"code": -4, "error_message": "Error en formato JSON"}

    def get_balance(self) -> Dict:
        """
        Obtener balance de cuenta

        Returns:
            Dict con {code, balance, gift_balance} o error
        """
        if not self._validate_credentials():
            return {"code": -1, "error_message": ERROR_CODES[-1]}

        params = {
            "account": self.account,
            "password": self.password
        }

        try:
            logger.info("📊 Consultando balance de cuenta...")
            url = f"{self.base_url}/getbalance"
            logger.info(f"📡 URL: {url}")
            logger.info(f"🔐 Account: {self.account}")

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = self._parse_response(response)

            if data.get('code') == 0:
                logger.info(
                    f"✅ Balance obtenido - "
                    f"Saldo: {data.get('balance')}, "
                    f"Saldo regalo: {data.get('gift_balance')}"
                )

            return data

        except requests.exceptions.Timeout:
            logger.error(f"❌ TIMEOUT: El servidor no respondió en 10 segundos. Verifica conectividad a {self.base_url}")
            return {"code": -98, "error_message": "Timeout de conexión"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ ERROR DE CONEXIÓN: No se puede conectar a {self.base_url}")
            logger.error(f"   Detalle: {str(e)}")
            logger.error(f"   Posibles causas:")
            logger.error(f"   - IP/puerto incorrectos")
            logger.error(f"   - Servidor no está disponible")
            logger.error(f"   - Firewall bloqueando conexión")
            logger.error(f"   - Render.com no tiene acceso a esa red")
            return {"code": -97, "error_message": f"No se puede conectar: {str(e)}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión: {str(e)}")
            return {"code": -99, "error_message": f"Error de conexión: {str(e)}"}

    def send_sms(
        self,
        numbers: Union[str, List[str]],
        content: str,
        sender: Optional[str] = None,
        sendtime: Optional[str] = None,
        use_post: bool = False
    ) -> Dict:
        """
        Enviar SMS

        Args:
            numbers: Número(s) de teléfono (string o lista)
            content: Contenido del mensaje (máx 1024 caracteres)
            sender: Remitente opcional
            sendtime: Tiempo de envío (formato: 20171001123015)
            use_post: Usar POST en lugar de GET (para >100 números)

        Returns:
            Dict con código de respuesta e ID de SMS
        """
        if not self._validate_credentials():
            return {"code": -1, "error_message": ERROR_CODES[-1]}

        # Validaciones
        if isinstance(numbers, list):
            numbers_str = ",".join(str(n) for n in numbers)
        else:
            numbers_str = str(numbers)

        if not numbers_str:
            logger.error("❌ Parámetro 'numbers' vacío")
            return {"code": -2, "error_message": ERROR_CODES[-2]}

        if not content:
            logger.error("❌ Parámetro 'content' vacío")
            return {"code": -6, "error_message": ERROR_CODES[-6]}

        if len(content) > MAX_MESSAGE_LENGTH:
            logger.error(f"❌ Mensaje demasiado largo (máx {MAX_MESSAGE_LENGTH})")
            return {"code": -5, "error_message": ERROR_CODES[-5]}

        # Preparar parámetros
        params = {
            "account": self.account,
            "password": self.password,
            "numbers": numbers_str,
            "content": content
        }

        if sender:
            params["sender"] = sender
        if sendtime:
            params["sendtime"] = sendtime

        try:
            url = f"{self.base_url}/sendsms"

            if use_post or len(numbers_str.split(",")) > SMS_LIMIT_GET:
                # Usar POST para más de 100 números
                logger.info(f"📤 Enviando SMS vía POST a {len(numbers_str.split(','))} números...")
                response = self.session.post(url, json=params, timeout=30)
            else:
                # Usar GET para ≤ 100 números
                logger.info(f"📤 Enviando SMS vía GET a {len(numbers_str.split(','))} números...")
                response = self.session.get(url, params=params, timeout=10)

            response.raise_for_status()
            data = self._parse_response(response)

            if data.get('code') == 0:
                logger.info(f"✅ SMS enviados exitosamente - ID: {data.get('id')}")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error enviando SMS: {str(e)}")
            return {"code": -99, "error_message": f"Error de conexión: {str(e)}"}

    def send_sms_batch(
        self,
        numbers: List[str],
        content: str,
        sender: Optional[str] = None,
        sendtime: Optional[str] = None,
        batch_size: int = 10000
    ) -> List[Dict]:
        """
        Enviar SMS en lotes (para volúmenes muy grandes)

        Args:
            numbers: Lista de números de teléfono
            content: Contenido del mensaje
            sender: Remitente opcional
            sendtime: Tiempo de envío
            batch_size: Tamaño de cada lote (máx 10000)

        Returns:
            Lista de respuestas por lote
        """
        if not numbers:
            logger.error("❌ Lista de números vacía")
            return [{"code": -2, "error_message": ERROR_CODES[-2]}]

        results = []
        total_numbers = len(numbers)

        logger.info(f"📦 Dividiendo {total_numbers} números en lotes de {batch_size}...")

        for i in range(0, total_numbers, batch_size):
            batch = numbers[i:i + batch_size]
            lote_num = (i // batch_size) + 1

            logger.info(f"🔄 Procesando lote {lote_num} ({len(batch)} números)...")

            result = self.send_sms(
                numbers=batch,
                content=content,
                sender=sender,
                sendtime=sendtime,
                use_post=True
            )

            results.append({
                "lote": lote_num,
                "numeros_enviados": len(batch),
                "respuesta": result
            })

        logger.info(f"✅ Completados {len(results)} lotes")
        return results

    def get_report(self, ids: Union[str, List[str]]) -> Dict:
        """
        Obtener reporte de SMS enviados

        Args:
            ids: ID(s) de SMS a consultar (máx 200 por solicitud)

        Returns:
            Dict con detalles de entrega
        """
        if not self._validate_credentials():
            return {"code": -1, "error_message": ERROR_CODES[-1]}

        # Convertir a string separado por comas
        if isinstance(ids, list):
            ids_str = ",".join(str(id_) for id_ in ids)
        else:
            ids_str = str(ids)

        params = {
            "account": self.account,
            "password": self.password,
            "id": ids_str
        }

        try:
            logger.info(f"📋 Consultando reporte para IDs: {ids_str[:50]}...")
            url = f"{self.base_url}/getreport"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = self._parse_response(response)
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error obteniendo reporte: {str(e)}")
            return {"code": -99, "error_message": f"Error de conexión: {str(e)}"}

    def get_incoming_sms(self, limit: int = INCOMING_SMS_LIMIT) -> Dict:
        """
        Obtener SMS entrantes

        Args:
            limit: Cantidad máxima (máx 50)

        Returns:
            Dict con SMS recibidos
        """
        if not self._validate_credentials():
            return {"code": -1, "error_message": ERROR_CODES[-1]}

        limit = min(limit, INCOMING_SMS_LIMIT)

        params = {
            "account": self.account,
            "password": self.password,
            "limit": limit
        }

        try:
            logger.info(f"📨 Obteniendo SMS entrantes (límite: {limit})...")
            url = f"{self.base_url}/getsms"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = self._parse_response(response)
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error obteniendo SMS: {str(e)}")
            return {"code": -99, "error_message": f"Error de conexión: {str(e)}"}

    def create_sms_task(
        self,
        task_type: int,
        numbers: Union[str, List[str]],
        content: str,
        sendtime: Optional[str] = None,
        sender: Optional[str] = None,
        interval: Optional[int] = None,
        end_time: Optional[str] = None
    ) -> Dict:
        """
        Crear tarea de envío programado

        Args:
            task_type: Tipo de tarea (0=inmediata, 1=programada, 2=intervalo, etc.)
            numbers: Número(s) de teléfono
            content: Contenido del mensaje
            sendtime: Hora de envío (formato: 20171001123015)
            sender: Remitente opcional
            interval: Intervalo en horas (para task_type=2)
            end_time: Hora de finalización (formato: 20171001123015)

        Returns:
            Dict con respuesta de creación de tarea
        """
        if not self._validate_credentials():
            return {"code": -1, "error_message": ERROR_CODES[-1]}

        # Convertir números a string
        if isinstance(numbers, list):
            numbers_str = ",".join(str(n) for n in numbers)
        else:
            numbers_str = str(numbers)

        task_type_name = TASK_TYPES.get(task_type, "Desconocido")
        logger.info(f"⏰ Creando tarea de tipo: {task_type_name}")

        payload = {
            "account": self.account,
            "password": self.password,
            "jobtype": task_type,
            "contacts": numbers_str,
            "content": content
        }

        if sendtime:
            payload["sendtime"] = sendtime
        if sender:
            payload["sender"] = sender
        if interval:
            payload["interval"] = interval
        if end_time:
            payload["endtime"] = end_time

        try:
            url = f"{self.base_url}/smsjob"
            logger.info(f"📝 Enviando solicitud de tarea a {url}...")
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = self._parse_response(response)
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error creando tarea: {str(e)}")
            return {"code": -99, "error_message": f"Error de conexión: {str(e)}"}


def test_connection():
    """Función para probar la conexión"""
    print("\n" + "="*60)
    print("🧪 PRUEBA DE CONEXIÓN A TRAFFILINK API")
    print("="*60 + "\n")

    api = TrafficLinkAPI()

    # Test 1: Balance
    print("1️⃣  Obteniendo balance...")
    balance = api.get_balance()
    print(f"Respuesta: {json.dumps(balance, indent=2, ensure_ascii=False)}\n")

    print("="*60)
    print("✅ Conexión completada")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_connection()

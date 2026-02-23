"""
SMS Marketing API - Flask Application
Optimizado para Render
"""

import logging
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify

from config import config
from database import db
from traffilink_api import traffilink

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ============================================================================
# RUTAS - HEALTH & STATS
# ============================================================================

@app.route('/')
def index():
    """Dashboard principal"""
    try:
        stats = db.obtener_stats()
        return render_template('index.html', stats=stats)
    except Exception as e:
        logger.error(f"Error en index: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """Health check"""
    try:
        stats = db.obtener_stats()
        balance = traffilink.consultar_balance()

        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'balance': balance.get('balance') if balance.get('exito') else 'N/A'
        }), 200
    except Exception as e:
        logger.error(f"Error en health: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Obtener estadísticas"""
    try:
        stats = db.obtener_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error en stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/balance')
def get_balance():
    """Obtener balance de TraffiLink"""
    try:
        resultado = traffilink.consultar_balance()

        if resultado.get('exito'):
            return jsonify({
                'balance': resultado.get('balance'),
                'moneda': 'EUR',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({'error': resultado.get('error')}), 400

    except Exception as e:
        logger.error(f"Error consultando balance: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# RUTAS - SMS OPERATIONS
# ============================================================================

@app.route('/api/sms/send', methods=['POST'])
def send_sms():
    """Enviar un SMS individual"""
    try:
        data = request.get_json()

        numero = data.get('numero', '').strip()
        contenido = data.get('mensaje', '').strip()

        # Validar
        if not numero:
            return jsonify({'error': 'Numero requerido'}), 400
        if not contenido:
            return jsonify({'error': 'Mensaje requerido'}), 400

        # Agregar a DB
        sms_id = db.agregar_sms(numero, contenido)
        if not sms_id:
            return jsonify({'error': 'SMS duplicado recientemente'}), 409

        # Enviar a TraffiLink
        resultado = traffilink.enviar_sms(numero, contenido, str(sms_id))

        if resultado.get('exito'):
            db.actualizar_sms(
                sms_id,
                status='sent',
                traffilink_id=resultado.get('traffilink_id')
            )

            return jsonify({
                'exito': True,
                'sms_id': sms_id,
                'traffilink_id': resultado.get('traffilink_id'),
                'numero': numero,
                'status': 'sent'
            }), 200
        else:
            db.actualizar_sms(
                sms_id,
                status='failed',
                error_msg=resultado.get('error')
            )

            return jsonify({
                'exito': False,
                'sms_id': sms_id,
                'error': resultado.get('error')
            }), 400

    except Exception as e:
        logger.error(f"Error enviando SMS: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/send-batch', methods=['POST'])
def send_batch():
    """Enviar multiplesms SMS"""
    try:
        data = request.get_json()
        sms_list = data.get('sms', [])

        if not sms_list:
            return jsonify({'error': 'Lista de SMS vacia'}), 400

        if len(sms_list) > 100:
            return jsonify({'error': 'Maximo 100 SMS por batch'}), 400

        resultados = []

        for sms in sms_list:
            numero = sms.get('numero', '').strip()
            contenido = sms.get('mensaje', '').strip()

            if not numero or not contenido:
                resultados.append({'error': 'Numero o mensaje vacio'})
                continue

            # Agregar a DB
            sms_id = db.agregar_sms(numero, contenido)
            if not sms_id:
                resultados.append({
                    'numero': numero,
                    'error': 'SMS duplicado'
                })
                continue

            # Enviar
            resultado = traffilink.enviar_sms(numero, contenido, str(sms_id))

            if resultado.get('exito'):
                db.actualizar_sms(
                    sms_id,
                    status='sent',
                    traffilink_id=resultado.get('traffilink_id')
                )
                resultados.append({
                    'sms_id': sms_id,
                    'numero': numero,
                    'status': 'sent',
                    'traffilink_id': resultado.get('traffilink_id')
                })
            else:
                db.actualizar_sms(
                    sms_id,
                    status='failed',
                    error_msg=resultado.get('error')
                )
                resultados.append({
                    'sms_id': sms_id,
                    'numero': numero,
                    'status': 'failed',
                    'error': resultado.get('error')
                })

        return jsonify({
            'total': len(sms_list),
            'resultados': resultados
        }), 200

    except Exception as e:
        logger.error(f"Error en batch: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/status/<int:sms_id>')
def get_sms_status(sms_id):
    """Consultar estado de un SMS"""
    try:
        sms = db.obtener_sms(sms_id)

        if not sms:
            return jsonify({'error': 'SMS no encontrado'}), 404

        # Si esta en pending y tenemos traffilink_id, consultar estado
        if sms['status'] == 'sent' and sms['traffilink_id']:
            resultado = traffilink.consultar_estado(sms['traffilink_id'])

            if resultado.get('exito'):
                nuevo_estado = resultado.get('estado')
                if nuevo_estado != 'pending':
                    db.actualizar_sms(sms_id, status=nuevo_estado)
                    sms['status'] = nuevo_estado

        return jsonify({
            'id': sms['id'],
            'numero': sms['numero'],
            'contenido': sms['contenido'],
            'status': sms['status'],
            'traffilink_id': sms['traffilink_id'],
            'error': sms['error_msg'],
            'created_at': sms['created_at'],
            'updated_at': sms['updated_at']
        }), 200

    except Exception as e:
        logger.error(f"Error consultando estado: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# RUTAS - WEBHOOKS
# ============================================================================

@app.route('/webhook/traffilink', methods=['POST'])
def webhook_traffilink():
    """Webhook para reportes de TraffiLink"""
    try:
        datos = request.get_json()

        if not datos:
            return jsonify({'error': 'No data'}), 400

        resultado = traffilink.procesar_webhook(datos)

        if resultado.get('exito'):
            traffilink_id = resultado.get('traffilink_id')
            estado = resultado.get('estado')

            logger.info(f"Webhook procesado: {traffilink_id} -> {estado}")

            return jsonify({
                'status': 'ok',
                'message': 'Report received',
                'traffilink_id': traffilink_id,
                'estado': estado
            }), 200
        else:
            return jsonify({'error': resultado.get('error')}), 400

    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = config.PORT
    debug = config.DEBUG

    logger.info(f"SMS Marketing API iniciando...")
    logger.info(f"Base de datos: {config.DATABASE_URL}")
    logger.info(f"TraffiLink: {config.TRAFFILINK_URL}")
    logger.info(f"Debug: {debug}")
    logger.info(f"Puerto: {port}")

    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)

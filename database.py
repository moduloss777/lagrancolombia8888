"""
Gestor de base de datos SQLite simplificado
"""

import sqlite3
import json
import logging
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor centralizado de base de datos"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_URL
        self.init_db()
    
    def get_connection(self):
        """Obtener conexión a BD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Inicializa las tablas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabla: SMS
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT NOT NULL,
                    contenido TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    traffilink_id TEXT,
                    error_msg TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Tabla: Stats
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_sent INTEGER DEFAULT 0,
                    total_delivered INTEGER DEFAULT 0,
                    total_failed INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sms_status ON sms(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sms_numero ON sms(numero)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sms_created ON sms(created_at)')
            
            # Insertar fila inicial en stats si no existe
            cursor.execute('SELECT COUNT(*) as count FROM stats')
            if cursor.fetchone()['count'] == 0:
                cursor.execute('INSERT INTO stats (total_sent, total_delivered, total_failed) VALUES (0, 0, 0)')
            
            conn.commit()
            logger.info(f"✅ Base de datos inicializada: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando BD: {e}")
        finally:
            conn.close()
    
    def agregar_sms(self, numero, contenido, metadata=None):
        """Agregar SMS a la cola"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sms (numero, contenido, metadata)
                VALUES (?, ?, ?)
            ''', (numero, contenido, json.dumps(metadata or {})))
            
            sms_id = cursor.lastrowid
            conn.commit()
            logger.info(f"✅ SMS agregado: {sms_id} → {numero}")
            return sms_id
            
        except Exception as e:
            logger.error(f"❌ Error agregando SMS: {e}")
            return None
        finally:
            conn.close()
    
    def actualizar_sms(self, sms_id, status=None, traffilink_id=None, error_msg=None):
        """Actualizar estado de SMS"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = ['updated_at = CURRENT_TIMESTAMP']
            params = []
            
            if status:
                updates.append('status = ?')
                params.append(status)
            if traffilink_id:
                updates.append('traffilink_id = ?')
                params.append(traffilink_id)
            if error_msg:
                updates.append('error_msg = ?')
                params.append(error_msg)
            
            params.append(sms_id)
            
            query = f'UPDATE sms SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            
            # Actualizar stats
            if status == 'delivered':
                cursor.execute('UPDATE stats SET total_delivered = total_delivered + 1, updated_at = CURRENT_TIMESTAMP')
            elif status == 'failed':
                cursor.execute('UPDATE stats SET total_failed = total_failed + 1, updated_at = CURRENT_TIMESTAMP')
            elif status == 'sent':
                cursor.execute('UPDATE stats SET total_sent = total_sent + 1, updated_at = CURRENT_TIMESTAMP')
            
            conn.commit()
            logger.info(f"✅ SMS actualizado: {sms_id} → {status}")
            
        except Exception as e:
            logger.error(f"❌ Error actualizando SMS: {e}")
        finally:
            conn.close()
    
    def obtener_sms(self, sms_id):
        """Obtener SMS por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM sms WHERE id = ?', (sms_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def obtener_pendientes(self, limit=10):
        """Obtener SMS pendientes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM sms WHERE status = ? LIMIT ?', ('pending', limit))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def obtener_stats(self):
        """Obtener estadísticas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM stats LIMIT 1')
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def obtener_sms_por_numero(self, numero):
        """Obtener último SMS de un número"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM sms WHERE numero = ? ORDER BY created_at DESC LIMIT 1', (numero,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

# Instancia global
db = DatabaseManager()

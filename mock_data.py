"""
Mock Data Provider - Datos simulados para testing/demo
Usado cuando Traffilink API no está disponible
"""
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)

class MockDataProvider:
    """Proporciona datos simulados para la aplicación"""

    @staticmethod
    def get_balance():
        """Retornar balance simulado"""
        logger.info("📦 [MOCK] Retornando balance simulado")
        return {
            "code": 0,
            "balance": round(random.uniform(1000, 10000), 2),
            "gift_balance": round(random.uniform(100, 500), 2),
            "currency": "COP",
            "mock": True
        }

    @staticmethod
    def get_sms_stats():
        """Retornar estadísticas de SMS"""
        logger.info("📦 [MOCK] Retornando estadísticas de SMS")
        return {
            "total_sent": random.randint(100, 10000),
            "total_delivered": random.randint(50, 9000),
            "total_failed": random.randint(0, 100),
            "success_rate": round(random.uniform(0.85, 0.99), 2),
            "mock": True
        }

    @staticmethod
    def get_hourly_distribution():
        """Retornar distribución por hora"""
        logger.info("📦 [MOCK] Retornando distribución horaria")
        return {
            "hours": [f"{i:02d}:00" for i in range(24)],
            "counts": [random.randint(10, 100) for _ in range(24)],
            "mock": True
        }

    @staticmethod
    def get_kpis():
        """Retornar KPIs principales"""
        logger.info("📦 [MOCK] Retornando KPIs")
        return {
            "total_sms": random.randint(1000, 100000),
            "today_sms": random.randint(100, 5000),
            "success_rate": round(random.uniform(0.85, 0.99), 2),
            "avg_delivery_time": round(random.uniform(0.5, 5), 1),
            "total_balance": round(random.uniform(1000, 50000), 2),
            "mock": True
        }

    @staticmethod
    def get_insights():
        """Retornar insights automáticos"""
        logger.info("📦 [MOCK] Retornando insights")
        insights_list = [
            "📈 Tendencia ascendente en envíos (↑15%)",
            "⚡ Hora pico: 14:00 - 16:00",
            "✅ Tasa de éxito por encima del promedio",
            "💡 Considera campañas en horario matutino",
            "🎯 Operador preferido: Movilcom",
            "⏱️ Tiempo promedio de entrega: 2.3s",
        ]
        return {
            "insights": random.sample(insights_list, 3),
            "mock": True
        }

    @staticmethod
    def get_activity_summary():
        """Retornar resumen de actividad"""
        logger.info("📦 [MOCK] Retornando resumen de actividad")
        return {
            "summary": {
                "today": {
                    "sent": random.randint(100, 1000),
                    "delivered": random.randint(80, 950),
                    "failed": random.randint(0, 50),
                },
                "week": {
                    "sent": random.randint(1000, 10000),
                    "delivered": random.randint(800, 9500),
                    "failed": random.randint(0, 500),
                },
                "month": {
                    "sent": random.randint(5000, 50000),
                    "delivered": random.randint(4000, 47500),
                    "failed": random.randint(0, 2500),
                }
            },
            "mock": True
        }

    @staticmethod
    def get_sms_history():
        """Retornar historial de SMS"""
        logger.info("📦 [MOCK] Retornando historial de SMS")
        statuses = ["delivered", "failed", "sent", "pending"]
        history = []
        for i in range(20):
            history.append({
                "id": f"sms_{i}",
                "number": f"300{random.randint(1000000, 9999999)}",
                "content": f"Mensaje de prueba {i}",
                "status": random.choice(statuses),
                "date": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
                "cost": round(random.uniform(0.05, 0.5), 2)
            })
        return {
            "sms_list": history,
            "total": len(history),
            "mock": True
        }

    @staticmethod
    def get_reports(report_type="sms"):
        """Retornar reportes simulados"""
        logger.info(f"📦 [MOCK] Retornando reporte: {report_type}")

        if report_type == "sms":
            rows = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                rows.append({
                    "fecha": date,
                    "enviados": random.randint(100, 1000),
                    "entregados": random.randint(80, 950),
                    "fallidos": random.randint(0, 50),
                })
        elif report_type == "delivery":
            rows = []
            for i in range(20):
                rows.append({
                    "numero": f"300{random.randint(1000000, 9999999)}",
                    "estado": random.choice(["entregado", "fallido", "pendiente"]),
                    "fecha": (datetime.now() - timedelta(hours=random.randint(0, 48))).isoformat(),
                })
        elif report_type == "transactions":
            rows = []
            for i in range(10):
                rows.append({
                    "fecha": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                    "tipo": random.choice(["compra", "gasto", "reembolso"]),
                    "monto": round(random.uniform(50, 5000), 2),
                    "saldo": round(random.uniform(1000, 50000), 2),
                })
        else:
            rows = []

        return {
            "rows": rows,
            "type": report_type,
            "mock": True
        }

    @staticmethod
    def send_sms_mock(numbers, content):
        """Simular envío de SMS"""
        logger.info(f"📦 [MOCK] Simulando envío de SMS a {len(numbers)} números")
        successful = int(len(numbers) * random.uniform(0.8, 1.0))
        failed = len(numbers) - successful

        return {
            "code": 0,
            "sent_count": successful,
            "failed_count": failed,
            "balance_remaining": round(random.uniform(1000, 50000), 2),
            "message_id": f"mock_msg_{datetime.now().timestamp()}",
            "mock": True
        }

    @staticmethod
    def get_tasks():
        """Retornar lista de tareas simuladas"""
        logger.info("📦 [MOCK] Retornando tareas simuladas")
        tasks = []
        task_types = ["Inmediata", "Programada", "Intervalo", "Diaria", "Semanal", "Mensual"]
        statuses = ["active", "paused", "completed"]

        for i in range(5):
            tasks.append({
                "id": f"task_{i}",
                "type": random.choice(task_types),
                "type_name": random.choice(task_types),
                "status": random.choice(statuses),
                "contacts_count": random.randint(10, 1000),
                "executed": random.randint(0, 100),
                "next_execution": (datetime.now() + timedelta(hours=random.randint(1, 48))).isoformat(),
            })

        return {
            "tasks": tasks,
            "total": len(tasks),
            "active": sum(1 for t in tasks if t["status"] == "active"),
            "paused": sum(1 for t in tasks if t["status"] == "paused"),
            "mock": True
        }

# Singleton instance
mock_provider = MockDataProvider()

if __name__ == "__main__":
    print("🧪 Testing Mock Data Provider")
    print("\n✅ Balance:", mock_provider.get_balance())
    print("✅ Stats:", mock_provider.get_sms_stats())
    print("✅ Insights:", mock_provider.get_insights())

from database.mysql_db import get_stats, get_all_applications
from backend.utils.logger import get_logger
log = get_logger('analytics')


class AnalyticsService:
    def get_stats(self) -> dict:
        return get_stats()

    def agent_pipeline_status(self) -> list:
        from database.mysql_db import get_connection
        conn = get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT agent_name, status, message, started_at, finished_at
                FROM agent_log
                ORDER BY started_at DESC
                LIMIT 20
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            from database.mysql_db import _serialize
            return [_serialize(r) for r in rows]
        except Exception as e:
            log.error(f"agent_pipeline_status error: {e}")
            return []

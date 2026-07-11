# models/emission_source_model.py
from models.database import get_db


class EmissionSourceDAO:
    """排放源数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, category_type, range_type, scenario_type, source_type,
                       activity_category, subcategory, source_name, unit, equipment, data_source
                FROM emission_sources
                ORDER BY id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(source_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, category_type, range_type, scenario_type, source_type,
                       activity_category, subcategory, source_name, unit, equipment, data_source
                FROM emission_sources
                WHERE id = ?
            ''', (source_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emission_sources 
                (category_type, range_type, scenario_type, source_type, activity_category,
                 subcategory, source_name, unit, equipment, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('category_type', '货运物流类别'),
                data.get('range_type', ''),
                data.get('scenario_type', ''),
                data.get('source_type', ''),
                data.get('activity_category', ''),
                data.get('subcategory', ''),
                data.get('source_name', ''),
                data.get('unit', ''),
                data.get('equipment', ''),
                data.get('data_source', '')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(source_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE emission_sources 
                SET category_type = ?, range_type = ?, scenario_type = ?, source_type = ?,
                    activity_category = ?, subcategory = ?, source_name = ?, unit = ?,
                    equipment = ?, data_source = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('category_type', '货运物流类别'),
                data.get('range_type', ''),
                data.get('scenario_type', ''),
                data.get('source_type', ''),
                data.get('activity_category', ''),
                data.get('subcategory', ''),
                data.get('source_name', ''),
                data.get('unit', ''),
                data.get('equipment', ''),
                data.get('data_source', ''),
                source_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(source_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM emission_sources WHERE id = ?', (source_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_batch(ids):
        if not ids:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f'DELETE FROM emission_sources WHERE id IN ({placeholders})', ids)
            conn.commit()
            return cursor.rowcount
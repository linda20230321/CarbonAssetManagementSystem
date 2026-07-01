# models/emission_factor_model.py
from models.database import get_db


class EmissionFactorDAO:
    """排放因子数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, factor_type, category, subcategory, unit, factor_value,
                       calorific_value, carbon_content, oxidation_rate, region,
                       coverage, product_type, data_source, effective_date, status
                FROM emission_factors
                ORDER BY id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(factor_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, factor_type, category, subcategory, unit, factor_value,
                       calorific_value, carbon_content, oxidation_rate, region,
                       coverage, product_type, data_source, effective_date, status
                FROM emission_factors
                WHERE id = ?
            ''', (factor_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO emission_factors 
                (factor_type, category, subcategory, unit, factor_value, calorific_value,
                 carbon_content, oxidation_rate, region, coverage, product_type,
                 data_source, effective_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('factor_type', ''),
                data.get('category', ''),
                data.get('subcategory', ''),
                data.get('unit', ''),
                data.get('factor_value', 0),
                data.get('calorific_value'),
                data.get('carbon_content'),
                data.get('oxidation_rate'),
                data.get('region'),
                data.get('coverage'),
                data.get('product_type'),
                data.get('data_source', ''),
                data.get('effective_date', ''),
                data.get('status', '启用')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(factor_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE emission_factors 
                SET factor_type = ?, category = ?, subcategory = ?, unit = ?,
                    factor_value = ?, calorific_value = ?, carbon_content = ?,
                    oxidation_rate = ?, region = ?, coverage = ?, product_type = ?,
                    data_source = ?, effective_date = ?, status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('factor_type', ''),
                data.get('category', ''),
                data.get('subcategory', ''),
                data.get('unit', ''),
                data.get('factor_value', 0),
                data.get('calorific_value'),
                data.get('carbon_content'),
                data.get('oxidation_rate'),
                data.get('region'),
                data.get('coverage'),
                data.get('product_type'),
                data.get('data_source', ''),
                data.get('effective_date', ''),
                data.get('status', '启用'),
                factor_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(factor_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM emission_factors WHERE id = ?', (factor_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_batch(ids):
        if not ids:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f'DELETE FROM emission_factors WHERE id IN ({placeholders})', ids)
            conn.commit()
            return cursor.rowcount
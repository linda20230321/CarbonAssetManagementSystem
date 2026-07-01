# models/organization_model.py
import json
from models.database import get_db


class OrganizationDAO:
    """运营组织数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_code, org_name, org_type, parent_id,
                       contact_person, contact_phone, contact_email, address, status
                FROM organizations
                ORDER BY id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_code, org_name, org_type, parent_id,
                       contact_person, contact_phone, contact_email, address, status
                FROM organizations
                WHERE id = ?
            ''', (org_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_children(parent_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_code, org_name, org_type, parent_id,
                       contact_person, contact_phone, contact_email, address, status
                FROM organizations
                WHERE parent_id = ?
                ORDER BY id
            ''', (parent_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO organizations 
                (org_code, org_name, org_type, parent_id, contact_person, 
                 contact_phone, contact_email, address, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('org_code', ''),
                data.get('org_name', ''),
                data.get('org_type', ''),
                data.get('parent_id'),
                data.get('contact_person', ''),
                data.get('contact_phone', ''),
                data.get('contact_email', ''),
                data.get('address', ''),
                data.get('status', '启用')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(org_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE organizations 
                SET org_code = ?, org_name = ?, org_type = ?, parent_id = ?,
                    contact_person = ?, contact_phone = ?, contact_email = ?,
                    address = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('org_code', ''),
                data.get('org_name', ''),
                data.get('org_type', ''),
                data.get('parent_id'),
                data.get('contact_person', ''),
                data.get('contact_phone', ''),
                data.get('contact_email', ''),
                data.get('address', ''),
                data.get('status', '启用'),
                org_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM organizations WHERE id = ?', (org_id,))
            conn.commit()
            return cursor.rowcount > 0


class SourceConfigDAO:
    """排放源配置数据访问对象"""

    @staticmethod
    def save(org_id, org_name, selections):
        with get_db() as conn:
            cursor = conn.cursor()
            # 先删除旧的配置
            cursor.execute('DELETE FROM source_configs WHERE org_id = ?', (org_id,))
            # 插入新的配置
            count = 0
            for key, value in selections.items():
                parts = key.split('_')
                source_id = int(parts[0]) if parts[0].isdigit() else 0
                source_name = parts[1] if len(parts) > 1 else ''
                cursor.execute('''
                    INSERT INTO source_configs (org_id, org_name, source_id, source_name, is_selected)
                    VALUES (?, ?, ?, ?, ?)
                ''', (org_id, org_name, source_id, source_name, 1 if value else 0))
                count += 1
            conn.commit()
            return count

    @staticmethod
    def get_by_org(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT source_id, source_name, is_selected 
                FROM source_configs 
                WHERE org_id = ?
            ''', (org_id,))
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                key = f"{row['source_id']}_{row['source_name']}"
                result[key] = bool(row['is_selected'])
            return result


class EnergyDataDAO:
    """能耗数据访问对象"""

    @staticmethod
    def save(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO energy_data 
                (org_id, org_name, period_type, period_year, period_month, 
                 period_quarter, period_start, period_end, data_json, total_emission)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('org_id'),
                data.get('org_name'),
                data.get('period_type', '月度'),
                data.get('period_year', 2024),
                data.get('period_month', 1),
                data.get('period_quarter'),
                data.get('period_start'),
                data.get('period_end'),
                json.dumps(data.get('details', [])),
                data.get('total', 0)
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_org(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_id, org_name, period_type, period_year, period_month,
                       period_quarter, period_start, period_end, data_json, total_emission,
                       created_at
                FROM energy_data 
                WHERE org_id = ?
                ORDER BY created_at DESC
            ''', (org_id,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                item = dict(row)
                try:
                    item['data_json'] = json.loads(item['data_json']) if item['data_json'] else []
                except:
                    item['data_json'] = []
                result.append(item)
            return result


class CalculationMethodDAO:
    """核算方法数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, method_name, emission_type, data_type, unit,
                       param_config, formula, is_referenced, is_enabled,
                       created_at, updated_at
                FROM calculation_methods
                ORDER BY id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(method_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, method_name, emission_type, data_type, unit,
                       param_config, formula, is_referenced, is_enabled
                FROM calculation_methods
                WHERE id = ?
            ''', (method_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO calculation_methods 
                (method_name, emission_type, data_type, unit, param_config, formula, is_referenced, is_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('method_name', ''),
                data.get('emission_type', '能源消耗'),
                data.get('data_type', '系统默认'),
                data.get('unit', 'kgCO2'),
                data.get('param_config', ''),
                data.get('formula', ''),
                data.get('is_referenced', 0),
                data.get('is_enabled', 1)
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(method_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE calculation_methods 
                SET method_name = ?, emission_type = ?, data_type = ?, unit = ?,
                    param_config = ?, formula = ?, is_referenced = ?, is_enabled = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('method_name', ''),
                data.get('emission_type', '能源消耗'),
                data.get('data_type', '系统默认'),
                data.get('unit', 'kgCO2'),
                data.get('param_config', ''),
                data.get('formula', ''),
                data.get('is_referenced', 0),
                data.get('is_enabled', 1),
                method_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(method_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM calculation_methods WHERE id = ?', (method_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_batch(ids):
        if not ids:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f'DELETE FROM calculation_methods WHERE id IN ({placeholders})', ids)
            conn.commit()
            return cursor.rowcount# models/organization_model.py
import json
from models.database import get_db


class OrganizationDAO:
    """运营组织数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_code, org_name, org_type, parent_id,
                       contact_person, contact_phone, contact_email, address, status
                FROM organizations
                ORDER BY id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_code, org_name, org_type, parent_id,
                       contact_person, contact_phone, contact_email, address, status
                FROM organizations
                WHERE id = ?
            ''', (org_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_children(parent_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_code, org_name, org_type, parent_id,
                       contact_person, contact_phone, contact_email, address, status
                FROM organizations
                WHERE parent_id = ?
                ORDER BY id
            ''', (parent_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO organizations 
                (org_code, org_name, org_type, parent_id, contact_person, 
                 contact_phone, contact_email, address, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('org_code', ''),
                data.get('org_name', ''),
                data.get('org_type', ''),
                data.get('parent_id'),
                data.get('contact_person', ''),
                data.get('contact_phone', ''),
                data.get('contact_email', ''),
                data.get('address', ''),
                data.get('status', '启用')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(org_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE organizations 
                SET org_code = ?, org_name = ?, org_type = ?, parent_id = ?,
                    contact_person = ?, contact_phone = ?, contact_email = ?,
                    address = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('org_code', ''),
                data.get('org_name', ''),
                data.get('org_type', ''),
                data.get('parent_id'),
                data.get('contact_person', ''),
                data.get('contact_phone', ''),
                data.get('contact_email', ''),
                data.get('address', ''),
                data.get('status', '启用'),
                org_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM organizations WHERE id = ?', (org_id,))
            conn.commit()
            return cursor.rowcount > 0


class SourceConfigDAO:
    """排放源配置数据访问对象"""

    @staticmethod
    def save(org_id, org_name, selections):
        with get_db() as conn:
            cursor = conn.cursor()
            # 先删除旧的配置
            cursor.execute('DELETE FROM source_configs WHERE org_id = ?', (org_id,))
            # 插入新的配置
            count = 0
            for key, value in selections.items():
                parts = key.split('_')
                source_id = int(parts[0]) if parts[0].isdigit() else 0
                source_name = parts[1] if len(parts) > 1 else ''
                cursor.execute('''
                    INSERT INTO source_configs (org_id, org_name, source_id, source_name, is_selected)
                    VALUES (?, ?, ?, ?, ?)
                ''', (org_id, org_name, source_id, source_name, 1 if value else 0))
                count += 1
            conn.commit()
            return count

    @staticmethod
    def get_by_org(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT source_id, source_name, is_selected 
                FROM source_configs 
                WHERE org_id = ?
            ''', (org_id,))
            rows = cursor.fetchall()
            result = {}
            for row in rows:
                key = f"{row['source_id']}_{row['source_name']}"
                result[key] = bool(row['is_selected'])
            return result


class EnergyDataDAO:
    """能耗数据访问对象"""

    @staticmethod
    def save(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO energy_data 
                (org_id, org_name, period_type, period_year, period_month, 
                 period_quarter, period_start, period_end, data_json, total_emission)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('org_id'),
                data.get('org_name'),
                data.get('period_type', '月度'),
                data.get('period_year', 2024),
                data.get('period_month', 1),
                data.get('period_quarter'),
                data.get('period_start'),
                data.get('period_end'),
                json.dumps(data.get('details', [])),
                data.get('total', 0)
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_org(org_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, org_id, org_name, period_type, period_year, period_month,
                       period_quarter, period_start, period_end, data_json, total_emission,
                       created_at
                FROM energy_data 
                WHERE org_id = ?
                ORDER BY created_at DESC
            ''', (org_id,))
            rows = cursor.fetchall()
            result = []
            for row in rows:
                item = dict(row)
                try:
                    item['data_json'] = json.loads(item['data_json']) if item['data_json'] else []
                except:
                    item['data_json'] = []
                result.append(item)
            return result


class CalculationMethodDAO:
    """核算方法数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, method_name, emission_type, data_type, unit,
                       param_config, formula, is_referenced, is_enabled,
                       created_at, updated_at
                FROM calculation_methods
                ORDER BY id
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(method_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, method_name, emission_type, data_type, unit,
                       param_config, formula, is_referenced, is_enabled
                FROM calculation_methods
                WHERE id = ?
            ''', (method_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO calculation_methods 
                (method_name, emission_type, data_type, unit, param_config, formula, is_referenced, is_enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('method_name', ''),
                data.get('emission_type', '能源消耗'),
                data.get('data_type', '系统默认'),
                data.get('unit', 'kgCO2'),
                data.get('param_config', ''),
                data.get('formula', ''),
                data.get('is_referenced', 0),
                data.get('is_enabled', 1)
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(method_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE calculation_methods 
                SET method_name = ?, emission_type = ?, data_type = ?, unit = ?,
                    param_config = ?, formula = ?, is_referenced = ?, is_enabled = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('method_name', ''),
                data.get('emission_type', '能源消耗'),
                data.get('data_type', '系统默认'),
                data.get('unit', 'kgCO2'),
                data.get('param_config', ''),
                data.get('formula', ''),
                data.get('is_referenced', 0),
                data.get('is_enabled', 1),
                method_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(method_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM calculation_methods WHERE id = ?', (method_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_batch(ids):
        if not ids:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f'DELETE FROM calculation_methods WHERE id IN ({placeholders})', ids)
            conn.commit()
            return cursor.rowcount
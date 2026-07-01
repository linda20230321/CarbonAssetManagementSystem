# models/product_model.py
import json
from models.database import get_db


class ProductCategoryDAO:
    """产品分类数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, category_name, icon, sort_order FROM product_categories ORDER BY sort_order')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(category_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, category_name, icon, sort_order FROM product_categories WHERE id = ?',
                           (category_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO product_categories (category_name, icon, sort_order)
                VALUES (?, ?, ?)
            ''', (data.get('category_name', ''), data.get('icon', '📁'), data.get('sort_order', 0)))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(category_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE product_categories SET category_name=?, icon=?, sort_order=?
                WHERE id=?
            ''', (data.get('category_name', ''), data.get('icon', '📁'), data.get('sort_order', 0), category_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(category_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM product_categories WHERE id = ?', (category_id,))
            conn.commit()
            return cursor.rowcount > 0


class ProductDAO:
    """产品数据访问对象"""

    @staticmethod
    def get_all():
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.product_name, p.unit, p.description, p.sort_order,
                       p.product_code, p.product_model, p.specification, p.functional_unit,
                       p.declared_unit, p.design_life, p.reference_standard,
                       c.id as category_id, c.category_name, c.icon
                FROM products p
                JOIN product_categories c ON p.category_id = c.id
                ORDER BY c.sort_order, p.sort_order
            ''')
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(product_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.product_name, p.unit, p.description, p.sort_order,
                       p.product_code, p.product_model, p.specification, p.functional_unit,
                       p.declared_unit, p.design_life, p.reference_standard,
                       c.id as category_id, c.category_name, c.icon
                FROM products p
                JOIN product_categories c ON p.category_id = c.id
                WHERE p.id = ?
            ''', (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_by_category(category_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.product_name, p.unit, p.description, p.sort_order,
                       p.product_code, p.product_model, p.specification, p.functional_unit,
                       p.declared_unit, p.design_life, p.reference_standard
                FROM products p
                WHERE p.category_id = ?
                ORDER BY p.sort_order
            ''', (category_id,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def create(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products 
                (category_id, product_name, unit, description, sort_order,
                 product_code, product_model, specification, functional_unit,
                 declared_unit, design_life, reference_standard)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('category_id'),
                data.get('product_name', ''),
                data.get('unit', ''),
                data.get('description', ''),
                data.get('sort_order', 0),
                data.get('product_code', ''),
                data.get('product_model', ''),
                data.get('specification', ''),
                data.get('functional_unit', ''),
                data.get('declared_unit', ''),
                data.get('design_life', ''),
                data.get('reference_standard', '')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(product_id, data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE products 
                SET category_id=?, product_name=?, unit=?, description=?, sort_order=?,
                    product_code=?, product_model=?, specification=?, functional_unit=?,
                    declared_unit=?, design_life=?, reference_standard=?
                WHERE id=?
            ''', (
                data.get('category_id'),
                data.get('product_name', ''),
                data.get('unit', ''),
                data.get('description', ''),
                data.get('sort_order', 0),
                data.get('product_code', ''),
                data.get('product_model', ''),
                data.get('specification', ''),
                data.get('functional_unit', ''),
                data.get('declared_unit', ''),
                data.get('design_life', ''),
                data.get('reference_standard', ''),
                product_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(product_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
            conn.commit()
            return cursor.rowcount > 0


class ProductConfigDAO:
    """产品配置数据访问对象"""

    @staticmethod
    def get_by_product(product_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT stage, config_json FROM product_configs WHERE product_id = ?', (product_id,))
            result = {}
            for row in cursor.fetchall():
                try:
                    result[row['stage']] = json.loads(row['config_json'])
                except:
                    result[row['stage']] = []
            return result

    @staticmethod
    def save(product_id, stage, config):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO product_configs (product_id, stage, config_json)
                VALUES (?, ?, ?)
                ON CONFLICT(product_id, stage) DO UPDATE SET
                    config_json = excluded.config_json,
                    updated_at = CURRENT_TIMESTAMP
            ''', (product_id, stage, json.dumps(config)))
            conn.commit()
            return cursor.rowcount > 0


class ProductFootprintDAO:
    """产品碳足迹数据访问对象"""

    @staticmethod
    def save(data):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO product_footprints 
                (product_id, product_name, category_name, quantity, 
                 total_emission, stages_json, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data.get('product_id'), data.get('product_name', ''),
                  data.get('category_name', ''), data.get('quantity', 1),
                  data.get('total_emission', 0),
                  json.dumps(data.get('stages', {})),
                  json.dumps(data.get('details', []))))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_product(product_id, limit=20):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, product_id, product_name, category_name, quantity,
                       total_emission, stages_json, details_json, calculated_at
                FROM product_footprints
                WHERE product_id = ?
                ORDER BY calculated_at DESC
                LIMIT ?
            ''', (product_id, limit))
            result = []
            for row in cursor.fetchall():
                item = dict(row)
                try:
                    item['stages_json'] = json.loads(item['stages_json']) if item['stages_json'] else {}
                except:
                    item['stages_json'] = {}
                try:
                    item['details_json'] = json.loads(item['details_json']) if item['details_json'] else []
                except:
                    item['details_json'] = []
                result.append(item)
            return result
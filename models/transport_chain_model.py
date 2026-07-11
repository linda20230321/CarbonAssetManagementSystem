# models/transport_chain_model.py
import sqlite3
import json
from models.database import get_db


class TransportChainDAO:
    """运输链数据访问对象"""

    @staticmethod
    def get_all():
        """获取所有运输链记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, chain_type, start_location, end_location, 
                       train_type, seat_type, energy_type, transport_mode,
                       distance, weight, turnover, 
                       rail_emission, rail_intensity, rail_energy_intensity,
                       road_emission, road_intensity,
                       reduction_amount, reduction_rate,
                       chain_transport, chain_handling, chain_storage, chain_other,
                       created_at
                FROM transport_chain_records
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(record_id):
        """根据ID获取记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, chain_type, start_location, end_location, 
                       train_type, seat_type, energy_type, transport_mode,
                       distance, weight, turnover, 
                       rail_emission, rail_intensity, rail_energy_intensity,
                       road_emission, road_intensity,
                       reduction_amount, reduction_rate,
                       chain_transport, chain_handling, chain_storage, chain_other,
                       route_data, created_at
                FROM transport_chain_records
                WHERE id = ?
            ''', (record_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create(data):
        """创建新记录"""
        with get_db() as conn:
            cursor = conn.cursor()

            # 检查表是否存在，不存在则创建
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transport_chain_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chain_type TEXT,
                    start_location TEXT,
                    end_location TEXT,
                    train_type TEXT,
                    seat_type TEXT,
                    energy_type TEXT,
                    transport_mode TEXT,
                    distance REAL,
                    weight REAL,
                    turnover REAL,
                    rail_emission REAL,
                    rail_intensity REAL,
                    rail_energy_intensity REAL,
                    road_emission REAL,
                    road_intensity REAL,
                    road_energy_intensity REAL,
                    reduction_amount REAL,
                    reduction_rate REAL,
                    chain_transport REAL,
                    chain_handling REAL,
                    chain_storage REAL,
                    chain_other REAL,
                    route_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                INSERT INTO transport_chain_records 
                (chain_type, start_location, end_location, train_type, seat_type, 
                 energy_type, transport_mode, distance, weight, turnover,
                 rail_emission, rail_intensity, rail_energy_intensity,
                 road_emission, road_intensity, road_energy_intensity,
                 reduction_amount, reduction_rate,
                 chain_transport, chain_handling, chain_storage, chain_other,
                 route_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('chain_type', '客运'),
                data.get('start_location', ''),
                data.get('end_location', ''),
                data.get('train_type', ''),
                data.get('seat_type', ''),
                data.get('energy_type', ''),
                data.get('transport_mode', ''),
                data.get('distance', 0),
                data.get('weight', 0),
                data.get('turnover', 0),
                data.get('rail_emission', 0),
                data.get('rail_intensity', 0),
                data.get('rail_energy_intensity', 0),
                data.get('road_emission', 0),
                data.get('road_intensity', 0),
                data.get('road_energy_intensity', 0),
                data.get('reduction_amount', 0),
                data.get('reduction_rate', 0),
                data.get('chain_transport', 0),
                data.get('chain_handling', 0),
                data.get('chain_storage', 0),
                data.get('chain_other', 0),
                json.dumps(data.get('route_data', []))
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update(record_id, data):
        """更新记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transport_chain_records 
                SET chain_type = ?, start_location = ?, end_location = ?,
                    train_type = ?, seat_type = ?, energy_type = ?, transport_mode = ?,
                    distance = ?, weight = ?, turnover = ?,
                    rail_emission = ?, rail_intensity = ?, rail_energy_intensity = ?,
                    road_emission = ?, road_intensity = ?, road_energy_intensity = ?,
                    reduction_amount = ?, reduction_rate = ?,
                    chain_transport = ?, chain_handling = ?, chain_storage = ?, chain_other = ?,
                    route_data = ?
                WHERE id = ?
            ''', (
                data.get('chain_type', '客运'),
                data.get('start_location', ''),
                data.get('end_location', ''),
                data.get('train_type', ''),
                data.get('seat_type', ''),
                data.get('energy_type', ''),
                data.get('transport_mode', ''),
                data.get('distance', 0),
                data.get('weight', 0),
                data.get('turnover', 0),
                data.get('rail_emission', 0),
                data.get('rail_intensity', 0),
                data.get('rail_energy_intensity', 0),
                data.get('road_emission', 0),
                data.get('road_intensity', 0),
                data.get('road_energy_intensity', 0),
                data.get('reduction_amount', 0),
                data.get('reduction_rate', 0),
                data.get('chain_transport', 0),
                data.get('chain_handling', 0),
                data.get('chain_storage', 0),
                data.get('chain_other', 0),
                json.dumps(data.get('route_data', [])),
                record_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(record_id):
        """删除记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transport_chain_records WHERE id = ?', (record_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_batch(ids):
        """批量删除"""
        if not ids:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f'DELETE FROM transport_chain_records WHERE id IN ({placeholders})', ids)
            conn.commit()
            return cursor.rowcount
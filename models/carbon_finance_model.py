# models/carbon_finance_model.py
import sqlite3
from models.database import get_db


class CarbonFinanceDAO:
    """碳金融数据访问对象"""

    # ========== 项目管理 ==========

    @staticmethod
    def get_projects(filters=None):
        """获取项目列表"""
        with get_db() as conn:
            cursor = conn.cursor()
            sql = '''
                SELECT id, project_name, initiator, method_name, method_file, 
                       other_files, status, review_status, review_comment,
                       created_at, updated_at
                FROM carbon_projects
                ORDER BY created_at DESC
            '''
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_project(project_id):
        """获取单个项目"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project_name, initiator, method_name, method_file, 
                       other_files, status, review_status, review_comment,
                       created_at, updated_at
                FROM carbon_projects
                WHERE id = ?
            ''', (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create_project(data):
        """创建项目"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO carbon_projects 
                (project_name, initiator, method_name, method_file, other_files, 
                 status, review_status, review_comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('project_name', ''),
                data.get('initiator', ''),
                data.get('method_name', ''),
                data.get('method_file', ''),
                data.get('other_files', ''),
                data.get('status', '草稿'),
                data.get('review_status', '未提交'),
                data.get('review_comment', '')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update_project(project_id, data):
        """更新项目"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE carbon_projects 
                SET project_name = ?, initiator = ?, method_name = ?, 
                    method_file = ?, other_files = ?, status = ?, 
                    review_status = ?, review_comment = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('project_name', ''),
                data.get('initiator', ''),
                data.get('method_name', ''),
                data.get('method_file', ''),
                data.get('other_files', ''),
                data.get('status', '草稿'),
                data.get('review_status', '未提交'),
                data.get('review_comment', ''),
                project_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_project(project_id):
        """删除项目"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM carbon_audits WHERE project_id = ?', (project_id,))
            cursor.execute('DELETE FROM carbon_projects WHERE id = ?', (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def submit_project(project_id, comment=''):
        """提交核证 - 更新项目状态并创建审核记录"""
        with get_db() as conn:
            cursor = conn.cursor()

            # 1. 获取项目信息
            cursor.execute('''
                SELECT project_name, initiator, method_name 
                FROM carbon_projects 
                WHERE id = ?
            ''', (project_id,))
            project = cursor.fetchone()

            if not project:
                return False

            # 2. 更新项目状态
            cursor.execute('''
                UPDATE carbon_projects 
                SET status = '已提交', review_status = '待审核', 
                    review_comment = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (comment, project_id))

            # 3. 检查是否已有审核记录
            cursor.execute('SELECT id FROM carbon_audits WHERE project_id = ?', (project_id,))
            existing = cursor.fetchone()

            if not existing:
                # 4. 创建审核记录
                cursor.execute('''
                    INSERT INTO carbon_audits 
                    (project_id, project_name, initiator, method_name, 
                     audit_status, audit_comment)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    project_id,
                    project['project_name'],
                    project['initiator'],
                    project['method_name'],
                    '待审核',
                    ''
                ))

            conn.commit()
            return True

    # ========== 审核管理 ==========

    @staticmethod
    def get_audits(filters=None):
        """获取审核列表"""
        with get_db() as conn:
            cursor = conn.cursor()
            sql = '''
                SELECT id, project_id, project_name, initiator, method_name, 
                       audit_report, audit_status, audit_comment,
                       created_at, updated_at
                FROM carbon_audits
                ORDER BY created_at DESC
            '''
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    @staticmethod
    def get_audit(audit_id):
        """获取单个审核记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project_id, project_name, initiator, method_name, 
                       audit_report, audit_status, audit_comment,
                       created_at, updated_at
                FROM carbon_audits
                WHERE id = ?
            ''', (audit_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_audit_by_project(project_id):
        """根据项目ID获取审核记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project_id, project_name, initiator, method_name, 
                       audit_report, audit_status, audit_comment,
                       created_at, updated_at
                FROM carbon_audits
                WHERE project_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create_audit(data):
        """创建审核记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO carbon_audits 
                (project_id, project_name, initiator, method_name, 
                 audit_report, audit_status, audit_comment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('project_id'),
                data.get('project_name', ''),
                data.get('initiator', ''),
                data.get('method_name', ''),
                data.get('audit_report', ''),
                data.get('audit_status', '待审核'),
                data.get('audit_comment', '')
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def update_audit(audit_id, data):
        """更新审核记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE carbon_audits 
                SET audit_report = ?, audit_status = ?, audit_comment = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                data.get('audit_report', ''),
                data.get('audit_status', '待审核'),
                data.get('audit_comment', ''),
                audit_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete_audit(audit_id):
        """删除审核记录"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM carbon_audits WHERE id = ?', (audit_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def approve_audit(audit_id, comment=''):
        """审核通过 - 报告传送"""
        with get_db() as conn:
            cursor = conn.cursor()
            # 更新审核记录
            cursor.execute('''
                UPDATE carbon_audits 
                SET audit_status = '已通过', audit_comment = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (comment, audit_id))
            # 获取关联的项目ID
            cursor.execute('SELECT project_id FROM carbon_audits WHERE id = ?', (audit_id,))
            row = cursor.fetchone()
            if row:
                project_id = row['project_id']
                # 更新项目状态
                cursor.execute('''
                    UPDATE carbon_projects 
                    SET status = '已核证', review_status = '已通过',
                        review_comment = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (comment, project_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def reject_audit(audit_id, comment=''):
        """驳回审核"""
        with get_db() as conn:
            cursor = conn.cursor()
            # 更新审核记录
            cursor.execute('''
                UPDATE carbon_audits 
                SET audit_status = '驳回', audit_comment = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (comment, audit_id))
            # 获取关联的项目ID
            cursor.execute('SELECT project_id FROM carbon_audits WHERE id = ?', (audit_id,))
            row = cursor.fetchone()
            if row:
                project_id = row['project_id']
                # 更新项目状态
                cursor.execute('''
                    UPDATE carbon_projects 
                    SET status = '驳回', review_status = '未通过',
                        review_comment = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (comment, project_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def upload_audit_report(audit_id, report_file):
        """上传审核报告"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE carbon_audits 
                SET audit_report = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (report_file, audit_id))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def transmit_report(audit_id, comment=''):
        """报告传送 - 标记为已传送"""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE carbon_audits 
                SET audit_status = '已传送', audit_comment = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (comment, audit_id))
            conn.commit()
            return cursor.rowcount > 0
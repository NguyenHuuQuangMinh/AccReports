from config.database import get_cursor

class RoleModel:

    def __init__(self):
        self.conn, self.cursor = get_cursor()

    def close(self):
        self.conn.close()

    def get_all_roles(self):
        self.cursor.execute("SELECT RoleId, RoleName FROM Roles WHERE Status = 1")
        return self.cursor.fetchall()

    def get_role_name_by_id(self, role_id):
        self.cursor.execute(
            "SELECT RoleName FROM Roles WHERE RoleId = ?",
            (role_id,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_roles(self,keyword='', status='', sort='asc',page=1, per_page=5):
        sql = """
              SELECT RoleId, RoleName, Status,COUNT(*) OVER() AS total_count
              FROM Roles
              WHERE 1 = 1 
              """
        params = []

        # Search theo username / fullname
        if keyword:
            sql += " AND (RoleName LIKE ?)"
            params.extend([f"%{keyword}%"])

        # Filter status
        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        # Sort username
        order = "ASC" if sort == 'asc' else "DESC"
        sql += f" ORDER BY RoleName {order}"

        # Phân trang
        offset = (page - 1) * per_page
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, per_page])

        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        if rows:
            total = rows[0][3]
        else:
            total = 0

        return rows, total

    def get_role_by_id(self, role_id):
        self.cursor.execute(
            "SELECT RoleName, Status FROM Roles WHERE RoleId = ?",
            (role_id,)
        )
        row = self.cursor.fetchone()
        return row

    def update_Role(self, id, name,status):
        self.cursor.execute(
            "UPDATE Roles SET RoleName=?, Status=? WHERE RoleId=? ",
            name,status,id
        )
        self.conn.commit()

    def create_role(self, name, status ):
        self.cursor.execute(
            "INSERT INTO Roles (RoleName, Status) VALUES (?, ?)", name,status
        )
        self.conn.commit()

    def delete_role(self, id):
        self.cursor.execute("SELECT 1 FROM Roles WHERE RoleId = ?", id)
        if not self.cursor.fetchone():
            return False

        self.cursor.execute(
            '''DELETE FROM Roles WHERE RoleId = ?''', id
        )
        self.conn.commit()
        return True

    def get_all_role_ids(self,exclude_role_id, keyword='', status=''):

        sql = "SELECT RoleId FROM Roles WHERE RoleId != ?"
        params = [exclude_role_id]

        if keyword:
            sql += " AND RoleName LIKE ?"
            params += [f"%{keyword}%"]

        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()

        return [row[0] for row in rows]

    def delete_all_roles(self, keyword='', status=''):
        sql = "DELETE FROM Roles WHERE 1 = 1"
        params = []

        if keyword:
            sql += " AND RoleName LIKE ?"
            params += [f"%{keyword}%"]
        if status != '':
            if int(status) in (0, 1):
                sql += " AND Status = ?"
                params.append(int(status))

        self.cursor.execute(sql, params)
        deleted = self.cursor.rowcount

        self.conn.commit()
        return deleted

    def role_permission(self, role_id):
        sql_get_permis = '''SELECT r.Id, r.ReportName
                            FROM RoleReportPermissions p 
                            INNER JOIN Reports r ON p.ReportId = r.Id
                            WHERE p.RoleId = ?'''

        sql_report = '''SELECT r.Id, r.ReportName
                        FROM Reports r
                        WHERE r.Id NOT IN (
                            SELECT ReportId
                            FROM RoleReportPermissions
                            WHERE RoleId = ?
                        )'''

        self.cursor.execute(sql_get_permis, role_id)
        assigned_report = self.cursor.fetchall()

        self.cursor.execute(sql_report, role_id)
        available_report = self.cursor.fetchall()

        return assigned_report, available_report

    def cate_permission(self, role_id):
        sql_get_permis = '''SELECT c.Id, c.Name
                            FROM RoleCategoryPermissions p 
                            INNER JOIN Categories c ON p.CategoryId = c.Id
                            WHERE p.RoleId = ?'''

        sql_report = '''SELECT c.Id, c.Name
                        FROM Categories c
                        WHERE c.Id NOT IN (
                            SELECT CategoryId
                            FROM RoleCategoryPermissions
                            WHERE RoleId = ?
                        )'''

        self.cursor.execute(sql_get_permis, role_id)
        assigned_report = self.cursor.fetchall()

        self.cursor.execute(sql_report, role_id)
        available_report = self.cursor.fetchall()

        return assigned_report, available_report

    def update_permission(self, id_role, id_report_list):
        sql_delete = '''DELETE FROM RoleReportPermissions WHERE RoleId = ?'''
        sql_inset = '''INSERT INTO RoleReportPermissions (RoleId, ReportId) VALUES (?, ?)'''
        self.cursor.execute("SELECT 1 FROM Roles WHERE RoleId = ?", id_role)
        if not self.cursor.fetchone():
            self.conn.close()
            return False

        self.cursor.execute(sql_delete, id_role)

        for rid in id_report_list:
            self.cursor.execute(sql_inset,id_role, rid)

        self.conn.commit()
        return True

    def update_permission_cate(self, id_role, id_cate_list):
        sql_delete = '''DELETE FROM RoleCategoryPermissions WHERE RoleId = ?'''
        sql_inset = '''INSERT INTO RoleCategoryPermissions (RoleId, CategoryId) VALUES (?, ?)'''
        self.cursor.execute("SELECT 1 FROM Roles WHERE RoleId = ?", id_role)
        if not self.cursor.fetchone():
            self.conn.close()
            return False

        self.cursor.execute(sql_delete, id_role)

        for rid in id_cate_list:
            self.cursor.execute(sql_inset,id_role, rid)

        self.conn.commit()
        return True

import secrets
from datetime import datetime, timedelta, timezone
from config.database import get_cursor

class APIKeyModel:

    def __init__(self):
        self.conn, self.cursor = get_cursor()

    def close(self):
        self.conn.close()

    def create(self, user_id, app_name):
        key = secrets.token_hex(32)
        created_at = datetime.now(timezone.utc) + timedelta(hours=7)
        expired_at = created_at + timedelta(days=365)
        sql = """ INSERT INTO ApiKeys (UserId, AppName, ApiKey, CreatedAt, ExpiredAt)
                  VALUES (?, ?, ?, ?, ?)"""

        self.cursor.execute(sql, (user_id, app_name, key, created_at, expired_at))
        self.conn.commit()
        return key

    def list_API(self,keyword,user_id):
        sql = """ SELECT Id, AppName, ApiKey, CreatedAt, ExpiredAt, Status
                  FROM ApiKeys 
                  WHERE UserId = ?"""
        params = [user_id]
        if keyword:
            sql += " AND (AppName LIKE ?)"
            params.extend([f"%{keyword}%"])
        sql += f" ORDER BY CreatedAt DESC"
        self.cursor.execute(sql, params)
        keys = self.cursor.fetchall()
        return keys

    def list_API_report(self, keyword, user_id):
        sql = """ SELECT ar.Id, ar.ApiLink, r.ReportName, ar.CreatedAt
                  FROM ApiReports ar INNER JOIN  Reports r ON ar.ReportId = r.Id
                  WHERE UserId = ?"""
        params = [user_id]
        if keyword:
            sql += " AND (r.ReportName LIKE ?)"
            params.extend([f"%{keyword}%"])
        sql += f" ORDER BY CreatedAt DESC"
        self.cursor.execute(sql, params)
        keys = self.cursor.fetchall()
        return keys

    def check_API(self, API_Key):
        sql = """SELECT api.UserId, api.ExpiredAt, api.Status
                    FROM ApiKeys api INNER JOIN Users u ON api.UserId = u.Id
                    WHERE api.ApiKey = ? AND u.Status = 1"""
        self.cursor.execute(sql, (API_Key,))
        return self.cursor.fetchone()

    def delete_API(self,Id_API):
        self.cursor.execute("SELECT 1 FROM ApiKeys WHERE Id = ?", Id_API)
        if not self.cursor.fetchone():
            self.conn.close()
            return False

        # Xóa
        self.cursor.execute("DELETE FROM ApiKeys WHERE Id = ?", Id_API)
        self.conn.commit()
        return True

    def get_API_Key(self,Id_API):
        sql = """SELECT ApiKey
                    FROM ApiKeys
                    WHERE Id = ?"""

        self.cursor.execute(sql, (Id_API,))
        row = self.cursor.fetchone()

        if row:
            return row.ApiKey
        else:
            return None

    def check_api_report(self, report_id, user_id):
        sql = """SELECT ApiLink
                 FROM ApiReports
                 WHERE ReportId = ? AND UserId = ?"""
        self.cursor.execute(sql, (report_id, user_id))
        row = self.cursor.fetchone()
        if row:
            return True
        else:
            return False


    def create_api_report(self, report_id, user_id):
        created_at = datetime.now(timezone.utc) + timedelta(hours=7)
        if self.check_api_report(report_id, user_id):
            return "EXISTS"

        sql_params = """SELECT ParamName, ParamValue
                        FROM ReportParams
                        WHERE ReportId = ?"""

        self.cursor.execute(sql_params, (report_id,))
        params = self.cursor.fetchall()

        query_parts = []

        for p in params:
            name = p.ParamName
            value = p.ParamValue

            if value is None or value == '':
                value = "?"

            query_parts.append(f"{name}={value}")

        if query_parts:
            params_str = "&".join(query_parts)
        else:
            params_str = ""

        api_link = (
            f"http://misa.tntoadcorporation.com/api/report/download/{report_id}"
            f"?{params_str}"
        )

        sql_insert = """INSERT INTO ApiReports (ReportId, UserId, ApiLink, CreatedAt)
                        VALUES (?, ?, ?, ?)"""

        self.cursor.execute(sql_insert, (report_id, user_id, api_link, created_at))
        self.conn.commit()

        return "CREATED"

    def delete_API_report (self,Id_API):
        # Kiểm tra user tồn tại
        self.cursor.execute("SELECT 1 FROM ApiReports WHERE Id = ?", Id_API)
        if not self.cursor.fetchone():
            self.conn.close()
            return False

        # Xóa
        self.cursor.execute("DELETE FROM ApiReports WHERE Id = ?", Id_API)
        self.conn.commit()
        return True







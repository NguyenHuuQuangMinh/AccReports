from flask import session
from config.database import get_cursor
from dotenv import load_dotenv
import os

load_dotenv()
class ReportModel:
    @staticmethod
    def create_report(name, file_url, file_download, params, discrip, cateID):
        conn, cursor = get_cursor()
        sql = """
        INSERT INTO Reports (ReportName, FilePath, DownloadLink, Status,Description, CategoryId)
        OUTPUT INSERTED.Id
        VALUES (?, ?, ?,1,?,?)
        """

        cursor.execute(sql, name, file_url,file_download,discrip,cateID)
        report_id = cursor.fetchone()[0]
        if params:
            param_sql = """
                    INSERT INTO ReportParams (ReportId, ParamName, ParamValue, Label, DataType, AllowNull, AllowAll)
                    VALUES (?, ?, ?,?,?,?,?)
                """
            for p in params:
                cursor.execute(param_sql, report_id, p['name'], p['value'], p['label'], p['type'], p['null'], p['all'])
        conn.commit()

    @staticmethod
    def create_report_cate(name):
        conn, cursor = get_cursor()
        sql = """
            INSERT INTO Categories (Name, Status)
            VALUES (?,1)
            """
        cursor.execute(sql, name)
        conn.commit()

    @staticmethod
    def get_reports(keyword='', status='', sort='asc', category = '',page=1, per_page=5):
        conn, cursor = get_cursor()
        userId = session['user_id']
        idRole = session['roleID']
        sql = """
              SELECT r.Id, r.ReportName, r.FilePath, r.Status,r.Description,c.Name as name ,COUNT(*) OVER() AS total_count
              FROM Reports r
              LEFT JOIN Favorites f
                   ON f.ReportId = r.Id
                   AND f.UserId = ?
              LEFT JOIN Categories c ON c.Id = r.CategoryId \
              """
        params = [int(userId)]
        if idRole != 1:
            sql += """
            INNER JOIN RoleReportPermissions p
                ON p.ReportId = r.Id
            WHERE p.RoleId = ?
            """
            params.append(int(idRole))
        else:
            sql += """ WHERE 1 = 1 """
        if category != '':
            sql += " AND r.CategoryId = ?"
            params.append(int(category))
        # Search theo username / fullname
        if keyword:
            sql += " AND (r.ReportName LIKE ?)"
            params.extend([f"%{keyword}%"])

        # Filter status
        if status != '':
            if int(status) in (0, 1):
                sql += " AND r.Status = ?"
                params.append(int(status))

        # Sort username
        order = "ASC" if sort == 'asc' else "DESC"
        sql += f" ORDER BY CASE WHEN f.ReportId IS NOT NULL THEN 0 ELSE 1 END,f.ReportId,r.ReportName {order}"

        # Phân trang
        offset = (page - 1) * per_page
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, per_page])

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()

        if rows:
            total = rows[0][6]
        else:
            total = 0
        return rows,total
    @staticmethod
    def get_all_category():
        conn, cursor = get_cursor()

        sql = "SELECT * FROM Categories WHERE Status = 1"
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        categories = [{'id': r[0], 'name': r[1]} for r in rows]  # tùy thứ tự cột
        return categories

    @staticmethod
    def get_category_roles(role_id):
        conn, cursor = get_cursor()

        sql = "SELECT c.* FROM Categories c INNER JOIN RoleCategoryPermissions p ON p.CategoryId = c.Id WHERE c.Status = 1"
        params = []
        if role_id != 1:
            sql+= "AND p.RoleId = ?"
            params.append(int(role_id))
        else:
            sql+= "AND 1 = 1"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        categories = [{'id': r[0], 'name': r[1]} for r in rows]  # tùy thứ tự cột
        return categories

    @staticmethod
    def get_reports_cate(keyword='', status='', sort='asc', page=1, per_page=5):
        conn, cursor = get_cursor()
        sql = """
                  SELECT Id,Name,Status,COUNT(*) OVER() AS total_count
                  FROM Categories 
                  WHERE 1 = 1 \
                  """
        params = []

        # Search theo username / fullname
        if keyword:
            sql += " AND (Name LIKE ?)"
            params.extend([f"%{keyword}%"])

        # Filter status
        if status != '':
            if int(status) in (0, 1):
                sql += " AND Status = ?"
                params.append(int(status))

        # Sort username
        order = "ASC" if sort == 'asc' else "DESC"
        sql += f" ORDER BY Name {order}"

        # Phân trang
        offset = (page - 1) * per_page
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, per_page])

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()

        if rows:
            total = rows[0][3]
        else:
            total = 0
        return rows, total

    @staticmethod
    def get_by_id(report_id):
        conn, cursor = get_cursor()
        cursor.execute("""
                       SELECT Id, ReportName, FilePath, DownloadLink, Status, Description, CategoryId
                       FROM Reports
                       WHERE Id = ?
                       """, (report_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return None

        cursor.execute("""
                SELECT Id, ParamName, ParamValue, Label, DataType, AllowNull, AllowAll
                FROM ReportParams
                WHERE ReportId = ?
                ORDER BY Id
            """, (report_id,))
        params = cursor.fetchall()
        cursor.close()
        return {
                    "Id": row.Id,
                    "ReportName": row.ReportName,
                    "FilePath": row.FilePath,
                    "DownloadLink": row.DownloadLink,
                    "Status": row.Status,
                    "Description": row.Description,
                    "CategoryId": row.CategoryId,
                    "Params": [
                        {"id": p.Id, "name": p.ParamName, "value": p.ParamValue, "label": p.Label, "datatype":p.DataType, "allow_null": p.AllowNull, "allow_all": p.AllowAll}
                        for p in params
                    ]
                }

    @staticmethod
    def get_cate_by_id(report_cate_id):
        conn, cursor = get_cursor()
        cursor.execute("""
                           SELECT Id, Name, Status
                           FROM Categories
                           WHERE Id = ?
                           """, (report_cate_id,))
        row = cursor.fetchone()
        cursor.close()
        return row

    @staticmethod
    def get_reports_by_ids(ids=None,keyword=None, sort=None, category=None):
        if not ids:
            return []
        conn, cursor = get_cursor()
        conditions = []
        params = []
        if ids:
            conditions.append(f"Id IN ({','.join('?' for _ in ids)})")
            params.extend(ids)

        if keyword:
            conditions.append("(ReportName LIKE ?)")
            kw = f"%{keyword}%"
            params.append(kw)
        if category:
            conditions.append(f"CategoryId = ?")
            params.append(int(category))
        query = "SELECT * FROM Reports"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        order = "ASC" if sort == 'asc' else "DESC"
        query += f" ORDER BY ReportName {order}"

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return rows

    @staticmethod
    def update_report(id, report_name, filepath, downloadLink,status, params, description,category):
        conn, cursor = get_cursor()
        cursor.execute("""
                           UPDATE Reports
                           SET ReportName = ?, FilePath = ?, DownloadLink = ?,Status = ?, Description = ?, CategoryId = ?
                           WHERE Id = ?
                           """, (report_name, filepath, downloadLink,int(status),description, category, id))

        cursor.execute("DELETE FROM ReportParams WHERE ReportId = ?", id)

        # Insert lại
        for p in params:
            cursor.execute("""
                    INSERT INTO ReportParams (ReportId, ParamName, ParamValue, Label, DataType, AllowNull, AllowAll)
                    VALUES (?, ?, ?, ?, ?,?,?)
                """, id, p['name'], p['value'], p['label'], p['type'], p['null'], p['all'])

        conn.commit()
        cursor.close()

    @staticmethod
    def update_report_cate(id, Cate_name,status):
        conn, cursor = get_cursor()
        cursor.execute("""
                               UPDATE Categories
                               SET Name = ?,Status = ?
                               WHERE Id = ?
                               """, (Cate_name, int(status), id))
        conn.commit()
        cursor.close()

    @staticmethod
    def count_reports():
        conn, cursor = get_cursor()
        cursor.execute("SELECT COUNT(*) FROM Reports Where Status = 1")
        total = cursor.fetchone()[0]
        cursor.close()
        return total

    @staticmethod
    def delete_report(report_id):
        conn, cursor = get_cursor()

        # Kiểm tra user tồn tại
        cursor.execute("SELECT 1 FROM Reports WHERE Id = ?", report_id)
        if not cursor.fetchone():
            conn.close()
            return False

        # Xóa
        cursor.execute("DELETE FROM Reports WHERE Id = ?", report_id)
        conn.commit()
        cursor.close()
        return True

    @staticmethod
    def delete_report_cate(report_cate_id):
        conn, cursor = get_cursor()

        # Kiểm tra user tồn tại
        cursor.execute("SELECT 1 FROM Categories WHERE Id = ?", report_cate_id)
        if not cursor.fetchone():
            conn.close()
            return False

        # Xóa
        cursor.execute("DELETE FROM Categories WHERE Id = ?", report_cate_id)
        conn.commit()
        cursor.close()
        return True

    @staticmethod
    def build_download_link(report,override_params=None, type="EXCEL"):
        Type_download = type
        FileDownload = report["DownloadLink"]
        base_url = {{{os.getenv('DOWNLOAD_LINK')}}}
        final_params = []
        for p in report["Params"]:
            name = p["name"]
            value = p["value"]
            param_data = None
            # Nếu user nhập → dùng user value
            if override_params and name in override_params:
                param_data = override_params[name]

            if param_data:
                if param_data["all"] == 1:
                    final_params.append(f"{name}=ALL")
                    continue

                if param_data["null"] == 1:
                    final_params.append(f"{name}:isnull=true")
                    continue

                value = param_data["value"]
            if name:
                if value:

                    if "," in str(value):

                        values = [v.strip() for v in str(value).split(",") if v.strip()]

                        for v in values:
                            final_params.append(f"{name}={v}")

                    else:
                        final_params.append(f"{name}={value}")

                else:
                    final_params.append(f"{name}=")
        query_string = "&".join(final_params)
        url = (
            f"{base_url}?"
            f"{FileDownload}"
            f"&rs:Format={Type_download}"
        )

        if query_string:
            url += f"&{query_string}"

        return url

    @staticmethod
    def get_all_report_ids(keyword='', status='', category=''):
        conn, cursor = get_cursor()

        sql = "SELECT Id FROM Reports WHERE 1=1"

        params = []
        if category:
            sql += " AND CategoryId = ?"
            params.append(int(category))
        if keyword:
            sql += " AND (ReportName LIKE ?)"
            params += [f"%{keyword}%"]

        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()

        return [row[0] for row in rows]

    @staticmethod
    def get_all_report_cate_ids(keyword='', status=''):
        conn, cursor = get_cursor()

        sql = "SELECT Id FROM Categories WHERE 1=1"

        params = []
        if keyword:
            sql += " AND (Name LIKE ?)"
            params += [f"%{keyword}%"]

        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()

        return [row[0] for row in rows]

    @staticmethod
    def delete_all_reports(keyword='', status='', category=''):
        conn, cursor = get_cursor()
        sql = "DELETE FROM Reports WHERE 1=1"
        params = []

        if category != '':
            if category:
                sql += " AND CategoryId = ?"
                params.append(int(category))
        if keyword:
            sql += " AND (ReportName LIKE ?)"
            params += [f"%{keyword}%"]
        if status != '':
            if int(status) in (0, 1):
                sql += " AND Status = ?"
                params.append(int(status))

        cursor.execute(sql, params)
        deleted = cursor.rowcount

        conn.commit()
        cursor.close()
        return deleted

    @staticmethod
    def delete_all_reports_cate(keyword='', status=''):
        conn, cursor = get_cursor()
        sql = "DELETE FROM Categories WHERE 1=1"
        params = []

        if keyword:
            sql += " AND (Name LIKE ?)"
            params += [f"%{keyword}%"]
        if status != '':
            if int(status) in (0, 1):
                sql += " AND Status = ?"
                params.append(int(status))

        cursor.execute(sql, params)
        deleted = cursor.rowcount

        conn.commit()
        cursor.close()
        return deleted
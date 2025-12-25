from config.database import get_cursor

class ReportModel:
    @staticmethod
    def create_report(name, file_url, file_download, params):
        conn, cursor = get_cursor()
        sql = """
        INSERT INTO Reports (ReportName, FilePath, DownloadLink, Status)
        OUTPUT INSERTED.Id
        VALUES (?, ?, ?,1)
        """

        cursor.execute(sql, name, file_url,file_download)
        report_id = cursor.fetchone()[0]
        if params:
            param_sql = """
                    INSERT INTO ReportParams (ReportId, ParamName, ParamValue)
                    VALUES (?, ?, ?)
                """
            for p in params:
                cursor.execute(param_sql, report_id, p['name'], p['value'])
        conn.commit()

    @staticmethod
    def get_reports(keyword='', status='', sort='asc'):
        conn, cursor = get_cursor()

        sql = """
              SELECT Id, ReportName, FilePath, Status
              FROM Reports
              WHERE 1 = 1 \
              """
        params = []

        # Search theo username / fullname
        if keyword:
            sql += " AND (ReportName LIKE ?)"
            params.extend([f"%{keyword}%"])

        # Filter status
        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        # Sort username
        order = "ASC" if sort == 'asc' else "DESC"
        sql += f" ORDER BY ReportName {order}"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        cursor.close()

        return rows

    @staticmethod
    def get_by_id(report_id):
        conn, cursor = get_cursor()
        cursor.execute("""
                       SELECT Id, ReportName, FilePath, DownloadLink, Status
                       FROM Reports
                       WHERE Id = ?
                       """, (report_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return None

        cursor.execute("""
                SELECT Id, ParamName, ParamValue
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
                    "Params": [
                        {"id": p.Id, "name": p.ParamName, "value": p.ParamValue}
                        for p in params
                    ]
                }

    @staticmethod
    def get_reports_by_ids(ids=None,keyword=None, sort=None):
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

        query = "SELECT * FROM Reports"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        order = "ASC" if sort == 'asc' else "DESC"
        query += f" ORDER BY ReportName {order}"

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return rows

    @staticmethod
    def update_report(id, report_name, filepath, downloadLink,status, params):
        conn, cursor = get_cursor()
        cursor.execute("""
                           UPDATE Reports
                           SET ReportName = ?, FilePath = ?, DownloadLink = ?,Status     = ?
                           WHERE Id = ?
                           """, (report_name, filepath, downloadLink,int(status), id))

        cursor.execute("DELETE FROM ReportParams WHERE ReportId = ?", id)

        # Insert lại
        for p in params:
            cursor.execute("""
                    INSERT INTO ReportParams (ReportId, ParamName, ParamValue)
                    VALUES (?, ?, ?)
                """, id, p['name'], p['value'])

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
    def build_download_link(report,override_params=None):
        base_url = report["DownloadLink"]  # https://webconnect...
        final_params = []
        for p in report["Params"]:
            name = p["name"]
            value = p["value"]

            # Nếu user nhập → dùng user value
            if override_params and name in override_params:
                value = override_params[name]

            if name and value:
                final_params.append(f"{name}={value}")

        query_string = "&".join(final_params)

        url = f"{base_url}"

        if query_string:
            url += f"&{query_string}"

        return url
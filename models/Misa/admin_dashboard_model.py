from config.database import get_cursor

class AdminDashboardModel:

    def __init__(self):
        self.conn, self.cursor = get_cursor()

    def close(self):
        self.conn.close()

    def get_total_users(self):
        self.cursor.execute("SELECT COUNT(Id) FROM Users")
        return self.cursor.fetchone()[0]

    def get_active_users(self):
        self.cursor.execute("SELECT COUNT(Id) FROM Users WHERE Status = 1 AND Online = 1 AND Id != 1")
        return self.cursor.fetchone()[0]

    def get_active_reports(self):
        self.cursor.execute("SELECT COUNT(Id) FROM Reports WHERE Status = 1")
        return self.cursor.fetchone()[0]

    def get_total_reports(self):
        self.cursor.execute("SELECT COUNT(Id) FROM Reports")
        return self.cursor.fetchone()[0]

    def get_latest_reports(self, limit=5):
        sql = """
        SELECT TOP (?) Id, ReportName, FilePath, Status
        FROM Reports
        WHERE Status = 1
        ORDER BY Id DESC
        """
        self.cursor.execute(sql, (limit,))
        return self.cursor.fetchall()

    def top_down_reports(self, limit=5):
        sql = """
                SELECT TOP (?) *
                FROM (
                    SELECT 
                        r.Id,
                        r.ReportName,
                        COUNT(*) AS TotalDownloads
                    FROM DownloadHistory dh
                    JOIN Reports r ON dh.ReportId = r.Id
                    WHERE dh.Action = 'download'
                    GROUP BY r.Id, r.ReportName
                ) t
                ORDER BY t.TotalDownloads DESC
        """
        self.cursor.execute(sql, (limit,))
        return self.cursor.fetchall()

    def top_api_reports(self, limit=5):
        sql = """
                SELECT TOP (?) *
                FROM (
                    SELECT 
                        r.Id,
                        r.ReportName,
                        COUNT(*) AS TotalAPI
                    FROM DownloadHistory dh
                    JOIN Reports r ON dh.ReportId = r.Id
                    WHERE dh.Action = 'API'
                    GROUP BY r.Id, r.ReportName
                ) t
                ORDER BY t.TotalAPI DESC
        """
        self.cursor.execute(sql, (limit,))
        return self.cursor.fetchall()

    def top_view_reports(self, limit=5):
        sql = """
                SELECT TOP (?) 
                           r.Id,
                           r.ReportName,
                           COUNT(*) AS TotalViews
                    FROM DownloadHistory dh
                    JOIN Reports r ON dh.ReportId = r.Id
                    WHERE dh.Action = 'view'
                    GROUP BY r.Id, r.ReportName
                    ORDER BY TotalViews DESC
                """
        self.cursor.execute(sql, (limit,))
        return self.cursor.fetchall()

    def top_like_reports(self,limit=5):
        sql = """
                SELECT TOP (?) 
                   r.Id,
                   r.ReportName,
                   COUNT(*) AS TotalFavorites
                FROM Favorites f
                JOIN Reports r ON f.ReportId = r.Id
                GROUP BY r.Id, r.ReportName
                ORDER BY TotalFavorites DESC
                """
        self.cursor.execute(sql, (limit,))
        return self.cursor.fetchall()

    def download_history_admin(self, from_date=None, to_date=None,keyword = None,action_choice=''):
        query = """
                SELECT 
                    dh.Id,
                    dh.ReportId,
                    u.FullName,
                    r.ReportName,
                    r.FilePath,
                    dh.Action,
                    dh.CreatedAt
                FROM DownloadHistory dh
                     JOIN Reports r ON dh.ReportId = r.Id
                     JOIN Users u ON u.Id = dh.UserId
                WHERE 1 = 1
            """
        params = []

        if from_date:
            query += " AND CAST(dh.CreatedAt AS DATE) >= ?"
            params.append(from_date)

        if to_date:
            query += " AND CAST(dh.CreatedAt AS DATE) <= ?"
            params.append(to_date)

        if keyword:
            query += " AND (r.ReportName LIKE ? OR u.FullName LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if action_choice != '':
            query += " AND dh.Action = ?"
            params.append(action_choice)

        query += " ORDER BY dh.CreatedAt DESC"
        self.cursor.execute(query, params)
        histories = self.cursor.fetchall()

        count_query = """
                      SELECT SUM(CASE WHEN Action = 'download' THEN 1 ELSE 0 END) AS total_download, \
                             SUM(CASE WHEN Action = 'view' THEN 1 ELSE 0 END)     AS total_view, \
                             SUM(CASE WHEN Action = 'API' THEN 1 ELSE 0 END)      AS total_api
                      FROM DownloadHistory dh
                      WHERE 1 = 1 \
                      """

        count_params = []

        if from_date:
            count_query += " AND CAST(dh.CreatedAt AS DATE) >= ?"
            count_params.append(from_date)

        if to_date:
            count_query += " AND CAST(dh.CreatedAt AS DATE) <= ?"
            count_params.append(to_date)

        if keyword:
            count_query += " AND (dh.ReportId IN (SELECT Id FROM Reports WHERE ReportName LIKE ?) "
            count_query += " OR dh.UserId IN (SELECT Id FROM Users WHERE FullName LIKE ?))"
            count_params.extend([f"%{keyword}%", f"%{keyword}%"])

        if action_choice:
            count_query += " AND dh.Action = ?"
            count_params.append(action_choice)

        self.cursor.execute(count_query, count_params)
        total_download, total_view, total_api = self.cursor.fetchone()

        return histories, total_download or 0, total_view or 0, total_api or 0

    def get_action(self):
        query = """
                SELECT distinct Action
                FROM DownloadHistory 
                """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return [r[0] for r in rows]

    def get_action_summary_detail(self, action_choice=None,action=None, from_date=None, to_date=None, keyword=None):
        query = """
                SELECT r.ReportName, u.FullName,
                       COUNT(*) AS Total
                FROM DownloadHistory dh
                         JOIN Reports r ON dh.ReportId = r.Id
                         JOIN Users u ON u.Id = dh.UserId
                WHERE 1 = 1
                """
        params = []
        if action:
            query += " AND dh.Action = ?"
            params.append(action)
        if action_choice:
            if action_choice != action:
                query += " AND dh.Action = ?"
                params.append(action_choice)

        if from_date:
            query += " AND CAST(dh.CreatedAt AS DATE) >= ?"
            params.append(from_date)

        if to_date:
            query += " AND CAST(dh.CreatedAt AS DATE) <= ?"
            params.append(to_date)

        if keyword:
            query += " AND (r.ReportName LIKE ? OR u.FullName LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        query += " GROUP BY r.ReportName, u.FullName ORDER BY Total DESC"

        self.cursor.execute(query, params)
        return self.cursor.fetchall()
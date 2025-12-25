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
        self.cursor.execute("SELECT COUNT(Id) FROM Users WHERE Status = 1")
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


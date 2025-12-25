from config.database import get_cursor

class FavoriteModel:

    @staticmethod
    def toggle(user_id, report_id):
        conn, cursor = get_cursor()

        cursor.execute("""
            SELECT 1
            FROM Favorites
            WHERE UserId = ? AND ReportId = ?
        """, (user_id, report_id))

        exists = cursor.fetchone()

        if exists:
            cursor.execute("""
                DELETE FROM Favorites
                WHERE UserId = ? AND ReportId = ?
            """, (user_id, report_id))
            liked = 0
        else:
            cursor.execute("""
                INSERT INTO Favorites (UserId, ReportId)
                VALUES (?, ?)
            """, (user_id, report_id))
            liked = 1

        conn.commit()
        return liked

    @staticmethod
    def get_user_favorites(user_id):
        conn, cursor = get_cursor()

        cursor.execute("""
            SELECT ReportId
            FROM Favorites
            WHERE UserId = ?
        """, (user_id,))

        rows = cursor.fetchall()
        return {r.ReportId for r in rows}

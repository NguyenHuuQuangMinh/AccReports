import hashlib
from config.database import get_cursor
from datetime import datetime

class UserModel:

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def create_user(username, password, full_name, role):
        conn, cursor = get_cursor()

        password_hash = UserModel.hash_password(password)

        sql = """
        INSERT INTO Users (Username, PasswordHash, FullName, Role, Status)
        VALUES (?, ?, ?, ?, 1)
        """

        cursor.execute(sql, username, password_hash, full_name, role)
        conn.commit()

    @staticmethod
    def change_password(user_id, old_password, new_password):
        connection, cursor = get_cursor()
        cursor.execute("""SELECT 1
                          FROM Users
                          WHERE Id = ?
                            And PasswordHash = ?""", user_id, old_password)

        if not cursor.fetchone():
            connection.close()
            return False

        cursor.execute("""UPDATE Users
                          SET PasswordHash = ?
                          WHERE Id = ?""", UserModel.hash_password(new_password), user_id)

        connection.commit()
        return True

    @staticmethod
    def get_users(keyword='', status='', sort='asc'):
        conn, cursor = get_cursor()

        sql = """
              SELECT Id, Username, FullName, Role, Status
              FROM Users
              WHERE 1 = 1 
              """
        params = []

        # Search theo username / fullname
        if keyword:
            sql += " AND (Username LIKE ? OR FullName LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        # Filter status
        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        # Sort username
        order = "ASC" if sort == 'asc' else "DESC"
        sql += f" ORDER BY Username {order}"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        cursor.close()

        return rows

    @staticmethod
    def update_password(user_id, password_hash):
        conn, cursor = get_cursor()
        cursor.execute(
            "UPDATE Users SET PasswordHash=? WHERE Id=?",
            password_hash, user_id
        )
        conn.commit()

    @staticmethod
    def get_by_id(user_id):
        conn, cursor = get_cursor()
        cursor.execute("""
                       SELECT Id, Username, FullName, Role, Status, passwordHash
                       FROM Users
                       WHERE Id = ?
                       """, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        return row

    @staticmethod
    def update_user(id, full_name, role, status, password = None):
        conn, cursor = get_cursor()
        if password is not None:
            cursor.execute("""
                           UPDATE Users
                           SET FullName = ?,
                               Role     = ?,
                               Status   = ?,
                               PasswordHash = ?
                           WHERE Id = ?
                           """, (full_name, role, int(status),password, id))
        else:
            cursor.execute("""
                           UPDATE Users
                           SET FullName     = ?,
                               Role         = ?,
                               Status       = ?
                           WHERE Id = ?
                           """, (full_name, role, int(status), id))
        conn.commit()
        cursor.close()

    @staticmethod
    def delete_user(user_id):
        conn, cursor = get_cursor()

        # Kiểm tra user tồn tại
        cursor.execute("SELECT 1 FROM Users WHERE Id = ?", user_id)
        if not cursor.fetchone():
            conn.close()
            return False

        # Xóa
        cursor.execute("DELETE FROM Users WHERE Id = ?", user_id)
        conn.commit()
        cursor.close()
        return True

    @staticmethod
    def authenticate(username, password):
        connection, cursor = get_cursor()
        password_hash = UserModel.hash_password(password)
        cursor.execute("""SELECT Id AS id,
                            Username AS username,
                            Role AS role,
                            Online As onl
                          FROM Users 
                          WHERE LOWER(Username) = LOWER(?)
                            AND PasswordHash = ?
                            AND Status = 1""", username, password_hash)
        row = cursor.fetchone()
        return row

    @staticmethod
    def log_history(user_id, report_id, action):
        conn, cursor = get_cursor()
        cursor.execute(
            "INSERT INTO DownloadHistory (UserId, ReportId, Action, CreatedAt) VALUES (?, ?, ?, ?)",
            (user_id, report_id, action, datetime.now())
        )
        conn.commit()

    @staticmethod
    def download_history(user_id, from_date=None, to_date=None,keyword = None):
        conn, cursor = get_cursor()
        query = """
                SELECT 
                    dh.Id,
                    dh.ReportId,
                    r.ReportName,
                    r.FilePath,
                    dh.Action,
                    dh.CreatedAt
                FROM DownloadHistory dh
                JOIN Reports r ON dh.ReportId = r.Id
                WHERE dh.UserId = ?
            """
        params = [user_id]

        if from_date:
            query += " AND CAST(dh.CreatedAt AS DATE) >= ?"
            params.append(from_date)

        if to_date:
            query += " AND CAST(dh.CreatedAt AS DATE) <= ?"
            params.append(to_date)

        if keyword:
            query += " AND r.ReportName LIKE ?"
            params.append(f"%{keyword}%")

        query += " ORDER BY dh.CreatedAt DESC"
        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def update_online(user_id, status: bool):
        conn, cursor = get_cursor()
        sql = "UPDATE Users SET Online = ? WHERE Id = ?"
        conn.execute(sql, (1 if status else 0, user_id))
        conn.commit()


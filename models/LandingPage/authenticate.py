from config.database import get_cursor
import hashlib

class AuthenticLinkModel:
    def __init__(self):
        self.conn, self.cursor = get_cursor()

    def close(self):
        self.conn.close()

    def hash_password(self,password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def authetic(self, username, password):
        model = AuthenticLinkModel()
        passchek = model.hash_password(password)
        sql = """SELECT u.Id AS id,
                            u.Username AS username,
                            u.FullName AS full_name,
                            u.Role AS role,
                            u.RoleId AS roleID,
                            u.Online As onl,
                            u.Status as status,
                            r.Status as roleStatus
                          FROM Users u INNER JOIN Roles r ON u.RoleId = r.RoleId
                          WHERE LOWER(Username) = LOWER(?)
                            AND PasswordHash = ?"""
        self.cursor.execute(sql, (username, passchek))
        row = self.cursor.fetchone()
        self.cursor.close()
        return row

    def get_by_id(self,user_id):
        self.cursor.execute("""
                       SELECT Id, Username, FullName, Role, RoleId, Status, passwordHash
                       FROM Users
                       WHERE Id = ?
                       """, (user_id,))
        row = self.cursor.fetchone()
        self.cursor.close()
        return row

    def update_password(self,user_id, password):
        model = AuthenticLinkModel()
        password_hash = model.hash_password(password)
        self.cursor.execute(
            "UPDATE Users SET PasswordHash=? WHERE Id=?",
            password_hash, user_id
        )
        self.conn.commit()



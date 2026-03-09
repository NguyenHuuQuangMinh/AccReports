from config.database import get_cursor
class LinkUserModel:

    def __init__(self):
        self.conn, self.cursor = get_cursor()

    def close(self):
        self.conn.close()

    def insert_folder(self, name, userId):
        sql = '''SELECT 1 FROM Folders WHERE FolderName=? AND UserId=?'''
        self.cursor.execute(sql, (name, userId))
        check = self.cursor.fetchone()
        if check:
            return 'EXIST'

        sql_insert = '''INSERT INTO Folders (FolderName, UserId) VALUES (?, ?)'''
        self.cursor.execute(sql_insert, (name, userId))
        self.conn.commit()
        return 'OK'

    def get_all_link_folder(self, userId, keyword):
        sql = """SELECT f.Id AS BrandID,
                    f.FolderName AS BrandName,
                    l.LinkName,
                    l.Url,
                    l.Id AS LinkId
               FROM Folders f
                        LEFT JOIN LinkUser l
                                  ON l.FolderId = f.Id
                                      AND l.UserId = ?
               WHERE  f.UserId = ?\
            """
        params = [int(userId), int(userId)]
        if keyword:
            sql += " AND l.LinkName Like ?"
            params.append(f"%{keyword}%")

        sql += " ORDER BY f.FolderName"
        self.cursor.execute(sql, params)
        row = self.cursor.fetchall()
        return row

    def get_folders(self, userId):
        sql ='''SELECT Id,FolderName FROM Folders WHERE UserId=?'''
        self.cursor.execute(sql, (userId,))
        row = self.cursor.fetchall()
        return row

    def insert_link(self, user_id, link_name, link_url, folder_id):
        sql = '''SELECT 1 \
                 FROM LinkUser \
                 WHERE LinkName = ? \
                   AND UserId = ? AND FolderId = ?'''
        self.cursor.execute(sql, (link_name, user_id, folder_id))
        check = self.cursor.fetchone()
        if check:
            return 'EXIST'

        sql_insert = '''INSERT INTO LinkUser (LinkName, Url, UserId, FolderId) values (?,?,?,?) '''
        self.cursor.execute(sql_insert, (link_name, link_url, user_id, folder_id))
        self.conn.commit()
        return 'OK'

    def update_link_folder(self, link_id, folder_id, user_id):
        sql = '''UPDATE LinkUser SET FolderId = ? WHERE Id = ? AND UserId = ?'''
        self.cursor.execute(sql, (folder_id, link_id,user_id))
        self.conn.commit()

    def delete_link(self, link_id, user_id):
        sql = '''SELECT 1 FROM LinkUser WHERE Id = ? AND UserId = ?'''
        self.cursor.execute(sql, (link_id, user_id))
        if not self.cursor.fetchone():
            return False
        sql_delete = '''DELETE FROM LinkUser WHERE Id = ? AND UserId = ?'''
        self.cursor.execute(sql_delete, (link_id, user_id))
        self.conn.commit()
        return True

    def delete_folder(self, folder_id, user_id):
        sql = '''SELECT 1 FROM Folders WHERE Id = ? AND UserId = ?'''
        self.cursor.execute(sql, (folder_id, user_id))
        if not self.cursor.fetchone():
            return False
        sql_delete = '''DELETE FROM Folders WHERE Id = ? AND UserId = ?'''
        self.cursor.execute(sql_delete, (folder_id, user_id))
        self.conn.commit()
        return True

    def update_brand(self, brand_id, newname):
        sql = '''SELECT 1 FROM Folders WHERE Id = ?'''
        self.cursor.execute(sql, (brand_id,))
        if not self.cursor.fetchone():
            return 'k'
        sql_update = '''UPDATE Folders SET FolderName = ? WHERE Id = ?'''
        self.cursor.execute(sql_update, (newname, brand_id))
        self.conn.commit()
        return 'OK'

    def update_link(self, user_id,folder_id, link_id, link_name, link_url):
        sql = '''SELECT 1 FROM LinkUser WHERE UserId = ? AND FolderId = ? AND Id = ?'''
        self.cursor.execute(sql, (user_id, folder_id, link_id))
        if not self.cursor.fetchone():
            return 'EXIST'
        sql_update = '''UPDATE LinkUser SET LinkName = ?, Url = ? WHERE Id = ? AND UserId = ?'''
        self.cursor.execute(sql_update, (link_name, link_url, link_id,user_id))
        self.conn.commit()
        return 'OK'
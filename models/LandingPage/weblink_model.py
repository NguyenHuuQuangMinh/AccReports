from config.database import get_cursor
import os
import shutil
from werkzeug.utils import secure_filename

class LinkModel:

    def __init__(self):
        self.conn, self.cursor = get_cursor()

    def close(self):
        self.conn.close()

    def create_folder_save_pic(self, name, logo_file):
        base_path = os.path.join("static", "picture", name)
        os.makedirs(base_path, exist_ok=True)
        filename = secure_filename(logo_file.filename)
        save_path = os.path.join(base_path, filename)
        logo_file.save(save_path)
        return f"picture/{name}/{filename}"

    def get_all_brand_ids(self,keyword='', status=''):

        sql = "SELECT Id FROM Brands WHERE 1=1"
        params = []

        if keyword:
            sql += " AND BrandName LIKE ?"
            params.append(f"%{keyword}%")

        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def get_all_brand(self):
        sql = "SELECT Id, BrandName FROM Brands WHERE Status = 1"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return rows

    def get_all_link_ids(self,brand = '',keyword='', status=''):

        sql = "SELECT l.Id FROM Links l INNER JOIN BrandLinkMap bl ON l.Id = bl.LinkId WHERE 1=1"
        params = []
        if brand:
            sql += " AND bl.BrandId LIKE ?"
            params.append(int(brand))
        if keyword:
            sql += " AND l.LinkName LIKE ?"
            params.append(f"%{keyword}%")

        if status in ('0', '1'):
            sql += " AND l.Status = ?"
            params.append(int(status))

        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def get_brands(self,keyword='', status='', sort='asc',page=1, per_page=5):
        sql = """
              SELECT Id, BrandName, Status,COUNT(*) OVER() AS total_count
              FROM Brands
              WHERE 1 = 1 
              """
        params = []

        # Search theo username / fullname
        if keyword:
            sql += " AND (BrandName LIKE ?)"
            params.extend([f"%{keyword}%"])

        # Filter status
        if status in ('0', '1'):
            sql += " AND Status = ?"
            params.append(int(status))

        # Sort username
        order = "ASC" if sort == 'asc' else "DESC"
        sql += f" ORDER BY BrandName {order}"

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

    def get_links(self,brand='',keyword='', status='', sort='asc',page=1, per_page=5):
        sql = """
              SELECT l.Id, l.LinkName,l.Url, l.Status,b.Id as IdBrand,b.BrandName ,COUNT(*) OVER() AS total_count
              FROM Links l INNER JOIN BrandLinkMap bl ON l.Id = bl.LinkId
                           INNER JOIN Brands b ON b.Id = bl.BrandId
              WHERE 1 = 1 
              """
        params = []
        if brand is not None and brand != '':
            sql += " AND (bl.BrandId = ?)"
            params.append(int(brand))
        # Search theo username / fullname
        if keyword:
            sql += " AND (l.LinkName LIKE ?)"
            params.extend([f"%{keyword}%"])

        # Filter status
        if status in ('0', '1'):
            sql += " AND l.Status = ?"
            params.append(int(status))

        # Sort username
        order = "ASC" if sort == 'asc' else "DESC"
        sql += f" ORDER BY l.LinkName {order}"

        # Phân trang
        offset = (page - 1) * per_page
        sql += " OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([offset, per_page])

        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        if rows:
            total = rows[0][6]
        else:
            total = 0

        return rows, total

    def add_links(self, name, url, brand):
        sql = """
              INSERT INTO Links(LinkName, Url, Status)
              OUTPUT INSERTED.Id
              VALUES (?, ?, 1)
              \
              """

        self.cursor.execute(sql, (name, url))
        id_link = self.cursor.fetchone()[0]

        sql_insert_map = """INSERT INTO BrandLinkMap (BrandId, LinkId) VALUES (?,?)"""
        self.cursor.execute(sql_insert_map, (brand, id_link))
        self.conn.commit()

    def add_brands(self, name, logo_path, color):
        sql = """
              INSERT INTO Brands(BrandName, LogoLink, Color, Status)
              VALUES (?, ?, ?, 1) \
              """

        self.cursor.execute(sql, (name, logo_path, color))
        self.conn.commit()

    def delete_all_brands(self, keyword='', status=''):
        sql = "DELETE FROM Brands WHERE 1 = 1"
        params = []

        if keyword:
            sql += " AND BrandName LIKE ?"
            params += [f"%{keyword}%"]
        if status != '':
            if int(status) in (0, 1):
                sql += " AND Status = ?"
                params.append(int(status))

        self.cursor.execute(sql, params)
        deleted = self.cursor.rowcount

        self.conn.commit()
        return deleted

    def delete_all_links(self, keyword='', status='', brand =''):
        sql = "DELETE L FROM Links L JOIN BrandLinkMap BLM ON L.Id = BLM.LinkId WHERE 1 = 1"
        params = []
        if brand:
            sql += "AND BLM.BrandId = ?"
            params.append(int(brand))
        if keyword:
            sql += " AND L.LinkName LIKE ?"
            params.append(f"%{keyword}%")
        if status != '':
            if int(status) in (0, 1):
                sql += " AND L.Status = ?"
                params.append(int(status))

        self.cursor.execute(sql, params)
        deleted = self.cursor.rowcount

        self.conn.commit()
        return deleted

    def delete_brand(self, id):
        self.cursor.execute("SELECT 1 FROM Brands WHERE Id = ?", id)
        if not self.cursor.fetchone():
            return False

        self.cursor.execute(
            "SELECT LogoLink FROM Brands WHERE Id = ?", (id,)
        )

        row = self.cursor.fetchone()
        if not row:
            return False

        logo_path = row.LogoLink

        self.cursor.execute(
            '''DELETE FROM Brands WHERE Id = ?''', id
        )
        self.conn.commit()

        try:
            # Thư mục gốc cho phép xóa
            base_dir = os.path.abspath(os.path.join("static", "picture"))

            # logo_path = picture/apple/logo.png
            # → lấy folder brand: picture/apple
            brand_folder = os.path.dirname(logo_path)

            # Đường dẫn tuyệt đối tới folder brand
            folder_path = os.path.abspath(os.path.join("static", brand_folder))

            # 🔒 Kiểm tra an toàn
            if folder_path.startswith(base_dir + os.sep) and os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print("✅ Đã xóa folder brand:", folder_path)
            else:
                print("⛔ Từ chối xóa folder:", folder_path)

        except Exception as e:
            print("❌ Lỗi khi xóa folder ảnh:", e)

        return True

    def delete_link(self, id):
        self.cursor.execute("SELECT 1 FROM Links WHERE Id = ?", id)
        if not self.cursor.fetchone():
            return False

        self.cursor.execute(
            '''DELETE FROM Links WHERE Id = ?''', id
        )
        self.conn.commit()
        return True

    def get_brand_by_id(self, brand_id):
        self.cursor.execute(
            "SELECT BrandName, Status, LogoLink, Color FROM Brands WHERE Id = ?",
            (brand_id,)
        )
        row = self.cursor.fetchone()
        return row

    def get_link_by_id(self, link_id, brand_id):
        self.cursor.execute(
            "SELECT L.Id, L.LinkName, L.Url, L.Status, BLM.BrandId \
                    FROM Links L INNER JOIN BrandLinkMap BLM ON L.Id = BLM.LinkId \
                    WHERE L.Id = ? AND BLM.BrandId = ?",
            (link_id,brand_id)
        )
        row = self.cursor.fetchone()
        return row

    def update_brand(self,id,name,color,logo, status):
        self.cursor.execute(
            "UPDATE Brands SET BrandName=?, LogoLink=?, Status=?, Color=? WHERE Id=? ",
            (name,logo,status,color ,id)
        )
        self.conn.commit()

    def update_link(self,id,name,url,status, brand):
        self.cursor.execute(
            "UPDATE Links SET LinkName=?, Url=?, Status=? WHERE Id=? ",
            (name,url,status,id)
        )

        self.cursor.execute(
            "UPDATE BrandLinkMap SET BrandId=? WHERE LinkId=?",
            (brand, id)
        )
        self.conn.commit()

    def get_all_link_brand(self ,keyword):
        sql="""SELECT 
                    b.Id AS BrandID,
                    b.BrandName,
                    b.LogoLink,
                    b.Color,
                    l.LinkName,
                    l.Url
                FROM Brands b
                LEFT JOIN BrandLinkMap bm 
                    ON b.Id = bm.BrandId
                LEFT JOIN Links l 
                    ON l.Id = bm.LinkId 
                   AND l.Status = 1
                WHERE b.Status = 1
                """
        params = []
        if keyword:
            sql += " AND l.LinkName Like ?"
            params.append(f"%{keyword}%")

        sql += " ORDER BY b.Id"
        self.cursor.execute(sql, params)
        row = self.cursor.fetchall()
        return row

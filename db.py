import sqlite3
import csv

class DB:
    def __init__(self, db_name) -> None:
        self.db_name = db_name

    def create_table(self):
        try:
            conn, cur = self.connect()
            cur.execute("""CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY, 
                        title varchar(255), 
                        company varchar(255),
                        location varchar(255),
                        easy_apply boolean,
                        keyword varchar(255),
                        link varchar(400),
                        found_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        publish_date DATE,
                        applied boolean,
                        applied_at DATETIME NULL
                        )
                        """)
            self.save(conn, cur)
            self.close(conn, cur)

        except Exception as e:
            print(e)

    def update(self):
        pass

    def delete(self):
        pass

    def connect(self):
        conn = sqlite3.Connection(self.db_name)
        cur = conn.cursor()
        return conn, cur

    def save(self, conn, cur):
        conn.commit()

    def close(self, conn, cur):
        try:
            if cur:
                cur.close()  # Cierra el cursor si existe
        except Exception as e:
            print(f"Error to close cursor: {e}")

        try:
            if conn:
                conn.close()  # Cierra la conexión si existe
        except Exception as e:
            print(f"Erwror to close connection: {e}")

    def export_to_csv(self, table_name, csv_filename):
        conn, cur = self.connect()
        try:
            cur.execute(f"SELECT * FROM {table_name}")
            rows = cur.fetchall()
            headers = [description[0] for description in cur.description] 

            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(headers)
                csvwriter.writerows(rows)

            print(f"Data exported to {csv_filename} successfully.")

        except Exception as e:
            print(f"Error to export data: {e}")

        finally:
            self.close(conn, cur)
        
class Jobs(DB):
    def __init__(self, db_name) -> None:
        super().__init__(db_name)
        self.columns = ('id', 'title', 'company', 'location', 'easy_apply', 'keyword', 'link')

    def insert(self, id, title, company, location, easy_apply, keyword,link, publish_date):
        try:
            conn, cur = self.connect()
            cur.execute(
                """INSERT INTO jobs 
                        (id, title, company, location, easy_apply, keyword, link, publish_date, applied) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                        (id, title, company, location, easy_apply, keyword, link, publish_date, False))

            self.save(conn, cur)

            return True
        
        except sqlite3.OperationalError as oe:

            if 'no such table' in str(oe).lower():
                self.create_table()
                return self.insert(id, title, company, location, easy_apply, link)

            else:
                raise oe

        except Exception as e:
            raise e
        
        finally:
            self.close(conn, cur)

    def select(self) -> list:
        conn, cur = self.connect()
        cur.execute("SELECT * FROM jobs")
        rows = cur.fetchall()
        self.close(conn, cur)
        print(rows)
        return rows
    
    def select_ids(self):
        conn, cur = self.connect()
        cur.execute("SELECT id FROM jobs")
        rows = cur.fetchall()
        self.close(conn, cur)
        
        # transform a unique list of tuples into a list of ids
        rows = [row[0] for row in rows]
        
        return rows
    
    def export_to_csv(self):
        super().export_to_csv('jobs', 'jobs.csv')
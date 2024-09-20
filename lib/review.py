# lib/review.py
from __init__ import CURSOR, CONN
from employee import Employee  # Employee import to handle relationship

class Review:
    all = {}

    def __init__(self, year, comment, employee_id, id=None):
        self.id = id
        self.year = year
        self.comment = comment
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, Employee ID: {self.employee_id}>"

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, int):
            self._year = year
        else:
            raise ValueError("Year must be an integer")

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, comment):
        if isinstance(comment, str) and len(comment):
            self._comment = comment
        else:
            raise ValueError("Comment must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if isinstance(employee_id, int) and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError("employee_id must reference an employee in the database")

    @classmethod
    def create_table(cls):
        """Create the reviews table in the database."""
        sql = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            comment TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the reviews table."""
        sql = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Save the Review instance to the database."""
        sql = "INSERT INTO reviews (year, comment, employee_id) VALUES (?, ?, ?)"
        CURSOR.execute(sql, (self.year, self.comment, self.employee_id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        """Update the corresponding database record for the Review instance."""
        sql = "UPDATE reviews SET year = ?, comment = ?, employee_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.year, self.comment, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the Review instance from the database."""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        del type(self).all[self.id]
        self.id = None

    @classmethod
    def create(cls, year, comment, employee_id):
        """Create a new Review instance and save it to the database."""
        review = cls(year, comment, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance corresponding to a database row."""
        review = cls.all.get(row[0])
        if review:
            review.year = row[1]
            review.comment = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Find a review by its ID."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_employee_id(cls, employee_id):
        """Find all reviews by an employee's ID."""
        sql = "SELECT * FROM reviews WHERE employee_id = ?"
        rows = CURSOR.execute(sql, (employee_id,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]

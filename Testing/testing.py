import unittest

from db import DB
import os

class  Test(unittest.TestCase):
    def test_insert(self):
        db = DB('test.db')
        self.assertEqual(db.insert(1, 'title', 'company', 'location', True, 'link'), True)
        self.assertEqual(db.select(), [(1, 'title', 'company', 'location', True, 'link')])
        # remove test.db
        os.remove('test.db')
        

if __name__ == '__main__':
    unittest.main()
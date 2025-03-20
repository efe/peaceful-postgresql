import unittest
from peaceful_postgresql.query import detect_locks, extract_table_names
from peaceful_postgresql.constants import LockType
import sqlparse


class TestQueryAnalysis(unittest.TestCase):

    def test_detect_locks_ddl(self):
        # Test CREATE TABLE
        sql = "CREATE TABLE new_users (id INT PRIMARY KEY)"
        expected = {"new_users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

        # Test ALTER TABLE
        sql = "ALTER TABLE users ADD COLUMN email VARCHAR(255)"
        expected = {"users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

        # Test DROP TABLE
        sql = "DROP TABLE users"
        expected = {"users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

        # Test TRUNCATE
        sql = "TRUNCATE TABLE users"
        expected = {"users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

    @unittest.skip
    def test_detect_locks_maintenance(self):
        # Test VACUUM FULL
        sql = "VACUUM FULL users"
        expected = {"users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

        # Test CLUSTER
        sql = "CLUSTER users"
        expected = {"users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

        # Test REINDEX
        sql = "REINDEX TABLE users"
        expected = {"users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

    def test_detect_locks_explicit(self):
        # Test explicit SHARE lock
        sql = "LOCK TABLE users IN SHARE MODE"
        expected = {"users": LockType.SHARE.value}
        self.assertEqual(detect_locks(sql), expected)

        # Test explicit ACCESS EXCLUSIVE lock
        sql = "LOCK TABLE users IN ACCESS EXCLUSIVE MODE"
        expected = {"users": LockType.ACCESS_EXCLUSIVE.value}
        self.assertEqual(detect_locks(sql), expected)

    def test_detect_locks_multiple_statements(self):
        # Test multiple statements
        sql = """
        SELECT * FROM users;
        UPDATE orders SET status = 'completed';
        ALTER TABLE products ADD COLUMN price DECIMAL;
        """
        expected = {
            "products": LockType.ACCESS_EXCLUSIVE.value
        }
        self.assertEqual(detect_locks(sql), expected)

    def test_detect_locks_edge_cases(self):
        # Test empty statement
        self.assertEqual(detect_locks(""), {})
        
        # Test comment only
        self.assertEqual(detect_locks("-- This is a comment"), {})
        
        # Test invalid SQL
        self.assertEqual(detect_locks("NOT A VALID SQL"), {})


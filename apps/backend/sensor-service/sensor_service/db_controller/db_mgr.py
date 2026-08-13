"""
Database operations and initialization
"""

import logging
import os
import sqlite3

from sensor_service.db_controller.db_exceptions import DuplicateEventError

logger = logging.getLogger(__name__)


class DBMgr:
    """SQLite database manager"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.environ.get(
            "DB_PATH", "./data/database.db"
        )

        logger.info(f"Initializing database at {self.db_path}")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a database connection

        Returns:
            SQLite database connection

        Raises:
            Exception: If connection fails
        """
        try:
            logger.debug(f"Creating database connection to {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e!s}")
            raise Exception(f"Database connection error: {e!s}")

    def close_connection(self, conn: sqlite3.Connection) -> None:
        """
        Close a database connection

        Args:
            conn: SQLite connection to close
        """
        if conn:
            conn.close()

    def execute_query(
        self, query: str, params: tuple = ()
    ) -> list[tuple]:
        """
        Execute a SELECT query and return results

        Args:
            query: SQL SELECT query
            params: Query parameters for parameterized queries

        Returns:
            List of result tuples

        Raises:
            Exception: If query execution fails
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Database query error: {e!s}")
        finally:
            self.close_connection(conn)

    def execute_update(self, query: str, params: tuple = ()) -> None:
        """
        Execute an INSERT/UPDATE/DELETE query

        Args:
            query: SQL INSERT/UPDATE/DELETE query
            params: Query parameters for parameterized queries

        Raises:
            Exception: If query execution fails
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        except sqlite3.IntegrityError as e:
            if conn is not None:
                conn.rollback()
            if "UNIQUE" in str(e) or "event_id" in str(e).lower():
                raise DuplicateEventError(str(e))
            raise Exception(f"Database update error: {e!s}")
        except Exception as e:
            if conn is not None:
                conn.rollback()
            raise Exception(f"Database update error: {e!s}")
        finally:
            self.close_connection(conn)

    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script (for initialization)

        Args:
            script: SQL script to execute

        Raises:
            Exception: If script execution fails
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database script error: {e!s}")
        finally:
            self.close_connection(conn)

    def health_check(self) -> bool:
        """Check if database connection is alive"""
        try:
            # logger.debug("Running database health check")
            self.execute_query("SELECT 1")
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e!s}")
            return False


db_mgr = DBMgr()

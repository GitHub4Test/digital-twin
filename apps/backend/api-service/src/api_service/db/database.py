"""
Database operations and initialization
"""

import sqlite3
import os
import json
import logging
from typing import List, Tuple, Any
from uuid import uuid4
from api_service.models import SensorReadingResponse
from api_service.db.exceptions import DuplicateEventError

logger = logging.getLogger(__name__)


class Database:
    """SQLite database handler for sensor readings"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.environ.get("DB_PATH", "./data/database.db")
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Create and return a database connection
        
        Returns:
            SQLite database connection
        
        Raises:
            Exception: If connection fails
        """
        try:
            logger.debug(f"Creating database connection to {self.db_path}")
            return sqlite3.connect(self.db_path)
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise Exception(f"Database connection error: {str(e)}")
    
    def _close_connection(self, conn: sqlite3.Connection) -> None:
        """
        Close a database connection
        
        Args:
            conn: SQLite connection to close
        """
        if conn:
            conn.close()
    
    def _execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
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
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Database query error: {str(e)}")
        finally:
            self._close_connection(conn)
    
    def _execute_update(self, query: str, params: Tuple = ()) -> None:
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
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database update error: {str(e)}")
        finally:
            self._close_connection(conn)
    
    def _execute_script(self, script: str) -> None:
        """
        Execute a SQL script (for initialization)
        
        Args:
            script: SQL script to execute
        
        Raises:
            Exception: If script execution fails
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.executescript(script)
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database script error: {str(e)}")
        finally:
            self._close_connection(conn)
    
    def _create_sensor_reading_from_row(self, row: Tuple) -> SensorReadingResponse:
        """
        Convert database row to SensorReadingResponse object
        
        Args:
            row: Tuple of (event_id, timestamp, temperature, humidity, status)
        
        Returns:
            SensorReadingResponse object
        """
        return SensorReadingResponse(
            event_id=row[0],
            timestamp=row[1],
            temperature=row[2],
            humidity=row[3],
            status=row[4]
        )
    
    def init(self) -> None:
        """Initialize database with sensor table"""
        logger.info(f"Initializing database at {self.db_path}")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Create sensor table
        schema = """
            CREATE TABLE IF NOT EXISTS sensor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'RECEIVED',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """
        self._execute_script(schema)
        logger.info("Sensor table initialized")

        # Create outbox_events table
        schema = """
            CREATE TABLE IF NOT EXISTS outbox_events (
                id TEXT PRIMARY KEY,
                aggregate_type TEXT NOT NULL,
                aggregate_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                retry_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                published_at TEXT
            );
        """
        self._execute_script(schema)
        logger.info("Outbox events table initialized")

    def insert_reading(self, event_id: str, timestamp: str, temperature: float, humidity: float) -> dict:
        """
        Insert sensor reading into database
        
        Args:
            event_id: Unique identifier for the event
            timestamp: ISO format timestamp
            temperature: Temperature value
            humidity: Humidity value
        
        Returns:
            Dictionary with status and message
        """
        logger.info(f"Inserting sensor reading: event_id={event_id}, temp={temperature}C, humidity={humidity}%")
        query = """
                INSERT INTO sensor (
                    event_id, timestamp, temperature, humidity, status
                )
                VALUES (?, ?, ?, ?, ?)
                """
        self._execute_update(query, (event_id, timestamp, temperature, humidity, "RECEIVED"))
        logger.info(f"Sensor reading inserted successfully: event_id={event_id}")
        return {"status": "success", "message": "Sensor reading recorded"}
    
    def create_reading_and_outbox_event(
        self,
        event_id: str,
        timestamp: str,
        temperature: float,
        humidity: float,
        outbox_payload: dict,
    ):
        """
        Insert sensor reading and corresponding outbox event in a single transaction
        
        Args:
            event_id: Unique identifier for the event
            timestamp: ISO format timestamp
            temperature: Temperature value
            humidity: Humidity value
            outbox_payload: Payload to store in outbox_events table
        
        Raises:
            DuplicateEventError: If event_id already exists in sensor table
            Exception: For any other database errors
        """
        try:
            conn = self._get_connection()
            conn.execute("BEGIN")

            # insert into sensor table
            conn.execute(
                """
                INSERT INTO sensor (
                    event_id, timestamp, temperature, humidity, status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    timestamp,
                    temperature,
                    humidity,
                    "RECEIVED",
                ),
            )

            # insert into outbox_events table
            conn.execute(
                """
                INSERT INTO outbox_events (
                    id,
                    aggregate_type,
                    aggregate_id,
                    event_type,
                    payload,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid4()),
                    "SensorReading",
                    event_id,
                    "sensor.reading.received",
                    json.dumps(outbox_payload),
                    "PENDING",
                ),
            )

            conn.commit()

        except sqlite3.IntegrityError as e:
            conn.rollback()

            if "UNIQUE" in str(e):
                raise DuplicateEventError(str(e))
            raise
        except Exception:
            conn.rollback()
            raise
        finally:
            self._close_connection(conn)

    def get_pending_outbox_events(self, limit: int = 10):
        """Retrieve pending outbox events for processing
           args:
                limit: Maximum number of events to retrieve
           returns:
                List of pending outbox events as dictionaries 
        """
        logger.info(f"Retrieving pending outbox events: limit={limit}")
        query = """
                SELECT *
                FROM outbox_events
                WHERE status = 'PENDING'
                ORDER BY created_at
                LIMIT ?
                """;

        rows = self._execute_query(query, (limit,))
        events = [dict(row) for row in rows]
        logger.info(f"Retrieved {len(events)} pending outbox events")
        return events

    def mark_outbox_event_published(self, event_id: str):
        """Mark an outbox event as published
           args:
                event_id: ID of the outbox event to mark as published
        """
        logger.info(f"Marking outbox event as published: event_id={event_id}")
        query = """
            UPDATE outbox_events
            SET status = 'PUBLISHED',
                published_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """
        self._execute_update(query, (event_id,))
        logger.info(f"Outbox event marked as published: event_id={event_id}")

    def increment_outbox_retry(self, event_id: str):
        """Increment the retry count for an outbox event
           args:
                event_id: ID of the outbox event to increment retry count for
        """
        logger.info(f"Incrementing retry count for outbox event: event_id={event_id}")
        query = """
            UPDATE outbox_events
            SET retry_count = retry_count + 1
            WHERE id = ?
            """
        self._execute_update(query, (event_id,))
        logger.info(f"Retry count incremented: event_id={event_id}")

    def mark_reading_processed(self, event_id: str):
        """Mark a sensor reading as processed
           args:
                event_id: ID of the sensor reading to mark as processed
        """
        logger.info(f"Marking sensor reading as processed: event_id={event_id}")
        query = """
            UPDATE sensor
            SET status = 'PROCESSED',
                updated_at = CURRENT_TIMESTAMP
            WHERE event_id = ?
            """
        self._execute_update(query, (event_id,))
        logger.info(f"Sensor reading marked as processed: event_id={event_id}")

    def get_readings(self, limit: int = 200) -> List[SensorReadingResponse]:
        """
        Retrieve sensor readings from database
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of sensor readings ordered by timestamp (most recent first)
        """
        logger.info(f"Retrieving sensor readings from database: limit={limit}")
        query = "SELECT event_id, timestamp, temperature, humidity, status FROM sensor ORDER BY timestamp DESC LIMIT ?"
        rows = self._execute_query(query, (limit,))
        readings = [self._create_sensor_reading_from_row(row) for row in rows]
        logger.info(f"Retrieved {len(readings)} sensor readings from database")
        return readings
    
    def clear_readings(self) -> dict:
        """
        Clear all sensor data from database
        
        Returns:
            Dictionary with status and message
        """
        logger.info("Clearing all sensor readings from database")
        query = "DELETE FROM sensor"
        self._execute_update(query)
        logger.info("All sensor readings cleared from database")
        return {"status": "success", "message": "All sensor data cleared"}

    def health_check(self) -> bool:
        """Check if database connection is alive"""
        try:
            logger.debug("Running database health check")
            self._execute_query("SELECT 1")
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

db = Database()
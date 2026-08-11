import sqlite3
import os
import json
import logging
from typing import List, Tuple, Any
from uuid import uuid4

from sensor_service.db_controller.db_exceptions import DuplicateEventError
from sensor_service.generated.sensor.v1 import sensor_pb2, sensor_pb2_grpc

from sensor_service.db_controller.db_mgr import db_mgr

logger = logging.getLogger(__name__)

class SensorReadingMgr:
    """Handler for sensor readings"""

    def __init__(self, db_mgr=db_mgr):
        self.db_mgr = db_mgr

    def _create_sensor_reading_from_row(self, row: Tuple):
        """
        Convert database row to SensorReadingResponse object
        
        Args:
            row: Tuple of (event_id, timestamp, temperature, humidity, status)
        
        Returns:
            SensorReadingResponse object
        """
        reading = {
            "event_id": row[0],
            "timestamp": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "status": row[4],
        }
        return reading        
    
    def init_tables(self) -> None:
        """Initialize database with sensor table"""
        
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
        self.db_mgr._execute_script(schema)
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
        self.db_mgr._execute_script(schema)
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
        self.db_mgr._execute_update(query, (event_id, timestamp, temperature, humidity, "RECEIVED"))
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
        conn = None
        try:
            conn = self.db_mgr._get_connection()
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
            if conn is not None:
                conn.rollback()

            if "UNIQUE" in str(e):
                raise DuplicateEventError(str(e)) from e
            raise
        except Exception:
            if conn is not None:
                conn.rollback()
            raise
        finally:
            self.db_mgr._close_connection(conn)

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

        rows = self.db_mgr._execute_query(query, (limit,))
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
        self.db_mgr._execute_update(query, (event_id,))
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
        self.db_mgr._execute_update(query, (event_id,))
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
        self.db_mgr._execute_update(query, (event_id,))
        logger.info(f"Sensor reading marked as processed: event_id={event_id}")

    def get_readings(self, limit: int = 200) -> List:
        """
        Retrieve sensor readings from database
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of sensor readings ordered by timestamp (most recent first)
        """
        logger.info(f"Retrieving sensor readings from database: limit={limit}")
        query = "SELECT event_id, timestamp, temperature, humidity, status FROM sensor ORDER BY timestamp DESC LIMIT ?"
        rows = self.db_mgr._execute_query(query, (limit,))
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
        conn = None
        try:
            conn = self.db_mgr._get_connection()
            conn.execute("BEGIN")
            event_ids = [row[0] for row in conn.execute("SELECT event_id FROM sensor").fetchall()]
            conn.execute("DELETE FROM sensor")
            if event_ids:
                placeholders = ", ".join("?" for _ in event_ids)
                sql = f"DELETE FROM outbox_events WHERE aggregate_id IN ({placeholders})"

                # nosemgrep: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query
                conn.execute(sql, event_ids)
            conn.commit()
        except Exception as e:
            if conn is not None:
                conn.rollback()
            raise Exception(f"Database clear error: {str(e)}")
        finally:
            self.db_mgr._close_connection(conn)

        logger.info("All sensor readings cleared from database")
        return {"status": "success", "message": "All sensor data cleared"}

    def health_check(self) -> bool:
        """Check if database connection is alive"""
        try:
            logger.debug("Running database health check")
            self.db_mgr._execute_query("SELECT 1")
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


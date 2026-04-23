"""
Database operations and initialization
"""

import sqlite3
import os
from typing import List
from src.models import SensorReadingResponse


class Database:
    """SQLite database handler for sensor readings"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.environ.get("DB_PATH", "./data/database.db")
    
    def init(self):
        """Initialize database with sensor table"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor (
                timestamp TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def insert_reading(self, timestamp: str, temperature: float, humidity: float) -> dict:
        """
        Insert sensor reading into database
        
        Args:
            timestamp: ISO format timestamp
            temperature: Temperature value
            humidity: Humidity value
        
        Returns:
            Dictionary with status and message
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sensor (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                (timestamp, temperature, humidity)
            )
            conn.commit()
            conn.close()
            return {"status": "success", "message": "Sensor reading recorded"}
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
    
    def get_readings(self, limit: int = 200) -> List[SensorReadingResponse]:
        """
        Retrieve sensor readings from database
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of sensor readings ordered by timestamp (most recent first)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, temperature, humidity FROM sensor ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            readings = [
                SensorReadingResponse(
                    timestamp=row[0],
                    temperature=row[1],
                    humidity=row[2]
                )
                for row in rows
            ]
            return readings
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
    
    def clear_readings(self) -> dict:
        """
        Clear all sensor data from database
        
        Returns:
            Dictionary with status and message
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sensor")
            conn.commit()
            conn.close()
            return {"status": "success", "message": "All sensor data cleared"}
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def health_check(self) -> bool:
        """Check if database connection is alive"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            return True
        except Exception:
            return False
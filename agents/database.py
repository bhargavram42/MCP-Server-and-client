"""
MCP Tools for call transcript database operations
Provides tools to fetch transcripts and store analysis results
"""

import sqlite3
import json
from typing import Optional, List, Dict
from datetime import datetime

DB_PATH = "call_transcripts.db"

class TranscriptDatabase:
    """Database access layer for call transcripts"""
    
    @staticmethod
    def get_transcript_by_id(transcript_id: int) -> Optional[Dict]:
        """Fetch a call transcript by ID"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, customer_id, customer_name, transcript, 
                   call_date, duration_seconds, phone_number
            FROM call_transcripts
            WHERE id = ?
            ''', (transcript_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_all_transcripts() -> List[Dict]:
        """Fetch all call transcripts"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, customer_id, customer_name, duration_seconds, call_date
            FROM call_transcripts
            ORDER BY call_date DESC
            ''')
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def get_transcript_by_customer(customer_id: str) -> List[Dict]:
        """Fetch all transcripts for a specific customer"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, customer_id, customer_name, transcript, call_date
            FROM call_transcripts
            WHERE customer_id = ?
            ORDER BY call_date DESC
            ''', (customer_id,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def save_analysis_result(
        transcript_id: int,
        customer_id: str,
        intent: str,
        sentiment: str,
        confidence_score: float,
        raw_analysis: str
    ) -> Dict:
        """Save analysis results to database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO analysis_results
            (transcript_id, customer_id, intent, sentiment, confidence_score, raw_analysis)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (transcript_id, customer_id, intent, sentiment, confidence_score, raw_analysis))
            conn.commit()
            result_id = cursor.lastrowid
            conn.close()
            
            return {
                "success": True,
                "analysis_id": result_id,
                "message": f"Analysis saved for transcript {transcript_id}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_analysis_result(analysis_id: int) -> Optional[Dict]:
        """Fetch a saved analysis result"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, transcript_id, customer_id, intent, sentiment, 
                   confidence_score, analysis_date, raw_analysis
            FROM analysis_results
            WHERE id = ?
            ''', (analysis_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_customer_analysis_history(customer_id: str) -> List[Dict]:
        """Fetch all analysis results for a customer"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id, transcript_id, intent, sentiment, confidence_score, analysis_date
            FROM analysis_results
            WHERE customer_id = ?
            ORDER BY analysis_date DESC
            ''', (customer_id,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]

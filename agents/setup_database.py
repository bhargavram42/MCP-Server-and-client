"""
Database setup script for call transcript analysis
Creates SQLite database with call transcripts and analysis results
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "call_transcripts.db"

def init_database():
    """Create database schema and insert sample data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create call_transcripts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS call_transcripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        transcript TEXT NOT NULL,
        call_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        duration_seconds INTEGER,
        phone_number TEXT
    )
    ''')
    
    # Create analysis_results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transcript_id INTEGER NOT NULL,
        customer_id TEXT NOT NULL,
        intent TEXT,
        sentiment TEXT,
        confidence_score REAL,
        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        raw_analysis TEXT,
        FOREIGN KEY (transcript_id) REFERENCES call_transcripts(id)
    )
    ''')
    
    # Insert sample call transcripts
    sample_transcripts = [
        {
            "customer_id": "CUST001",
            "customer_name": "John Smith",
            "transcript": "Agent: Hello, thank you for calling. How can I help you today? Customer: Hi, I'm calling about my recent order. I received it yesterday but one item was damaged. Agent: I'm sorry to hear that. Let me help you with that. Can you tell me which item was damaged? Customer: Yes, the laptop stand was broken. Agent: I apologize for the inconvenience. I can send you a replacement immediately at no cost. Would that work for you? Customer: Yes, that would be great. Thank you so much for your help! Agent: You're welcome. I'll process this right away.",
            "duration_seconds": 180,
            "phone_number": "+1-555-0001"
        },
        {
            "customer_id": "CUST002",
            "customer_name": "Sarah Johnson",
            "transcript": "Agent: Welcome back! What brings you in today? Customer: I want to cancel my subscription. Agent: Oh no! May I ask why you'd like to cancel? Customer: Your service is too expensive compared to competitors. Agent: I understand. Let me see if I can offer you a better plan. We have a 30% discount available right now. Customer: That would be helpful. How much would that be? Agent: It would be $35 instead of $50 per month. Customer: Okay, I'll keep it then. Thank you!",
            "duration_seconds": 240,
            "phone_number": "+1-555-0002"
        },
        {
            "customer_id": "CUST003",
            "customer_name": "Michael Brown",
            "transcript": "Agent: Hi there! How can we assist you? Customer: I can't log into my account! This is really frustrating! I've been trying for 20 minutes! Agent: I'm very sorry you're experiencing this issue. Let me help you reset your password. Customer: Yes, please do that. This is unacceptable! Agent: I completely understand your frustration. I'll send a password reset link to your email right now. Customer: Fine. But I expect this to work! Agent: It will work, and I sincerely apologize for the trouble. You should receive the email within a few seconds.",
            "duration_seconds": 300,
            "phone_number": "+1-555-0003"
        },
        {
            "customer_id": "CUST004",
            "customer_name": "Emily Davis",
            "transcript": "Agent: Hello! Welcome to our support team. Customer: Hi, I'd like to upgrade my plan to the premium version. Agent: Absolutely! That's a great choice. The premium plan includes 24/7 support, unlimited storage, and advanced features. Customer: That sounds perfect. How much extra will that cost? Agent: It's an additional $15 per month. Would you like me to process that upgrade? Customer: Yes, please go ahead. Agent: Done! Your upgrade is now active. You'll see all the new features in your account. Is there anything else I can help you with? Customer: No, that's all. Thank you!",
            "duration_seconds": 150,
            "phone_number": "+1-555-0004"
        },
        {
            "customer_id": "CUST005",
            "customer_name": "David Wilson",
            "transcript": "Agent: Hi, this is support. What's the issue? Customer: I have a billing question. I was charged twice for last month. Agent: Let me look into that for you. Can you confirm your account email? Customer: It's david.wilson@email.com. Agent: Found it. You're right, there was a duplicate charge. I've initiated a refund for $99.99. It should appear in your account within 3-5 business days. Customer: Thank you! I appreciate you fixing this quickly. Agent: My pleasure! Is there anything else? Customer: No, that's all. Have a good day! Agent: You too, thank you for calling!",
            "duration_seconds": 210,
            "phone_number": "+1-555-0005"
        }
    ]
    
    # Insert transcripts
    for transcript in sample_transcripts:
        cursor.execute('''
        INSERT INTO call_transcripts 
        (customer_id, customer_name, transcript, duration_seconds, phone_number)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            transcript["customer_id"],
            transcript["customer_name"],
            transcript["transcript"],
            transcript["duration_seconds"],
            transcript["phone_number"]
        ))
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized at {DB_PATH}")
    print(f"✓ Created 5 sample call transcripts")

def get_all_transcripts():
    """Fetch all transcripts from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, customer_id, customer_name FROM call_transcripts')
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    init_database()
    print("\nSample transcripts in database:")
    transcripts = get_all_transcripts()
    for t in transcripts:
        print(f"  - ID: {t[0]}, Customer: {t[1]} ({t[2]})")

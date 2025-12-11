"""
Test client for Call Transcript Analysis Agent
Tests all agent capabilities and endpoints
"""

import asyncio
import subprocess
import json
import sys
from agent import CallAnalysisAgent
from database import TranscriptDatabase
from setup_database import init_database, DB_PATH
import os

class AnalysisTestClient:
    """Test client for the analysis agent"""
    
    def __init__(self):
        self.test_results = []
    
    def print_section(self, title):
        """Print a formatted section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    
    def print_result(self, test_name, result, details=""):
        """Print a test result"""
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
        if details:
            print(f"     {details}")
        self.test_results.append((test_name, result))
    
    def test_database_setup(self):
        """Test 1: Database initialization"""
        self.print_section("Test 1: Database Setup")
        
        # Check if database exists
        db_exists = os.path.exists(DB_PATH)
        self.print_result("Database file exists", db_exists, DB_PATH)
        
        # Get transcripts
        transcripts = TranscriptDatabase.get_all_transcripts()
        has_data = len(transcripts) > 0
        self.print_result("Database has sample data", has_data, f"{len(transcripts)} transcripts loaded")
        
        return db_exists and has_data
    
    def test_transcript_retrieval(self):
        """Test 2: Fetch transcripts"""
        self.print_section("Test 2: Transcript Retrieval")
        
        # Test get all transcripts
        all_transcripts = TranscriptDatabase.get_all_transcripts()
        result1 = len(all_transcripts) > 0
        self.print_result("Get all transcripts", result1, f"Retrieved {len(all_transcripts)} transcripts")
        
        # Test get by ID
        if all_transcripts:
            transcript = TranscriptDatabase.get_transcript_by_id(all_transcripts[0]["id"])
            result2 = transcript is not None and "transcript" in transcript
            self.print_result("Get transcript by ID", result2, f"Transcript ID: {all_transcripts[0]['id']}")
        else:
            result2 = False
            self.print_result("Get transcript by ID", False, "No transcripts available")
        
        # Test get by customer
        if all_transcripts:
            customer_id = all_transcripts[0]["customer_id"]
            transcripts = TranscriptDatabase.get_transcript_by_customer(customer_id)
            result3 = len(transcripts) > 0
            self.print_result("Get customer transcripts", result3, f"Customer {customer_id}: {len(transcripts)} transcripts")
        else:
            result3 = False
            self.print_result("Get customer transcripts", False, "No customers available")
        
        return result1 and result2 and result3
    
    def test_sentiment_analysis(self):
        """Test 3: Sentiment analysis"""
        self.print_section("Test 3: Sentiment Analysis")
        
        test_cases = [
            ("positive", "Thank you so much! I really appreciate your help. This is amazing!"),
            ("negative", "This is terrible! I'm frustrated and angry with your service!"),
            ("neutral", "Okay, I understand. This is fine.")
        ]
        
        all_passed = True
        for expected_sentiment, test_text in test_cases:
            sentiment, confidence = CallAnalysisAgent._analyze_sentiment(test_text)
            passed = sentiment == expected_sentiment
            all_passed = all_passed and passed
            self.print_result(
                f"Sentiment detection: {expected_sentiment}",
                passed,
                f"Detected: {sentiment} (confidence: {confidence:.2f})"
            )
        
        return all_passed
    
    def test_intent_extraction(self):
        """Test 4: Intent extraction"""
        self.print_section("Test 4: Intent Extraction")
        
        test_cases = [
            ("complaint", "The item arrived damaged and broken. This is unacceptable!"),
            ("cancellation", "I want to cancel my subscription immediately."),
            ("billing", "Why was I charged twice? I need a refund!"),
            ("upgrade", "I'd like to upgrade to the premium plan please."),
            ("account_access", "I forgot my password and can't login to my account.")
        ]
        
        all_passed = True
        for expected_intent, test_text in test_cases:
            intent_result = CallAnalysisAgent._extract_intent(test_text)
            passed = intent_result["category"] == expected_intent
            all_passed = all_passed and passed
            self.print_result(
                f"Intent detection: {expected_intent}",
                passed,
                f"Detected: {intent_result['category']} (confidence: {intent_result['confidence']:.2f})"
            )
        
        return all_passed
    
    def test_full_analysis(self):
        """Test 5: Full transcript analysis"""
        self.print_section("Test 5: Full Transcript Analysis")
        
        # Get a sample transcript
        all_transcripts = TranscriptDatabase.get_all_transcripts()
        if not all_transcripts:
            self.print_result("Full analysis", False, "No transcripts available")
            return False
        
        transcript_id = all_transcripts[0]["id"]
        transcript_data = TranscriptDatabase.get_transcript_by_id(transcript_id)
        
        # Analyze
        analysis = CallAnalysisAgent.analyze_transcript(transcript_data["transcript"])
        
        has_intent = "intent" in analysis
        has_sentiment = "sentiment" in analysis
        has_confidence = "overall_confidence" in analysis
        
        all_passed = has_intent and has_sentiment and has_confidence
        
        self.print_result("Transcript analysis", all_passed)
        print(f"     Intent: {analysis.get('intent')} ({analysis.get('intent_confidence', 0):.2f})")
        print(f"     Sentiment: {analysis.get('sentiment')} ({analysis.get('sentiment_confidence', 0):.2f})")
        print(f"     Overall Confidence: {analysis.get('overall_confidence', 0):.2f}")
        
        return all_passed
    
    def test_database_save(self):
        """Test 6: Save analysis to database"""
        self.print_section("Test 6: Analysis Database Storage")
        
        # Get a sample transcript
        all_transcripts = TranscriptDatabase.get_all_transcripts()
        if not all_transcripts:
            self.print_result("Save analysis", False, "No transcripts available")
            return False
        
        transcript_id = all_transcripts[0]["id"]
        customer_id = all_transcripts[0]["customer_id"]
        transcript_data = TranscriptDatabase.get_transcript_by_id(transcript_id)
        
        # Analyze and save
        result = CallAnalysisAgent.analyze_and_save(
            transcript_id=transcript_id,
            customer_id=customer_id,
            transcript_text=transcript_data["transcript"]
        )
        
        saved = result["database_save"]["success"]
        analysis_id = result["database_save"].get("analysis_id")
        
        self.print_result("Save analysis to database", saved, f"Analysis ID: {analysis_id}")
        
        # Verify retrieval
        if saved and analysis_id:
            retrieved = TranscriptDatabase.get_analysis_result(analysis_id)
            verified = retrieved is not None and retrieved.get("intent") is not None
            self.print_result("Retrieve saved analysis", verified)
        else:
            self.print_result("Retrieve saved analysis", False, "Nothing was saved")
        
        return saved
    
    def test_customer_analysis_history(self):
        """Test 7: Customer analysis history"""
        self.print_section("Test 7: Customer Analysis History")
        
        # Get a sample customer
        all_transcripts = TranscriptDatabase.get_all_transcripts()
        if not all_transcripts:
            self.print_result("Get analysis history", False, "No transcripts available")
            return False
        
        customer_id = all_transcripts[0]["customer_id"]
        
        # Get history
        history = TranscriptDatabase.get_customer_analysis_history(customer_id)
        has_history = len(history) > 0
        
        self.print_result("Get customer analysis history", has_history, f"Customer {customer_id}: {len(history)} analyses")
        
        return has_history
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("  CALL TRANSCRIPT ANALYSIS AGENT - TEST SUITE")
        print("="*70)
        
        # Check if DB needs initialization
        if not os.path.exists(DB_PATH):
            print("\nInitializing database...")
            init_database()
        
        # Run tests
        test_database_setup = self.test_database_setup()
        test_retrieval = self.test_transcript_retrieval()
        test_sentiment = self.test_sentiment_analysis()
        test_intent = self.test_intent_extraction()
        test_full = self.test_full_analysis()
        test_save = self.test_database_save()
        test_history = self.test_customer_analysis_history()
        
        # Summary
        self.print_section("Test Summary")
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, result in self.test_results if result)
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if passed_tests == total_tests:
            print("\n[SUCCESS] ALL TESTS PASSED!")
        else:
            print("\n[FAILED] SOME TESTS FAILED")
            print("\nFailed tests:")
            for test_name, result in self.test_results:
                if not result:
                    print(f"  - {test_name}")
        
        return passed_tests == total_tests


def print_usage():
    """Print usage information"""
    print("""
    Usage: python test_agent.py [OPTION]
    
    Options:
        test          Run all tests (default)
        setup         Initialize database with sample data
        analyze ID    Analyze transcript with given ID
        help          Show this help message
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            print("Initializing database...")
            init_database()
        elif command == "analyze" and len(sys.argv) > 2:
            transcript_id = int(sys.argv[2])
            transcript = TranscriptDatabase.get_transcript_by_id(transcript_id)
            if transcript:
                analysis = CallAnalysisAgent.analyze_transcript(transcript["transcript"])
                print(f"\nAnalysis for Transcript {transcript_id}:")
                print(json.dumps(analysis, indent=2))
            else:
                print(f"Transcript {transcript_id} not found")
        elif command == "help":
            print_usage()
        else:
            print_usage()
    else:
        # Run all tests
        client = AnalysisTestClient()
        success = client.run_all_tests()
        sys.exit(0 if success else 1)

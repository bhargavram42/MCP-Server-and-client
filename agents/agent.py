"""
Call Transcript Analysis Agent
Analyzes call transcripts to extract intent, sentiment, and customer information
"""

import json
import re
from typing import Dict, Tuple
from database import TranscriptDatabase

class CallAnalysisAgent:
    """Agent for analyzing call transcripts"""
    
    INTENTS = {
        "complaint": ["damaged", "broken", "issue", "problem", "wrong", "defective", "not working"],
        "cancellation": ["cancel", "terminate", "stop", "close account", "quit"],
        "billing": ["charge", "billing", "refund", "payment", "invoice", "duplicate", "expensive"],
        "upgrade": ["upgrade", "premium", "increase", "add", "more features"],
        "account_access": ["login", "password", "reset", "access", "lock", "forgot"],
        "support": ["help", "question", "howto", "how do i", "can you"],
        "complaint_resolution": ["sorry", "apologize", "make it right", "compensation"],
    }
    
    SENTIMENT_KEYWORDS = {
        "positive": ["thank", "appreciate", "great", "perfect", "love", "excellent", "satisfied", "happy"],
        "negative": ["frustrated", "angry", "upset", "furious", "terrible", "horrible", "unacceptable", "annoyed"],
        "neutral": ["okay", "fine", "alright", "sure", "understand"]
    }
    
    @staticmethod
    def analyze_transcript(transcript: str) -> Dict:
        """
        Analyze a call transcript and extract intent, sentiment, and key information
        
        Args:
            transcript: The call transcript text
            
        Returns:
            Dict with intent, sentiment, confidence_score, and details
        """
        intent = CallAnalysisAgent._extract_intent(transcript)
        sentiment, sentiment_confidence = CallAnalysisAgent._analyze_sentiment(transcript)
        
        return {
            "intent": intent["category"],
            "intent_confidence": intent["confidence"],
            "sentiment": sentiment,
            "sentiment_confidence": sentiment_confidence,
            "overall_confidence": (intent["confidence"] + sentiment_confidence) / 2,
            "analysis_details": {
                "intent_keywords_found": intent["keywords_found"],
                "sentiment_indicators": intent["indicators"]
            }
        }
    
    @staticmethod
    def _extract_intent(transcript: str) -> Dict:
        """Extract the primary intent from the transcript"""
        transcript_lower = transcript.lower()
        intent_scores = {}
        keywords_found = {}
        
        # Score each intent category
        for intent_category, keywords in CallAnalysisAgent.INTENTS.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword in transcript_lower:
                    occurrences = transcript_lower.count(keyword)
                    score += occurrences
                    found_keywords.append(keyword)
            
            if score > 0:
                intent_scores[intent_category] = score
                keywords_found[intent_category] = found_keywords
        
        # Determine primary intent
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[primary_intent] / 10, 1.0)  # Normalize to 0-1
        else:
            primary_intent = "general_inquiry"
            confidence = 0.3
        
        return {
            "category": primary_intent,
            "confidence": confidence,
            "keywords_found": keywords_found.get(primary_intent, []),
            "indicators": intent_scores
        }
    
    @staticmethod
    def _analyze_sentiment(transcript: str) -> Tuple[str, float]:
        """Analyze the sentiment of the call"""
        transcript_lower = transcript.lower()
        sentiment_scores = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        
        # Count sentiment indicators
        for sentiment_type, keywords in CallAnalysisAgent.SENTIMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in transcript_lower:
                    sentiment_scores[sentiment_type] += transcript_lower.count(keyword)
        
        # Determine overall sentiment
        total_sentiment_words = sum(sentiment_scores.values())
        
        if total_sentiment_words == 0:
            return "neutral", 0.5
        
        # Calculate confidence as percentage of dominant sentiment
        dominant_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        confidence = sentiment_scores[dominant_sentiment] / total_sentiment_words
        
        return dominant_sentiment, confidence
    
    @staticmethod
    def analyze_and_save(transcript_id: int, customer_id: str, transcript_text: str) -> Dict:
        """
        Analyze a transcript and save results to database
        
        Args:
            transcript_id: ID of the transcript in database
            customer_id: Customer ID
            transcript_text: Full transcript text
            
        Returns:
            Analysis results with database save status
        """
        # Perform analysis
        analysis = CallAnalysisAgent.analyze_transcript(transcript_text)
        
        # Save to database
        raw_analysis = json.dumps(analysis)
        db_result = TranscriptDatabase.save_analysis_result(
            transcript_id=transcript_id,
            customer_id=customer_id,
            intent=analysis["intent"],
            sentiment=analysis["sentiment"],
            confidence_score=analysis["overall_confidence"],
            raw_analysis=raw_analysis
        )
        
        return {
            "analysis": analysis,
            "database_save": db_result
        }

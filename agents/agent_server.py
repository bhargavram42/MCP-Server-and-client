"""
FastMCP Server for Call Transcript Analysis
Provides MCP tools and HTTP endpoints for analyzing call transcripts
"""

from fastmcp import FastMCP
from typing import Optional, List, Dict
from database import TranscriptDatabase
from agent import CallAnalysisAgent
import json

# Create FastMCP server instance
mcp = FastMCP("call-analysis-server", "1.0.0")

# ============================================================================
# MCP TOOLS - For LLM/Agent Integration
# ============================================================================

@mcp.tool()
def get_transcript(transcript_id: int) -> Dict:
    """
    Fetch a call transcript by ID from the database.
    
    Args:
        transcript_id: The ID of the transcript to fetch
    
    Returns:
        Dictionary containing transcript details (id, customer_id, customer_name, 
        transcript text, call_date, duration, phone_number)
    """
    result = TranscriptDatabase.get_transcript_by_id(transcript_id)
    if result is None:
        return {"error": f"Transcript {transcript_id} not found"}
    return result


@mcp.tool()
def list_all_transcripts() -> List[Dict]:
    """
    Get a list of all available call transcripts in the database.
    
    Returns:
        List of transcripts with id, customer_id, customer_name, duration, and call_date
    """
    return TranscriptDatabase.get_all_transcripts()


@mcp.tool()
def get_customer_transcripts(customer_id: str) -> List[Dict]:
    """
    Fetch all call transcripts for a specific customer.
    
    Args:
        customer_id: The customer ID to search for
    
    Returns:
        List of transcripts for the specified customer
    """
    return TranscriptDatabase.get_transcript_by_customer(customer_id)


@mcp.tool()
def analyze_transcript(transcript_id: int, customer_id: str) -> Dict:
    """
    Analyze a call transcript to extract intent, sentiment, and save results.
    
    Args:
        transcript_id: The ID of the transcript to analyze
        customer_id: The customer ID associated with the transcript
    
    Returns:
        Analysis results including:
        - intent: The primary intent (complaint, cancellation, billing, upgrade, etc.)
        - sentiment: Call sentiment (positive, negative, neutral)
        - confidence scores for each
        - overall_confidence: Combined confidence score
    """
    # Fetch transcript
    transcript_data = TranscriptDatabase.get_transcript_by_id(transcript_id)
    if isinstance(transcript_data, dict) and "error" in transcript_data:
        return {"error": f"Could not fetch transcript {transcript_id}"}
    
    # Perform analysis and save
    result = CallAnalysisAgent.analyze_and_save(
        transcript_id=transcript_id,
        customer_id=customer_id,
        transcript_text=transcript_data["transcript"]
    )
    
    return {
        "transcript_id": transcript_id,
        "customer_id": customer_id,
        "analysis": result["analysis"],
        "saved_to_database": result["database_save"]["success"]
    }


@mcp.tool()
def get_analysis_result(analysis_id: int) -> Dict:
    """
    Retrieve a previously saved analysis result.
    
    Args:
        analysis_id: The ID of the analysis result to retrieve
    
    Returns:
        Stored analysis with intent, sentiment, confidence scores, and timestamp
    """
    result = TranscriptDatabase.get_analysis_result(analysis_id)
    if result is None:
        return {"error": f"Analysis {analysis_id} not found"}
    return result


@mcp.tool()
def get_customer_analysis_history(customer_id: str) -> List[Dict]:
    """
    Fetch all analysis results for a specific customer.
    
    Args:
        customer_id: The customer ID to search for
    
    Returns:
        List of all analyses performed for this customer
    """
    return TranscriptDatabase.get_customer_analysis_history(customer_id)


@mcp.tool()
def batch_analyze_customer(customer_id: str) -> Dict:
    """
    Analyze all transcripts for a specific customer in one call.
    
    Args:
        customer_id: The customer ID to analyze
    
    Returns:
        Dictionary with analysis for all customer transcripts
    """
    # Get all transcripts for customer
    transcripts = TranscriptDatabase.get_transcript_by_customer(customer_id)
    
    if isinstance(transcripts, list) and len(transcripts) > 0 and "error" in transcripts[0]:
        return {"error": "Could not fetch customer transcripts"}
    
    results = []
    for transcript in transcripts:
        analysis = CallAnalysisAgent.analyze_and_save(
            transcript_id=transcript["id"],
            customer_id=customer_id,
            transcript_text=transcript["transcript"]
        )
        results.append({
            "transcript_id": transcript["id"],
            "intent": analysis["analysis"]["intent"],
            "sentiment": analysis["analysis"]["sentiment"],
            "confidence": analysis["analysis"]["overall_confidence"]
        })
    
    return {
        "customer_id": customer_id,
        "transcripts_analyzed": len(results),
        "analyses": results
    }


# ============================================================================
# HTTP ENDPOINTS - For REST API Integration
# ============================================================================

@mcp.resource(uri="http://localhost:8000/api/transcripts/{transcript_id}")
def get_transcript_endpoint(transcript_id: int) -> Dict:
    """HTTP endpoint to fetch a transcript by ID"""
    return get_transcript(transcript_id)


@mcp.resource(uri="http://localhost:8000/api/transcripts")
def list_transcripts_endpoint() -> Dict:
    """HTTP endpoint to list all transcripts"""
    return {"transcripts": list_all_transcripts()}


@mcp.resource(uri="http://localhost:8000/api/customers/{customer_id}/transcripts")
def get_customer_transcripts_endpoint(customer_id: str) -> Dict:
    """HTTP endpoint to get transcripts for a customer"""
    return {"customer_id": customer_id, "transcripts": get_customer_transcripts(customer_id)}


@mcp.resource(uri="http://localhost:8000/api/analyze/{transcript_id}")
def analyze_endpoint(transcript_id: int, customer_id: str) -> Dict:
    """HTTP endpoint to analyze a transcript"""
    return analyze_transcript(transcript_id, customer_id)


@mcp.resource(uri="http://localhost:8000/api/analysis/{analysis_id}")
def get_analysis_endpoint(analysis_id: int) -> Dict:
    """HTTP endpoint to retrieve analysis results"""
    return get_analysis_result(analysis_id)


@mcp.resource(uri="http://localhost:8000/api/customers/{customer_id}/analysis")
def get_customer_analysis_endpoint(customer_id: str) -> Dict:
    """HTTP endpoint to get analysis history for a customer"""
    return {
        "customer_id": customer_id,
        "analyses": get_customer_analysis_history(customer_id)
    }


@mcp.resource(uri="http://localhost:8000/api/customers/{customer_id}/batch-analyze")
def batch_analyze_endpoint(customer_id: str) -> Dict:
    """HTTP endpoint to batch analyze all customer transcripts"""
    return batch_analyze_customer(customer_id)


# ============================================================================
# SERVER INFO AND HEALTH CHECK
# ============================================================================

@mcp.tool()
def server_health() -> Dict:
    """
    Health check endpoint. Returns server status and available tools.
    
    Returns:
        Server status information
    """
    return {
        "status": "healthy",
        "server": "call-analysis-server",
        "version": "1.0.0",
        "available_tools": [
            "get_transcript",
            "list_all_transcripts",
            "get_customer_transcripts",
            "analyze_transcript",
            "get_analysis_result",
            "get_customer_analysis_history",
            "batch_analyze_customer",
            "server_health"
        ]
    }


if __name__ == "__main__":
    mcp.run()

# Call Transcript Analysis Agent

A complete MCP-based agent system for analyzing customer call transcripts. Extracts customer intent, sentiment analysis, and stores results in SQLite.

## Features

### 1. **Automated Analysis**
- **Intent Detection**: Identifies customer intent (complaint, cancellation, billing, upgrade, account access, support)
- **Sentiment Analysis**: Classifies call sentiment (positive, negative, neutral)
- **Confidence Scoring**: Provides confidence metrics for each analysis component

### 2. **Database Integration**
- SQLite database for storing call transcripts
- Persistent storage of analysis results
- Customer-based analysis history tracking

### 3. **MCP Tools** (For AI/LLM Integration)
- `get_transcript()` - Fetch transcripts
- `analyze_transcript()` - Analyze a transcript for intent and sentiment
- `get_customer_analysis_history()` - Get all analyses for a customer
- `batch_analyze_customer()` - Analyze all customer transcripts

## Project Files

- `agent.py` - Core analysis agent
- `agent_server.py` - FastMCP server with tools & endpoints
- `database.py` - SQLite database operations
- `setup_database.py` - Database initialization & sample data
- `test_agent.py` - Comprehensive test suite

## Quick Start

```bash
# 1. Initialize database
python setup_database.py

# 2. Run tests
python test_agent.py

# 3. Start server
python agent_server.py
```

## Output Example

The agent returns:
- **customer_id**: CUST001
- **intent**: complaint (confidence: 0.85)
- **sentiment**: positive (confidence: 0.9)
- **overall_confidence**: 0.875

## Database Schema

Two tables:
- `call_transcripts` - Stores call recordings/text
- `analysis_results` - Stores intent, sentiment, and analysis metadata

## Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [MCP Protocol Specification](https://modelcontextprotocol.io)

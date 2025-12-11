# Call Transcript Analysis Agent - Usage Guide

## System Overview

This agent system analyzes customer call transcripts to extract:
1. **Intent**: What the customer wants (complaint, cancellation, billing, upgrade, account access, support)
2. **Sentiment**: How the customer feels (positive, negative, neutral)
3. **Customer ID**: Who the customer is
4. **Confidence Scores**: How certain the analysis is

All data is persisted in SQLite and accessible via MCP tools.

## File Structure

```
agents/
├── setup_database.py        # Initialize database with sample data
├── database.py              # SQLite CRUD operations
├── agent.py                 # Analysis engine (intent + sentiment)
├── agent_server.py          # FastMCP server with tools & endpoints
├── test_agent.py            # Test suite
├── test_mcp_client.py       # MCP tool testing client
├── call_transcripts.db      # SQLite database (auto-created)
└── README.md                # Quick reference
```

## Setup

### Step 1: Initialize Database

```bash
python setup_database.py
```

This creates:
- `call_transcripts.db` with 2 tables
- 5 sample call transcripts

Output:
```
✓ Database initialized at call_transcripts.db
✓ Created 5 sample call transcripts

Sample transcripts in database:
  - ID: 1, Customer: CUST001 (John Smith)
  - ID: 2, Customer: CUST002 (Sarah Johnson)
  - ID: 3, Customer: CUST003 (Michael Brown)
  - ID: 4, Customer: CUST004 (Emily Davis)
  - ID: 5, Customer: CUST005 (David Wilson)
```

### Step 2: Run Tests

```bash
python test_agent.py
```

Tests 7 categories with 17 total assertions:
- Database setup
- Transcript retrieval
- Sentiment analysis
- Intent extraction
- Full analysis
- Database storage
- Customer history

Expected output: `✓ ALL TESTS PASSED!`

## Usage

### Option A: Test Individual Transcript

```bash
python test_agent.py analyze 1
```

Output:
```json
{
  "intent": "support",
  "intent_confidence": 0.4,
  "sentiment": "positive",
  "sentiment_confidence": 1.0,
  "overall_confidence": 0.7,
  "analysis_details": {
    "intent_keywords_found": ["help", "can you"],
    "sentiment_indicators": {...}
  }
}
```

### Option B: Use Python API Directly

```python
from agent import CallAnalysisAgent
from database import TranscriptDatabase

# Get transcript
transcript = TranscriptDatabase.get_transcript_by_id(1)

# Analyze it
analysis = CallAnalysisAgent.analyze_transcript(transcript["transcript"])

# Save analysis
result = TranscriptDatabase.save_analysis_result(
    transcript_id=1,
    customer_id=transcript["customer_id"],
    intent=analysis["intent"],
    sentiment=analysis["sentiment"],
    confidence=analysis["overall_confidence"],
    raw_analysis=str(analysis)
)

print(f"Analysis saved with ID: {result['analysis_id']}")

# Retrieve later
saved = TranscriptDatabase.get_analysis_result(result['analysis_id'])
print(saved)
```

### Option C: Use MCP Server

```bash
# Terminal 1: Start server
python agent_server.py

# Terminal 2: Use MCP client
python test_mcp_client.py
```

MCP tools available:
- `get_transcript(transcript_id)` - Fetch by ID
- `list_all_transcripts()` - Get all
- `get_customer_transcripts(customer_id)` - Get by customer
- `analyze_transcript(transcript_id, customer_id)` - Analyze and save
- `get_analysis_result(analysis_id)` - Retrieve analysis
- `get_customer_analysis_history(customer_id)` - Get all analyses
- `batch_analyze_customer(customer_id)` - Analyze all customer transcripts
- `server_health()` - Health check

## Database Schema

### Table: call_transcripts

```sql
CREATE TABLE call_transcripts (
    id INTEGER PRIMARY KEY,
    customer_id TEXT NOT NULL,
    customer_name TEXT,
    transcript TEXT NOT NULL,
    call_date TEXT,
    duration_seconds INTEGER,
    phone_number TEXT
)
```

### Table: analysis_results

```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY,
    transcript_id INTEGER NOT NULL,
    customer_id TEXT NOT NULL,
    intent TEXT,
    sentiment TEXT,
    confidence_score REAL,
    analysis_date TEXT,
    raw_analysis TEXT,
    FOREIGN KEY(transcript_id) REFERENCES call_transcripts(id)
)
```

## Analysis Output Format

Each analysis returns:

```json
{
  "intent": "complaint",
  "intent_confidence": 0.85,
  "sentiment": "positive",
  "sentiment_confidence": 0.9,
  "overall_confidence": 0.875,
  "analysis_details": {
    "intent_keywords_found": ["damaged", "broken"],
    "sentiment_indicators": {
      "positive": 2,
      "negative": 0,
      "neutral": 1
    }
  }
}
```

## Intent Categories

| Intent | Keywords |
|--------|----------|
| complaint | damaged, broken, issue, problem, wrong, defective, not working |
| cancellation | cancel, terminate, stop, close account, quit |
| billing | charge, billing, refund, payment, invoice, duplicate, expensive |
| upgrade | upgrade, premium, increase, add, more features |
| account_access | login, password, reset, access, lock, forgot |
| support | help, question, howto, how do i, can you |
| complaint_resolution | sorry, apologize, make it right, compensation |

## Sentiment Categories

| Sentiment | Keywords |
|-----------|----------|
| positive | thank, appreciate, great, perfect, love, excellent, satisfied, happy |
| negative | frustrated, angry, upset, furious, terrible, horrible, unacceptable, annoyed |
| neutral | okay, fine, alright, sure, understand |

## Integration Examples

### With Claude/LLM

```python
import anthropic
from database import TranscriptDatabase

client = anthropic.Anthropic()

# Get analysis from agent
analysis = CallAnalysisAgent.analyze_transcript(transcript_text)

# Use with Claude
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": f"""
            A customer called with the following analysis:
            - Intent: {analysis['intent']} (confidence: {analysis['intent_confidence']})
            - Sentiment: {analysis['sentiment']} (confidence: {analysis['sentiment_confidence']})
            
            Generate a response action for the support team.
            """
        }
    ]
)

print(message.content[0].text)
```

### With REST API

```python
import requests

# If you expose agent_server.py via an HTTP wrapper:
response = requests.post(
    "http://localhost:8000/api/analyze/1",
    json={"customer_id": "CUST001"}
)

print(response.json())
```

## Customization

### Add New Intent Category

1. Edit `agent.py`
2. Add to `INTENT_KEYWORDS` dict
3. Re-run tests

```python
INTENT_KEYWORDS = {
    # ... existing ...
    "refund_request": ["refund", "money back", "reimburse"],
}
```

### Add New Sentiment Keywords

1. Edit `agent.py`
2. Update sentiment lists
3. Re-run tests

```python
SENTIMENT_KEYWORDS = {
    "positive": [..., "wonderful", "fantastic"],
    "negative": [..., "pathetic"],
    "neutral": [...]
}
```

## Troubleshooting

### Database Not Found

```
Error: call_transcripts.db not found
```

**Solution**: Run `python setup_database.py`

### No Transcripts Found

```
Error: No transcripts found for customer
```

**Solution**: Check customer_id format (e.g., "CUST001")

### Low Confidence Scores

The keyword-based analysis has limitations:
- No semantic understanding
- Context-insensitive matching
- Requires exact keyword matches

**Solution**: Use ML-based sentiment/intent models for production

## Performance Notes

- **Analysis Speed**: ~1ms per transcript (keyword-based)
- **Database Size**: Grows ~100 bytes per analysis
- **Concurrent Users**: SQLite supports 1 writer, unlimited readers

For production:
- Use PostgreSQL for concurrent write access
- Add ML/transformer models for better accuracy
- Cache frequently accessed transcripts

## Future Enhancements

- [ ] ML-based intent classification (transformers)
- [ ] Multi-language support
- [ ] Real-time sentiment trending
- [ ] Customer journey analysis
- [ ] Automated escalation rules
- [ ] Integration with ticketing systems
- [ ] Audio transcript processing (STT)
- [ ] Dashboard UI for analysis results

## Testing Results

```
Total Tests: 17
Passed: 17
Failed: 0
Success Rate: 100.0%
```

Test categories:
✓ Database setup
✓ Transcript retrieval  
✓ Sentiment analysis
✓ Intent extraction
✓ Full analysis
✓ Database storage
✓ Customer analysis history

## License

MIT

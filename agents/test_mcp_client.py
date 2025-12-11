#!/usr/bin/env python3
"""
Test client for the Call Transcript Analysis MCP Server.

Demonstrates calling MCP tools via JSON-RPC 2.0.
"""

import json
import asyncio
import subprocess
import sys
from typing import Any, Dict

class MCPTestClient:
    """Client to test MCP tools."""
    
    def __init__(self):
        self.request_id = 1
        self.process = None
    
    async def start_server(self) -> None:
        """Start the MCP server in background."""
        print("Starting MCP server...")
        try:
            self.process = subprocess.Popen(
                [sys.executable, "agent_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            await asyncio.sleep(2)  # Give server time to start
            print("✓ Server started\n")
        except Exception as e:
            print(f"✗ Failed to start server: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        """Call an MCP tool via JSON-RPC."""
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": f"tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        self.request_id += 1
        
        try:
            request_str = json.dumps(request) + "\n"
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
            
            # Read response
            response_line = self.process.stdout.readline()
            response = json.loads(response_line)
            
            return response
        except Exception as e:
            return {"error": str(e)}
    
    async def run_tests(self) -> None:
        """Run test sequence."""
        print("=" * 70)
        print("MCP SERVER TOOL TESTS")
        print("=" * 70)
        print()
        
        # Test 1: List all transcripts
        print("Test 1: get_transcript(1)")
        print("-" * 70)
        try:
            result = await self.call_tool("get_transcript", {"transcript_id": 1})
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"Error: {e}\n")
        
        # Test 2: Analyze transcript
        print("Test 2: analyze_transcript(2)")
        print("-" * 70)
        try:
            result = await self.call_tool("analyze_transcript", {
                "transcript_id": 2,
                "customer_id": "CUST002"
            })
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"Error: {e}\n")
        
        # Test 3: Get customer analysis history
        print("Test 3: get_customer_analysis_history(CUST001)")
        print("-" * 70)
        try:
            result = await self.call_tool("get_customer_analysis_history", {
                "customer_id": "CUST001"
            })
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"Error: {e}\n")
        
        # Test 4: Batch analyze customer
        print("Test 4: batch_analyze_customer(CUST003)")
        print("-" * 70)
        try:
            result = await self.call_tool("batch_analyze_customer", {
                "customer_id": "CUST003"
            })
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"Error: {e}\n")
        
        # Test 5: Server health
        print("Test 5: server_health()")
        print("-" * 70)
        try:
            result = await self.call_tool("server_health", {})
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"Error: {e}\n")
        
        print("=" * 70)
        print("✓ Test sequence complete!")
        print("=" * 70)
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()

async def main():
    """Main entry point."""
    client = MCPTestClient()
    try:
        await client.start_server()
        await client.run_tests()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

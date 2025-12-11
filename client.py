"""
Simple MCP Client to test the example-server
Connects to the server running on STDIO and tests all available tools
"""

import asyncio
import subprocess
import json
import sys
from typing import Any

class MCPClient:
    def __init__(self, server_path: str):
        """Initialize the MCP client and start the server process"""
        self.server_path = server_path
        self.process = None
        self.message_id = 0
    
    async def start_server(self):
        """Start the MCP server as a subprocess"""
        print("🚀 Starting MCP server...")
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print("✓ Server started successfully")
            await asyncio.sleep(1)  # Give server time to initialize
        except Exception as e:
            print(f"✗ Failed to start server: {e}")
            raise
    
    async def send_request(self, method: str, params: dict = None) -> dict:
        """Send a JSON-RPC request to the server"""
        self.message_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        
        try:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response1
            response_line = self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line)
                return response
            else:
                return {"error": "No response from server"}
        except Exception as e:
            return {"error": str(e)}
    
    async def list_tools(self) -> dict:
        """List all available tools on the server"""
        print("\n📋 Fetching available tools...")
        response = await self.send_request("tools/list")
        return response
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call a tool on the server"""
        print(f"\n🔧 Calling tool: {tool_name}")
        print(f"Arguments: {arguments}")
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        return response
    
    async def run_tests(self):
        """Run a series of tests on the server"""
        try:
            # Test 1: List available tools
            print("\n" + "="*60)
            print("TEST 1: List Available Tools")
            print("="*60)
            tools_response = await self.list_tools()
            print(json.dumps(tools_response, indent=2))
            
            # Test 2: Call greet tool
            print("\n" + "="*60)
            print("TEST 2: Call greet() tool")
            print("="*60)
            result = await self.call_tool("greet", {"name": "Alice"})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test 3: Call greet with age
            print("\n" + "="*60)
            print("TEST 3: Call greet() with age parameter")
            print("="*60)
            result = await self.call_tool("greet", {"name": "Bob", "age": 30})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test 4: Call calculate tool (add)
            print("\n" + "="*60)
            print("TEST 4: Call calculate() - Addition")
            print("="*60)
            result = await self.call_tool("calculate", {
                "operation": "add",
                "a": 15,
                "b": 7
            })
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test 5: Call calculate tool (multiply)
            print("\n" + "="*60)
            print("TEST 5: Call calculate() - Multiplication")
            print("="*60)
            result = await self.call_tool("calculate", {
                "operation": "multiply",
                "a": 6,
                "b": 9
            })
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test 6: Call get_weather tool
            print("\n" + "="*60)
            print("TEST 6: Call get_weather() tool")
            print("="*60)
            result = await self.call_tool("get_weather", {"city": "London"})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            # Test 7: Call get_weather with unknown city
            print("\n" + "="*60)
            print("TEST 7: Call get_weather() with unknown city")
            print("="*60)
            result = await self.call_tool("get_weather", {"city": "Paris"})
            print(f"Result: {json.dumps(result, indent=2)}")
            
            print("\n" + "="*60)
            print("✓ All tests completed!")
            print("="*60)
            
        except Exception as e:
            print(f"✗ Test failed: {e}")
        finally:
            await self.stop_server()
    
    async def stop_server(self):
        """Stop the server process"""
        if self.process:
            print("\n🛑 Stopping server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print("✓ Server stopped")
            except subprocess.TimeoutExpired:
                self.process.kill()
                print("✓ Server forcefully stopped")


async def main():
    """Main function to run the client"""
    server_path = "server.py"
    
    client = MCPClient(server_path)
    await client.start_server()
    await client.run_tests()


if __name__ == "__main__":
    print("🌐 MCP Client - Testing example-server")
    print("-" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Client interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        sys.exit(1)

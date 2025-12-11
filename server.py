from fastmcp import FastMCP
from typing import Optional

# Create an MCP server instance
mcp = FastMCP("example-server", "1.0.0")

# Define a tool using the @mcp.tool() decorator
@mcp.tool()
def greet(name: str, age: Optional[int] = None) -> str:
    """
    Greet a user by name with optional age information.
    
    Args:
        name: The name of the person to greet
        age: Optional age of the person
    
    Returns:
        A greeting message
    """
    if age:
        return f"Hello {name}! You are {age} years old."
    return f"Hello {name}!"

@mcp.tool()
def calculate(operation: str, a: float, b: float) -> float:
    """
    Perform a simple arithmetic operation.
    
    Args:
        operation: One of 'add', 'subtract', 'multiply', or 'divide'
        a: First number
        b: Second number
    
    Returns:
        The result of the operation
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")


@mcp.tool()
def get_weather(city: str) -> dict:
    """
    Get mock weather data for a city.
    
    Args:
        city: The name of the city
    
    Returns:
        A dictionary with weather information
    """
    # Mock weather data
    weather_data = {
        "London": {"temperature": 12, "condition": "Cloudy", "humidity": 75},
        "New York": {"temperature": 5, "condition": "Snowy", "humidity": 60},
        "Tokyo": {"temperature": 15, "condition": "Partly Cloudy", "humidity": 70},
        "Sydney": {"temperature": 28, "condition": "Sunny", "humidity": 50},
    }
    
    if city in weather_data:
        return {"city": city, **weather_data[city]}
    else:
        return {"city": city, "error": "Weather data not available for this city"}


if __name__ == "__main__":
    mcp.run()
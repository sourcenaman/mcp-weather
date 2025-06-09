from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("weather", log_level="DEBUG", host="0.0.0.0", port=8000)

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url=url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}
        
def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    
    url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    
    point_data = await make_nws_request(url)
    forecast_url = point_data["properties"]["forecast"]

    forecast_data = await make_nws_request(forecast_url)

    # Format forecast periods
    periods = forecast_data["properties"]["periods"]
    formatted = []
    for period in periods[:5]:  # Next 5 periods
        formatted.append(
            f"{period['name']}:\n"
            f"Temperature: {period['temperature']}°F\n"
            f"Wind: {period['windSpeed']} {period['windDirection']}\n"
            f"Forecast: {period['detailedForecast']}\n"
        )
    
    return "\n---\n\n".join(formatted)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="streamable-http")


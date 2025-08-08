import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP weather server", port=8001)

@mcp.tool()
async def get_weather(location: str) -> str:
    """Fetch real-time weather for the given location using Open-Meteo."""
    # Step 1: Geocode the location
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    async with httpx.AsyncClient() as client:
        geo_resp = await client.get(geo_url, params={"name": location, "count": 1})
        geo_data = geo_resp.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"Could not find location: {location}"

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        # Step 2: Fetch current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }

        weather_resp = await client.get(weather_url, params=weather_params)
        weather_data = weather_resp.json()

        if "current_weather" not in weather_data:
            return f"Could not fetch weather data for {location}"

        temp = weather_data["current_weather"]["temperature"]
        wind = weather_data["current_weather"]["windspeed"]

        return f"Current temperature in {location} is {temp}°C with windspeed {wind} km/h."
    
if __name__ == "__main__":
    mcp.run(transport="streamable-http")

import requests
import sys
import os

def check_api_health(url="http://localhost:8000/health"):
    """Check API health status."""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print(f"API is healthy at {url}")
                return True
            else:
                print(f"API returned unhealthy status: {data}")
                return False
        else:
            print(f"API health check failed with status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Connection to API failed: {e}")
        return False

if __name__ == "__main__":
    # Get URL from environment or use default
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip('/') + "/health"
    sys.exit(0 if check_api_health(api_url) else 1)

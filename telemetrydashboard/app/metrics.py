import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from os import getenv

APP_SERVICE_URL = getenv("APP_SERVICE_URL", "http://localhost:8000")
CHANNEL_SERVICE_URL = getenv("CHANNEL_SERVICE_URL", "http://localhost:8001")


class MetricsCollector:
    def __init__(self):
        self.app_service_url = APP_SERVICE_URL
        self.channel_service_url = CHANNEL_SERVICE_URL
        self._health_cache: Dict[str, Dict[str, Any]] = {}
        self._last_fetch: Dict[str, datetime] = {}

    async def get_app_service_health(self) -> Dict[str, Any]:
        """Fetch health status from App Service"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.app_service_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    self._health_cache["app_service"] = data
                    self._last_fetch["app_service"] = datetime.utcnow()
                    return {"status": "healthy", "data": data, "error": None}
                return {"status": "unhealthy", "data": None, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "data": None, "error": str(e)}

    async def get_channel_service_health(self) -> Dict[str, Any]:
        """Fetch health status from Channel Service"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.channel_service_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    self._health_cache["channel_service"] = data
                    self._last_fetch["channel_service"] = datetime.utcnow()
                    return {"status": "healthy", "data": data, "error": None}
                return {"status": "unhealthy", "data": None, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "data": None, "error": str(e)}

    async def get_channel_service_stats(self) -> Dict[str, Any]:
        """Fetch stats from Channel Service"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.channel_service_url}/stats")
                if response.status_code == 200:
                    return {"status": "healthy", "data": response.json(), "error": None}
                return {"status": "unhealthy", "data": None, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "data": None, "error": str(e)}

    async def get_app_service_metrics(self) -> Dict[str, Any]:
        """Fetch metrics from App Service"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try to get API metrics
                response = await client.get(f"{self.app_service_url}/api/v1/health")
                if response.status_code == 200:
                    return {"status": "healthy", "data": response.json(), "error": None}
                # Fallback to root health
                response = await client.get(f"{self.app_service_url}/health")
                if response.status_code == 200:
                    return {"status": "healthy", "data": response.json(), "error": None}
                return {"status": "unhealthy", "data": None, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "data": None, "error": str(e)}

    async def get_all_metrics(self) -> Dict[str, Any]:
        """Collect all metrics from both services"""
        app_health = await self.get_app_service_health()
        channel_health = await self.get_channel_service_health()
        channel_stats = await self.get_channel_service_stats()
        app_metrics = await self.get_app_service_metrics()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "app_service": {
                    "url": self.app_service_url,
                    "health": app_health,
                    "metrics": app_metrics
                },
                "channel_service": {
                    "url": self.channel_service_url,
                    "health": channel_health,
                    "stats": channel_stats
                }
            },
            "summary": {
                "total_services": 2,
                "healthy": sum(1 for s in [app_health, channel_health] if s["status"] == "healthy"),
                "unhealthy": sum(1 for s in [app_health, channel_health] if s["status"] == "unhealthy"),
                "unreachable": sum(1 for s in [app_health, channel_health] if s["status"] == "unreachable")
            }
        }


# Global collector instance
metrics_collector = MetricsCollector()
import os
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class GeocodingService:
    """Сервис для работы с геокодированием через DaData"""
    def __init__(self):
        self.api_key = os.getenv("DADATA_API_KEY")
        self.url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address"

    async def geocode_coordinates(self, latitude: str, longitude: str) -> Optional[str]:
        """
        Выполняет обратное геокодирование (координаты -> адрес)
        """
        if not self.api_key:
            return None

        try:
            lat = float(latitude)
            lon = float(longitude)

            coordinates = {"lat": lat, "lon": lon}

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url=self.url,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Token {self.api_key}"
                    },
                    json=coordinates
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("suggestions") and len(data["suggestions"]) > 0:
                        address = data["suggestions"][0]["value"]
                        return address
                    else:
                        return None
                else:
                    return None
        except Exception as e:
            print(f"Ошибка геокодирования: {e}")
            return None

    async def geocode_address(self, address: str) -> Optional[tuple[str, str]]:
        if not self.api_key or not address:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url="https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Token {self.api_key}"
                    },
                    json={"query": address, "count": 1}
                )
            if response.status_code != 200:
                return None
            suggestions = response.json().get("suggestions") or []
            if not suggestions:
                return None
            data = suggestions[0].get("data") or {}
            latitude = data.get("geo_lat")
            longitude = data.get("geo_lon")
            if not latitude or not longitude:
                return None
            return str(latitude), str(longitude)
        except Exception:
            return None

    async def get_address_or_coordinates(
            self,
            latitude: str,
            longitude: str
    ) -> tuple[Optional[str], str, str]:
        """
        Получает адрес или возвращает координаты в случае ошибки
        """
        address = await self.geocode_coordinates(latitude, longitude)
        return address, latitude, longitude

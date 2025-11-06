import asyncio
import os
from dotenv import load_dotenv
import httpx

load_dotenv("../../../.env")
api_key = os.getenv("DADATA_API_KEY")




async def geocode_coordinates(coordinates: dict) -> str:
    """
    Выполняет обратное геокодирование
    :param coordinates: широта, долгота
    :return: ближайший адрес в формате строки
    """
    url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address"
    api_key = os.getenv("DADATA_API_KEY")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Token {api_key}"
            },
            json=coordinates
        )
        return response.json()["suggestions"][0]["value"]


if __name__ == "__main__":
    address = asyncio.run(geocode_coordinates(coordinates={ "lat": 50.543259, "lon": 137.012984 }))
    print(address)
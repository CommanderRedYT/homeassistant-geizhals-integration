"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout

from bs4 import BeautifulSoup
import re

class GeizhalsIntegrationApiClientError(Exception):
    """Exception to indicate a general API error."""


class GeizhalsIntegrationApiClientCommunicationError(
    GeizhalsIntegrationApiClientError,
):
    """Exception to indicate a communication error."""


class GeizhalsIntegrationApiClientAuthenticationError(
    GeizhalsIntegrationApiClientError,
):
    """Exception to indicate an authentication error."""


class GeizhalsIntegrationInvalidUrlError(
    GeizhalsIntegrationApiClientError,
):
    """Exception to indicate an invalid URL error."""

def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise GeizhalsIntegrationApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


def price_to_float(price_str):
    """
    Converts a price string like "€ 399,99" or "$1,234.56" to a floating point number.
    Handles any currency symbol, spaces, thousands separators, and both comma/dot as decimal delimiter.
    """
    # Remove all non-digit, non-separator characters (keep digits, dots, commas, colons)
    cleaned = re.sub(r'[^\d.,:]', '', price_str)

    # If there are both comma and dot/colon, detect which is decimal
    # Find the last separator (comma, dot, colon)
    # All separators before the last are treated as thousands separators and removed
    separators = [m.start() for m in re.finditer(r'[.,:]', cleaned)]

    if separators:
        last_sep = separators[-1]
        decimal_sep = cleaned[last_sep]
        integer_part = cleaned[:last_sep].replace(",", "").replace(".", "").replace(":", "")
        decimal_part = cleaned[last_sep + 1:]
        normalized = integer_part + '.' + decimal_part  # always use dot for float
    else:
        # No separators, just digits
        normalized = cleaned

    try:
        return float(normalized)
    except ValueError:
        raise ValueError(f"Could not convert '{price_str}' to float.")


class GeizhalsIntegrationApiClient:
    """Sample API Client."""

    def __init__(
        self,
        url: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self._url = url
        self._session = session

    def extract_current_price(self, html_data: str) -> dict:
        out_data = {
            "min_price": None,
            "max_price": None,
            "name": "",
        }

        try:
            soup = BeautifulSoup(html_data, "html.parser")

            # get prices from elements with ids "pricerange-min" and "pricerange-max"
            min_price_element_text = soup.find(id="pricerange-min").get_text().strip()
            max_price_element_text = soup.find(id="pricerange-max").get_text().strip()

            if not min_price_element_text or not max_price_element_text:
                raise GeizhalsIntegrationInvalidUrlError()

            min_price_float = price_to_float(min_price_element_text)
            max_price_float = price_to_float(max_price_element_text)

            out_data["min_price"] = min_price_float
            out_data["max_price"] = max_price_float
            out_data["name"] = soup.select_one('h1.variant__header__headline').get_text().rsplit("|", 1)[0]

            return out_data
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise GeizhalsIntegrationApiClientError(
                msg,
            ) from exception


    async def async_get_data(self) -> Any:
        """Get data from the API."""
        html_data = await self._api_wrapper(
            method="get",
            url=self._url,
        )
        return self.extract_current_price(html_data)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        url = url.strip()
        try:
            if not url.startswith("https://geizhals.at") and not url.startswith("https://geizhals.de"):
                print(f"Url {url} is not Geizhals")
                raise GeizhalsIntegrationInvalidUrlError()

            if not "?" in url:
                url = f"{url}?"
            else:
                url = f"{url}&"

            url = f"{url}hloc=at&hloc=de&hloc=pl&hloc=uk&hloc=eu"

            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                )
                _verify_response_or_raise(response)
                return await response.text()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise GeizhalsIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise GeizhalsIntegrationApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise GeizhalsIntegrationApiClientError(
                msg,
            ) from exception

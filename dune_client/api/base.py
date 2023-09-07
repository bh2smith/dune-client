""""
Basic Dune Client Class responsible for refreshing Dune Queries
Framework built on Dune's API Documentation
https://duneanalytics.notion.site/API-Documentation-1b93d16e0fa941398e15047f643e003a
"""
from __future__ import annotations

import logging.config
import os
from json import JSONDecodeError
from typing import Dict, Optional, Any

import requests
from requests import Response


# pylint: disable=too-few-public-methods
class BaseDuneClient:
    """
    A Base Client for Dune which sets up default values
    and provides some convenient functions to use in other clients
    """

    BASE_URL = "https://api.dune.com"
    DEFAULT_TIMEOUT = 10

    def __init__(
        self, api_key: str, client_version: str = "v1", performance: str = "medium"
    ):
        self.token = api_key
        self.client_version = client_version
        self.performance = performance
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(message)s")

    @classmethod
    def from_env(cls) -> BaseDuneClient:
        """
        Constructor allowing user to instantiate a client from environment variable
        without having to import dotenv or os manually
        We use `DUNE_API_KEY` as the environment variable that holds the API key.
        """
        return cls(os.environ["DUNE_API_KEY"])

    @property
    def api_version(self) -> str:
        """Returns client version string"""
        return f"/api/{self.client_version}"

    def default_headers(self) -> Dict[str, str]:
        """Return default headers containing Dune Api token"""
        return {"x-dune-api-key": self.token}


class BaseRouter(BaseDuneClient):
    """Extending the Base Client with elementary api routing"""

    def _handle_response(self, response: Response) -> Any:
        """Generic response handler utilized by all Dune API routes"""
        try:
            # Some responses can be decoded and converted to DuneErrors
            response_json = response.json()
            self.logger.debug(f"received response {response_json}")
            return response_json
        except JSONDecodeError as err:
            # Others can't. Only raise HTTP error for not decodable errors
            response.raise_for_status()
            raise ValueError("Unreachable since previous line raises") from err

    def _route_url(self, route: str) -> str:
        return f"{self.BASE_URL}{self.api_version}{route}"

    def _get(
        self,
        route: str,
        params: Optional[Any] = None,
        raw: bool = False,
    ) -> Any:
        """Generic interface for the GET method of a Dune API request"""
        url = self._route_url(route)
        self.logger.debug(f"GET received input url={url}")
        response = requests.get(
            url=url,
            headers=self.default_headers(),
            timeout=self.DEFAULT_TIMEOUT,
            params=params,
        )
        if raw:
            return response
        return self._handle_response(response)

    def _post(self, route: str, params: Optional[Any] = None) -> Any:
        """Generic interface for the POST method of a Dune API request"""
        url = self._route_url(route)
        self.logger.debug(f"POST received input url={url}, params={params}")
        response = requests.post(
            url=url,
            json=params,
            headers=self.default_headers(),
            timeout=self.DEFAULT_TIMEOUT,
        )
        return self._handle_response(response)

    def _patch(self, route: str, params: Any) -> Any:
        """Generic interface for the PATCH method of a Dune API request"""
        url = self._route_url(route)
        self.logger.debug(f"PATCH received input url={url}, params={params}")
        response = requests.request(
            method="PATCH",
            url=url,
            json=params,
            headers={"x-dune-api-key": self.token},
            timeout=self.DEFAULT_TIMEOUT,
        )
        return self._handle_response(response)
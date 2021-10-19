from typing import Any, Optional
import json

import requests

from quickforex.logger import get_module_logger


logger = get_module_logger(__name__)


class HttpRequesterBase(object):
    def __init__(self, api_url: str):
        self._api_url = api_url

    def response_check_hook(self, response_payload: Any) -> None:
        pass

    def response_transform_hook(self, response_payload: Any) -> Any:
        return response_payload

    def _handle_response(self, response: requests.Response) -> Any:
        response.raise_for_status()
        response_payload = response.json()
        logger.debug(f"received response {json.dumps(response_payload)}")
        self.response_check_hook(response_payload)
        return self.response_transform_hook(response_payload)

    def get(self, endpoint: str, params: Optional[dict[str, str]] = None) -> Any:
        resource_url = f"{self._api_url}/{endpoint}"
        logger.debug(
            f"sending request to {resource_url} with params={json.dumps(params)}"
        )
        response = requests.get(resource_url, params=params)
        return self._handle_response(response)

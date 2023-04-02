import json
import time
from typing import Optional, Any

import requests
import logging
from requests.auth import AuthBase, HTTPBasicAuth, HTTPProxyAuth, HTTPDigestAuth


class VSphereClientException(Exception):
    """An exception raised when an unexpected situation occurs inside the VSphere client."""


class VSphereClientBuilderException(Exception):
    """An exception raised when the builder failed to build the client."""


API_SESSION_PATH = '/rest/com/vmware/cis/session'
CONNECTION_RETRY = 5
CONNECTION_RETRY_DELAY_SEC = 5
REQUEST_RETRY_DELAY_SEC = 5


class VSphereClient:
    """An API client specialized for VSphere API"""

    def __init__(self,
                 url: str,
                 auth: AuthBase,
                 timeout: Optional[int] = None,
                 ssl_verify: bool = True):
        self._url = url
        self._auth = auth
        self._timeout = timeout

        # Init session
        self._session = requests.Session()
        self._session.verify = ssl_verify

    def connect(self):
        logging.debug(f"Connecting to the vSphere {self._url}...")
        for i in range(CONNECTION_RETRY):
            response = self._session.post(self.make_url(API_SESSION_PATH), auth=self._auth)
            if response.status_code in (200, 201):
                break
            logging.error(f"Failed to connect to vSphere {self._url}. Retry {i + 1}/{CONNECTION_RETRY}...")
            time.sleep(CONNECTION_RETRY_DELAY_SEC)
        else:
            msg = f"Not able to connect to the vSphere {self._url}"
            logging.critical(msg)
            raise VSphereClientException(msg)
        logging.info(f"Connected to vSphere {self._url}")

    def make_url(self, path: str = '') -> str:
        return f'{self._url}{path}'

    def query(self,
              path: str,
              method: str = 'get',
              data: Optional[dict] = None,
              params: Optional[dict] = None,
              try_count: int = 5,
              response_key: Optional[str] = 'value'
              ) -> Any:
        # Sanitize parameters and data
        params = {} if params is None else params
        data = None if data is None else json.dumps(data)

        # Make the requests
        response, url = self._query(data, method, params, path, try_count)

        # Handle the answer
        logging.debug(f"Request to {url} successful!")
        if response_key:
            return response.json().get(response_key, None)
        return response.json()

    def _query(self, data, method, params, path, try_count):
        url = self.make_url(path)
        for i in range(try_count):
            response = self._session.__getattribute__(method)(
                url,
                params=params,
                data=data,
                timeout=self._timeout,
                auth=self._auth
            )
            if response.status_code in (200, 201):
                break
            logging.error(f"Query to {url} failed. Retry {i + 1}/{try_count}...")
            self.connect()
            time.sleep(REQUEST_RETRY_DELAY_SEC)
        else:
            # If the loop exit normally (no break), the request failed.
            msg = f"Not able to make a request on {url} within {try_count} tries."
            logging.critical(msg)
            raise VSphereClientException(msg)
        return response, url

    def get(self, path, params=None, response_key: Optional[str] = 'value'):
        return self.query(path=path, method='get', params=params, response_key=response_key)

    def post(self, path, data, params=None, response_key: Optional[str] = 'value'):
        return self.query(path=path, method='post', data=data, params=params, response_key=response_key)

    def put(self, path, data, params=None, response_key: Optional[str] = 'value'):
        return self.query(path=path, method='put', data=data, params=params, response_key=response_key)

    def patch(self, path, data, params=None, response_key: Optional[str] = 'value'):
        return self.query(path=path, method='patch', data=data, params=params, response_key=response_key)

    def delete(self, path, params=None, response_key: Optional[str] = 'value'):
        return self.query(path=path, method='delete', params=params, response_key=response_key)


class VSphereClientBuilder:
    """Builder for the VSphereClient"""

    def __init__(self, url: str):
        if url.endswith('/'):
            url = url[:-2]
        self._url = url
        self._auth = None
        self._timeout = None
        self._ssl_verify = False

    def build(self) -> VSphereClient:
        if self._auth is None:
            raise VSphereClientBuilderException("Must set up authentication parameters.")
        return VSphereClient(
            self._url,
            self._auth,
            self._timeout,
            self._ssl_verify
        )

    def with_timeout(self, value: int):
        if value <= 0:
            raise ValueError(f"Invalid timeout value: {value}. Must be greater or equal than 0")
        self._timeout = value
        return self

    def with_ssl_verification(self):
        self._ssl_verify = True
        return self

    def without_ssl_verification(self):
        self._ssl_verify = False
        return self

    def with_http_basic_auth(self, username: str, password: str):
        self._auth = HTTPBasicAuth(username, password)
        return self

    def with_http_proxy_auth(self, username: str, password: str):
        self._auth = HTTPProxyAuth(username, password)
        return self

    def with_http_digest_auth(self, username: str, password: str):
        self._auth = HTTPDigestAuth(username, password)
        return self


def build_client_from_configuration(config: dict) -> VSphereClient:
    builder = VSphereClientBuilder(config['url'])

    auth = config['authentication']
    if 'basic' in auth:
        builder.with_http_basic_auth(auth['basic']['username'], auth['basic']['password'])
    elif 'proxy' in auth:
        raise NotImplementedError()
    elif 'digest' in auth:
        raise NotImplementedError()

    if 'ssl' in config:
        if auth['ssl'] is True:
            builder.with_ssl_verification()
        else:
            builder.without_ssl_verification()

    if 'timeout' in config:
        builder.with_timeout(config['timeout'])

    return builder.build()

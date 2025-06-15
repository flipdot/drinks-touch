from datetime import datetime, timedelta
from urllib.parse import urlparse

import config
import requests


class KeycloakAdmin:
    def __init__(
        self, client_id=None, client_secret=None, oidc_discovery_url=None, timeout=10
    ):
        self.client_id = client_id or config.OIDC_CLIENT_ID
        self.client_secret = client_secret or config.OIDC_CLIENT_SECRET
        self.oidc_discovery_url = oidc_discovery_url or config.OIDC_DISCOVERY_URL
        self.access_token = None
        self.access_token_expires_at = datetime.now()
        self.token_endpoint = None
        self.admin_base_url = None
        self.timeout = timeout

    def _reload_oidc_discovery(self):
        discovery_response = requests.get(self.oidc_discovery_url, timeout=self.timeout)
        discovery_response.raise_for_status()
        discovery = discovery_response.json()
        self.token_endpoint = discovery["token_endpoint"]
        self.userinfo_endpoint = discovery["userinfo_endpoint"]
        self.issuer = discovery["issuer"]
        parsed = urlparse(self.issuer)
        self.admin_base_url = (
            parsed.scheme + "://" + parsed.netloc + "/admin" + parsed.path
        )

    def login(self):
        if self.token_endpoint is None:
            self._reload_oidc_discovery()

        token_response = requests.post(
            self.token_endpoint,
            data={
                "grant_type": "client_credentials",
                "client_id": config.OIDC_CLIENT_ID,
                "client_secret": config.OIDC_CLIENT_SECRET,
            },
            timeout=self.timeout,
        )
        token_response.raise_for_status()
        token = token_response.json()
        self.access_token = token["access_token"]
        self.access_token_expires_at = (
            datetime.now()
            + timedelta(seconds=token["expires_in"])
            - timedelta(seconds=config.OIDC_REFRESH_BUFFER)
        )

    def get_user_list(self, **kwargs):
        return self._admin_request("/users", **kwargs)

    def _admin_request(self, path: str, stream: bool = False):
        assert path.startswith("/"), "Path must start with /"
        if self.access_token is None or self.access_token_expires_at < datetime.now():
            self.login()

        res = requests.get(
            self.admin_base_url + path,
            headers={"Authorization": f"Bearer {self.access_token}"},
            stream=stream,
            timeout=self.timeout,
        )
        res.raise_for_status()
        if stream:
            return res
        else:
            return res.json()


# Example usage:
if __name__ == "__main__":
    from pprint import pprint

    admin = KeycloakAdmin()
    users = admin.get_user_list()
    pprint(users)

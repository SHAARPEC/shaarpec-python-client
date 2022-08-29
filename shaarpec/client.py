"""Client for SHAARPEC Analytics API."""
from __future__ import annotations
from typing import Union

import httpx

from oidcish.device import DeviceFlow, DeviceSettings
from oidcish.code import CodeFlow, CodeSettings


class Client:
    """Client for SHAARPEC Analytics API.

    The input is the base URL to the Analytics API and authentication credentials via device or
    code flow. The `.with_device(...)` and `.with_code(...)` class methods are provided and can
    be used to construct a client . See examples of usage.

    API data is returned as `httpx.Response` objects.
    \f
    Examples
    --------
    >>> from shaarpec import Client
    >>> client = Client.with_device(
            "https://api.shaarpec.com/",
            auth={"host": "https://idp.shaarpec.com"})
        )
    >>> client.get("terminology/allergy_type").json()
    {'419263009': 'Allergy to tree pollen',
     '420174000': 'Allergy to wheat',
     '425525006': 'Allergy to dairy product',
     '714035009': 'Allergy to soya',
     '419474003': 'Allergy to mould',
     '232347008': 'Dander (animal) allergy',
     '91934008': 'Allergy to nut',
     '417532002': 'Allergy to fish',
     '300913006': 'Shellfish allergy',
     '232350006': 'House dust mite allergy',
     '418689008': 'Allergy to grass pollen',
     '91935009': 'Allergy to peanuts',
     '91930004': 'Allergy to eggs',
     '300916003': 'Latex allergy',
     '424213003': 'Allergy to bee venom'}
    >>> client.get("population", conditions=["T78.2", "K81.0"])
    [{'patient_origin_id': '4c92f494-3c98-f8dd-1473-da9eb0196f6f',
        'age': '10-16',
        'is_alive': True,
        'gender': 'F',
        'deceased_year': 0},
    ...
    """

    def __init__(self, host: str, auth: Union[CodeFlow, DeviceFlow], **kwargs) -> None:
        timeout = kwargs.pop('timeout',60)
        self._auth = auth
        self._client = httpx.Client(
            base_url=host,
            timeout=timeout,
            headers={"accept": "application/json"},
            **kwargs
        )

    @classmethod
    def with_device(cls, host: str, auth: DeviceSettings, **kwargs) -> Client:
        """Authenticate with IDP server using device flow.

        The client on the IDP server must support device flow. Authentication arguments can be
        provided as keywords or omitted and read from a .env file in the working directory.
        The environment variables are prefixed with OIDCISH, so OIDCISH_CLIENT_ID etc.
        \f
        Parameters
        ----------
          host : str
            The IDP host name.
          **kwargs : Authentication details and other arguments.

            Valid authentication arguments are:
              client_id: str, The client ID.
              client_secret: str, The client secret.
              scope: str, A space separated, case-sensitive list of scopes.
                          (Default = openid profile offline_access)
              audience: str = The access claim was designated for this audience.

        Examples
        --------
        >>> from shaarpec import Client
        >>> client = Client.with_device(
                "https://api.shaarpec.com",
                auth={
                    "host": "https://idp.example.com",
                    "client_id": ...,
                    "client_secret": ...,
                    "scope": ...,
                    "audience": ...,
                }
            )
        # Or, read auth variables from .env in working dir
        >>> client = Client.with_device(
                "https://api.shaarpec.com",
                auth={"host": "https://idp.example.com"}
            )
        >>> client.get("terminology/allergy_type").json()
        ...
        """
        auth_dict = dict(auth)
        auth_host = auth_dict.pop("host")
        return cls(host=host, auth=DeviceFlow(host=auth_host, **auth_dict), **kwargs)

    @classmethod
    def with_code(cls, host: str, auth: CodeSettings, **kwargs) -> Client:
        """Authenticate with IDP server using code flow.

        The client on the IDP server must support code flow. Authentication arguments can be
        provided as keywords or omitted and read from a .env file in the working directory.
        The environment variables are prefixed with OIDCISH, so OIDCISH_CLIENT_ID etc.
        \f
        Parameters
        ----------
          host : str
            The IDP host name.
          **kwargs : Authentication details and other arguments.

            Valid authentication arguments are:
              client_id: str, The client ID.
              client_secret: str, The client secret.
              redirect_uri: str, Must exactly match one of the allowed redirect URIs for the client.
                                 (Default = http://localhost)
              username: str = The user name.
              password: str = The user password.
              scope: str, A space separated, case-sensitive list of scopes.
                          (Default = openid profile offline_access)
              audience: str = The access claim was designated for this audience.

        Examples
        --------
        >>> from shaarpec import Client
        >>> client = Client.with_code(
                "https://api.shaarpec.com",
                auth={
                    "host": "https://idp.example.com",
                    "client_id": ...,
                    "client_secret": ...,
                    "redirect_uri": ...,
                    "username": ...,
                    "password": ...,
                    "scope": ...,
                    "audience": ...,
                }
            )
        # Or, read auth variables from .env in working dir
        >>> client = Client.with_code(
                "https://api.shaarpec.com",
                auth={"host": "https://idp.example.com"}
            )
        >>> client.get("terminology/allergy_type").json()
        ...
        """
        auth_dict = dict(auth)
        auth_host = auth_dict.pop("host")
        return cls(host=host, auth=CodeFlow(host=auth_host, **auth_dict), **kwargs)

    @property
    def auth(self) -> Union[CodeFlow, DeviceFlow]:
        """Return the authentication credentials."""
        return self._auth

    def get(self, uri: str, **kwargs) -> httpx.Response:
        """Get the resource at `uri`.

        Keyword arguments are passed as query parameters.
        """
        access_token = (
            self.auth.credentials.access_token
            if self.auth.credentials is not None
            else "no-token"
        )
        response = self._client.get(
            uri,
            headers={
                "Authorization": f"Bearer {access_token}",
                "x-auth-request-access-token": access_token,
            },
            params=kwargs,
        )

        return response

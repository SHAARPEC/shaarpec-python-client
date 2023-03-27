"""Client for SHAARPEC Analytics API."""
from __future__ import annotations
from typing import Optional, Union, Any
import pathlib
import time

import background
import httpx

from oidcish import DeviceFlow, CodeFlow, CredentialsFlow

from shaarpec.tasks import Task


class Client:
    """Client for SHAARPEC Analytics API.

    The input is the base URL to the Analytics API and authentication credentials via device or
    code flow. The `.with_device(...)` and `.with_code(...)` class methods are provided and can
    be used to construct a client. See examples of usage.

    API data is returned as `httpx.Response` objects.
    \f
    Examples
    --------
    >>> from shaarpec import Client
    >>> client = Client.with_device(
            host="https://api.shaarpec.com/",
            auth={
                "host": "https://idp.shaarpec.com"
                "client_id": ...,
                "client_secret": ...,
                "audience": ...,
                "scope": ...
            }
        )
    # Or
    # >>> client = Client.with_device(
    #        host="https://api.shaarpec.com/",
    #        auth="./path/to/my/env.file"
    #    )
    #
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

    def __init__(
        self, host: str, auth: Optional[Union[CodeFlow, DeviceFlow]], **kwargs
    ) -> None:
        timeout = kwargs.pop("timeout", 60)
        self._auth = auth
        self._client = httpx.Client(
            base_url=host,
            timeout=timeout,
            headers={"accept": "application/json"},
            **kwargs,
        )

    @classmethod
    def with_device(
        cls, host: str, auth: Union[dict[str, Any], str, None], **kwargs
    ) -> Client:
        """Authenticate with IDP host using device flow.

        The IDP host must support device flow. Authentication can be provided to
        `auth` as a dict, as environment variables, or as the path to an env file. The
        environment variables are always prefixed with OIDCISH, so OIDCISH_CLIENT_ID
        etc.
        \f
        Parameters
        ----------
          host : str
            The Analytics API base URL.
          auth : dict or string
            Authentication details and other arguments.

            If dict, then valid keywords in this dict are:
              host: str, The IDP host name (OIDCISH_HOST).
              client_id: str, The client ID (OIDCISH_CLIENT_ID).
              client_secret: str, The client secret (OIDCISH_CLIENT_SECRET).
              scope: str, A space separated, case-sensitive list of scopes
                (OIDCISH_SCOPE).
                          (default: openid profile offline_access)
              audience: str, The access claim was designated for this audience
                (OIDCISH_AUDIENCE).

            If string, then path to file with the corresponding variables.


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
        # Or, read auth variables from env file
        >>> client = Client.with_device(
                host="https://api.shaarpec.com",
                auth="path/to/my/file.env"
            )
        >>> client.get("terminology/allergy_type").json()
        ...
        """
        match auth:
            case None:
                return cls(host=host, auth=None, **kwargs)
            case str():
                return cls(host=host, auth=DeviceFlow(_env_file=auth), **kwargs)
            case dict():
                auth_host = auth.pop("host")
                return cls(host=host, auth=DeviceFlow(host=auth_host, **auth), **kwargs)
            case _:
                raise TypeError(
                    f"Object {auth} is not of recognized type ({type(auth)})."
                )

    @classmethod
    def with_code(
        cls, host: str, auth: Optional[dict[str, Any]] = None, **kwargs
    ) -> Client:
        """Authenticate with IDP server using code flow.

        The IDP host must support authorization code flow. Authentication can be
        provided to `auth` as a dict, as environment variables, or as the path to an
        env file. The environment variables are always prefixed with OIDCISH, so
        OIDCISH_CLIENT_ID etc.
        \f
        Parameters
        ----------
          host : str
             The Analytics API base URL.
          auth : dict or str,
            Authentication details and other arguments.

            If dict, then valid keyword in this dict are:
              host: str, The IDP host name (OIDCISH_HOST).
              client_id: str, The client ID (OIDCISH_CLIENT_ID).
              client_secret: str, The client secret (OIDCISH_CLIENT_SECRET).
              redirect_uri: str, Must exactly match one of the allowed redirect URIs
                for the client (OIDCISH_REDIRECT_URI).
                (default: http://localhost)
              username: str = The user name (OIDCISH_USERNAME).
              password: str = The user password (OIDCISH_PASSWORD).
              scope: str, A space separated, case-sensitive list of scopes
                (OIDCISH_SCOPE).
                          (default: openid profile offline_access)
              audience: str = The access claim was designated for this audience
                (OIDCISH_AUDIENCE).

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
        # Or, read auth variables from env file
        >>> client = Client.with_code(
                host="https://api.shaarpec.com",
                auth="path/to/my/file.env"
            )
        >>> client.get("terminology/allergy_type").json()
        ...
        """
        match auth:
            case None:
                return cls(host=host, auth=None, **kwargs)
            case str():
                return cls(host=host, auth=CodeFlow(_env_file=auth), **kwargs)
            case dict():
                auth_host = auth.pop("host")
                return cls(host=host, auth=CodeFlow(host=auth_host, **auth), **kwargs)
            case _:
                raise TypeError(
                    f"Object {auth} is not of recognized type ({type(auth)})."
                )

    @classmethod
    def with_credentials(
        cls, host: str, auth: Union[dict[str, Any], str, None], **kwargs
    ) -> Client:
        """Authenticate with IDP host using client credentials flow.

        The IDP host must support client credentials flow. Authentication can be provided to
        `auth` as a dict, as environment variables, or as the path to an env file. The
        environment variables are always prefixed with OIDCISH, so OIDCISH_CLIENT_ID
        etc.
        \f
        Parameters
        ----------
          host : str
            The Analytics API base URL.
          auth : dict or string
            Authentication details and other arguments.

            If dict, then valid keywords in this dict are:
              host: str, The IDP host name (OIDCISH_HOST).
              client_id: str, The client ID (OIDCISH_CLIENT_ID).
              client_secret: str, The client secret (OIDCISH_CLIENT_SECRET).
              audience: str, The access claim was designated for this audience
                (OIDCISH_AUDIENCE).

            If string, then path to file with the corresponding variables.

        Examples
        --------
        >>> from shaarpec import Client
        >>> client = Client.with_credentials(
                "https://api.shaarpec.com",
                auth={
                    "host": "https://idp.example.com",
                    "client_id": ...,
                    "client_secret": ...,
                    "audience": ...,
                }
            )
        # Or, read auth variables from env file
        >>> client = Client.with_credentials(
                host="https://api.shaarpec.com",
                auth="path/to/my/file.env"
            )
        >>> client.get("terminology/allergy_type").json()
        ...
        """
        match auth:
            case None:
                return cls(host=host, auth=None, **kwargs)
            case str():
                return cls(host=host, auth=CredentialsFlow(_env_file=auth), **kwargs)
            case dict():
                auth_host = auth.pop("host")
                return cls(host=host, auth=CredentialsFlow(host=auth_host, **auth), **kwargs)
            case _:
                raise TypeError(
                    f"Object {auth} is not of recognized type ({type(auth)})."
                )

    @classmethod
    def without_auth(cls, host: str, **kwargs) -> Client:
        """Create a client that does not use authentication.

        \f
        Parameters
        ----------
          host : str
            The Analytics API base URL.

        Examples
        --------
        >>> from shaarpec import Client
        >>> client = Client.without_auth("https://api.shaarpec.com")
        >>> client.get("terminology/allergy_type").json()
        ...
        """
        return cls(host=host, auth=None, **kwargs)

    @property
    def auth(self) -> Optional[Union[CodeFlow, DeviceFlow]]:
        """Return the authentication credentials."""
        return self._auth

    def get(self, uri: str, **kwargs) -> httpx.Response:
        """Get the resource at `uri`.

        Keyword arguments are passed as query parameters.
        """
        headers = {}

        if (auth := self.auth) is not None:
            if (credentials := auth.credentials) is not None:
                access_token = credentials.access_token

                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "x-auth-request-access-token": access_token,
                }

        response = self._client.get(
            uri,
            headers=headers,
            params=kwargs,
        )

        return response

    # pylint: disable=too-many-arguments
    def post(
        self, uri: str, content=None, data=None, files=None, json=None, **kwargs
    ) -> httpx.Response:
        """Post to the resource at `uri`.

        Keyword arguments are passed as query parameters.
        """
        headers = {}

        if (auth := self.auth) is not None:
            if (credentials := auth.credentials) is not None:
                access_token = credentials.access_token

                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "x-auth-request-access-token": access_token,
                }

        response = self._client.post(
            uri,
            content=content,
            data=data,
            files=files,
            json=json,
            headers=headers,
            params=kwargs,
        )

        return response

    def run(
        self,
        uri: str,
        content=None,
        data=None,
        files=None,
        json=None,
        poll_interval: float = 0.1,
        progress_bar: bool = True,
        **kwargs,
    ) -> Task:
        """Run a task at resource `uri`.

        A task is equivalent to posting and polling until the job is finished.

        Keyword arguments are passed as query parameters.
        """
        service = pathlib.Path(uri).parts[0]

        response = self.post(
            uri=uri, content=content, data=data, files=files, json=json, **kwargs
        )

        match response.status_code:
            case 202:
                pass
            case 401:
                raise RuntimeError("401: Not authenticated.")
            case _:
                raise RuntimeError(
                    "Did not receive 202 Accepted for the task. "
                    f"The actual response code was {response.status_code}. "
                    f"The actual message was {response.text}."
                )

        task_id = response.json().get("task_id")
        submitted_at = response.json().get("submitted_at")

        task = Task(
            service=service,
            task_id=task_id,
            submitted_at=submitted_at,
            status="submitted",
            success=None,
            progress=None,
            result=None,
            error=None,
            debugger=None,
        )

        if progress_bar:
            task.print()

        self._wait_for_task(task, poll_interval=poll_interval)

        return task

    @background.task
    def _wait_for_task(self, task: Task, poll_interval: float = 0.1) -> None:
        while task.status in ("submitted", "queued", "in_progress"):
            response = self.get(f"{task.service}/tasks/{task.task_id}/status")

            match response.status_code:
                case 401:
                    print(
                        f"Not authorized to run task id {task.task_id} on service {task.service}."
                    )
                    task.success = False
                    task.status = "unauthorized"

                case 404:
                    print(
                        f"Task with id {task.task_id} could not be found on service {task.service}."
                    )
                    task.success = False
                    task.status = "not_found"

                case 200:
                    match response.json():
                        case {"status": "not_found"}:
                            print(
                                f"Task with id {task.task_id} "
                                f"could not be found on service {task.service}."
                            )
                            task.status = "not_found"

                        case {"status": "in_progress" | "queued"} as data:
                            task.progress = data.get("progress")
                            task.status = data.get("status")
                            time.sleep(poll_interval)

                        case {"status": "complete", "success": True} as data:
                            resp = self.get(
                                f"{task.service}/tasks/{task.task_id}/results"
                            )

                            task.result = resp.json().get("result")
                            task.progress = 1.0
                            task.success = True
                            task.status = "complete"

                        case _ as data:
                            task.error = data.get("error")
                            task.success = False
                            task.status = "complete"

                case _:
                    print(f"An error occurred on service {task.service}.")
                    task.error = response.json().get("error")
                    task.success = False
                    task.status = "error"

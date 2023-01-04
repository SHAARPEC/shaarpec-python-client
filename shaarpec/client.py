"""Client for SHAARPEC Analytics API."""
from __future__ import annotations
from typing import Optional, Union, Any
import pathlib
import time

from pydantic import BaseModel
from tqdm.notebook import tqdm
import background
import httpx

from oidcish.device import DeviceFlow
from oidcish.code import CodeFlow, CodeSettings


class Task(BaseModel):
    """A running task."""

    service: str
    task_id: str
    submitted_at: str
    status: str
    success: Optional[bool]
    progress: Optional[float]
    result: Optional[Any]
    error: Optional[Any]

    @background.task
    def print(self, update_interval: float = 0.1) -> None:
        """Print the progress of the task."""
        initial = 0 if self.progress is None else int(100 * self.progress)

        with tqdm(initial=initial, total=100) as pbar:
            pbar.set_description(f"Task {self.status}")

            while self.status in ("submitted", "queued", "in_progress"):
                fraction = 0 if self.progress is None else self.progress
                pbar.update(int(100 * fraction) - pbar.n)
                pbar.set_description(f"Task {self.status}")
                time.sleep(update_interval)

            pbar.set_description(
                f"Task completed ({'successfully' if self.success else 'failed'})"
            )


class Client:
    """Client for SHAARPEC Analytics API

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
        timeout = kwargs.pop("timeout", 60)
        self._auth = auth
        self._client = httpx.Client(
            base_url=host,
            timeout=timeout,
            headers={"accept": "application/json"},
            **kwargs,
        )

    @classmethod
    def with_device(cls, host: str, auth: dict[str, Any], **kwargs) -> Client:
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
        auth_host = auth.pop("host")
        return cls(host=host, auth=DeviceFlow(host=auth_host, **auth), **kwargs)

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

    # pylint: disable=too-many-arguments
    def post(
        self, uri: str, content=None, data=None, files=None, json=None, **kwargs
    ) -> httpx.Response:
        """Post to the resource at `uri`.

        Keyword arguments are passed as query parameters.
        """
        access_token = (
            self.auth.credentials.access_token
            if self.auth.credentials is not None
            else "no-token"
        )
        response = self._client.post(
            uri,
            content=content,
            data=data,
            files=files,
            json=json,
            headers={
                "Authorization": f"Bearer {access_token}",
                "x-auth-request-access-token": access_token,
            },
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


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/SHAARPEC/shaarpec-python-client">
    <img src="images/logo.png" alt="Logo" width="248" height="95">
  </a>

  <p align="center">
    Python client for SHAARPEC Analytics API.
    <br />
    <a href="https://github.com/SHAARPEC/shaarpec-python-client"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/SHAARPEC/shaarpec-python-client">View Demo</a>
    ·
    <a href="https://github.com/SHAARPEC/shaarpec-python-client/issues">Report Bug</a>
    ·
    <a href="https://github.com/SHAARPEC/shaarpec-python-client/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![SHAARPEC API screenshot][product-screenshot]](https://www.shaarpec.com)

This is a Python client for simple access to the SHAARPEC Analytics API. Authentication is handled automatically via device flow, authorization code flow, or client credentials flow. Authentication can also be disabled if accessing a public Analytics API.

The SHAARPEC Analytics API provides calculations on the healthcare organization's resources, capacities, clinical outcomes, and much more. These results can be accessed via a standard REST API, which is usually protected by the SHAARPEC Identity Server.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

* [![Httpx][Httpx]][Httpx]
* [![Python][Python]][Python-url]

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

The shaarpec client is used as a standard Python library. It is always a good idea to install the library in a virtual environment.

### Installation

1. Install the library into your virtual environment.
   ```bash
   pip install shaarpec
   ```
2. Store your credentials to the SHAARPEC IdentityServer in an .env file.
   ```bash
   $ cat .env
   OIDCISH_HOST="https://idp.example.com"
   OIDCISH_CLIENT_ID="my client id"
   OIDCISH_CLIENT_SECRET="my client secret"
   OIDCISH_AUDIENCE="shaarpec_api.full_access_scope"
   OIDCISH_SCOPE="openid shaarpec_api.full_access_scope offline_access"
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

This library provides a Client class to easily interact with the SHAARPEC Analytics API. The class methods `Client.with_device(...)`,  `Client.with_code(...)`, and `Client.with_credentials(...)` create clients that authenticate with the SHAARPEC IdentityServer with either device flow (not tied to an individual user, recommended), code flow (tied to an individual user, for debugging and development), or credentials flow (non-interactive). There is also a class method `Client.without_auth(...)` that does not invoke the IDP server (but will only work if the Analytics API is public, otherwise give 401 Authentication invalid errors).

All API data is returned as `httpx.Response` objects.

Let's look at some code examples on how to get data from the Analytics API. First, import the client.
```python
from shaarpec import Client
```

Next, use [device flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/device-authorization-flow) or [code flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow) to connect the client to the API with the `Client.with_device(...)`, `Client.with_code(...)`, and/or `Client.with_credentials(...)` class methods.

The credentials can either be stored in a .env file in the working directory (as explained in the Prerequisites section), provided as a path, or given directly as arguments to the `auth` dict.
```python
# Create a client with device flow, give authentication details directly.
client = Client.with_device(
        host="https://api.shaarpec.com/",
        auth={
            "host": "https://idp.shaarpec.com",
            "client_id": ...,
            "client_secret": ...,
            "scope": ...,
            "audience": ...
        }
    )
# Create a client with device flow, read authentication details from .env file.
client = Client.with_device(host="https://api.shaarpec.com/", auth="path/to/.env")
```
Here `host` is the base URL to the Analytics API and `auth` is a dictionary with the login credentials. With device flow, the user needs to finish the sign-in by visiting a url provided by the IdentityServer. A message will be shown:

> Visit https://idp.shaarpec.com/device?userCode=XXXXXXXXX to complete sign-in.

The user visits the website, verifies that the user code is correct and confirms the sign-in. After a few seconds, the client will confirm the sign-in:

> SUCCESS: Authentication was successful. Took XX.Y seconds.

The client is now connected to the API. Visit the Analytics API Base URL to interactively test the endpoints and read their documentation and about their path and query parameters. These parameters are used in the regular (`requests` and `httpx`) way with `client.verb` calls, where `verb` is either `get` or `post`. 

### GET and POST

The `get` and `post` verbs are supported in the standard way. For example (API responses are returned as `httpx.Response` objects):
```python
client.get("terminology/allergy_type").json()
```
might return
```
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
```
or
```python
client.get("population", conditions=["T78.2", "K81.0"])
```
might return
```
[{'patient_origin_id': '4c92f494-3c98-f8dd-1473-da9eb0196f6f',
    'age': '10-16',
    'is_alive': True,
    'gender': 'F',
    'deceased_year': 0},
 ...
]
```

### Running tasks

SHAARPEC Analytics API supports long-running tasks by `POST`:ing to `/service/path/to/endpoint`, and then polling with `GET` to `/service/tasks/{task_id}/status` until the result becomes available at `/service/tasks/{task_id}/results`. There is a `run` function in the library that performs this pattern.

For example

```python
task = client.run("population/conditions")
```

will return a task with the comorbidities in the entire population. A task is a [Pydantic](https://docs.pydantic.dev/) model with the following properties:

```python
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
    debugger: Optional[Any]
```
As you can see, the success, progress, result and error are optional and updated automatically when available. The method comes with a progress bar which can be disabled via `client.run("path/to/task", progress_bar=False)`. If you want to use the task result in a subsequent command, you can wait (blocking) for the result with the `task.wait_for_result()` method:

```python
task = client.run("path/to/task")
print(f"The result is: {task.wait_for_result()}!")
```



<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/SHAARPEC/shaarpec-python-client/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

SHAARPEC Support - support@shaarpec.com

Project Link: [https://github.com/SHAARPEC/shaarpec-python-client](https://github.com/SHAARPEC/shaarpec-python-client)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/SHAARPEC/shaarpec-python-client.svg?style=for-the-badge
[contributors-url]: https://github.com/SHAARPEC/shaarpec-python-client/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/SHAARPEC/shaarpec-python-client.svg?style=for-the-badge
[forks-url]: https://github.com/SHAARPEC/shaarpec-python-client/network/members
[stars-shield]: https://img.shields.io/github/stars/SHAARPEC/shaarpec-python-client.svg?style=for-the-badge
[stars-url]: https://github.com/SHAARPEC/shaarpec-python-client/stargazers
[issues-shield]: https://img.shields.io/github/issues/SHAARPEC/shaarpec-python-client.svg?style=for-the-badge
[issues-url]: https://github.com/SHAARPEC/shaarpec-python-client/issues
[license-shield]: https://img.shields.io/github/license/SHAARPEC/shaarpec-python-client?style=for-the-badge
[license-url]: https://github.com/SHAARPEC/shaarpec-python-client/blob/master/LICENSE
[product-screenshot]: images/screenshot.png
[Httpx]: images/httpx.svg
[Httpx-url]: https://www.python-httpx.org/
[Python]: images/python-3.8.svg
[Python-url]: https://www.python.org/

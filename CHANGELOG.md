## 2.4.0 (July 6, 2023)

-   Migrated to ruff for linting.
-   Migrated to pydantic v2.
-   Upgraded all dependencies.

## 2.3.3 (May 8, 2023)

-   Fixed progressbar in jupyter again.

## 2.3.2 (May 2, 2023)

-   Fix string format bug when raising failed task error (PR https://github.com/SHAARPEC/shaarpec-python-client/pull/3).

## 2.3.1 (April 6, 2023)

-   Upgrade to latest version of oidcish with fixed refresh flow for client credentials.

## 2.3.0 (March 27, 2023)

-   Add support for client credentials flow.
-   Update dependencies.

## 2.2.2 (February 24, 2023)

-   Fixed package dependency for progressbar.

## 2.2.1 (February 23, 2023)

-   Fixed progressbar in console and notebook (see https://github.com/tqdm/tqdm/issues/1359).

## 2.2.0 (February 22, 2023)

-   Add connect without authentication.
-   Better handling of 401 error.
-   Fix progress bar in jupyter.
-   Upgrade dependencies.

## 2.1.0 (January 12, 2023)

-   Add function that waits for task result.
-   Check that task was accepted before proceeding.

## 2.0.1 (January 5, 2023)

-   Fix and update dependencies.

## 2.0.0 (January 5, 2023)

-   Add `client.run` method to run tasks in the API.
-   Add `client.post` method to POST to API.

## 1.0.1 (August 29, 2022)

-   Add 60 s client timeout by default.
-   Security updates.

## 1.0.0 (July 8, 2022)

-   Initial release.

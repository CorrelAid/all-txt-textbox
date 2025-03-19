# all.txt
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## :warning: Disclaimer :warning:

### Disclaimer 🇩🇪
Dies ist ein read-only Repository / Mirror, das den Frontend- und Backend-Code für den [Text-Box-Prototyp](https://box.all-txt.de/) enthält, der im Rahmen des Datenprojekts zwischen [all.txt](https://all-txt.de) und dem [Civic Data Lab](https://civic-data.de) entwickelt wurde. Der Code wurde entwickelt von [&effect data solutions GmbH](https://and-effect.com) basierend auf früheren Ideen und Skripten des all.txt-Teams. Der Code ist unter der MIT-Lizenz verfügbar (siehe LICENSE sowie weitere Hinweise für mehr Informationen). Code und Dokumentation ist in Englisch.

Weitere Hinweise:

- Teile des Codes, die maßgeblich auf geistigem Eigentum des all.txt-Teams beruhen, sind in dieser Open-Source-Version nicht enthalten - der Code ist dementsprechend kommentiert. Dies betrifft Teile von `backend/src/pipelines/gender_neutralizer.py` und `backend/src/database/migrations/data/gender-dictionary.yaml`.
- Der CI/CD-Setup (`gitlab-ci.yml`) ist spezifisch für GitLab. 

### Disclaimer 🇬🇧
This is a read-only repository / mirror of the repository containing the frontend and backend code for the [textbox prototype](https://box.all-txt.de/) that was developed as part of the data project (Datenvorhaben) between [all.txt](https://all-txt.de) and the [Civic Data Lab](https://civic-data.de). Developed by [&effect data solutions GmbH](https://and-effect.com) based on earlier ideas and scripts by the all.txt team. Code is available is under the MIT license (see LICENSE and further pointers for details). 

Further pointers:

- Parts of the code that are significantly based on intellectual property from the all.txt team are excluded in this open source version, they are marked as such. This affects parts of `backend/src/pipelines/gender_neutralizer.py` and `backend/src/database/migrations/data/gender-dictionary.yaml`.
- The CI/CD setup (`gitlab-ci.yml`) is specific to GitLab. 

## Development

### Start Local Development Server

#### Requirements

Please install the following requirements to get started with the local development environment.

- [Docker Desktop](https://docs.docker.com/get-docker/)
- [Node.js](https://nodejs.org/en/download/)
- [Poetry](https://python-poetry.org/docs/)
- [Python 3.11](https://www.python.org/downloads/)

#### Database and Cache

The PostgreSQL database and Redis cache are running in Docker containers. To start the database and
cache, run the following command:

```bash
docker compose up
```

You can stop the database and cache by pressing `Ctrl + C` in the terminal.

#### Backend

To install the current setup execute the following commands. Please ensure that you have `poetry`
installed to manage the backend dependencies.

```bash
cd backend
poetry install --no-root
```

Activate the environment with:

```bash
poetry shell
```

To start the backend server in reload mode, run the following command. The backend is started per
default on port `8000`. The automatically generated API documentation is available at
<http://localhost:8000/docs>.  

```bash
cd backend/src
uvicorn api:app --reload
```

#### Frontend

To install the current setup execute the following commands. Please ensure that you have `Node.js`
installed to manage the frontend dependencies.

```bash
cd frontend
npm install
```

To start the frontend server in development mode, run the following command. The frontend is started
per default on port `3000`. The frontend is available at <http://localhost:3000>.

```bash
cd frontend
npm run dev
```

You can stop the frontend server by pressing `Ctrl + C` in the terminal.

### Add New Dependencies

### Add, Change, or Delete Database Tables

We are using `SQLAlchemy` for database operations. To make changes to the database, add a new model,
update a model or delete a model in the `models` folder. For new tables, create a new file. For
example, to create a new table called `User`, add the following code:

```python
from datetime import datetime

from models.base import Base
from sqlalchemy import DateTime, String, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
```

After creating the model, import the model in the `models/__init__.py` file and append module export
by adding `User` to the `__all__` list. For example, to import the `User` model, add the following
code:

```python
from models.user import User

__all__ = [
    ...,
    "User",
]
```

We are using `alembic` for database migrations. `rev-id` is the revision id for the migration. `m`
is the message for the migration. Please check `database/migrations/versions` folder for the latest
revision id. The latest revision id is the highest number in the folder. The following command will
automatically create a new migration file in the `database/migrations/versions` folder with the
latest changes in the database models. To create a new migration, run the following command:

```bash
make alembic-revision rev-id="0006" m="Create users table"
```

After creating the migration, apply the migration to the database by running the following command:

```bash
make alembic-upgrade
```

You can also downgrade the migration by running the following command:

```bash
make alembic-downgrade
```

## Deployment

The deployment is configured using Docker Stack. The configuration is stored in the
`docker-swarm.yaml` file. The deployment is configured to run the backend, frontend, and the Redis
cache on a Docker Swarm environment. The traffic is routed through a
[Traefik](https://traefik.io/traefik/) reverse proxy. The PostgreSQL database is running as a
separate service on Scaleway.

The deployment can be executed in a GitLab CI/CD pipeline. The deployment is triggered by pushing
the changes to the remote repository. The containers for the backend and frontend are built and the
images are pushed to the GitLab registry. The building is automatically triggered by the GitLab
CI/CD pipeline. In a second step, the deployment is executed using the `docker stack deploy` command
on a remote Docker context. The services are deployed on a Docker Swarm cluster consisting currently
of a single node. The infrastructure setup is configured in the
[infrastructure repository](https://gitlab.com/devops8602704/infrastructure_all.txt).

Secrets are stored in the GitLab CI/CD environment variables and pasted into the build environment
during the second step. The secrets are configured in the remote Docker context as part of the
deployment and can be accessed by the configured services. The secrets are used to store the
database and Redis cache credentials.

You can start the deployment by pushing the changes to the remote repository and executing the jobs
in the [GitLab CI/CD pipeline](https://gitlab.com/devops8602704/all.txt/-/pipelines) linked to the
latest commit.

> [!IMPORTANT]  
> Please update the database role of the `app_api` user in the PostgreSQL database after making any
> changes to the database. The `app_api` user needs to have the `Read/Write` role for the `all_txt`
> database. The role can be updated in the Scaleway console. Please refer to the [Scaleway documentation](https://www.scaleway.com/en/docs/managed-databases/postgresql-and-mysql/how-to/manage-permissions/) for more
> information on how to update the database role.

## Rate Limiter

The Rate Limiter is a dependency that limits the number of requests a client can make to the server.
The Rate Limiter is based on [FastAPI-Limiter](https://pypi.org/project/fastapi-limiter/) package
and uses Redis as a cache. The Rate Limiter is used to protect the server from abuse and to ensure
that the server is not overwhelmed by too many requests. If the rate limit is exceeded, the server
will return a `429 Too Many Requests` status code with a `Retry-After` header that indicates how
long the client should wait before making another request.

The Rate Limiter can be bypassed by providing an API key (e.g.: `[redacted]`
). The API key is used to identify the client and to allow the client to make requests to the server
. The API key is generated by the server and is unique to the client. The API key is stored in the
Postgres database in the `api_keys` table.

Please use the classmethod `create_api_key` of the `RateLimiterWithApiKey` class to generate new
API keys. The key is automatically written to the database using the `create_api_key` method. You
can use the `comment` argument to add details about the client. Each API key can be uniquely
identified by the `id` field. The `key` field is the actual API secret. The `key` is stored as a
hash in the database. The API key that the client receives combines a prefix, the `id`, and the
decoded secret seperated with a `dash`. The API key needs to be stored in a secure place by the
client. The API key needs to be provided with each request in the `Authorization` header.

```sh
curl -X POST \
  --header 'Authorization: alltxt_11...11_aQ...5C' \
  --header 'Content-Type: application/json' \
  --data '{"text":"Lehrer"}' \
  'http://localhost:8000/'
  
```

### Configure Rate Limiter

You can configure the rate limiter adding the `RateLimiterWithApiKey` dependency to the endpoint.
You can set the number of requests and the time window in the `RateLimiterWithApiKey` dependency.
The following example limits the number of requests to 5 requests per minute. The rate limiter is
applied to the `/rate-limited-endpoint` endpoint.

```python
@app.post(
    path="/rate-limited-endpoint",
    dependencies=[Depends(RateLimiterWithApiKey(times=5, minutes=1))],
)
async def run_expansive_function():
    pass
```

### Generate and store API Keys

New API keys can be generated using the `create_api_key` classmethod of the `RateLimiterWithApiKey`.

```python
from dependencies import RateLimiterWithApiKey
import asyncio


async def main():
    key = await RateLimiterWithApiKey.create_api_key("all.txt Test API Key")
    print(key)

asyncio.run(main())
```

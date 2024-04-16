# Workspace

## Running Airflow in Docker

Before we run Airflow, let's create these folders below first. Please note that if you're using Windows, you can skip this step.

```sh
mkdir -p mnt/dags mnt/logs mnt/plugins mnt/tests
```

On **Linux**, please make sure to configure the Airflow user for the docker-compose:

```sh
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

```sh
docker compose build
docker compose up
```

To stop Airflow, run:

```bash
docker compose down
```

Navigate to the directory containing the HTML files
```sh cd airflow/mnt/dags/output/ ```
Start a simple HTTP server; use the appropriate Python command
```sh poetry run python -m http.server 8000 ```

Need to use ``` streamlit ``` for visualization 

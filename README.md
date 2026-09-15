# ArduPilot MAVLink GUI

Python MAVLink controller and telemetry GUI for ArduPilot vehicles.

## How to Install

### Docker

The `docker` subdirectory contains a Dockerfile as well as a Bash script, `build_docker_image.sh`, for installing an isolated Docker environment with all necessary dependencies for this project.

## Without Docker

### Dependencies

Linux:
- python3
- python3-tk
> Note, system package names can differ across Linux distributions

python:
- pymavlink
> Alternatively, run `python3 -m pip install -r requirements.txt`

## How to Run

If using the Docker environment, first
```
cd docker
./run_docker_container.sh
```

From this directory,
```
python3 main.py
```

----------------------------------------------------------------------------------------------------
Sean Hurley (seandhurley@live.com)  
September 15, 2026
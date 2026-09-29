# Drone Delivery System

A multi-agent drone delivery simulator. Drones pick up and deliver parcels across
a grid that contains static obstacles, dynamic weather events and the other drones
in the fleet. Routing is handled by A*, separation by a simple cooperative
avoidance step, and a PPO policy can be trained to replace the built-in
heuristic controller.

## Features

- Grid world with static and dynamic obstacles
- Fleet of battery-powered drones that fly pickup and delivery legs
- A* pathfinding over the grid
- Cooperative collision avoidance between drones
- Random order generator with expiry
- Weather events that drain battery
- Pluggable policies: heuristic, random walker, PPO
- Gymnasium environment for reinforcement learning
- FastAPI control plane with Prometheus metrics
- Pygame renderer for interactive runs
- Docker image and `docker compose` stack

## Project layout

```
.
├── src/drone_delivery/
│   ├── config/       Settings loaded from the environment or .env
│   ├── core/         Domain model: Grid, Drone, Order, World
│   ├── services/     Simulation, pathfinding, collision avoidance, metrics
│   ├── agents/       Policies that steer the fleet
│   ├── rl/           Gymnasium environment for PPO
│   ├── api/          FastAPI application
│   ├── rendering/    Pygame renderer
│   ├── utils/        Logging and observation helpers
│   └── cli/          Entry points: run_simulation, train, serve
├── tests/            Pytest suite
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

The package uses a `src/` layout, so `import drone_delivery` only resolves after
the project is installed (`pip install -e .`) or when `src` is on `PYTHONPATH`.
Pytest handles the second case through the `pythonpath` setting in
`pyproject.toml`.

## Requirements

- Python 3.10 or newer
- Optional extras: `api` (FastAPI/uvicorn), `viz` (pygame), `rl`
  (gymnasium/stable-baselines3/torch)

## Installation

```bash
git clone https://github.com/Oliprg3/Drone_delivery_system
cd Drone_delivery_system

python -m venv .venv
source .venv/bin/activate

pip install -e ".[all]"        # everything
pip install -e .               # core only, no optional extras
pip install -e ".[api,viz]"    # HTTP API and renderer
```

Copy the example environment file and edit it as needed:

```bash
cp .env.example .env
```

## Usage

### Run a simulation

```bash
drone-sim --agent heuristic --headless --max-steps 1000
# or, without installing the console scripts:
python -m drone_delivery.cli.run_simulation --agent heuristic --headless
```

Available policies are `heuristic` (default), `random` and `rl`. Drop
`--headless` to open the pygame window; close the window to stop the run.

### Start the HTTP API

```bash
drone-api --host 0.0.0.0 --port 8000
# or
uvicorn drone_delivery.api.server:app --reload
```

| Method | Path      | Description                                  |
| ------ | --------- | -------------------------------------------- |
| GET    | `/health` | Liveness probe                               |
| GET    | `/state`  | Fleet, orders, step counter and reward       |
| POST   | `/order`  | Inject an order (`{"pickup": [r, c], "delivery": [r, c]}`) |
| POST   | `/step`   | Advance the simulation by one tick           |
| POST   | `/reset`  | Rebuild the world                            |
| GET    | `/metrics`| Prometheus exposition format                 |

Interactive API docs are served at `/docs`.

### Train the PPO policy

```bash
drone-train --timesteps 50000 --output artifacts/drone_ppo
```

The checkpoint is written to `artifacts/drone_ppo.zip` and picked up
automatically by `--agent rl`. If no checkpoint exists, the RL policy logs a
warning and falls back to the heuristic controller instead of failing.

### Run tests and lint

```bash
make test      # or: python -m pytest
make lint      # or: python -m ruff check src tests
```

## Configuration

Every setting is read from the environment or a local `.env` file; see
`.env.example` for the full list with defaults. The most useful ones:

| Variable         | Default    | Meaning                                    |
| ---------------- | ---------- | ------------------------------------------ |
| `GRID_SIZE`      | `30,30`    | Grid dimensions as `rows,cols`             |
| `OBSTACLE_DENSITY` | `0.15`   | Fraction of blocked cells                  |
| `NUM_DRONES`     | `5`        | Fleet size                                 |
| `ORDER_FREQUENCY`| `0.3`      | Chance an order spawns each step           |
| `MAX_STEPS`      | `10000`    | Episode length                             |
| `API_ENABLED`    | `false`    | `python -m drone_delivery` serves the API  |
| `LOG_LEVEL`      | `INFO`     | Logging level                              |

## Docker

```bash
docker compose up -d api       # start the API on port 8000
docker compose --profile batch run --rm sim   # one headless batch run
docker compose down
```

## License

MIT, see [LICENSE](LICENSE).

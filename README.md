 DRONE DELIVERY SYSTEM

## Features
- Realistic drone physics (battery, speed, cargo)
- Dynamic obstacles and weather (wind, rain)
- A* pathfinding with re‑planning
- Cooperative collision avoidance
- Gym environment for Reinforcement Learning (PPO, DQN)
- REST API for real‑time control and monitoring
- Prometheus metrics
- Dockerised for easy deployment

## Quick Start
```bash
# Clone and install
git clone https://github.com/your-repo/drone_delivery
cd drone_delivery
pip install -r requirements.txt

# Run headless simulation with heuristic agents
python scripts/run_simulation.py --agent heuristic --headless

# Run with visualisation
python scripts/run_simulation.py --agent heuristic

# Start API server
uvicorn api.server:app --reload

# Train RL agent
python scripts/train_rl.py

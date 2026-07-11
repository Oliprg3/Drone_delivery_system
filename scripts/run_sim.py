import argparse
import time
from services.simulation import Simulation
from agents import HeuristicAgent, RandomAgent, RLAgent
from visualization import Renderer
from config import settings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=["heuristic", "random", "rl"], default="heuristic")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    sim = Simulation()
    renderer = None if args.headless else Renderer()
    agents = []
    for i in range(settings.NUM_DRONES):
        if args.agent == "heuristic":
            agents.append(HeuristicAgent(i, sim))
        elif args.agent == "random":
            agents.append(RandomAgent(i, sim))
        else:
            agents.append(RLAgent(i, sim))

    obs = sim.reset()
    for step in range(settings.MAX_STEPS):
        for agent in agents:
            agent.act(obs)  
        obs, reward, done, _ = sim.step([None]*len(agents)) 
        if renderer:
            renderer.render(sim.world)
            time.sleep(0.05)
        if done:
            break

    if renderer:
        renderer.close()
    print(f"Total deliveries: {len(sim.world.completed_orders)}")

if __name__ == "__main__":
    main()

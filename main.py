import random
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Agent-based model parameters
grid_size = (20, 20)
agents = []
commodity_prices = {'Oil': [], 'Wheat': [], 'Gold': []}
tick = 0
running = False
trade_links = []  # Store temporary trade interactions

# Define agent roles and their colors
agent_roles = {
    'Producer': 'green',  # 🟢 Farmers, miners
    'Consumer': 'blue',  # 🔵 Factories, buyers
    'Speculator': 'red'  # 🔴 Traders, hedge funds
}

# Supply and demand tracking
supply_demand = {
    'Oil': {'supply': 10, 'demand': 10},
    'Wheat': {'supply': 10, 'demand': 10},
    'Gold': {'supply': 10, 'demand': 10}
}


def initialize_model():
    """Initialize agents and commodity prices."""
    global agents, tick, commodity_prices
    tick = 0
    agents = [{'x': random.randint(0, grid_size[0] - 1),
               'y': random.randint(0, grid_size[1] - 1),
               'role': random.choice(list(agent_roles.keys()))}
              for _ in range(15)]

    for key in commodity_prices:
        commodity_prices[key] = [random.uniform(50, 150)]  # Set initial prices

    update_display()


def find_trade_partners():
    """Find nearby agents and create trade interactions."""
    global trade_links
    trade_links = []  # Clear previous trade links

    for i, agent in enumerate(agents):
        for j, other_agent in enumerate(agents):
            if i != j:
                if abs(agent['x'] - other_agent['x']) <= 2 and abs(agent['y'] - other_agent['y']) <= 2:

                    commodity = random.choice(list(supply_demand.keys()))  # FIX: Select a commodity

                    # Producer & Consumer Trade
                    if agent['role'] == 'Producer' and other_agent['role'] == 'Consumer':
                        trade_links.append((agent, other_agent))
                        supply_demand[commodity]['supply'] += 1
                        supply_demand[commodity]['demand'] += 1

                        # Speculators influence supply & demand randomly
                    elif agent['role'] == 'Speculator':
                        supply_demand[commodity]['demand'] += random.randint(-1, 1)
                        supply_demand[commodity]['supply'] += random.randint(-1, 1)


def update_model():
    """Update agent positions, simulate trading, and adjust commodity prices."""
    global tick
    tick += 1

    # Move agents randomly
    for agent in agents:
        agent['x'] = (agent['x'] + random.choice([-1, 0, 1])) % grid_size[0]
        agent['y'] = (agent['y'] + random.choice([-1, 0, 1])) % grid_size[1]

    # Simulate trading
    find_trade_partners()

    # Adjust commodity prices dynamically
    for key in commodity_prices:
        supply = max(supply_demand[key]['supply'], 1)
        demand = max(supply_demand[key]['demand'], 1)

        # 🔄 **Price Movement Calculation**
        price_change = ((demand - supply) / (supply + demand)) * 0.02

        # 🔄 **Introduce Correlation between Commodities**
        if key == "Oil":
            wheat_correlation = (commodity_prices["Oil"][-1] - 100) * 0.0002
            gold_correlation = (commodity_prices["Oil"][-1] - 100) * -0.0001
            price_change += wheat_correlation + gold_correlation

        elif key == "Wheat":
            oil_correlation = (commodity_prices["Oil"][-1] - 100) * 0.0003
            gold_correlation = (commodity_prices["Wheat"][-1] - 100) * 0.0001
            price_change += oil_correlation + gold_correlation

        elif key == "Gold":
            oil_correlation = (commodity_prices["Oil"][-1] - 100) * -0.0002
            wheat_correlation = (commodity_prices["Wheat"][-1] - 100) * 0.0003
            price_change += oil_correlation + wheat_correlation

            # Add some **random noise** for realism
        price_change += random.uniform(-0.005, 0.005)

        new_price = commodity_prices[key][-1] * (1 + price_change)
        commodity_prices[key].append(max(new_price, 1))  # Prevent negative prices

    update_display()


def run_model():
    """Continuously update the model at the selected tick rate."""
    global running
    running = True

    def loop():
        if running:
            update_model()
            root.after(int(1000 / tick_rate.get()), loop)

    loop()


def stop_model():
    """Stop the continuous model execution."""
    global running
    running = False


def update_display():
    """Update the visualization: Turtle space and line graphs."""
    ax_turtle.clear()
    ax_turtle.set_xticks(range(grid_size[0]))
    ax_turtle.set_yticks(range(grid_size[1]))
    ax_turtle.grid(True)

    # Draw agents with role colors
    for agent in agents:
        ax_turtle.scatter(agent['x'], agent['y'], color=agent_roles[agent['role']], s=100)

    # Draw trade interactions
    for trade in trade_links:
        agent_a, agent_b = trade
        ax_turtle.arrow(
            agent_a['x'], agent_a['y'],
            agent_b['x'] - agent_a['x'], agent_b['y'] - agent_a['y'],
            head_width=0.3, head_length=0.3, fc='black', ec='black', alpha=0.5
        )

    canvas_turtle.draw()

    # Update graphs
    for key, ax in ax_graphs.items():
        ax.clear()
        ax.plot(commodity_prices[key], label=key, linewidth=2)
        ax.legend()

    canvas_graphs.draw()


# Tkinter setup
root = tk.Tk()
root.title("Commodity Market Simulation")
root.geometry("900x600")

# Control Panel (Left Side)
control_frame = tk.Frame(root)
control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

tk.Button(control_frame, text="Initialize", command=initialize_model).pack(pady=5)
tk.Button(control_frame, text="Go", command=update_model).pack(pady=5)
tk.Button(control_frame, text="Go Forever", command=run_model).pack(pady=5)
tk.Button(control_frame, text="Stop", command=stop_model).pack(pady=5)

tick_rate = tk.IntVar(value=5)
tk.Label(control_frame, text="Tick Rate").pack()
tk.Scale(control_frame, from_=1, to=20, orient=tk.HORIZONTAL, variable=tick_rate).pack()

visual_frame = tk.Frame(root)
visual_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

fig_turtle, ax_turtle = plt.subplots(figsize=(5, 5))
canvas_turtle = FigureCanvasTkAgg(fig_turtle, master=visual_frame)
canvas_turtle.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

fig_graphs, ax_graphs = plt.subplots(1, 3, figsize=(10, 3))
ax_graphs = {key: ax for key, ax in zip(commodity_prices.keys(), ax_graphs)}
canvas_graphs = FigureCanvasTkAgg(fig_graphs, master=visual_frame)
canvas_graphs.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

initialize_model()
root.mainloop()

import random
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize Tkinter root first to avoid RuntimeError
root = tk.Tk()
root.title("Commodity Market Simulation")
root.geometry("1000x700")

# Model parameters
grid_size = (20, 20)
agents = []
commodity_prices = {'Oil': [], 'Wheat': [], 'Gold': []}
supply_demand = {'Oil': {'supply': 5, 'demand': 5},
                 'Wheat': {'supply': 5, 'demand': 5},
                 'Gold': {'supply': 5, 'demand': 5}}
trade_links = []
tick = 0
running = False

# UI Variables - Must be initialized AFTER root = tk.Tk()
num_agents = tk.IntVar(value=5)
speculator_aggression = tk.DoubleVar(value=1.0)
correlation_multiplier = tk.DoubleVar(value=0.0002)
tick_rate = tk.IntVar(value=5)


agent_roles = {
    'Producer': 'green',
    'Consumer': 'blue',
    'Speculator': 'red'
}

def initialize_model():
    """Initialize agents and reset commodity prices correctly."""
    global agents, tick, commodity_prices
    tick = 0
    agents.clear()  # Reset agents list

    # Get the updated number of agents from the UI
    num_agents_value = int(num_agents.get())
    roles = ['Producer', 'Consumer', 'Speculator']

    # print(f"Initializing {num_agents_value} agents...")  # Debugging print

    for _ in range(num_agents_value):
        agents.append({
            'x': random.randint(0, grid_size[0] - 1),
            'y': random.randint(0, grid_size[1] - 1),
            'role': random.choice(roles)
        })

    # ✅ Fix commodity price initialization to avoid a drop to zero
    for key in commodity_prices:
        commodity_prices[key] = [random.uniform(50, 150)]  # Start with a valid price
        # print(f"{key} initialized at {commodity_prices[key][0]}")  # Debugging print

    update_display()


def find_trade_partners():
    """Find nearby agents and create trade interactions."""
    global trade_links
    trade_links = []

    for i, agent in enumerate(agents):
        for j, other_agent in enumerate(agents):
            if i != j:
                if abs(agent['x'] - other_agent['x']) <= 2 and abs(agent['y'] - other_agent['y']) <= 2:
                    if (agent['role'] == 'Producer' and other_agent['role'] == 'Consumer') or \
                            (agent['role'] == 'Speculator' and random.random() < speculator_aggression.get()):
                        trade_links.append((agent, other_agent))

def update_model():
    """Ensure commodity price updates correctly with balanced correlations."""
    global tick
    tick += 1

    # Move agents randomly
    for agent in agents:
        agent['x'] = (agent['x'] + random.choice([-1, 0, 1])) % grid_size[0]
        agent['y'] = (agent['y'] + random.choice([-1, 0, 1])) % grid_size[1]

    find_trade_partners()

    # Introduce random supply-side shocks to Wheat
    if random.random() < 0.2:  # 20% chance of unexpected supply increase
        supply_demand["Wheat"]["supply"] += 1

    for key in commodity_prices:
        supply = max(supply_demand[key]['supply'], 1)
        demand = max(supply_demand[key]['demand'], 1)

        # limit percentage change
        price_change = max(min(((demand - supply) / (supply + demand)) * 0.02, 0.05), -0.05)

        if key == "Oil":
            price_change -= (commodity_prices["Oil"][-1] - 100) * (
                    correlation_multiplier.get() / 10000) * 1.0  # Negative correlation
            price_change -= (commodity_prices["Gold"][-1] - 100) * (correlation_multiplier.get() / 10000) * 0.5

        elif key == "Wheat":
            price_change += (100 - commodity_prices["Oil"][-1]) * (
                    correlation_multiplier.get() / 10000) * 0.5  # Positive correlation
            price_change += (commodity_prices["Gold"][-1] - 100) * (correlation_multiplier.get() / 10000) * 0.5

        elif key == "Gold":
            price_change -= (commodity_prices["Oil"][-1] - 100) * (correlation_multiplier.get() / 10000)
            price_change += (commodity_prices["Wheat"][-1] - 100) * (correlation_multiplier.get() / 10000) * 1.5

        price_change += random.uniform(-0.005, 0.005)

        new_price = max(commodity_prices[key][-1] * (1 + price_change), 10)  # Set a floor at 10
        commodity_prices[key].append(new_price)
        # **✅ Print Debugging Data**

        print(f"Tick {tick} | {key}: Supply={supply}, Demand={demand}, Price={new_price:.2f}")
    update_display()



def run_model():
    """Continuously update the model at the selected tick rate with smooth UI updates."""
    global running
    running = True

    def loop():
        if running:
            update_model()
            root.update_idletasks()  # ✅ Ensures smooth rendering without UI skipping
            root.after(int(1000 / tick_rate.get()), loop)

    loop()


def stop_model():
    """Stop the model."""
    global running
    running = False

def update_display():
    """Update visualization with proper x-axis scaling and smooth rendering."""
    ax_turtle.clear()
    ax_turtle.set_xticks(range(grid_size[0]))
    ax_turtle.set_yticks(range(grid_size[1]))
    ax_turtle.grid(True)

    # Plot agents with their role-based colors
    for agent in agents:
        ax_turtle.scatter(agent['x'], agent['y'], color=agent_roles[agent['role']])

    # Draw trade interactions
    for trade in trade_links:
        agent_a, agent_b = trade
        ax_turtle.arrow(agent_a['x'], agent_a['y'],
                        agent_b['x'] - agent_a['x'], agent_b['y'] - agent_a['y'],
                        head_width=0.3, head_length=0.3, fc='green', ec='green', alpha=0.7)

    canvas_turtle.draw_idle()  # ✅ Avoid excessive redraws

    # ✅ Ensure x-axis grows dynamically for price graphs
    for key, ax in ax_graphs.items():
        ax.clear()
        ax_turtle.set_title("Turtle Space: Market Agents & Trading")
        x_data = list(range(len(commodity_prices[key])))  # Correctly aligns time ticks
        y_data = commodity_prices[key]

        ax.plot(x_data, y_data, label=key)
        ax.set_xlim(0, max(10, len(x_data)))  # Ensure axis scales dynamically
        ax.set_xlabel("Time (Ticks)")
        ax.set_ylabel("Price")
        ax.set_title(key)  # ✅ Use key as title instead of legend

    canvas_graphs.draw_idle()  # ✅ Prevent unnecessary UI lag




# Control Panel (Left)
control_frame = tk.Frame(root)
control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

tk.Button(control_frame, text="Initialize", command=initialize_model).pack(pady=5)
tk.Button(control_frame, text="Go", command=update_model).pack(pady=5)
tk.Button(control_frame, text="Go Forever", command=run_model).pack(pady=5)
tk.Button(control_frame, text="Stop", command=stop_model).pack(pady=5)

# Grouped Control Elements with Borders
tick_frame = tk.LabelFrame(control_frame, text="Tick Rate", padx=5, pady=5)
tick_frame.pack(fill="x", padx=5, pady=5)
tk.Scale(tick_frame, from_=1, to=20, orient=tk.HORIZONTAL, variable=tick_rate).pack()

agent_frame = tk.LabelFrame(control_frame, text="Number of Agents", padx=5, pady=5)
agent_frame.pack(fill="x", padx=5, pady=5)
tk.Scale(agent_frame, from_=5, to=50, orient=tk.HORIZONTAL, variable=num_agents).pack()

correlation_frame = tk.LabelFrame(control_frame, text="Correlation Multiplier", padx=5, pady=5)
correlation_frame.pack(fill="x", padx=5, pady=5)
tk.Scale(correlation_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=correlation_multiplier).pack()

speculator_frame = tk.LabelFrame(control_frame, text="Speculator Aggression", padx=5, pady=5)
speculator_frame.pack(fill="x", padx=5, pady=5)
tk.Scale(speculator_frame, from_=1, to=10, orient=tk.HORIZONTAL, variable=speculator_aggression).pack()

# Visualization Panel
visual_frame = tk.Frame(root)
visual_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Turtle Space
fig_turtle, ax_turtle = plt.subplots(figsize=(5, 5))
canvas_turtle = FigureCanvasTkAgg(fig_turtle, master=visual_frame)
canvas_turtle.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Graphs
fig_graphs, ax_graphs = plt.subplots(1, 3, figsize=(10, 3))
fig_graphs.subplots_adjust(hspace=0.5, wspace=0.3, bottom=0.25)  # ✅ Increase space between graphs
ax_graphs = {key: ax for key, ax in zip(commodity_prices.keys(), ax_graphs)}
canvas_graphs = FigureCanvasTkAgg(fig_graphs, master=visual_frame)
canvas_graphs.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

initialize_model()
root.mainloop()

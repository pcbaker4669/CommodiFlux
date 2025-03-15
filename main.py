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

# Define agent roles and their colors
agent_roles = {
    'Producer': 'green',   # 🟢 Farmers, miners
    'Consumer': 'blue',    # 🔵 Factories, buyers
    'Speculator': 'red'    # 🔴 Traders, hedge funds
}

def initialize_model():
    """Initialize agents and commodity prices."""
    global agents, tick, commodity_prices
    tick = 0
    agents = [
        {'x': random.randint(0, grid_size[0]-1),
         'y': random.randint(0, grid_size[1]-1),
         'role': random.choice(list(agent_roles.keys()))}  # Assign a role
        for _ in range(10)
    ]
    for key in commodity_prices:
        commodity_prices[key] = [random.uniform(50, 150)]
    update_display()

def update_model():
    """Update agent positions and commodity prices."""
    global tick
    tick += 1
    for agent in agents:
        agent['x'] = (agent['x'] + random.choice([-1, 0, 1])) % grid_size[0]
        agent['y'] = (agent['y'] + random.choice([-1, 0, 1])) % grid_size[1]
    for key in commodity_prices:
        commodity_prices[key].append(commodity_prices[key][-1] * (1 + random.uniform(-0.02, 0.02)))
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

    # Plot agents with their role-based colors
    for agent in agents:
        ax_turtle.scatter(agent['x'], agent['y'], color=agent_roles[agent['role']], label=agent['role'], alpha=0.8)

    # Add legend to differentiate agent roles
    handles, labels = ax_turtle.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))  # Remove duplicate legends
    ax_turtle.legend(unique_labels.values(), unique_labels.keys(), loc='upper right')

    canvas_turtle.draw()

    # Update graphs
    for key, ax in ax_graphs.items():
        ax.clear()
        ax.plot(commodity_prices[key], label=key)
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

# Main visualization area (Turtle Space and Graphs)
visual_frame = tk.Frame(root)
visual_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Turtle Space (Top Panel)
fig_turtle, ax_turtle = plt.subplots(figsize=(5, 5))
canvas_turtle = FigureCanvasTkAgg(fig_turtle, master=visual_frame)
canvas_turtle.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Graphs (Bottom Panel)
fig_graphs, ax_graphs = plt.subplots(1, 3, figsize=(10, 3))
ax_graphs = {key: ax for key, ax in zip(commodity_prices.keys(), ax_graphs)}
canvas_graphs = FigureCanvasTkAgg(fig_graphs, master=visual_frame)
canvas_graphs.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

initialize_model()
root.mainloop()

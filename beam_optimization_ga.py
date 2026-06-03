import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ============================================================
# EXPERIMENT 9: Beam Optimization using Genetic Algorithm
# Subject: AI in Mechanical Engineering (ONT406)
# Sharda University
# ============================================================

class BeamConfigError(ValueError):
    """Raised for invalid beam material or geometry parameters."""
    pass

class GAError(RuntimeError):
    """Raised when the Genetic Algorithm cannot run."""
    pass

class PlotError(RuntimeError):
    """Raised when convergence plot cannot be saved."""
    pass

# -------------------------------------------------------
# Input Helpers
# -------------------------------------------------------
def get_positive_float(prompt):
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("  Error: Enter a numeric value.")
            continue
        if value <= 0:
            print("  Error: Value must be greater than zero.")
            continue
        return value

def get_positive_int(prompt, minimum=5):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("  Error: Enter a whole number.")
            continue
        if value < minimum:
            print(f"  Error: Value must be at least {minimum}.")
            continue
        return value

# -------------------------------------------------------
# Beam Configuration
# -------------------------------------------------------
class BeamConfig:
    """Stores and validates beam + GA parameters."""

    def __init__(self, rho, b_mm, L, sigma_yield, FoS):
        if rho <= 0:
            raise BeamConfigError(f"Density must be positive, got {rho}.")
        if b_mm <= 0:
            raise BeamConfigError(f"Width must be positive, got {b_mm}.")
        if L <= 0:
            raise BeamConfigError(f"Length must be positive, got {L}.")
        if sigma_yield <= 0:
            raise BeamConfigError(f"Yield strength must be positive, got {sigma_yield}.")
        if FoS <= 0:
            raise BeamConfigError(f"Factor of Safety must be positive, got {FoS}.")

        self.rho           = rho
        self.b             = b_mm / 1000    # mm → m
        self.L             = L
        self.sigma_yield   = sigma_yield    # MPa
        self.FoS           = FoS
        self.allowable     = sigma_yield / FoS

    def display(self):
        print(f"  Density         : {self.rho} kg/m³")
        print(f"  Width           : {self.b * 1000:.1f} mm")
        print(f"  Length          : {self.L} m")
        print(f"  Yield Strength  : {self.sigma_yield} MPa")
        print(f"  Factor of Safety: {self.FoS}")
        print(f"  Allowable Stress: {self.allowable:.2f} MPa")

# -------------------------------------------------------
# Fitness Function
# -------------------------------------------------------
def make_fitness(cfg):
    """Build a fitness function from a BeamConfig."""
    def fitness(t_mm):
        if t_mm <= 0:
            return 0.0
        t       = t_mm / 1000
        volume  = cfg.b * t * cfg.L
        weight  = cfg.rho * volume
        # Simplified stress model: stress inversely proportional to thickness
        stress  = 100.0 / t
        penalty = 1000.0 if stress > cfg.allowable else 0.0
        # 1e-9 prevents division by zero
        return 1.0 / (weight + penalty + 1e-9)
    return fitness

# -------------------------------------------------------
# Genetic Algorithm
# -------------------------------------------------------
def run_ga(fitness_fn, pop_size, generations, t_min, t_max, mut_std):
    """
    Manual Genetic Algorithm.
    Returns (best_thickness_mm, fitness_history_list).
    Raises GAError on invalid inputs.
    """
    if t_min <= 0:
        raise GAError("Minimum thickness must be positive.")
    if t_max <= t_min:
        raise GAError("Maximum thickness must be greater than minimum.")
    if pop_size < 4:
        raise GAError("Population size must be at least 4.")
    if generations < 1:
        raise GAError("Number of generations must be at least 1.")
    if mut_std <= 0:
        raise GAError("Mutation std must be positive.")

    # Initialise random population
    try:
        population = np.random.uniform(t_min, t_max, pop_size)
    except (ValueError, OverflowError) as e:
        raise GAError(f"Population initialisation failed: {e}")

    history = []

    for gen in range(generations):
        # --- Evaluate fitness ---
        try:
            fitnesses = np.array([fitness_fn(t) for t in population])
        except (TypeError, ArithmeticError) as e:
            raise GAError(f"Fitness evaluation failed at generation {gen}: {e}")

        history.append(float(np.max(fitnesses)))

        # --- Selection: keep top 50% ---
        sorted_idx = np.argsort(fitnesses)[::-1]
        parents    = population[sorted_idx[: pop_size // 2]]

        # --- Crossover: average consecutive pairs ---
        children = []
        for i in range(0, len(parents) - 1, 2):
            children.append((parents[i] + parents[i + 1]) / 2.0)
        if len(parents) % 2 != 0:
            children.append(parents[-1])

        # --- Mutation: Gaussian noise, clipped to valid range ---
        children = np.array(children, dtype=float)
        try:
            mutation = np.random.normal(0.0, mut_std, len(children))
        except (ValueError, OverflowError) as e:
            raise GAError(f"Mutation step failed: {e}")

        children = np.clip(children + mutation, t_min, t_max)

        # --- New generation ---
        population = np.concatenate([parents, children])[:pop_size]

    # --- Final best ---
    try:
        final_fitnesses = np.array([fitness_fn(t) for t in population])
    except (TypeError, ArithmeticError) as e:
        raise GAError(f"Final evaluation failed: {e}")

    best_idx = int(np.argmax(final_fitnesses))
    best_t   = float(population[best_idx])

    return best_t, history

# -------------------------------------------------------
# Display Results
# -------------------------------------------------------
def display_results(best_t, cfg):
    t_m    = best_t / 1000
    volume = cfg.b * t_m * cfg.L
    weight = cfg.rho * volume
    stress = 100.0 / t_m

    print(f"\n{'='*55}")
    print("  GENETIC ALGORITHM OPTIMIZATION RESULTS")
    print(f"{'='*55}")
    print(f"  Optimal Thickness : {best_t:.4f} mm")
    print(f"  Beam Volume       : {volume:.6f} m³")
    print(f"  Minimum Weight    : {weight:.4f} kg")
    print(f"  Stress at Optimal : {stress:.2f} MPa")
    print(f"  Allowable Stress  : {cfg.allowable:.2f} MPa")
    if stress <= cfg.allowable:
        print(f"  Design Status     : SAFE ✓")
    else:
        print(f"  Design Status     : UNSAFE ✗ — reduce FoS or check parameters")
    print(f"{'='*55}")

# -------------------------------------------------------
# Plot Convergence
# -------------------------------------------------------
def plot_convergence(history, filename="ga_convergence.png"):
    if not history:
        raise PlotError("No fitness history to plot.")
    try:
        plt.figure(figsize=(8, 5))
        plt.plot(history, color="steelblue", linewidth=2)
        plt.xlabel("Generation")
        plt.ylabel("Best Fitness")
        plt.title("Genetic Algorithm Convergence")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(filename, dpi=150)
        plt.close()
        print(f"  ✓ Convergence plot saved: {filename}")
    except (TypeError, ValueError) as e:
        raise PlotError(f"Plot generation failed: {e}")
    except OSError as e:
        raise PlotError(f"Could not save plot: {e}")

# -------------------------------------------------------
# Main Program
# -------------------------------------------------------
def main():
    print("=" * 55)
    print("   EXPERIMENT 09: Beam Optimization (Genetic Algorithm)")
    print("   AI in Mechanical Engineering — ONT406")
    print("   Sharda University")
    print("=" * 55)

    cfg     = None
    best_t  = None
    history = None

    while True:
        print("\n--- MENU ---")
        print("1. Use Preset Beam (Steel, b=50mm, L=1m)")
        print("2. Enter Custom Beam Parameters")
        print("3. Run Genetic Algorithm")
        print("4. Show Convergence Plot")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice in ["3", "4"] and cfg is None:
            print("  Error: Define beam parameters first (option 1 or 2).")
            continue
        if choice == "4" and history is None:
            print("  Error: Run the GA first (option 3).")
            continue

        if choice == "1":
            try:
                cfg = BeamConfig(
                    rho=7850, b_mm=50, L=1.0,
                    sigma_yield=250, FoS=2.0
                )
                print("\n  Preset beam loaded:")
                cfg.display()
            except BeamConfigError as e:
                print(f"  Config Error: {e}")

        elif choice == "2":
            print("\n  --- Enter Beam Parameters ---")
            try:
                rho         = get_positive_float("  Density (kg/m³)         : ")
                b_mm        = get_positive_float("  Width (mm)              : ")
                L           = get_positive_float("  Length (m)              : ")
                sigma_yield = get_positive_float("  Yield Strength (MPa)    : ")
                FoS         = get_positive_float("  Factor of Safety        : ")
                cfg = BeamConfig(rho, b_mm, L, sigma_yield, FoS)
                print("\n  Beam configured:")
                cfg.display()
            except BeamConfigError as e:
                print(f"  Config Error: {e}")

        elif choice == "3":
            print("\n  --- GA Parameters ---")
            try:
                t_min  = get_positive_float("  Min thickness to search (mm): ")
                t_max  = get_positive_float("  Max thickness to search (mm): ")
                if t_max <= t_min:
                    print("  Error: Max must be greater than min.")
                    continue
                pop    = get_positive_int(
                    "  Population size (min 10)       : ", minimum=10)
                gens   = get_positive_int(
                    "  Number of generations (min 10) : ", minimum=10)
                mut    = get_positive_float(
                    "  Mutation std deviation (mm)    : ")

                print(f"\n  Running GA ({gens} generations)...")
                fitness_fn    = make_fitness(cfg)
                best_t, history = run_ga(
                    fitness_fn, pop, gens, t_min, t_max, mut
                )
                display_results(best_t, cfg)

            except GAError as e:
                print(f"  GA Error: {e}")
                best_t  = None
                history = None

        elif choice == "4":
            try:
                plot_convergence(history)
            except PlotError as e:
                print(f"  Plot Error: {e}")

        elif choice == "5":
            print("\nExiting. Goodbye!")
            break

        else:
            print("  Error: Invalid choice. Please enter 1 through 5.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Program interrupted by user. Goodbye!")

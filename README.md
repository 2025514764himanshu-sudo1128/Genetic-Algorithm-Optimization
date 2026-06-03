# Experiment 09: Mechanical Design Optimization using Genetic Algorithm

**Subject:** AI in Mechanical Engineering (ONT406)
**Sharda University, Greater Noida**

---

## Aim
To optimize the dimensions of a structural beam to minimize weight while satisfying Von Mises stress constraints using a Genetic Algorithm (GA).

---

## Concepts Covered
- Genetic Algorithm (GA) — inspired by natural evolution
- Fitness function design with penalty
- Selection, Crossover, Mutation operations
- Weight minimization under stress constraints
- Convergence analysis over generations

---

## Formulas Used

| Formula | Description |
|---|---|
| Weight = ρ × b × t × L | Beam weight |
| Fitness = 1 / (Weight + Penalty) | GA fitness function |
| σ_allowable = σ_yield / FoS | Allowable stress |
| Penalty = 1000 if σ > σ_allowable | Constraint penalty |

---

## Software Required

| Software | Purpose | Download Link |
|---|---|---|
| Python 3.x | Programming language | https://www.python.org/downloads/ |
| VS Code | Code editor | https://code.visualstudio.com/ |
| Git | Version control | https://git-scm.com/ |

---

## Installation Steps

### Step 1: Install Python
```
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or above
3. CHECK "Add Python to PATH"
4. Verify: python --version
```

### Step 2: Install Required Libraries
```bash
pip install numpy matplotlib
```

### Step 3: Optional — Install PyGAD (Advanced GA Library)
```bash
pip install pygad
```
> Note: The provided code uses a manual GA implementation
> so PyGAD is optional. Install it if you want to explore
> the official PyGAD version from the lab manual.

### Step 4: Verify Installation
```bash
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import matplotlib; print('Matplotlib:', matplotlib.__version__)"
```

---

## How to Run

```bash
git clone https://github.com/2025514764himanshu-sudo1128/Exp09-Genetic-Algorithm-Optimization.git
cd Exp09-Genetic-Algorithm-Optimization
python beam_optimization_ga.py
```

---

## Output Files Generated
```
ga_convergence.png   - Fitness improvement over generations
```

---

## Expected Console Output
```
=== Genetic Algorithm Optimization Results ===
Optimal Thickness: 8.02 mm
Minimum Weight: 3.14 kg
Stress at optimal: 12.47 MPa
Allowable Stress: 125 MPa
Design Status: SAFE
```

---

## Author
**Himanshu Kumar** (2025514764)
Department of Electrical, Electronics and Communication Engineering
Sharda University, Greater Noida

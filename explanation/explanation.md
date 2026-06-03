# Experiment 09 — Code Explanation
# Beam Optimization using Genetic Algorithm

---

## What is this program doing?

An engineer needs to design a steel beam that:
- Is as LIGHT as possible (saves material and cost)
- Does NOT fail under stress (safety constraint)

Finding the perfect thickness manually requires
testing thousands of combinations. A Genetic Algorithm
does this automatically by mimicking natural evolution.

---

## Genetic Algorithm — Explained Simply

**Inspired by Darwin's Theory of Evolution:**

- **Population** = Group of candidate designs (different thicknesses)
- **Fitness** = How good each design is (lighter + safer = better)
- **Selection** = Keep the best designs, discard bad ones
- **Crossover** = Combine two good designs to create a child design
- **Mutation** = Randomly tweak a design slightly
- **Generation** = One complete round of evolution

After many generations, the population converges to
the optimal (or near-optimal) design.

---

## Line by Line Explanation

---

### Lines 5-11 (Material Constants)
```python
rho          = 7850    # Steel density (kg/m³)
L            = 1.0     # Beam length (m)
b            = 0.05    # Beam width (m)
sigma_yield  = 250     # Yield strength (MPa)
FoS          = 2       # Factor of Safety
allowable    = sigma_yield / FoS
```
These are the fixed engineering constraints.
Only the **thickness** will be optimized.

**allowable = 250/2 = 125 MPa:**
The maximum stress we allow in the beam.
Beam must not exceed this stress.

---

### Lines 14-29 (Fitness Function)
```python
def fitness(t_mm):
    t = t_mm / 1000         # mm to m
    volume = b * t * L
    weight = rho * volume
    stress = 100 / t        # MPa
    penalty = 0
    if stress > allowable:
        penalty = 1000
    return 1 / (weight + penalty)
```
**What is a Fitness Function?**
A mathematical function that scores how good each design is.
Higher fitness = better design.

**Our design goal:**
Minimize weight → maximum fitness = 1/(minimum weight)

**Weight calculation:**
Weight = ρ × b × t × L
Thinner beam → less volume → less weight → higher fitness.

**The penalty:**
If stress > 125 MPa → add huge penalty (1000).
This makes unsafe designs have very LOW fitness.
GA will naturally avoid them because they score poorly.

**Why 1/(weight + penalty)?**
We want to MINIMIZE weight.
GA naturally MAXIMIZES fitness.
So fitness = 1/weight converts minimization → maximization.

---

### Lines 32-60 (Genetic Algorithm Function)
```python
def genetic_algorithm(pop_size=50, generations=100, t_min=5, t_max=50):
    population = np.random.uniform(t_min, t_max, pop_size)
```
**pop_size=50:**
Start with 50 different thickness values (5mm to 50mm).
This is the initial generation.

**np.random.uniform(t_min, t_max, pop_size):**
Creates 50 random thickness values between 5mm and 50mm.
This is Generation 0 — random starting point.

---

### The Evolution Loop
```python
for gen in range(generations):
    fitnesses = np.array([fitness(t) for t in population])
```
**List comprehension:**
`[fitness(t) for t in population]`
Calculates fitness for every thickness in the population.
Equivalent to a for loop but shorter.

---

### Selection
```python
sorted_idx = np.argsort(fitnesses)[::-1]
parents = population[sorted_idx[:pop_size//2]]
```
**np.argsort():**
Returns indices that would sort the array ascending.
`[::-1]` reverses to descending (best first).

**parents = top 50% designs:**
`pop_size//2` = 50//2 = 25 best designs.
The worst 25 are discarded — survival of the fittest!

---

### Crossover
```python
for i in range(0, len(parents)-1, 2):
    child = (parents[i] + parents[i+1]) / 2
    children.append(child)
```
**What is crossover?**
Combine two parent designs to create a child.
Here: child thickness = average of two parents.

**Example:**
Parent 1: 12mm (good fitness)
Parent 2: 18mm (good fitness)
Child: (12+18)/2 = 15mm (hopefully also good!)

---

### Mutation
```python
mutation = np.random.normal(0, 1, len(children))
children = np.clip(np.array(children) + mutation, t_min, t_max)
```
**What is mutation?**
Add a small random change to each child.
Prevents the algorithm from getting stuck.

**np.random.normal(0, 1, ...):**
Random values centered at 0 with std=1.
Most changes are small (±1mm), occasionally larger.

**np.clip(..., t_min, t_max):**
Keeps values within valid range (5mm to 50mm).
Prevents physically impossible solutions.

---

### New Generation
```python
population = np.concatenate([parents, children])
population = population[:pop_size]
```
New generation = best parents + their children.
Back to 50 individuals, ready for next generation.

**This continues for 100 generations.**
With each generation, the designs get better.
By generation 100, the population has converged
to near-optimal designs.

---

### Lines 63-67 (Best Solution)
```python
fitnesses = np.array([fitness(t) for t in population])
best_idx = np.argmax(fitnesses)
best_t = population[best_idx]
```
**np.argmax():**
Returns the index of the maximum value.
`population[best_idx]` = the thickness with highest fitness.

---

### Lines 70-76 (Results)
```python
t_m = best_thickness / 1000
weight = rho * b * t_m * L
stress = 100 / t_m
```
Calculate the actual engineering values for the optimal design.

**Design validation:**
- Is stress ≤ 125 MPa? → Safe
- What is the minimum weight achieved?

---

### Convergence Plot
```python
plt.plot(history, ...)
```
Shows fitness improving over generations.
Should see rapid improvement early, then leveling off.
This "plateau" means the algorithm has converged.

---

## Why GA Over Brute Force?

**Brute force (try every thickness):**
- 5mm to 50mm with 0.001mm resolution
- 45,000 thickness values to try
- For 3 variables: 45,000³ = 91 BILLION combinations

**Genetic Algorithm:**
- 50 individuals × 100 generations = 5,000 evaluations
- Finds near-optimal in 0.005% of the search space!

---

## GA vs Other Optimization Methods

| Method | Best For | Limitations |
|---|---|---|
| Genetic Algorithm | Complex, multi-variable, non-linear | Approximate, not always global optimum |
| Gradient Descent | Smooth mathematical functions | Gets stuck in local minima |
| Brute Force | Small search spaces | Exponentially slow for many variables |
| GA | Large, complex, constrained problems | Needs fitness function design |

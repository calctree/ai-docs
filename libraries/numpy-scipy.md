# numpy + scipy — Numerical Computing & Scientific Routines

## When to Use
`numpy` provides N-dimensional arrays and vectorised math; `scipy` adds optimisation, integration, interpolation, statistics, linear algebra, signal processing, and special functions. Use them for:

- Any numerical computation more complex than what MathJS supports
- Vector/matrix math (transformations, eigenvalues, linear systems)
- Integration, root finding, optimisation
- Statistics, distributions, hypothesis testing
- Interpolation, curve fitting
- Signal processing (FFT, filters)

For tabular data use `pandas`. For symbolic math use `sympy`. For plotting use `matplotlib`.

## Installation
Already installed:
```python
import numpy as np
import scipy
from scipy import optimize, integrate, interpolate, stats, linalg, signal
```

## Units
**Unit-naive**. NumPy and SciPy operate on plain numbers. Strip `ct.quantity` before passing in:
```python
L_m = L.to('m').magnitude
arr = np.linspace(0, L_m, 100)
```

## NumPy Essentials

### Array creation
```python
np.array([1, 2, 3])
np.zeros(5); np.ones((3, 3)); np.eye(4)
np.linspace(0, 10, 50)
np.arange(0, 10, 0.5)
np.logspace(-3, 3, 7)
```

### Shape and indexing
```python
a = np.arange(12).reshape(3, 4)
a[0, :]          # first row
a[:, 1]          # second column
a[a > 5]         # boolean mask
```

### Vectorised math
```python
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x) + np.cos(2*x)
mean = np.mean(y); std = np.std(y); peak = np.max(np.abs(y))
```

### Linear algebra
```python
A = np.array([[3, 1], [1, 2]])
b = np.array([9, 8])
x = np.linalg.solve(A, b)
eigvals, eigvecs = np.linalg.eig(A)
```

## SciPy Essentials

### Optimisation
```python
from scipy.optimize import minimize, root_scalar, curve_fit

# Minimise a scalar function
res = minimize(lambda x: (x[0]-2)**2 + (x[1]+3)**2, x0=[0, 0])
x_opt = res.x

# Root finding
sol = root_scalar(lambda x: x**3 - 2*x - 5, bracket=[1, 3], method='brentq')
root = sol.root

# Curve fitting
def model(x, a, b): return a * np.exp(-b * x)
popt, pcov = curve_fit(model, x_data, y_data, p0=[1, 0.1])
```

### Integration
```python
from scipy.integrate import quad, solve_ivp

# Definite integral
area, err = quad(lambda x: np.sin(x)**2, 0, np.pi)

# ODE solver
def deriv(t, y): return -0.5 * y
sol = solve_ivp(deriv, [0, 10], [1.0], t_eval=np.linspace(0, 10, 100))
```

### Interpolation
```python
from scipy.interpolate import interp1d, UnivariateSpline
f = interp1d(x_known, y_known, kind='cubic')
y_new = f(x_new)
```

### Statistics
```python
from scipy import stats
mean, ci = stats.t.interval(0.95, df=len(data)-1, loc=np.mean(data), scale=stats.sem(data))
slope, intercept, r, p, se = stats.linregress(x, y)
```

### Signal processing
```python
from scipy.signal import butter, filtfilt, find_peaks

b, a = butter(N=4, Wn=0.1, btype='low')
filtered = filtfilt(b, a, raw)
peaks, props = find_peaks(filtered, height=0.5, distance=20)
```

## CalcTree Integration

### Output Variables
NumPy scalars (`np.float64`, `np.int64`) need to be cast to plain Python types before becoming page scope variables:
```python
M_max_value = float(np.max(np.abs(moments)))   # NOT just np.max(...)
n_peaks = int(len(peaks))
```

### Output Arrays
Small arrays (≤ ~100 elements) can be exposed as Python lists:
```python
moment_diagram = np.linspace(0, 10, 50).tolist()
```
For large arrays, generate a chart instead.

### Charts (matplotlib)
Same pattern as everywhere else:
```python
import matplotlib.pyplot as plt
import ctconfig

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, y)
ax.set_xlabel('x'); ax.set_ylabel('sin(x)'); ax.grid(True)

ctconfig.plot_prefix = "sine"
plt.show()
```
Then in MDX: `<Mention key="sine1" value="sine1" variableType="image" />`.

## Examples

### Example 1: Find the natural period of a SDOF
```python
import numpy as np

m = 5000        # kg
k = 2.5e6       # N/m
omega_n = np.sqrt(k / m)
T_n = float(2 * np.pi / omega_n)        # s
f_n = float(1 / T_n)                    # Hz
```

### Example 2: Solve a 3-equation linear system
```python
import numpy as np

A = np.array([
    [4, -2,  1],
    [1,  3, -1],
    [2,  1,  5],
])
b = np.array([11, 5, 13])
x = np.linalg.solve(A, b)
x1, x2, x3 = float(x[0]), float(x[1]), float(x[2])
```

### Example 3: Fit a power-law to test data
```python
import numpy as np
from scipy.optimize import curve_fit

strain = np.array([0.001, 0.002, 0.005, 0.01, 0.02])
stress = np.array([200, 280, 360, 420, 470])

def power(eps, a, n): return a * eps**n
popt, _ = curve_fit(power, strain, stress, p0=[100, 0.3])
a_fit, n_fit = float(popt[0]), float(popt[1])
```

### Example 4: Numerical integration of a load distribution
```python
import numpy as np
from scipy.integrate import quad

def w(x): return 5 + 2*x        # kN/m varying from 5 to 25 over 10 m
total_load, _ = quad(w, 0, 10)
total_load = float(total_load)
```

### Example 5: ODE — beam deflection by direct integration
```python
import numpy as np
from scipy.integrate import solve_ivp

EI = 30000        # kN·m²
L = 10            # m
w = 15            # kN/m
# Mid-span deflection from analytical: 5wL^4 / (384 EI)
# Or numerically: integrate v''(x) = M(x) / EI

def M(x): return w*L*x/2 - w*x**2/2

def deriv(x, y):
    # y[0] = v, y[1] = v'
    return [y[1], M(x) / EI]

# This needs a 2-pt BVP (v(0)=v(L)=0). Use shooting:
from scipy.optimize import brentq
def shoot(slope0):
    sol = solve_ivp(deriv, [0, L], [0, slope0], t_eval=np.linspace(0, L, 100))
    return sol.y[0, -1]

slope0 = brentq(shoot, -10, 10)
sol = solve_ivp(deriv, [0, L], [0, slope0], t_eval=np.linspace(0, L, 100))
delta_max_mm = float(np.min(sol.y[0]) * 1000)
```

## Common Mistakes
- **Returning numpy scalars to MathJS**: Always cast `float(np.max(...))` / `int(...)` before assignment to a page variable. MathJS sees `np.float64` as an opaque object.
- **Mutating arrays expecting copies**: `b = a` is a reference. Use `b = a.copy()` for an independent array.
- **Mixing `np.array` with `list` operators**: `[1,2,3] + [4,5,6]` concatenates; `np.array([1,2,3]) + np.array([4,5,6])` element-wise adds. Be deliberate.
- **`scipy.optimize.minimize` without `x0`**: Always pass an initial guess; many algorithms require it.
- **Forgetting `bracket` for `root_scalar`**: For the `brentq` method you need a bracket where the function changes sign, otherwise it raises.
- **Using `np.matrix`**: Deprecated. Use `np.array` with `@` for matrix multiplication.
- **Re-wrapping `ct.quantity` in numpy**: numpy doesn't understand pint quantities. Convert to plain floats first.

# handcalcs — Formatted Engineering Calculations

## When to Use
`handcalcs` renders Python code as **hand-calculation-style LaTeX**, showing the symbolic formula, the substituted values, and the result — exactly like an engineer would write it on paper. Use it when:

- The user wants a "show your working" style calculation page (typical for design checks under codes like AS3600, EC2, AISC)
- You're writing design code clause checks that need to be auditable
- The output needs to look professional / submission-ready

Use it together with `forallpeople` (if available) for unit-aware variables, or pair with CalcTree's `ct.quantity()`.

## Installation
Already installed. Import:
```python
import handcalcs.render
from handcalcs.decorator import handcalc
```

## Two Modes

### Mode 1: Cell magic (one block of calculations)
In a Jupyter-style cell, use `%%render`. CalcTree's Python engine supports this via the IPython compatibility layer:

```python
%%render
f_c = 40       # MPa
f_y = 500      # MPa
b   = 300      # mm
d   = 550      # mm
A_s = 1500     # mm²
M_star = 250   # kN·m

# Computed
a    = (A_s * f_y) / (0.85 * f_c * b)
phi  = 0.85
M_n  = A_s * f_y * (d - a/2) / 1e6   # kN·m
phi_M_n = phi * M_n
UR   = M_star / phi_M_n
```

The block renders as LaTeX showing symbolic → substituted → result for each line.

### Mode 2: Decorator (one function, called multiple times)
```python
from handcalcs.decorator import handcalc

@handcalc(override="long")
def flexural_capacity(A_s, f_y, d, b, f_c, phi=0.85):
    a = (A_s * f_y) / (0.85 * f_c * b)
    M_n = A_s * f_y * (d - a/2) / 1e6
    phi_M_n = phi * M_n
    return phi_M_n

latex_str, result = flexural_capacity(1500, 500, 550, 300, 40)
```
`latex_str` is the rendered LaTeX, `result` is the function's return value.

## Render Overrides
Pass via `%%render long` or `@handcalc(override="long")`:
- `long` — symbolic, substituted, result on separate lines (default best for design docs)
- `short` — symbolic = substituted = result on one line
- `symbolic` — symbolic only
- `params` — just declare values, no computation rendering

## CalcTree Integration

### Output variables
Variables defined inside a `%%render` cell remain in the Python module scope after the cell runs, so they become page scope variables exactly like a normal Python block.

```python
%%render
f_c = 40
f_y = 500
A_s = 1500
b = 300
d = 550
M_star = 250

a = (A_s * f_y) / (0.85 * f_c * b)
phi_M_n = 0.85 * A_s * f_y * (d - a/2) / 1e6   # kN·m
UR = M_star / phi_M_n
```

`phi_M_n` and `UR` are now mentionable on the page.

### Unit handling
handcalcs renders units automatically when variables are `forallpeople` Physical objects, OR pint quantities (which is what `ct.quantity` provides). For maximum compatibility in CalcTree, use `ct.quantity`:

```python
%%render
f_c = ct.quantity("40 MPa")
f_y = ct.quantity("500 MPa")
A_s = ct.quantity("1500 mm^2")
b   = ct.quantity("300 mm")
d   = ct.quantity("550 mm")

a = (A_s * f_y) / (0.85 * f_c * b)
phi_M_n = 0.85 * A_s * f_y * (d - a/2)
phi_M_n_kNm = phi_M_n.to("kN*m")
```

### Symbol naming for nice rendering
handcalcs follows conventions:
- `f_c` → f_c (subscript)
- `phi_M_n` → φM_n
- `M_star` → M*  (use `_star` suffix for stars)
- `epsilon_cu` → ε_cu
- Greek names (alpha, beta, gamma, delta, epsilon, theta, lambda, mu, pi, rho, sigma, tau, phi, psi, omega) auto-convert to Greek letters

## Examples

### Example 1: AS3600 Cl 8.1 Flexural Capacity (one cell)
```python
%%render
# AS3600 Cl 8.1 — Singly reinforced rectangular beam
f_c = 40       # MPa
f_y = 500      # MPa
b   = 300      # mm
d   = 550      # mm
A_s = 1500     # mm²
phi = 0.85

# alpha_2 and gamma per Cl 8.1.3
alpha_2 = 0.85 - 0.0015 * f_c
gamma   = 0.97 - 0.0025 * f_c

# Stress block
a = (A_s * f_y) / (alpha_2 * f_c * b)

# Design moment capacity (kN·m)
phi_M_u = phi * A_s * f_y * (d - a/2) / 1e6
```

### Example 2: Decorator for reusable check
```python
from handcalcs.decorator import handcalc

@handcalc(override="long")
def shear_capacity_as3600(b_v, d_v, f_c, A_sv, f_sy_f, s):
    """AS3600 Cl 8.2 simplified shear."""
    V_uc = 0.17 * (f_c**0.5) * b_v * d_v / 1e3        # kN, concrete contribution
    V_us = (A_sv * f_sy_f * d_v) / s / 1e3            # kN, shear reo
    phi_V_u = 0.7 * (V_uc + V_us)                     # kN
    return phi_V_u

latex, phi_V_u = shear_capacity_as3600(300, 510, 40, 100, 500, 200)
```

### Example 3: Combine with anastruct results
```python
from anastruct import SystemElements

ss = SystemElements(EI=30000)
ss.add_element([[0, 0], [10, 0]])
ss.add_support_hinged(1)
ss.add_support_roll(2, direction='y')
ss.q_load(q=-15, element_id=1)
ss.solve()

M_star = max(abs(m) for m in ss.get_element_result_range('moment')[0])  # kN·m
```

```python
%%render
# AS3600 design check, M_star carried over from previous block
f_c = 40
f_y = 500
b   = 300
d   = 550
A_s = 1500
phi = 0.85

a       = (A_s * f_y) / (0.85 * f_c * b)
phi_M_u = phi * A_s * f_y * (d - a/2) / 1e6   # kN·m
UR      = M_star / phi_M_u                     # M_star from previous block
```

## Common Mistakes

- **Using `print()` to show results**: handcalcs renders the calculation IS the output. Don't `print` — let the cell render.
- **Multi-statement lines**: One assignment per line. `a = b; c = d` won't render correctly.
- **Inline conditionals**: Not all Python is renderable. Avoid complex one-liners — prefer step-by-step.
- **Unit mixing without `ct.quantity`**: If you mix bare numbers and units, the rendered output will be inconsistent. Pick one approach per cell.
- **Missing intermediate variables**: handcalcs only renders lines that exist. If you want the substituted formula shown, you must write it as its own line. Don't collapse 4 steps into one.
- **Forgetting `%%render` is cell-scoped**: It only applies to that one cell. Each Python block in CalcTree is a separate cell.
- **Greek letters via Unicode**: Use ASCII names (`phi`, `alpha`) — handcalcs converts them. Don't paste φ directly.

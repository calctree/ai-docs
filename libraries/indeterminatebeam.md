# indeterminatebeam — Beam Analysis with Auto-Plot Capture

## When to Use
`indeterminatebeam` is a popular Python library for analysing 1D beams (statically determinate or indeterminate) with a clean, object-oriented API. The CalcTree Python runtime has **special support** for it: it automatically detects `Beam` instances in user code and renders schematic, internal force, and reaction plots as matplotlib figures (without you needing `plot_prefix`).

Use it when:

- The user wants a beam analysis with built-in schematic + diagrams
- The structure is 1D (single beam, multiple supports, point/distributed/moment loads)
- You want plots "for free" without manually constructing matplotlib figures

For multi-element frames use `anastruct`. For very simple continuous beams `pycba` is faster. For 3D use `PyNite`.

## Installation
Already installed. Imports:
```python
from indeterminatebeam import (
    Beam, Support, PointLoadV, PointLoadH, PointTorque,
    DistributedLoadV, TrapezoidalLoadV,
)
```

## Coordinate System
- X is along the beam (start at 0, increases to right)
- V loads are vertical (downward = negative)
- H loads are horizontal/axial
- Units: **N, m, N·m, Pa** (SI base) by default. Library is unit-agnostic if you stay consistent.

## Key API

### Beam construction
```python
beam = Beam(span=10, E=200e9, I=222e-6)   # length m, E Pa, I m⁴
```
Optional `A` for axial.

### Supports
```python
beam.add_supports(
    Support(0, (1, 1, 0)),        # pin at x=0 (UX, UY restrained, RZ free)
    Support(10, (0, 1, 0)),       # roller at x=10 (UY only)
)
```
The tuple is `(DX, DY, RZ)` — 1 = restrained, 0 = free. For a fully fixed support use `(1, 1, 1)`.

### Loads
```python
beam.add_loads(
    DistributedLoadV(force=-15000, span=(0, 10)),   # N/m, downward (negative)
    PointLoadV(force=-50000, coord=5),              # 50 kN at x=5
    PointTorque(torque=20000, coord=3),             # N·m
)
```

### Analysis
```python
beam.analyse()
```

### Results
- `beam.get_reaction(x_coord, direction)` — `direction` is `'y'`, `'x'`, or `'m'`
- `beam.get_bending_moment(x_coord)` — N·m at position
- `beam.get_shear_force(x_coord)`
- `beam.get_normal_force(x_coord)`
- `beam.get_deflection(x_coord)` — m

For peaks, sample over the span:
```python
import numpy as np
xs = np.linspace(0, 10, 200)
M = [beam.get_bending_moment(x) for x in xs]
M_max = float(max(abs(m) for m in M))
```

## CalcTree Auto-Plot Capture (special)

The CalcTree Python runtime ([indeterminatebeam_utils.py](python-engine/ctpyeng/execute_source_function/indeterminatebeam_utils.py)) automatically detects any `Beam` instance in `user_globals` AFTER your code runs and emits these matplotlib figures into the page image bag:

- **Beam Schematic** — geometry + supports + loads
- **Normal Force**, **Shear Force**, **Bending Moment**, **Deflection** diagrams
- **Reaction Forces** plot

Each figure is keyed by the variable name of the beam, so referencing it in MDX uses the variable name + a suffix. Practically: assign your beam to a clearly named variable (e.g. `beam_main`) and the runtime will produce images. Use `print` or check the runtime logs to discover exact image keys for each figure (the runtime emits them as `<beam_var>_schematic`, `<beam_var>_bending_moment`, etc.).

**Important:** because the runtime captures these automatically, you generally do NOT need to call `plt.show()` or set `ctconfig.plot_prefix` manually for indeterminatebeam plots. Just create the beam, analyse, and the figures appear.

After running, follow up with `generateCalculation` MDX containing the appropriate `<Mention key="..." variableType="image" />` for each figure you want displayed.

## CalcTree Integration

### Output Variables
```python
from indeterminatebeam import Beam, Support, DistributedLoadV
import numpy as np

beam_main = Beam(span=10, E=200e9, I=222e-6)
beam_main.add_supports(
    Support(0, (1, 1, 0)),
    Support(10, (0, 1, 0)),
)
beam_main.add_loads(DistributedLoadV(force=-15000, span=(0, 10)))
beam_main.analyse()

xs = np.linspace(0, 10, 200)
M_max = float(max(abs(beam_main.get_bending_moment(x)) for x in xs))   # N·m
V_max = float(max(abs(beam_main.get_shear_force(x)) for x in xs))      # N
delta_max = float(max(abs(beam_main.get_deflection(x)) for x in xs))   # m

R_left  = float(beam_main.get_reaction(0, 'y'))
R_right = float(beam_main.get_reaction(10, 'y'))
```

### Unit handling
indeterminatebeam expects raw SI numbers (N, m, Pa). Strip page quantities first:
```python
L_m = L.to('m').magnitude
E_Pa = E.to('Pa').magnitude
I_m4 = I.to('m^4').magnitude
q_Npm = q.to('N/m').magnitude

beam = Beam(span=L_m, E=E_Pa, I=I_m4)
beam.add_supports(Support(0, (1,1,0)), Support(L_m, (0,1,0)))
beam.add_loads(DistributedLoadV(force=-q_Npm, span=(0, L_m)))
beam.analyse()
```

## Examples

### Example 1: Simply supported beam under UDL
```python
from indeterminatebeam import Beam, Support, DistributedLoadV

beam = Beam(span=8, E=200e9, I=80e-6)
beam.add_supports(Support(0, (1,1,0)), Support(8, (0,1,0)))
beam.add_loads(DistributedLoadV(force=-12000, span=(0, 8)))
beam.analyse()

M_mid = float(beam.get_bending_moment(4))
delta_mid = float(beam.get_deflection(4))
```

### Example 2: Fixed-fixed propped cantilever
```python
from indeterminatebeam import Beam, Support, PointLoadV

beam = Beam(span=6, E=200e9, I=120e-6)
beam.add_supports(
    Support(0, (1, 1, 1)),     # fixed
    Support(6, (0, 1, 0)),     # roller
)
beam.add_loads(PointLoadV(force=-30000, coord=4))
beam.analyse()

M_fixed = float(beam.get_bending_moment(0))
M_under_load = float(beam.get_bending_moment(4))
delta_max = float(max(abs(beam.get_deflection(x)) for x in [1,2,3,4,5]))
```

### Example 3: Multi-load combination
```python
from indeterminatebeam import Beam, Support, PointLoadV, DistributedLoadV, PointTorque

beam = Beam(span=10, E=200e9, I=222e-6)
beam.add_supports(Support(0, (1,1,0)), Support(10, (0,1,0)))
beam.add_loads(
    DistributedLoadV(force=-8000, span=(0, 10)),
    PointLoadV(force=-25000, coord=4),
    PointTorque(torque=15000, coord=6),
)
beam.analyse()
```

## Common Mistakes
- **Positive load values for gravity**: Use `force=-15000` for downward UDL/point load. Positive is upward.
- **Wrong support tuple order**: It's `(DX, DY, RZ)` — `(1,1,0)` is a pin, `(0,1,0)` is a roller, `(1,1,1)` is fully fixed. Beginners often mix the order.
- **Querying outside the span**: `get_bending_moment(x)` only works for `0 <= x <= span`. Out-of-range gives zero or noise.
- **Forgetting `analyse()`**: Result methods return zero/None until you call `beam.analyse()`.
- **Mixing units**: Library expects N, m, Pa. Convert kN/MPa/mm to base SI before passing in.
- **Manually calling `plt.show()` for the auto-plots**: The runtime captures Beam plots without explicit show. If you also call `plt.show()` you may end up with duplicated or empty figures.
- **Re-using a `Beam` after `analyse()`**: Once analysed, treat the object as immutable. To change loads/supports, create a new `Beam`.

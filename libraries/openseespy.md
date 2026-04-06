# openseespy + opsvis — Advanced FEA

## When to Use
`openseespy` is the Python interface to OpenSees, the canonical research-grade FEA library for earthquake engineering and nonlinear structural analysis. `opsvis` provides matplotlib visualisation. Use them when:

- The user needs nonlinear analysis (material or geometric nonlinearity)
- Pushover, time-history, modal, eigen analysis
- Concentrated plasticity / fibre sections / hysteretic materials
- Soil-structure interaction
- The user explicitly mentions "OpenSees", "pushover", "time history", "fibre section"

For linear 2D use `anastruct`. For linear 3D use `PyNite`. OpenSees is overkill for everyday design checks.

## Installation
Already installed. Standard import pattern:
```python
import openseespy.opensees as ops
import opsvis
```
OpenSees commands all live on the `ops` namespace.

## Units
**Unit-agnostic**. Pick a system at the start and stick with it. CalcTree convention: **N, m, Pa, kg** (SI base).

## Domain Lifecycle
Every analysis follows the same pattern:
1. `ops.wipe()` — clear any prior model
2. `ops.model('basic', '-ndm', 2|3, '-ndf', 3|6)` — set dimensions and DOFs per node
3. Define materials, sections, transforms, nodes, elements, supports, loads
4. Set up analysis (`system`, `numberer`, `constraints`, `integrator`, `algorithm`, `analysis`)
5. `ops.analyze(steps)`
6. Query results

## Key API

### Model setup
```python
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)   # 2D: 3 DOFs/node (UX, UY, RZ)
# Or for 3D:
# ops.model('basic', '-ndm', 3, '-ndf', 6)
```

### Nodes
```python
ops.node(1, 0.0, 0.0)
ops.node(2, 10.0, 0.0)
```

### Boundary conditions (`fix`)
```python
ops.fix(1, 1, 1, 0)   # 2D: pin (UX, UY restrained, RZ free)
ops.fix(2, 0, 1, 0)   # roller
```

### Materials
```python
# Linear elastic uniaxial
ops.uniaxialMaterial('Elastic', 1, 200e9)
# Bilinear steel
ops.uniaxialMaterial('Steel01', 2, 250e6, 200e9, 0.01)
# Concrete
ops.uniaxialMaterial('Concrete01', 3, -30e6, -0.002, -25e6, -0.005)
```

### Geometric transformation (essential for beams/columns)
```python
ops.geomTransf('Linear', 1)        # 2D linear
# 3D needs orientation vector:
# ops.geomTransf('Linear', 1, 0, 0, 1)
```

### Elements
```python
# Elastic beam-column
ops.element('elasticBeamColumn', 1, 1, 2, A=0.0123, E=200e9, Iz=222e-6, transfTag=1)
```
For nonlinear: `forceBeamColumn` / `dispBeamColumn` with fibre sections.

### Loads (time series + load pattern)
```python
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.eleLoad('-ele', 1, '-type', '-beamUniform', -15000)   # UDL on element 1 (N/m)
ops.load(2, 0, -50000, 0)                                  # nodal load at node 2
```

### Analysis setup (linear static)
```python
ops.system('BandSPD')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)
```

### Results
- `ops.nodeDisp(2, 2)` — vertical displacement of node 2 (m)
- `ops.nodeReaction(1)` — list of reaction components at node 1
- `ops.eleForce(1)` — element nodal forces (axial, shear, moment at each end)
- `ops.eleResponse(1, 'forces')` — alternative

### Eigen analysis
```python
periods = ops.eigen(3)   # 3 modes; returns eigenvalues
import math
T = [2*math.pi / math.sqrt(lam) for lam in periods]   # periods (s)
```

### Visualisation with `opsvis`
```python
import matplotlib.pyplot as plt
import ctconfig
import opsvis

opsvis.plot_model()
ctconfig.plot_prefix = "ops_model"
plt.show()

opsvis.section_force_diagram_2d('M', 1.0e-3)
ctconfig.plot_prefix = "ops_bmd"
plt.show()
```

## CalcTree Integration

### Output Variables (SI)
```python
import openseespy.opensees as ops

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)
ops.node(1, 0.0, 0.0)
ops.node(2, 10.0, 0.0)
ops.fix(1, 1, 1, 0)
ops.fix(2, 0, 1, 0)
ops.geomTransf('Linear', 1)
ops.element('elasticBeamColumn', 1, 1, 2, 0.0123, 200e9, 222e-6, 1)

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.eleLoad('-ele', 1, '-type', '-beamUniform', -15000)

ops.system('BandSPD')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

ele_forces = ops.eleForce(1)   # [N1, V1, M1, N2, V2, M2]
M_max = float(max(abs(ele_forces[2]), abs(ele_forces[5])))   # N·m
delta_mid = float(ops.nodeDisp(2, 2))                         # m
```

## Examples

### Example 1: Simply supported elastic beam
See "Output Variables" above.

### Example 2: Modal analysis of a 3-storey shear frame
```python
import openseespy.opensees as ops
import math

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Floors at 0, 3, 6, 9 m
for i, y in enumerate([0, 3, 6, 9]):
    ops.node(i+1, 0.0, y)
    if i == 0:
        ops.fix(i+1, 1, 1, 1)

ops.geomTransf('Linear', 1)
# Lump column stiffness — k = 12EI/h^3 simplified
for i in range(3):
    ops.element('elasticBeamColumn', i+1, i+1, i+2, 0.05, 200e9, 1.6e-3, 1)

# Lumped masses (kg) at floors 2,3,4
for i in [2, 3, 4]:
    ops.mass(i, 50000, 50000, 0)

eigvals = ops.eigen(3)
periods = [2*math.pi/math.sqrt(l) for l in eigvals]
T1, T2, T3 = float(periods[0]), float(periods[1]), float(periods[2])
```

### Example 3: Pushover (nonlinear)
```python
import openseespy.opensees as ops

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)
# ... build a fibre-section frame model ...

# Gravity loads first
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(top_node, 0, -100000, 0)

ops.system('BandGeneral'); ops.numberer('RCM'); ops.constraints('Transformation')
ops.integrator('LoadControl', 0.1); ops.algorithm('Newton'); ops.analysis('Static')
ops.analyze(10)
ops.loadConst('-time', 0.0)

# Lateral pushover
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 2, 2)
ops.load(top_node, 1.0, 0, 0)

drifts, base_shears = [], []
ops.integrator('DisplacementControl', top_node, 1, 0.001)
ops.analysis('Static')
for _ in range(200):
    ops.analyze(1)
    drifts.append(ops.nodeDisp(top_node, 1))
    base_shears.append(-ops.eleForce(1)[0])

import matplotlib.pyplot as plt, ctconfig
fig, ax = plt.subplots()
ax.plot(drifts, [bs/1000 for bs in base_shears])
ax.set_xlabel('Roof drift (m)'); ax.set_ylabel('Base shear (kN)')
ctconfig.plot_prefix = "pushover"
plt.show()
```

## Common Mistakes
- **Forgetting `ops.wipe()`**: State persists between blocks within a session — without `wipe()` you'll add to the previous model. Always start with `wipe()`.
- **Wrong DOF count for the model dimension**: 2D models need `'-ndf', 3`; 3D needs `'-ndf', 6`. Element forces and `fix()` arguments depend on this.
- **Missing geomTransf**: Beam-column elements REQUIRE a geometric transformation tag. Forgetting it causes obscure errors.
- **Mixing units**: OpenSees is unit-agnostic. Pick SI (N, m, Pa) and stick with it.
- **Plain `Linear` algorithm for nonlinear**: For nonlinear analysis use `Newton` (or `KrylovNewton`) with appropriate convergence test (`test('NormDispIncr', ...)`).
- **`opsvis` interactive figures**: `opsvis` uses matplotlib, so `ctconfig.plot_prefix` + `plt.show()` works correctly. Don't use any plotly-based visualisation for page output.
- **Assuming `nodeReaction` works without a load step**: Call `ops.reactions()` first to update reactions before reading them.

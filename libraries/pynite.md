# PyNite — 3D Structural Analysis

## When to Use
`PyNite` (imported as `Pynite` or `PyNiteFEA`) is a 3D finite element library for frames, trusses, plates, and shells. Use it when:

- The structure is genuinely 3D (out-of-plane geometry, biaxial bending, lateral-torsional)
- You need plate/shell elements (slabs, walls)
- The user mentions "3D frame", "space frame", "plate", "shell", "wall panel"

For 2D frames use `anastruct`. For continuous beams use `pycba`. For advanced nonlinear FEA use `openseespy`.

## Installation
Already installed as `pynitefea`. Import:
```python
from Pynite import FEModel3D
```

## Coordinate System
- Right-handed, X / Y / Z axes
- **Y is vertical** (gravity along -Y)
- Member local axes: x along the member, y/z perpendicular per orientation

## Units
**Unit-agnostic** but be consistent. CalcTree convention: **N, m, Pa** (SI base) so results align with the structural tile and downstream MathJS scope.

## Key API

### `FEModel3D()` — model container
```python
model = FEModel3D()
```

### Materials
```python
model.add_material(name='Steel', E=200e9, G=77e9, nu=0.3, rho=7850)
```
- `E`, `G`: elastic / shear modulus (Pa)
- `nu`: Poisson ratio
- `rho`: density (kg/m³)

### Sections
```python
model.add_section(name='UC310', A=0.0123, Iy=22.2e-6, Iz=222e-6, J=0.7e-6)
```
- `A`: area (m²)
- `Iy`, `Iz`: second moments of area (m⁴)
- `J`: torsional constant (m⁴)

### Nodes
```python
model.add_node('N1', X=0, Y=0, Z=0)
model.add_node('N2', X=10, Y=0, Z=0)
```

### Members
```python
model.add_member('M1', i_node='N1', j_node='N2', material_name='Steel', section_name='UC310')
```

### Plate / quad elements
```python
model.add_quad('Q1', i_node='N1', j_node='N2', m_node='N3', n_node='N4',
               t=0.2, material_name='Concrete')
```

### Supports
```python
model.def_support('N1', support_DX=True, support_DY=True, support_DZ=True,
                  support_RX=True, support_RY=True, support_RZ=True)  # fully fixed
model.def_support('N2', support_DY=True)                              # roller
```
Booleans for translations (DX/DY/DZ) and rotations (RX/RY/RZ).

### Loads
```python
# Nodal load: N (force) or N·m (moment)
model.add_node_load('N1', Direction='FY', P=-50000, case='Dead')

# Member point load
model.add_member_pt_load('M1', Direction='Fy', P=-10000, x=5, case='Live')

# Member distributed load
model.add_member_dist_load('M1', Direction='Fy', w1=-2000, w2=-2000,
                            x1=0, x2=10, case='Dead')
```
`Direction` for member loads uses local axes (lowercase: `Fx`, `Fy`, `Fz`); for nodal loads uses global (uppercase: `FX`, `FY`, `FZ`, `MX`, `MY`, `MZ`).

### Load combinations
```python
model.add_load_combo('1.2D+1.5L', factors={'Dead': 1.2, 'Live': 1.5})
```

### Analysis
```python
model.analyze(check_statics=True)        # linear static
# or
model.analyze_PDelta()                    # P-delta nonlinear
```

### Results
- `model.nodes['N2'].DX['1.2D+1.5L']` — translation in X (m) at node N2 for that combo
- `model.nodes['N1'].RxnFY['1.2D+1.5L']` — vertical reaction at N1 (N)
- `model.members['M1'].max_moment('Mz', '1.2D+1.5L')` — peak moment about local z (N·m)
- `model.members['M1'].max_shear('Fy', '1.2D+1.5L')`
- `model.members['M1'].plot_moment('Mz', combo_name='1.2D+1.5L')`
- `model.members['M1'].moment_array('Mz', n_points=50, combo_name='1.2D+1.5L')`

### Visualisation
```python
from Pynite.Visualization import Renderer
renderer = Renderer(model)
renderer.combo_name = '1.2D+1.5L'
renderer.render_loads = True
renderer.deformed_shape = True
renderer.deformed_scale = 50
renderer.render_model()
```
PyNite's renderer uses PyVista — it produces interactive plots. For CalcTree page output, prefer matplotlib of result arrays + `ctconfig.plot_prefix`.

## CalcTree Integration

### Output Variables (SI units)
```python
from Pynite import FEModel3D

model = FEModel3D()
model.add_material('Steel', E=200e9, G=77e9, nu=0.3, rho=7850)
model.add_section('UC', A=0.0123, Iy=22.2e-6, Iz=222e-6, J=0.7e-6)

model.add_node('N1', X=0, Y=0, Z=0)
model.add_node('N2', X=10, Y=0, Z=0)
model.def_support('N1', support_DX=True, support_DY=True, support_DZ=True,
                  support_RX=True, support_RY=True, support_RZ=True)
model.def_support('N2', support_DY=True, support_DZ=True)

model.add_member('M1', i_node='N1', j_node='N2', material_name='Steel', section_name='UC')
model.add_member_dist_load('M1', Direction='Fy', w1=-15000, w2=-15000, x1=0, x2=10)
model.add_load_combo('Strength', factors={'Case 1': 1.0})

model.analyze()

M_max = float(model.members['M1'].max_moment('Mz', 'Strength'))         # N·m
V_max = float(model.members['M1'].max_shear('Fy', 'Strength'))          # N
delta = float(model.nodes['N2'].DY['Strength'])                          # m
```

### Charts
```python
import matplotlib.pyplot as plt
import numpy as np
import ctconfig

x = np.linspace(0, 10, 50)
M = model.members['M1'].moment_array('Mz', n_points=50, combo_name='Strength')[1]

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(x, M / 1000)
ax.set_xlabel('Position (m)')
ax.set_ylabel('Moment Mz (kN·m)')
ax.grid(True)

ctconfig.plot_prefix = "pynite_bmd"
plt.show()
```

## Examples

### Example 1: Simply supported 3D beam
```python
from Pynite import FEModel3D

model = FEModel3D()
model.add_material('S', E=200e9, G=77e9, nu=0.3, rho=7850)
model.add_section('S1', A=0.0123, Iy=22.2e-6, Iz=222e-6, J=0.7e-6)

model.add_node('A', X=0, Y=0, Z=0)
model.add_node('B', X=8, Y=0, Z=0)
model.add_member('M', i_node='A', j_node='B', material_name='S', section_name='S1')

model.def_support('A', support_DX=True, support_DY=True, support_DZ=True,
                  support_RX=True)
model.def_support('B', support_DY=True, support_DZ=True)

model.add_member_dist_load('M', Direction='Fy', w1=-12000, w2=-12000, x1=0, x2=8)
model.add_load_combo('SLS', factors={'Case 1': 1.0})

model.analyze()
M_z_max = float(model.members['M'].max_moment('Mz', 'SLS'))
```

### Example 2: Portal frame with biaxial loading
```python
from Pynite import FEModel3D

model = FEModel3D()
model.add_material('S', E=200e9, G=77e9, nu=0.3, rho=7850)
model.add_section('Col', A=0.015, Iy=80e-6, Iz=300e-6, J=1.2e-6)
model.add_section('Bm', A=0.012, Iy=20e-6, Iz=250e-6, J=0.8e-6)

# Column bases
model.add_node('A', X=0, Y=0, Z=0)
model.add_node('B', X=6, Y=0, Z=0)
# Column tops
model.add_node('C', X=0, Y=4, Z=0)
model.add_node('D', X=6, Y=4, Z=0)

model.add_member('LC', 'A', 'C', 'S', 'Col')
model.add_member('RC', 'B', 'D', 'S', 'Col')
model.add_member('Bm', 'C', 'D', 'S', 'Bm')

model.def_support('A', support_DX=True, support_DY=True, support_DZ=True,
                  support_RX=True, support_RY=True, support_RZ=True)
model.def_support('B', support_DX=True, support_DY=True, support_DZ=True,
                  support_RX=True, support_RY=True, support_RZ=True)

model.add_member_dist_load('Bm', Direction='Fy', w1=-10000, w2=-10000, x1=0, x2=6)
model.add_node_load('C', Direction='FX', P=20000)

model.add_load_combo('Strength', factors={'Case 1': 1.0})
model.analyze()
```

## Common Mistakes
- **Unit drift**: PyNite is unit-agnostic. Use SI base (N, m, Pa) for compatibility with CalcTree's structural tile. NOT mm/MPa/kN.
- **Direction casing**: Member loads use lowercase local axes (`Fy`), nodal loads use uppercase global (`FY`). Mixing them silently fails.
- **Forgetting `add_load_combo`**: Without a combo, results methods raise. Always define at least one combo before analysis.
- **Under-restrained models**: PyNite needs full 6-DOF restraint somewhere. A typical SS beam still needs DZ + RX restrained at one end to suppress out-of-plane and torsion modes.
- **Using `Renderer` for page output**: PyVista renderers are interactive 3D — they don't flow through `ctconfig.plot_prefix`. Use matplotlib of `moment_array`/`shear_array` for page-embedded charts.
- **Missing material density**: If `rho` is omitted, self-weight is zero — fine for linear elastic but a trap if the user expected gravity.

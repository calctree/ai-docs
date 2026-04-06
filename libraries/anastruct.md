# anastruct — 2D Frame & Truss Analysis

## When to Use
`anastruct` is a 2D structural analysis library for frames, beams, and trusses using the direct stiffness method. Choose it when:

- You need bending moments, shear forces, axial forces, displacements, or reactions for a 2D structure
- The structure is planar (no 3D effects)
- You need to plot moment, shear, displacement, or reaction diagrams
- The user asks for beam analysis, frame analysis, portal frame, continuous beam, simply supported beam, cantilever, truss

For 3D structures use PyNite. For non-linear or advanced FEA use openseespy. For section properties (Ix, Zx, A) use sectionproperties.

## Installation
Already installed in the CalcTree Python runtime. Do NOT include `pip install` lines. Just `from anastruct import SystemElements`.

## Coordinate System
- X = horizontal, Y = vertical
- Gravity loads are negative Y (downward = negative)
- Lengths in metres, forces in kN, moments in kN·m, EI in kN·m² (anastruct's defaults)
- Angles in degrees for `add_support_roll`

## Key API

### `SystemElements(EA=15e3, EI=5e3, mesh=50, plot_backend='mpl')`
The model container. `EA` (axial stiffness) and `EI` (flexural stiffness) become the defaults for elements that don't specify their own.

### `ss.add_element(location, EA=None, EI=None, g=0, spring=None, mp=None)`
Adds a beam element. `location` is `[[x1, y1], [x2, y2]]`. Returns the element id (int).
- `EA`, `EI`: override defaults for this element
- `spring`: rotational releases, e.g. `{1: 0}` releases the start node (node 1 of element), `{2: 0}` the end. `0` = pin, finite value = rotational stiffness.

### `ss.add_truss_element(location, EA=None)`
Truss element (axial only, both ends pinned).

### Supports
- `ss.add_support_hinged(node_id)` — pin (restrains X, Y; rotation free)
- `ss.add_support_roll(node_id, direction='x' or 'y', angle=None)` — roller
- `ss.add_support_fixed(node_id)` — fully fixed
- `ss.add_support_spring(node_id, translation, k, roll=False)` — spring support

Node ids are auto-assigned: node 1 is the first endpoint of the first element, increasing sequentially.

### Loads
- `ss.q_load(q, element_id, direction='element')` — distributed load (kN/m). `direction` can be `'element'` (perpendicular), `'x'`, `'y'`. Use **negative q** for downward gravity load.
- `ss.point_load(node_id, Fx=0, Fy=0)` — point load on a node (kN). Use negative `Fy` for gravity.
- `ss.moment_load(node_id, Ty)` — applied moment (kN·m).

### `ss.solve()`
Runs the analysis. Returns the displacement vector. Call before extracting results.

### Results
- `ss.get_node_results_system()` — list of dicts per node: `{id, Fx, Fy, Ty, ux, uy, phi_y}`. `Fx/Fy` are reactions (zero at unsupported nodes).
- `ss.get_node_displacements()` — `[(node_id, ux, uy, phi_y), ...]`
- `ss.get_element_results(element_id=0, verbose=False)` — when `element_id=0`, returns list across all elements with `{id, length, alpha, u, N_1, N_2, wmax, wmin, Mmin, Mmax, q}`. For one element, returns a dict.
- `ss.get_element_result_range('moment'|'shear'|'axial')` — list of arrays, one per element, of values along the length.

### Plotting (returns matplotlib Figure)
- `ss.show_structure(show=False)` — geometry + supports + loads
- `ss.show_bending_moment(show=False)` — BMD
- `ss.show_shear_force(show=False)` — SFD
- `ss.show_axial_force(show=False)` — AFD
- `ss.show_displacement(show=False, factor=None)` — deflected shape
- `ss.show_reaction_force(show=False)` — reactions

Always pass `show=False` so the figure goes through CalcTree's chart pipeline.

## CalcTree Integration

### Output Variables (CRITICAL)
The last expression in a Python block, OR any top-level assigned variable, becomes available in page scope and can be referenced via `<Mention>`. Always assign your key results to clearly named module-scope variables.

```python
from anastruct import SystemElements

ss = SystemElements()
ss.add_element([[0, 0], [10, 0]])
ss.add_support_hinged(1)
ss.add_support_roll(2, direction='y')
ss.q_load(q=-15, element_id=1)
ss.solve()

# Extract maxima as named scope variables
moment_range = ss.get_element_result_range('moment')[0]
shear_range = ss.get_element_result_range('shear')[0]
disps = ss.get_node_displacements()

M_max = max(abs(m) for m in moment_range)         # kN·m
V_max = max(abs(v) for v in shear_range)          # kN
delta_mid = max(abs(d[2]) for d in disps) * 1000  # mm
```

`M_max`, `V_max`, `delta_mid` are now mentionable on the page.

### Unit Handling
anastruct itself is **unit-agnostic** — it expects consistent units (kN, m, kN·m). If page variables are `ct.quantity` objects, convert before passing to anastruct:

```python
# Page provides: L (with units), q (with units), E (with units), I (with units)
L_m = L.to('m').magnitude
q_kNm = q.to('kN/m').magnitude
EI_kNm2 = (E * I).to('kN*m^2').magnitude

ss = SystemElements(EI=EI_kNm2)
ss.add_element([[0, 0], [L_m, 0]])
ss.q_load(q=-q_kNm, element_id=1)
```

Wrap the result back into a quantity if downstream code expects units:

```python
M_max = ct.quantity(f'{max(abs(m) for m in moment_range)} kN*m')
```

### Charts
To render an anastruct plot on the page:

```python
import matplotlib.pyplot as plt
import ctconfig

ctconfig.plot_prefix = "bmd"
fig = ss.show_bending_moment(show=False)
plt.show()
```

This creates an output key `bmd1`. After running, you MUST call `generateCalculation` with MDX that includes:
```
<Mention key="bmd1" value="bmd1" variableType="image" />
```
Otherwise the chart will not appear on the page.

For multiple plots, each `plt.show()` increments the suffix (`bmd1`, `bmd2`, ...).

## Examples

### Example 1: Simply Supported Beam with UDL
```python
from anastruct import SystemElements
import matplotlib.pyplot as plt
import ctconfig

# 10 m beam, 15 kN/m UDL, EI = 30000 kN·m² (e.g. 310UC97)
ss = SystemElements(EI=30000)
ss.add_element([[0, 0], [10, 0]])
ss.add_support_hinged(1)
ss.add_support_roll(2, direction='y')
ss.q_load(q=-15, element_id=1)
ss.solve()

# Scope variables
moments = ss.get_element_result_range('moment')[0]
shears = ss.get_element_result_range('shear')[0]
disps = ss.get_node_displacements()

M_max = max(abs(m) for m in moments)              # 187.5 kN·m
V_max = max(abs(v) for v in shears)               # 75 kN
delta_max = max(abs(d[2]) for d in disps) * 1000  # mm

# Chart
ctconfig.plot_prefix = "beam_bmd"
ss.show_bending_moment(show=False)
plt.show()
```
Output variables: `M_max`, `V_max`, `delta_max`, image `beam_bmd1`.

### Example 2: Portal Frame
```python
from anastruct import SystemElements

ss = SystemElements(EI=20000, EA=8e5)
# Left column
ss.add_element([[0, 0], [0, 5]])
# Beam
ss.add_element([[0, 5], [8, 5]])
# Right column
ss.add_element([[8, 5], [8, 0]])

ss.add_support_fixed(1)   # base of left column
ss.add_support_fixed(4)   # base of right column

ss.q_load(q=-10, element_id=2)              # gravity on beam
ss.point_load(node_id=2, Fx=20)             # lateral load at top of left column

ss.solve()

# Reactions
nodes = ss.get_node_results_system()
R_left  = (nodes[0]['Fx'], nodes[0]['Fy'])
R_right = (nodes[3]['Fx'], nodes[3]['Fy'])

# Maxima across all elements
all_moments = [m for arr in ss.get_element_result_range('moment') for m in arr]
M_frame_max = max(abs(m) for m in all_moments)
```

### Example 3: Continuous Beam (3 spans)
```python
from anastruct import SystemElements

ss = SystemElements(EI=25000)
ss.add_element([[0, 0], [6, 0]])
ss.add_element([[6, 0], [12, 0]])
ss.add_element([[12, 0], [18, 0]])

ss.add_support_hinged(1)
ss.add_support_roll(2, direction='y')
ss.add_support_roll(3, direction='y')
ss.add_support_roll(4, direction='y')

ss.q_load(q=-12, element_id=1)
ss.q_load(q=-12, element_id=2)
ss.q_load(q=-12, element_id=3)

ss.solve()

# Hogging moment over interior supports
nodes = ss.get_node_results_system()
M_support_2 = nodes[1]['Ty']  # kN·m
M_support_3 = nodes[2]['Ty']
```

## Common Mistakes

- **Positive `q` for gravity**: Use `q=-15` for downward UDL, NOT `q=15`. Positive `q` pushes upward.
- **Forgetting `ss.solve()`**: Results methods return zeros if you forget to call solve.
- **Wrong node ids**: Node ids are auto-assigned in order of element creation. Sketch the geometry mentally — node 1 is the first point of the first element, not always at the origin.
- **Re-wrapping `ct.quantity`**: Page variables with units are already `ct.quantity` objects. Use `.to('m').magnitude` to extract a plain float for anastruct, never `ct.quantity(L)`.
- **Mixing units**: anastruct is unit-agnostic. If you pass `L` in mm and `EI` in N·m² you'll get garbage. Stick to kN, m, kN·m, kN·m² consistently.
- **`show=True` on plots**: Always use `show=False` so the figure flows through CalcTree's `ctconfig.plot_prefix` capture.
- **Missing `<Mention>` for charts**: A `plt.show()` call by itself doesn't put the image on the page — you must follow up with `generateCalculation` containing the `<Mention key="prefix1" .../>` tag.
- **Using `add_element` for trusses**: Use `add_truss_element` if you want axial-only behaviour with no moment continuity.

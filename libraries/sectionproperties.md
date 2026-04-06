# sectionproperties — Cross-Section Analysis

## When to Use
`sectionproperties` computes geometric and warping properties of arbitrary 2D cross-sections using a finite element mesh. Use it when:

- The user needs Ix, Iy, Zx, Zy, Sx (plastic modulus), J (torsion), Iw (warping), rx, ry, A
- The section is non-standard (custom plate girder, composite, built-up, hollow, with holes)
- Standard rolled sections aren't enough — for known catalog sections you can also use the built-in section library

For just selecting from a steel catalog (310UC97 etc.), prefer `steelpy` or hardcoded values; use `sectionproperties` when you need geometric truth from custom shapes.

## Installation
Already installed in CalcTree's Python runtime (with numba acceleration). Import from `sectionproperties.pre` and `sectionproperties.analysis`.

## Units
**Unit-agnostic**. Whatever length unit you put in, you get out (mm in → mm² for area, mm⁴ for I, mm³ for Z). Default convention in CalcTree: input geometry in **mm**, results converted to SI as needed.

## Key API

### Geometry creation
```python
from sectionproperties.pre.library import (
    rectangular_section, circular_section, i_section,
    channel_section, rectangular_hollow_section,
    circular_hollow_section, tee_section, angle_section,
)
```

Common constructors:
- `rectangular_section(d, b)` — depth, breadth
- `circular_section(d, n)` — diameter, number of facets (use 64+)
- `i_section(d, b, t_f, t_w, r, n_r)` — depth, flange width, flange thickness, web thickness, root radius, root facets
- `rectangular_hollow_section(d, b, t, r_out, n_r)` — RHS/SHS
- `circular_hollow_section(d, t, n)` — CHS

All return a `Geometry` object. Combine with `+` for compound sections, `-` (via `geom - hole`) for holes.

### Custom geometry
```python
from sectionproperties.pre import Geometry
from shapely.geometry import Polygon

poly = Polygon([(0, 0), (200, 0), (200, 300), (0, 300)])
geom = Geometry(geom=poly)
```

### Mesh + Section
```python
from sectionproperties.analysis import Section

geom.create_mesh(mesh_sizes=[5.0])  # smaller = more accurate, slower
section = Section(geometry=geom)
```

### Analyses
- `section.calculate_geometric_properties()` — area, centroid, Ix, Iy, Zx, Zy, rx, ry, principal axes
- `section.calculate_warping_properties()` — J (torsion constant), Iw (warping constant), shear centre. Requires geometric first.
- `section.calculate_plastic_properties()` — Sx, Sy (plastic moduli), shape factor

### Result accessors
- `section.get_area()` → A
- `section.get_ic()` → `(ixx_c, iyy_c, ixy_c)` about centroid
- `section.get_z()` → `(zxx_plus, zxx_minus, zyy_plus, zyy_minus)` elastic section moduli
- `section.get_s()` → `(sxx, syy)` plastic moduli (after `calculate_plastic_properties`)
- `section.get_rc()` → `(rx, ry)` radii of gyration
- `section.get_j()` → torsion constant
- `section.get_gamma()` → warping constant Iw

## CalcTree Integration

### Output Variables
Assign all useful properties to top-level variables so they appear on the page.

```python
from sectionproperties.pre.library import i_section
from sectionproperties.analysis import Section

# 310UC97-ish I-section (mm)
geom = i_section(d=308, b=305, t_f=15.4, t_w=9.9, r=16.5, n_r=8)
geom.create_mesh(mesh_sizes=[5.0])
sec = Section(geometry=geom)

sec.calculate_geometric_properties()
sec.calculate_plastic_properties()
sec.calculate_warping_properties()

A    = sec.get_area()                  # mm²
ixx, iyy, _ = sec.get_ic()             # mm⁴
zxx_plus, zxx_minus, zyy_plus, zyy_minus = sec.get_z()
sxx, syy = sec.get_s()                 # mm³ (plastic)
J        = sec.get_j()                 # mm⁴
Iw       = sec.get_gamma()             # mm⁶
```

### Converting to page-friendly units (with `ct.quantity`)
```python
A_qty   = ct.quantity(f'{A} mm^2').to('m^2')
Ix_qty  = ct.quantity(f'{ixx} mm^4').to('m^4')
Zx_qty  = ct.quantity(f'{min(zxx_plus, zxx_minus)} mm^3').to('m^3')
```

These are now mentionable on the page as `A_qty`, `Ix_qty`, `Zx_qty`.

### Charts
To plot the mesh or stress contours:
```python
import matplotlib.pyplot as plt
import ctconfig

ctconfig.plot_prefix = "section_geom"
sec.plot_mesh(materials=False)
plt.show()
```
Then in MDX: `<Mention key="section_geom1" value="section_geom1" variableType="image" />`.

## Examples

### Example 1: I-section properties
```python
from sectionproperties.pre.library import i_section
from sectionproperties.analysis import Section

geom = i_section(d=308, b=305, t_f=15.4, t_w=9.9, r=16.5, n_r=8)
geom.create_mesh(mesh_sizes=[5.0])
sec = Section(geometry=geom)
sec.calculate_geometric_properties()
sec.calculate_plastic_properties()

A   = sec.get_area()
ixx, iyy, _ = sec.get_ic()
zxx = min(sec.get_z()[:2])             # smaller of Zx+ / Zx-
sxx, syy = sec.get_s()
```

### Example 2: Box girder (RHS with internal stiffener — compound)
```python
from sectionproperties.pre.library import (
    rectangular_hollow_section, rectangular_section,
)
from sectionproperties.analysis import Section

box  = rectangular_hollow_section(d=600, b=400, t=12, r_out=24, n_r=8)
stiff = rectangular_section(d=576, b=10).align_center(align_to=box)
compound = box + stiff

compound.create_mesh(mesh_sizes=[8.0])
sec = Section(geometry=compound)
sec.calculate_geometric_properties()

A = sec.get_area()
ixx, iyy, _ = sec.get_ic()
```

### Example 3: Plate with hole
```python
from sectionproperties.pre.library import rectangular_section, circular_section
from sectionproperties.analysis import Section

plate = rectangular_section(d=300, b=200)
hole  = circular_section(d=80, n=64).shift_section(x_offset=100, y_offset=150)
geom  = plate - hole

geom.create_mesh(mesh_sizes=[3.0])
sec = Section(geometry=geom)
sec.calculate_geometric_properties()
A_net = sec.get_area()
```

## Common Mistakes

- **Forgetting `create_mesh` before `Section(...)`**: You'll get an error. Always mesh first.
- **Mesh too coarse**: For thin webs, use `mesh_sizes` ≤ web thickness, or properties drift.
- **Calling warping/plastic before geometric**: `calculate_geometric_properties()` must run first.
- **Mixing units**: Choose mm OR m and stay consistent. Mm is conventional and matches steel handbooks.
- **Re-wrapping `ct.quantity`**: If page provides dimensions as quantities, extract magnitudes in mm before passing into sectionproperties: `d_mm = d.to('mm').magnitude`.
- **Assuming `get_z()` returns one value**: It returns 4 (Zx+, Zx-, Zy+, Zy-). For a symmetric section they're equal in pairs; for asymmetric pick the smaller of the two opposite-fibre values for design.
- **Using sectionproperties for catalog sections in tight loops**: Meshing is slow. For 310UC97 etc., use steelpy or hardcoded values from a steel handbook.

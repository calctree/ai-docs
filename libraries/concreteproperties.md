# concreteproperties — Reinforced Concrete Section Analysis

## When to Use
`concreteproperties` performs detailed analysis of arbitrary reinforced concrete cross-sections: gross/cracked/transformed properties, moment capacity, moment-curvature, biaxial moment-axial interaction (M-N), and stress analyses. Use it when:

- The user needs accurate RC section capacity (φMn, φPn, M-N diagram)
- The user wants moment-curvature for ductility / pushover input
- The section is non-rectangular or has complex reinforcement layout
- Design code: AS3600, EC2, ACI318 (the library exposes options for each)

For simple flexural checks by hand, write a `handcalcs` block instead. For steel sections use `sectionproperties` + `steelpy`.

## Installation
Already installed. Standard imports:
```python
from concreteproperties.material import Concrete, SteelBar
from concreteproperties.stress_strain_profile import (
    ConcreteLinear, ConcreteLinearNoTension, RectangularStressBlock,
    SteelElasticPlastic,
)
from concreteproperties.pre import add_bar_rectangular_array
from concreteproperties.concrete_section import ConcreteSection
from sectionproperties.pre.library import concrete_rectangular_section
```

## Units
**Unit-agnostic** — but the convention in concreteproperties examples (and what the design-code formulas assume) is **N, mm, MPa**:
- Lengths: mm
- Areas: mm²
- Forces: N
- Moments: N·mm
- Stresses: MPa = N/mm²

This is the OPPOSITE of CalcTree's structural tile (SI base). When pulling page variables into concreteproperties, convert to mm/MPa first; when sending results back, convert to kN·m if needed.

## Key API

### Materials
```python
concrete = Concrete(
    name='40 MPa',
    density=2.4e-6,                                # kg/mm³
    stress_strain_profile=ConcreteLinearNoTension(elastic_modulus=32800, ultimate_strain=0.003),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=40, alpha=0.85, gamma=0.83, ultimate_strain=0.003,
    ),
    flexural_tensile_strength=3.8,
    colour='lightgrey',
)

steel = SteelBar(
    name='500 MPa',
    density=7.85e-6,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=500, elastic_modulus=200e3, fracture_strain=0.05,
    ),
    colour='grey',
)
```

### Geometry + bars
```python
geom = concrete_rectangular_section(
    d=600, b=400,
    dia_top=20, n_top=3,
    dia_bot=20, n_bot=4,
    n_circle=4,
    cover=40,
    area_top=None,
    area_bot=None,
    conc_mat=concrete,
    steel_mat=steel,
)
```
Or use `add_bar_rectangular_array` / `add_bar` to place reinforcement manually.

### Create the section and run analyses
```python
section = ConcreteSection(geom)

# Gross / cracked / transformed properties
gross = section.get_gross_properties()
cracked = section.calculate_cracked_properties(theta=0)

# Ultimate moment capacity (uniaxial)
ult = section.ultimate_bending_capacity(theta=0)
phi_M = 0.85 * ult.m_xy   # phi varies by code, use the correct factor for your code

# Moment-curvature
mk = section.moment_curvature_analysis(theta=0, kappa_inc=1e-6)

# Moment-axial interaction (M-N diagram)
mn = section.moment_interaction_diagram(theta=0)

# Stress under a given load
stress = section.calculate_uncracked_stress(n=0, m_x=200e6)   # N, N·mm
```

### Plotting
```python
import matplotlib.pyplot as plt
import ctconfig

ctconfig.plot_prefix = "rc_section"
section.plot_section()
plt.show()

ctconfig.plot_prefix = "rc_mk"
mk.plot_results()
plt.show()

ctconfig.plot_prefix = "rc_mn"
mn.plot_diagram()
plt.show()
```

## CalcTree Integration

### Output Variables
```python
ult = section.ultimate_bending_capacity(theta=0)
M_u_Nmm = float(ult.m_xy)            # N·mm
phi = 0.85
phi_M_u_kNm = phi * M_u_Nmm / 1e6     # kN·m

# Cracked properties
cracked = section.calculate_cracked_properties(theta=0)
I_cr_mm4 = float(cracked.i_cr)
M_cr_Nmm = float(cracked.m_cr)
M_cr_kNm = M_cr_Nmm / 1e6
```

### Combine with anastruct moment for utilisation
```python
from anastruct import SystemElements
ss = SystemElements(EI=30000)
ss.add_element([[0, 0], [10, 0]])
ss.add_support_hinged(1); ss.add_support_roll(2, direction='y')
ss.q_load(q=-15, element_id=1)
ss.solve()
M_star_kNm = float(max(abs(m) for m in ss.get_element_result_range('moment')[0]))

# concreteproperties capacity (built above)
phi_M_u_kNm = 0.85 * float(section.ultimate_bending_capacity(theta=0).m_xy) / 1e6

UR_flexure = M_star_kNm / phi_M_u_kNm
```

## Examples

### Example 1: Rectangular RC beam — flexural capacity
```python
from concreteproperties.material import Concrete, SteelBar
from concreteproperties.stress_strain_profile import (
    ConcreteLinearNoTension, RectangularStressBlock, SteelElasticPlastic,
)
from concreteproperties.concrete_section import ConcreteSection
from sectionproperties.pre.library import concrete_rectangular_section

concrete = Concrete(
    name='40MPa', density=2.4e-6,
    stress_strain_profile=ConcreteLinearNoTension(elastic_modulus=32800, ultimate_strain=0.003),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=40, alpha=0.85, gamma=0.83, ultimate_strain=0.003,
    ),
    flexural_tensile_strength=3.8, colour='lightgrey',
)
steel = SteelBar(
    name='500MPa', density=7.85e-6,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=500, elastic_modulus=200e3, fracture_strain=0.05,
    ),
    colour='grey',
)

geom = concrete_rectangular_section(
    d=600, b=400, dia_top=16, n_top=2, dia_bot=20, n_bot=4,
    n_circle=4, cover=40, area_top=None, area_bot=None,
    conc_mat=concrete, steel_mat=steel,
)

section = ConcreteSection(geom)
ult = section.ultimate_bending_capacity(theta=0)
phi_M_kNm = 0.85 * float(ult.m_xy) / 1e6
neutral_axis_mm = float(ult.d_n)
```

### Example 2: M-N interaction diagram for column
```python
mn = section.moment_interaction_diagram(theta=0, n_points=24)

import matplotlib.pyplot as plt, ctconfig
ctconfig.plot_prefix = "mn_diagram"
mn.plot_diagram()
plt.show()
```

## Common Mistakes
- **Unit confusion**: concreteproperties expects **N/mm/MPa**. Mixing in kN or m gives results that look reasonable but are wrong by 10³ or 10⁶.
- **Wrong density units**: density is in kg/mm³ here (2.4e-6, not 2400 kg/m³).
- **Forgetting `theta`**: For uniaxial bending about strong axis, `theta=0`. About weak axis, `theta=pi/2`.
- **Re-wrapping page quantities**: If page provides `f_c` as `ct.quantity`, extract the magnitude in MPa first (`f_c.to('MPa').magnitude`) before defining the material.
- **Returning N·mm to the page without converting**: Always convert to kN·m before assigning to a page scope variable, otherwise the user sees 10⁶× too large.
- **Using `Concrete()` without an `ultimate_stress_strain_profile`**: The library needs both the elastic profile (for serviceability) and the rectangular block (for ultimate). Forgetting one causes errors at analysis time.

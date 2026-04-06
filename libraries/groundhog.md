# groundhog — Geotechnical Engineering Toolkit

## When to Use
`groundhog` is a Python library of geotechnical engineering correlations and design functions: soil parameter correlations from in-situ tests (CPT, SPT), pile capacity (axial, lateral), shallow foundation bearing, slope stability, and more. It's the go-to library when:

- The user has CPT or SPT data and wants soil parameter estimates
- You need pile axial/lateral capacity per a published method (API, ICP, NGI)
- Bearing capacity / settlement of shallow foundations
- The user mentions "CPT", "SPT", "pile capacity", "bearing capacity", "geotechnical"

For soil-structure interaction or seismic site response, use `PySeismoSoil`. For 3D geological modelling use `gempy`.

## Installation
Already installed:
```python
import groundhog
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing
from groundhog.deepfoundations.axialcapacity import skinfriction, endbearing
from groundhog.shallowfoundations.capacity import shallow
```
The package is large and modular — import only what you need.

## Units
**Strict SI conventions** (m, kPa, kN, MPa). Most correlations expect:
- Depths in **m**
- Stresses in **kPa**
- Cone tip resistance qc in **MPa**
- Sleeve friction fs in **MPa** or **kPa** (varies — check the function signature)

When pulling page values, convert before passing.

## Key Modules

### CPT processing — `groundhog.siteinvestigation.insitutests.pcpt_processing`
```python
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing

cpt = PCPTProcessing(title='BH-01')
cpt.load_pandas(df)               # df with columns z [m], qc [MPa], fs [MPa], u2 [MPa]
cpt.set_reference_level(z_ref=0)
cpt.dropna_rows()
cpt.normalise_pcpt()              # adds Qt, Fr, Bq columns
cpt.plot_raw_pcpt()
```

### Soil parameter correlations — `groundhog.siteinvestigation.classification`
```python
from groundhog.siteinvestigation.correlations.cpt_correlations import (
    relativedensity_sand_baldi,
    frictionangle_sand_kulhawymayne,
    undrainedshearstrength_clay_lunne,
)
phi_deg = frictionangle_sand_kulhawymayne(qc=15, sigma_vo_eff=100)['phi [deg]']
Su_kPa = undrainedshearstrength_clay_lunne(qt=2.5, sigma_vo=80, Nkt=15)['Su [kPa]']
```
Each correlation returns a dict with the result and intermediate values, so you can capture the lot.

### Pile axial capacity — `groundhog.deepfoundations.axialcapacity`
```python
from groundhog.deepfoundations.axialcapacity.skinfriction import API_unit_shaft_friction_clay
fs = API_unit_shaft_friction_clay(undrained_shear_strength=80, sigma_vo_eff=120)['f_s [kPa]']
```

### Shallow foundation bearing — `groundhog.shallowfoundations.capacity`
```python
from groundhog.shallowfoundations.capacity import shallow
result = shallow.bearingcapacity_circular_vesic(
    diameter=2.0, depth=1.5,
    cohesion=30, friction_angle=28,
    unit_weight_above=18, unit_weight_below=19,
)
q_ult_kPa = result['q_ult [kPa]']
```

## CalcTree Integration

### Output Variables
```python
from groundhog.siteinvestigation.correlations.cpt_correlations import (
    frictionangle_sand_kulhawymayne,
)

qc_MPa = 12
sigma_vo_eff_kPa = 90
result = frictionangle_sand_kulhawymayne(qc=qc_MPa, sigma_vo_eff=sigma_vo_eff_kPa)
phi_deg = float(result['phi [deg]'])
```

### Reading uploaded CPT files
```python
import pandas as pd
import io
from groundhog.siteinvestigation.insitutests.pcpt_processing import PCPTProcessing

csv = ct.open('cpt_data.csv', mode='r').read()
df = pd.read_csv(io.StringIO(csv))   # expects z, qc, fs, u2 columns

cpt = PCPTProcessing(title='Test CPT')
cpt.load_pandas(df)
cpt.dropna_rows()
cpt.normalise_pcpt()

qc_max = float(df['qc'].max())
qc_avg = float(df['qc'].mean())
```

### Charts
```python
import matplotlib.pyplot as plt
import ctconfig

fig, ax = plt.subplots(figsize=(4, 8))
ax.plot(df['qc'], df['z'])
ax.invert_yaxis()
ax.set_xlabel('q_c (MPa)')
ax.set_ylabel('Depth (m)')
ax.grid(True)

ctconfig.plot_prefix = "cpt_profile"
plt.show()
```
Then in MDX: `<Mention key="cpt_profile1" value="cpt_profile1" variableType="image" />`.

## Examples

### Example 1: Bearing capacity of a strip footing
```python
from groundhog.shallowfoundations.capacity.bearingcapacityshallow import (
    bearingcapacity_strip_vesic,
)

result = bearingcapacity_strip_vesic(
    width=2.0, depth=1.0,
    cohesion=0, friction_angle=32,
    unit_weight_above=18, unit_weight_below=19,
)
q_ult_kPa = float(result['q_ult [kPa]'])
Nq = float(result['Nq [-]'])
Nc = float(result['Nc [-]'])
Ngamma = float(result['Ngamma [-]'])
```

### Example 2: Sand friction angle from CPT
```python
from groundhog.siteinvestigation.correlations.cpt_correlations import (
    frictionangle_sand_kulhawymayne,
)

depths = [2, 4, 6, 8, 10]
qcs    = [8, 10, 14, 16, 18]    # MPa
sigmas_eff = [d * 9 for d in depths]  # kPa, gamma_eff ~ 9 kN/m³

phis = []
for qc, s in zip(qcs, sigmas_eff):
    res = frictionangle_sand_kulhawymayne(qc=qc, sigma_vo_eff=s)
    phis.append(float(res['phi [deg]']))

phi_avg = sum(phis) / len(phis)
```

### Example 3: API pile shaft friction in clay
```python
from groundhog.deepfoundations.axialcapacity.skinfriction import (
    API_unit_shaft_friction_clay,
)

depths = [5, 10, 15, 20]      # m
Sus    = [40, 60, 80, 100]    # kPa
sigvos = [50, 100, 150, 200]  # kPa

f_s_total = 0
for Su, sv in zip(Sus, sigvos):
    res = API_unit_shaft_friction_clay(undrained_shear_strength=Su, sigma_vo_eff=sv)
    f_s_total += res['f_s [kPa]']
```

## Common Mistakes
- **Wrong stress units**: Most groundhog functions expect kPa for effective stress and MPa for cone tip resistance. Mixing them gives correlations that look reasonable but are wrong by ~1000×.
- **Forgetting `[unit]` keys**: Results are dicts where every key includes a unit suffix (`'Su [kPa]'`, `'phi [deg]'`). Don't try `result['Su']` — it'll KeyError.
- **Re-wrapping `ct.quantity`**: Strip page units explicitly to plain SI floats before passing.
- **Mixing depth conventions**: Some functions use depth-from-surface, some use depth-from-reference. Read the function's docstring.
- **Treating correlations as exact**: Geotechnical correlations have ±20–50% scatter. Communicate that in the report — never present a correlation result as a precise value.
- **Importing the whole package**: `import groundhog` loads a lot. Import the specific submodule you need.

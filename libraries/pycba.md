# pycba — Continuous Beam Analysis

## When to Use
`pycba` is a focused library for analysing continuous beams (single span, multi-span, with cantilevers). It uses the stiffness method and is much simpler than `anastruct` when the structure is just a beam on supports. Choose pycba when:

- The structure is a 1D beam (no frames, no trusses)
- You have multiple spans, possibly with cantilevers and varying EI
- You want quick moment/shear/deflection envelopes
- The user mentions "continuous beam", "two-span", "three-span", "cantilever"

For 2D frames or trusses use `anastruct`. For 3D use `PyNite`.

## Installation
Already installed. Imports:
```python
from pycba import BeamAnalysis
```

## Units
**Unit-agnostic** but the convention is **kN, m, kN/m, kN·m²**. EI must be consistent (e.g. kN·m²).

## Key API

### `BeamAnalysis(L, EI, R, LM, eletype=None)`
- `L`: list of span lengths (m). Each entry is one span between supports.
- `EI`: float (constant) or list (per span) of EI in kN·m².
- `R`: list of restraint codes describing supports — see below. There must be `len(L) + 1` supports.
- `LM`: list of load definitions (see below).
- `eletype`: optional list per span; usually leave default.

### Support codes (`R`)
Each support is encoded as `[v, m]`:
- `v`: vertical restraint (1 = fixed, 0 = free)
- `m`: rotational restraint (1 = fixed, 0 = free)

Common patterns:
- Pin: `[1, 0]`
- Fixed: `[1, 1]`
- Roller: `[1, 0]`
- Free end (cantilever tip): `[0, 0]`

`R` is given as a flat list of pairs:
```python
R = [1, 0,   # support 1 — pin
     1, 0,   # support 2 — pin
     1, 0]   # support 3 — pin (3 supports = 2 spans)
```

### Load matrix (`LM`)
Each row is a load: `[span_index, load_type, magnitude, a, b]`
- `span_index`: 1-based index of span
- `load_type`:
  - `1` = point load (kN), `a` = distance from left support of that span, `b` unused (set 0)
  - `2` = UDL (kN/m), `a` = start position in span, `b` = end position
  - `3` = moment load (kN·m), `a` = position
  - `4` = partial UDL with magnitude varying linearly (advanced)

UDL across the whole span: `[span_idx, 2, w, 0, L_span]`.

### Solving
```python
beam = BeamAnalysis(L=[10], EI=30000, R=[1,0,1,0], LM=[[1, 2, -15, 0, 10]])
beam.analyze()
```
`analyze()` runs the stiffness solve. Sign convention: downward loads are **negative**.

### Results
After `analyze()`, results are on `beam.beam_results`:
- `beam.beam_results.results.M` — array of bending moments along the beam (kN·m)
- `beam.beam_results.results.V` — shear force array (kN)
- `beam.beam_results.results.D` — deflection array (m)
- `beam.beam_results.results.R` — reactions at supports (kN, kN·m)
- `beam.beam_results.results.x` — x-coordinates corresponding to the above arrays

Convenience accessors:
- `beam.beam_results.Mmax`, `Mmin`
- `beam.beam_results.Vmax`, `Vmin`
- `beam.beam_results.Dmax`, `Dmin`

### Plotting
```python
import matplotlib.pyplot as plt
beam.plot_results()   # one figure with M, V, D subplots
```
Or build your own with `beam.beam_results.results.x` etc.

## CalcTree Integration

### Output Variables
```python
from pycba import BeamAnalysis

beam = BeamAnalysis(
    L=[6, 8, 6],                # 3 spans
    EI=30000,                   # kN·m²
    R=[1,0, 1,0, 1,0, 1,0],     # 4 pin supports
    LM=[
        [1, 2, -12, 0, 6],
        [2, 2, -12, 0, 8],
        [3, 2, -12, 0, 6],
    ],
)
beam.analyze()

M_max = float(max(abs(beam.beam_results.results.M)))     # kN·m
V_max = float(max(abs(beam.beam_results.results.V)))     # kN
D_max = float(max(abs(beam.beam_results.results.D))) * 1000  # mm
reactions = beam.beam_results.results.R                  # list of (V, M) per support
```

`M_max`, `V_max`, `D_max` are mentionable on the page.

### Unit handling
Strip page units before passing to pycba:
```python
L_m = L.to('m').magnitude
q_kNm = q.to('kN/m').magnitude
EI_kNm2 = (E * I).to('kN*m^2').magnitude
beam = BeamAnalysis(L=[L_m], EI=EI_kNm2, R=[1,0,1,0], LM=[[1,2,-q_kNm,0,L_m]])
```

### Charts
```python
import matplotlib.pyplot as plt
import ctconfig

ctconfig.plot_prefix = "beam_results"
beam.plot_results()
plt.show()
```
Then in MDX: `<Mention key="beam_results1" value="beam_results1" variableType="image" />`.

## Examples

### Example 1: Two-span continuous beam
```python
from pycba import BeamAnalysis

beam = BeamAnalysis(
    L=[8, 8],
    EI=25000,
    R=[1,0, 1,0, 1,0],
    LM=[
        [1, 2, -10, 0, 8],
        [2, 2, -10, 0, 8],
    ],
)
beam.analyze()

M_max = float(max(abs(beam.beam_results.results.M)))
M_support = float(beam.beam_results.results.M[len(beam.beam_results.results.M)//2])  # over interior support
V_max = float(max(abs(beam.beam_results.results.V)))
```

### Example 2: Cantilever with tip load
```python
from pycba import BeamAnalysis

beam = BeamAnalysis(
    L=[4],
    EI=15000,
    R=[1,1, 0,0],          # fixed at left, free at right
    LM=[[1, 1, -8, 4, 0]], # 8 kN at x=4 (tip)
)
beam.analyze()

M_fixed = float(beam.beam_results.results.M[0])           # kN·m at root
delta_tip = float(beam.beam_results.results.D[-1]) * 1000  # mm
```

### Example 3: Mixed loads
```python
from pycba import BeamAnalysis

beam = BeamAnalysis(
    L=[10],
    EI=30000,
    R=[1,0, 1,0],
    LM=[
        [1, 2, -8, 0, 10],   # UDL 8 kN/m
        [1, 1, -25, 5, 0],   # 25 kN point at midspan
    ],
)
beam.analyze()
```

## Common Mistakes
- **Wrong number of supports**: `R` must have `len(L) + 1` support pairs. Two spans → three supports → six numbers in `R`.
- **Positive load magnitudes for gravity**: Use `-w` for downward UDL. Positive UDL pushes upward.
- **Confusing point load `a`**: For point load, `a` is distance from the LEFT support of that span (not from the start of the beam).
- **Inconsistent units**: pycba is unit-agnostic. If `L` is in m and `EI` in N·m², deflections will be wrong by a factor of 1000. Stick to kN/m/kN·m².
- **Re-wrapping `ct.quantity`**: Strip units to plain floats before passing to pycba.
- **Indexing the result arrays**: They're 1D arrays sampled along the beam, NOT one entry per support. Use `.Mmax`/`.Mmin` accessors when possible.
- **Free-end roll support**: A roller support is `[1, 0]`, not `[0, 1]`. `[0, 0]` means free (cantilever tip).

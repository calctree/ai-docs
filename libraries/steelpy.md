# steelpy — Steel Section Database & Member Design

## When to Use
`steelpy` provides a database of standard steel sections (AISC W, HSS, channels, angles, plates) with their geometric properties and basic AISC 360 design checks. Use it when:

- The user mentions a catalog section by name ("W12X26", "HSS6X6X1/2")
- You need quick section properties (A, Ix, Sx, Zx, rx, J) without meshing
- You're doing AISC 360 LRFD checks (US codes)

For Australian sections (UB, UC, PFC, RHS, SHS), `steelpy` won't have them — use hardcoded values from a local handbook or create with `sectionproperties`. For arbitrary geometry use `sectionproperties`.

## Installation
Already installed. Import:
```python
from steelpy import aisc
```

## Section Catalog
Sections are accessed by shape group:
- `aisc.W_shapes` — wide flange
- `aisc.HSS_shapes` — hollow structural sections (rect/square)
- `aisc.HSS_R_shapes` — round HSS
- `aisc.C_shapes` — channels
- `aisc.MC_shapes` — miscellaneous channels
- `aisc.L_shapes` — angles
- `aisc.WT_shapes` — tees

Pick a section by attribute access (using underscores in place of `X`):
```python
W12x26 = aisc.W_shapes.W12X26
```

## Section properties
Common attributes (US units: inches, in², in³, in⁴ unless converted):
- `.area` — A
- `.Ix`, `.Iy`
- `.Sx`, `.Sy` — elastic section moduli
- `.Zx`, `.Zy` — plastic section moduli
- `.rx`, `.ry` — radii of gyration
- `.J` — torsion constant
- `.Cw` — warping constant
- `.d`, `.bf`, `.tf`, `.tw` — geometry

```python
shape = aisc.W_shapes.W12X26
A = shape.area      # in²
Ix = shape.Ix       # in⁴
Sx = shape.Sx       # in³
Zx = shape.Zx       # in³
```

## Units
**US customary by default** (inches, kips, ksi). Convert with `ct.quantity` for SI display:
```python
A_SI = ct.quantity(f'{shape.area} in^2').to('m^2')
Ix_SI = ct.quantity(f'{shape.Ix} in^4').to('m^4')
```

## CalcTree Integration

### Output Variables
```python
from steelpy import aisc

shape = aisc.W_shapes.W14X30
A_in2 = float(shape.area)
Ix_in4 = float(shape.Ix)
Zx_in3 = float(shape.Zx)
rx_in = float(shape.rx)

# SI conversions for downstream MathJS
A_m2 = (ct.quantity(f'{A_in2} in^2').to('m^2')).magnitude
Ix_m4 = (ct.quantity(f'{Ix_in4} in^4').to('m^4')).magnitude
Zx_m3 = (ct.quantity(f'{Zx_in3} in^3').to('m^3')).magnitude
```

### Combine with anastruct/PyNite
```python
from steelpy import aisc
from anastruct import SystemElements

shape = aisc.W_shapes.W14X30
E_psi = 29e6                                          # ksi → psi (US)
EI_kip_in2 = 29000 * shape.Ix                          # E in ksi × Ix in in⁴ = kip·in²
# For metric anastruct, convert:
EI_kNm2 = (ct.quantity(f'{EI_kip_in2} kip*in^2').to('kN*m^2')).magnitude

ss = SystemElements(EI=EI_kNm2)
ss.add_element([[0, 0], [10, 0]])
ss.add_support_hinged(1)
ss.add_support_roll(2, direction='y')
ss.q_load(q=-15, element_id=1)
ss.solve()
```

## Examples

### Example 1: Look up section properties
```python
from steelpy import aisc

shape = aisc.W_shapes.W12X26
A   = float(shape.area)   # in²
Ix  = float(shape.Ix)     # in⁴
Zx  = float(shape.Zx)     # in³
rx  = float(shape.rx)     # in
d   = float(shape.d)
bf  = float(shape.bf)
tf  = float(shape.tf)
tw  = float(shape.tw)
```

### Example 2: Iterate to find lightest section meeting Mu
```python
from steelpy import aisc

Mu_kip_in = 200 * 12          # 200 kip·ft → kip·in
Fy = 50                       # ksi
phi = 0.9
required_Zx = Mu_kip_in / (phi * Fy)   # in³

candidates = []
for name in dir(aisc.W_shapes):
    if not name.startswith('W'):
        continue
    shape = getattr(aisc.W_shapes, name)
    if shape.Zx >= required_Zx:
        candidates.append((name, float(shape.weight), float(shape.Zx)))

candidates.sort(key=lambda c: c[1])   # by weight
lightest_name, lightest_weight, lightest_Zx = candidates[0]
```

### Example 3: Compare HSS options for axial compression
```python
from steelpy import aisc

Pu = 100   # kips
Fy = 46    # ksi (HSS A500 Gr B)
KL = 12 * 12   # 12 ft → in

results = []
for name in ['HSS4X4X1_4', 'HSS5X5X1_4', 'HSS6X6X1_4']:
    s = getattr(aisc.HSS_shapes, name)
    rmin = min(float(s.rx), float(s.ry))
    slenderness = KL / rmin
    # AISC 360 simplified Pn — assume elastic for demonstration
    Fcr = 0.658**( (Fy * (slenderness/3.1416)**2 / 29000) ) * Fy
    phi_Pn = 0.9 * Fcr * float(s.area)
    results.append((name, slenderness, phi_Pn))
```

## Common Mistakes
- **Wrong attribute case**: section names use uppercase X (`W12X26`), not lowercase. Use `aisc.W_shapes.W12X26` not `W12x26`.
- **US vs SI units**: All steelpy values are US customary (in, in², in³, in⁴, ksi). If passing into a metric solver (anastruct, PyNite SI), convert via `ct.quantity` first.
- **Naming with fractions**: HSS sections use underscores for fractions (`HSS6X6X1_4` = HSS6×6×1/4). Look up the catalog if unsure.
- **Assuming AS/NZ sections**: steelpy does NOT include UB/UC/PFC/RHS/SHS metric sections. Use `sectionproperties` or hardcoded values for those.
- **Treating section properties as `ct.quantity` automatically**: They're plain floats. Wrap explicitly when crossing into the unit-aware part of the page.

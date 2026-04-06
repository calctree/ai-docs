# structuralcodes — Eurocode & fib MC2010 Design Functions

## When to Use
`structuralcodes` is a library of design-code functions for concrete (Eurocode 2, fib Model Code 2010) and structural materials. Use it when:

- The user wants formal Eurocode 2 design checks (concrete strengths, creep, shrinkage, anchorage, crack widths)
- You need fib Model Code 2010 material models
- The work needs traceable code references — every function maps to a clause

For Australian AS3600, this library does NOT have direct support — write `handcalcs` blocks with manual clause references. For US ACI 318, use the `concreteproperties` library or hand calcs.

## Installation
Already installed:
```python
import structuralcodes
from structuralcodes.codes import ec2_2004, mc2010
from structuralcodes.materials.concrete import ConcreteMC2010
from structuralcodes.materials.reinforcement import ReinforcementMC2010
```

## Units
**Unit-agnostic** but designed for **N, mm, MPa**. All Eurocode formulas in the library expect this. Convert page `ct.quantity` values explicitly:
```python
fck_MPa = f_ck.to('MPa').magnitude
```

## Key Modules

### `structuralcodes.codes.ec2_2004` — Eurocode 2 (2004)
- `fcm(fck)` — mean cylinder strength
- `fctm(fck)` — mean tensile strength
- `fctk_5(fck)` — 5% characteristic tensile
- `Ecm(fck)` — secant modulus
- `phi(fck, h0, RH, t0, ...)` — creep coefficient
- `eps_cs(fck, h0, RH, t)` — total shrinkage strain
- `epsilon_c1(fck)`, `epsilon_cu1(fck)` — strain limits

### `structuralcodes.codes.mc2010` — fib Model Code 2010
Same shape, more functions, generally more conservative.

### Materials
```python
concrete = ConcreteMC2010(fck=40)        # MPa
steel = ReinforcementMC2010(fyk=500, Es=200000, ftk=540, epsuk=0.05)
```

These objects expose computed properties (fcd, Ecm, εc1, εcu1, etc.) that combine cleanly with `concreteproperties`.

## CalcTree Integration

### Output Variables
```python
from structuralcodes.codes import ec2_2004 as ec2

f_ck = 40   # MPa
f_cm = float(ec2.fcm(f_ck))           # MPa
f_ctm = float(ec2.fctm(f_ck))         # MPa
E_cm = float(ec2.Ecm(f_ck))           # MPa

# Creep coefficient
phi_t = float(ec2.phi(fck=40, h0=200, RH=70, t0=28, t=18250))   # 50 years
# Shrinkage
eps_cs = float(ec2.eps_cs(fck=40, h0=200, RH=70, t=18250, ts=7))
```

### Combine with concreteproperties
```python
from structuralcodes.materials.concrete import ConcreteMC2010
from structuralcodes.materials.reinforcement import ReinforcementMC2010

mc_concrete = ConcreteMC2010(fck=40)
mc_steel = ReinforcementMC2010(fyk=500, Es=200000, ftk=540, epsuk=0.05)

# These objects have fcd, Ecm etc. properties — pull them as needed
fcd = float(mc_concrete.fcd)
Ecm = float(mc_concrete.Ecm)
```

## Examples

### Example 1: EC2 material properties for a class
```python
from structuralcodes.codes import ec2_2004 as ec2

f_ck = 35
f_cm = float(ec2.fcm(f_ck))
f_ctm = float(ec2.fctm(f_ck))
f_ctk_5 = float(ec2.fctk_5(f_ck))
E_cm = float(ec2.Ecm(f_ck))
eps_c1 = float(ec2.epsilon_c1(f_ck))
eps_cu1 = float(ec2.epsilon_cu1(f_ck))
```

### Example 2: 50-year creep + shrinkage for slab
```python
from structuralcodes.codes import ec2_2004 as ec2

t = 50 * 365              # days
t0 = 28
RH = 70                   # %
h0 = 200                  # mm — notional size 2Ac/u
fck = 40

phi_50y = float(ec2.phi(fck=fck, h0=h0, RH=RH, t0=t0, t=t))
eps_cs_50y = float(ec2.eps_cs(fck=fck, h0=h0, RH=RH, t=t, ts=7))
```

### Example 3: Long-term effective modulus
```python
from structuralcodes.codes import ec2_2004 as ec2

fck = 40
Ecm = ec2.Ecm(fck)
phi_t = ec2.phi(fck=fck, h0=200, RH=70, t0=28, t=18250)
E_eff = Ecm / (1 + phi_t)        # MPa
E_eff_GPa = float(E_eff) / 1000
```

## Common Mistakes
- **Treating return values as quantities**: All functions return plain floats in N/mm/MPa. Wrap with `ct.quantity` only if downstream MathJS needs units.
- **Wrong `h0`**: Notional size = 2 × area / perimeter exposed to drying, in mm. A common error is using full perimeter when only top is exposed.
- **`t` and `t0` units**: All times are in **days**, not seconds or years. Convert before passing.
- **`fck` already factored**: `fck` is the characteristic strength (e.g. 40 for C40). Don't divide by `gamma_c` first — the library does that internally where appropriate.
- **Mixing EC2 with AS3600 expectations**: φ factors, partial factors, and load combinations are EC2-specific. Don't blindly apply AS3600 ψ factors to EC2 outputs.
- **Assuming AS3600 support**: There is no `as3600` submodule. For AS3600 design checks, write the formulas explicitly in `handcalcs`.

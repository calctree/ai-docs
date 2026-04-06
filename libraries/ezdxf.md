# ezdxf — DXF File Read & Write

## When to Use
`ezdxf` reads and writes AutoCAD DXF files. Use it when:

- The user uploads a DXF and wants to extract geometry (lines, polylines, circles, blocks, layers)
- You need to generate a DXF as output (e.g. fabrication detail, layout drawing)
- The user mentions "DXF", "AutoCAD", "drawing", "extract from drawing"

For converting DXF geometry into a `sectionproperties` cross-section, use `cad-to-shapely` (see that library's bundle).

## Installation
Already installed (with drawing extras):
```python
import ezdxf
from ezdxf import recover, units
```

## Reading DXFs from a Workspace File

Use `ct.open()` to access uploaded files. ezdxf wants either a file path or a text/binary stream:
```python
import io
import ezdxf

content = ct.open('site.dxf', mode='r').read()
doc, auditor = ezdxf.recover.read(io.StringIO(content))   # forgiving read
msp = doc.modelspace()
```

Use `ezdxf.recover.read` rather than `ezdxf.read` — it handles malformed files gracefully and returns an `auditor` listing problems.

## Iterating Entities
```python
for entity in msp:
    print(entity.dxftype(), entity.dxf.layer)
```

Filter by type via querying:
```python
lines = msp.query('LINE')
polylines = msp.query('LWPOLYLINE')
circles = msp.query('CIRCLE')
texts = msp.query('TEXT MTEXT')
```

Or by layer:
```python
on_walls = msp.query('*[layer=="WALLS"]')
```

## Common Entity Properties

### LINE
```python
for line in msp.query('LINE'):
    p1 = line.dxf.start    # (x, y, z)
    p2 = line.dxf.end
    layer = line.dxf.layer
```

### LWPOLYLINE (lightweight polyline)
```python
for pl in msp.query('LWPOLYLINE'):
    pts = [(v[0], v[1]) for v in pl.get_points()]    # list of (x, y)
    closed = pl.is_closed
```

### CIRCLE / ARC
```python
for c in msp.query('CIRCLE'):
    cx, cy, _ = c.dxf.center
    r = c.dxf.radius
```

### TEXT / MTEXT
```python
for t in msp.query('TEXT'):
    print(t.dxf.text, t.dxf.insert)
```

## Writing a New DXF
```python
import ezdxf

doc = ezdxf.new(setup=True)        # setup=True adds standard linetypes/styles
msp = doc.modelspace()

msp.add_line((0, 0), (10, 0), dxfattribs={'layer': 'OUTLINE'})
msp.add_lwpolyline([(0, 0), (10, 0), (10, 5), (0, 5), (0, 0)],
                    dxfattribs={'layer': 'WALL'})
msp.add_circle((5, 2.5), 1.0, dxfattribs={'layer': 'FIXTURE'})
msp.add_text('NORTH', dxfattribs={'layer': 'NOTES'}).set_placement((11, 5))

doc.saveas('output.dxf')
```

To make `output.dxf` available as a workspace file, use `ct.keep_file('output.dxf')` or save into the working directory and rely on the runtime's file capture.

## CalcTree Integration

### Output Variables
ezdxf returns geometry as plain Python tuples and lists, which serialise fine. Common patterns:
```python
import io
import ezdxf
from ezdxf import recover

content = ct.open('plan.dxf', mode='r').read()
doc, auditor = recover.read(io.StringIO(content))
msp = doc.modelspace()

n_lines = int(len(msp.query('LINE')))
n_circles = int(len(msp.query('CIRCLE')))
layers = sorted({e.dxf.layer for e in msp})

# Sum line lengths on a specific layer
import math
total_wall_length = 0.0
for line in msp.query('LINE[layer=="WALLS"]'):
    p1 = line.dxf.start; p2 = line.dxf.end
    total_wall_length += math.hypot(p2[0]-p1[0], p2[1]-p1[1])
total_wall_length = float(total_wall_length)
```

### Charts (matplotlib preview of DXF geometry)
```python
import matplotlib.pyplot as plt
import ctconfig

fig, ax = plt.subplots(figsize=(8, 8))
for line in msp.query('LINE'):
    x = [line.dxf.start[0], line.dxf.end[0]]
    y = [line.dxf.start[1], line.dxf.end[1]]
    ax.plot(x, y, 'k-')
for pl in msp.query('LWPOLYLINE'):
    pts = [(v[0], v[1]) for v in pl.get_points()]
    if pl.is_closed: pts.append(pts[0])
    ax.plot([p[0] for p in pts], [p[1] for p in pts], 'b-')
for c in msp.query('CIRCLE'):
    circle = plt.Circle((c.dxf.center[0], c.dxf.center[1]), c.dxf.radius, fill=False)
    ax.add_patch(circle)

ax.set_aspect('equal')
ax.grid(True)
ax.set_title('DXF Preview')

ctconfig.plot_prefix = "dxf_preview"
plt.show()
```
Then in MDX: `<Mention key="dxf_preview1" value="dxf_preview1" variableType="image" />`.

## Examples

### Example 1: Layer summary of an uploaded DXF
```python
import io, ezdxf
from ezdxf import recover

content = ct.open('site.dxf', mode='r').read()
doc, auditor = recover.read(io.StringIO(content))
msp = doc.modelspace()

from collections import Counter
counts = Counter(e.dxf.layer for e in msp)
n_layers = int(len(counts))
busiest_layer = max(counts, key=counts.get)
busiest_count = int(counts[busiest_layer])
```

### Example 2: Extract closed polyline coordinates as a section outline
```python
import io, ezdxf
from ezdxf import recover

content = ct.open('section.dxf', mode='r').read()
doc, _ = recover.read(io.StringIO(content))
msp = doc.modelspace()

closed_pls = [pl for pl in msp.query('LWPOLYLINE') if pl.is_closed]
outline_pts = [(v[0], v[1]) for v in closed_pls[0].get_points()] if closed_pls else []

n_vertices = int(len(outline_pts))
```

### Example 3: Generate a simple frame layout DXF
```python
import ezdxf

doc = ezdxf.new(setup=True)
msp = doc.modelspace()

bays = 4
height = 4
span = 6
for i in range(bays + 1):
    x = i * span
    msp.add_line((x, 0), (x, height), dxfattribs={'layer': 'COL'})
for i in range(bays):
    msp.add_line((i*span, height), ((i+1)*span, height), dxfattribs={'layer': 'BM'})

doc.saveas('frame.dxf')
ct.keep_file('frame.dxf')
```

## Common Mistakes
- **Using `ezdxf.read` for messy files**: Many real-world DXFs have small inconsistencies. Use `ezdxf.recover.read` instead — it returns an auditor with non-fatal issues.
- **Forgetting `io.StringIO`/`BytesIO`**: `ct.open()` returns a file-like object whose `.read()` gives a string. Wrap in `StringIO` (text mode) or `BytesIO` (binary mode) before passing to ezdxf.
- **Treating `dxf.start`/`dxf.center` as 2D**: They're 3D tuples `(x, y, z)`. Slice with `[0]`/`[1]` for x/y in plan.
- **Not closing polylines**: For `add_lwpolyline`, repeat the first point at the end OR set `close=True` on the entity attributes if you want a closed shape.
- **Unit assumptions**: DXFs don't carry explicit units in entities — they reference the document `INSUNITS` header. Don't assume mm vs m. Check `doc.units` and convert as needed.
- **Saving outside the workspace**: Saving to a path the runtime doesn't capture means the file won't be available afterwards. Save in the cwd and rely on runtime capture, or call `ct.keep_file()` explicitly.

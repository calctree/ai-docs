# pandas + plotly / matplotlib — Data Analysis & Charting

## When to Use
Use `pandas` for tabular data manipulation and `matplotlib` (preferred for CalcTree chart capture) or `plotly` for visualisation. Choose this combo when:

- The user uploaded a CSV/Excel file and wants summaries, filters, joins, plots
- A calculation involves a table of values (load cases, member sizes, soil layers)
- The user wants a chart of any kind (line, bar, scatter, histogram, hatch profile)

**For chart output on a CalcTree page, prefer matplotlib** — it integrates with `ctconfig.plot_prefix` and `plt.show()`. Plotly works for interactive output but the page-mention pipeline is matplotlib-first.

## Installation
Already installed: `pandas`, `numpy`, `matplotlib`, `plotly`. Just import them.

## Reading Files

CalcTree exposes uploaded workspace files via `ct.open()`:
```python
import pandas as pd
import io

# CSV
csv_text = ct.open('loads.csv', mode='r').read()
df = pd.read_csv(io.StringIO(csv_text))

# Excel
xlsx_bytes = ct.open('design_data.xlsx', mode='rb').read()
df = pd.read_excel(io.BytesIO(xlsx_bytes), sheet_name='Loads')
```

## Key pandas patterns

### DataFrame creation from inline data
```python
import pandas as pd

df = pd.DataFrame({
    'load_case': ['DL', 'LL', 'WL', 'EQ'],
    'factor':    [1.2, 1.5, 1.0, 1.0],
    'magnitude': [50, 30, 25, 40],   # kN
})
df['factored'] = df['factor'] * df['magnitude']
```

### Selection / filtering
```python
df_critical = df[df['utilisation'] > 0.95]
worst = df.loc[df['utilisation'].idxmax()]
```

### Grouping / aggregation
```python
summary = df.groupby('load_case').agg(
    total=('factored', 'sum'),
    max=('factored', 'max'),
)
```

### Output a single scalar to page scope
```python
total_load = float(df['factored'].sum())     # cast away numpy → plain float
worst_UR   = float(df['utilisation'].max())
```

`total_load` and `worst_UR` are now mentionable on the page.

### Output the whole table to page scope
Convert to a list-of-dicts or markdown so it can be shown via the editor:
```python
loads_table = df.to_dict('records')
```

## matplotlib charting (CalcTree pipeline)

Always:
1. Set `ctconfig.plot_prefix = "..."` BEFORE `plt.show()`
2. Call `plt.show()` to flush the figure to CalcTree's image capture
3. Reference the image in MDX as `<Mention key="prefix1" value="prefix1" variableType="image" />`

```python
import matplotlib.pyplot as plt
import ctconfig

fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(df['x'], df['y'], label='Result')
ax.set_xlabel('Position (m)')
ax.set_ylabel('Moment (kN·m)')
ax.set_title('Bending Moment Diagram')
ax.legend()
ax.grid(True)

ctconfig.plot_prefix = "bmd"
plt.show()
```
After this block, you MUST call `generateCalculation` with MDX including `<Mention key="bmd1" .../>` or the chart won't render on the page. For multiple figures, suffix increments: `bmd1`, `bmd2`, ...

## plotly (use sparingly in CalcTree)
Plotly produces HTML/JS, which doesn't flow through `ctconfig.plot_prefix`. Use it only when the user explicitly wants interactivity AND you have downstream handling. Default to matplotlib.

```python
import plotly.express as px
fig = px.line(df, x='x', y='y', title='Bending Moment')
# fig.show() — does NOT post to CalcTree's image system
```

## Examples

### Example 1: Load case summary from CSV
```python
import pandas as pd
import io

csv_text = ct.open('load_cases.csv', mode='r').read()
df = pd.read_csv(io.StringIO(csv_text))

df['factored'] = df['load_factor'] * df['magnitude_kN']
total_factored = float(df['factored'].sum())
governing_case = df.loc[df['factored'].idxmax(), 'name']
```

### Example 2: Utilisation table with chart
```python
import pandas as pd
import matplotlib.pyplot as plt
import ctconfig

members = pd.DataFrame({
    'member': ['B1', 'B2', 'B3', 'B4', 'B5'],
    'M_star': [180, 220, 95, 310, 145],
    'phi_M_n': [250, 250, 200, 350, 200],
})
members['UR'] = members['M_star'] / members['phi_M_n']

worst_UR = float(members['UR'].max())
worst_member = members.loc[members['UR'].idxmax(), 'member']

fig, ax = plt.subplots(figsize=(8, 4))
colors = ['#d62728' if u > 1.0 else '#2ca02c' for u in members['UR']]
ax.bar(members['member'], members['UR'], color=colors)
ax.axhline(1.0, color='k', linestyle='--', label='UR = 1.0')
ax.set_ylabel('Utilisation Ratio')
ax.set_title('Member Utilisation Summary')
ax.legend()

ctconfig.plot_prefix = "util_chart"
plt.show()
```
Then in MDX: `<Mention key="util_chart1" value="util_chart1" variableType="image" />`.

### Example 3: Combine with anastruct results into a results table
```python
from anastruct import SystemElements
import pandas as pd

ss = SystemElements(EI=30000)
ss.add_element([[0, 0], [10, 0]])
ss.add_support_hinged(1)
ss.add_support_roll(2, direction='y')
ss.q_load(q=-15, element_id=1)
ss.solve()

results = pd.DataFrame({
    'x_m':       [i * 10 / 50 for i in range(51)],
    'M_kNm':     ss.get_element_result_range('moment')[0],
    'V_kN':      ss.get_element_result_range('shear')[0],
})

M_max = float(results['M_kNm'].abs().max())
V_max = float(results['V_kN'].abs().max())
```

## Common Mistakes

- **`numpy.float64` vs `float`**: pandas/numpy results are numpy scalars. CalcTree's MathJS bridge wants plain Python floats. Cast with `float(...)` or `int(...)` before assigning to scope variables.
- **Forgetting `ctconfig.plot_prefix`**: A `plt.show()` without `plot_prefix` produces an unnamed figure that won't be mentionable.
- **Forgetting the `<Mention>` tag**: After producing a chart, you MUST follow up with a `generateCalculation` call that includes the matching `<Mention key="prefix1" .../>` — otherwise the image is captured but never displayed.
- **Using `plotly.show()` and expecting page render**: Plotly doesn't go through CalcTree's matplotlib capture. Use matplotlib for charts on the page.
- **Reading files with `open()`**: Use `ct.open()` — workspace files aren't on the local filesystem.
- **Re-wrapping `ct.quantity` page variables**: If a page variable has units, it's already a quantity. To put it into a DataFrame, extract first: `df['L'] = [L.to('m').magnitude]`.
- **`df.head()` for output**: `head()` is for notebooks. To expose a table to the page, use `df.to_dict('records')` or build the markdown explicitly via `generateCalculation`.
- **Using `inplace=True` then assigning**: `df.dropna(inplace=True)` returns `None`. Don't do `df = df.dropna(inplace=True)`.

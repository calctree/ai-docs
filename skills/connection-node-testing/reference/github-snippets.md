# Verified GitHub Code Snippets

Real working ETABS Python code from open-source repos. Each snippet is tagged with
the test scenario(s) it validates. Use these as reference when debugging connection
scripts or extending the test suite.

## Source Repos

| Repo | Stars | Key Value |
|------|-------|-----------|
| [ebrahimraeyat/etabs_api](https://github.com/ebrahimraeyat/etabs_api) | 80 | Full OOP wrapper — database tables, load combos, results, design |
| [danielogg92/Etabs-API-Python](https://github.com/danielogg92/Etabs-API-Python) | 73 | Clean standalone functions — frames, materials, spandrels |
| [retug/ETABs](https://github.com/retug/ETABs) | 22 | Pier forces + brace checks to Excel with openpyxl |
| [mihdicaballero/ETABS-Ninja](https://github.com/mihdicaballero/ETABS-Ninja) | 16 | Drift analysis + matplotlib + DataFrame pipelines |
| [keshishianv/ETABS-Python-Codes](https://github.com/keshishianv/ETABS-Python-Codes) | 1 | Direct ETABS-to-Excel with openpyxl (frame members, forces) |
| [AesirX899/etabs-python-api](https://github.com/AesirX899/etabs-python-api) | 3 | Compact iterative drift + section resize loop |
| [EhsanAlizadeh1/ETABS-API-Example](https://github.com/EhsanAlizadeh1/ETABS-API-Example) | 5 | Full model build from scratch (load patterns, groups, mass source) |
| [nhniegas/Etabs_Designer](https://github.com/nhniegas/Etabs_Designer) | 1 | Beam design automation with concrete design code |
| [seybaskan/ETABS-TBDY2018-Automation](https://github.com/seybaskan/ETABS-TBDY2018-Automation) | 1 | Turkish code drift checks with pass/fail |
| [geoeq/geoeq](https://github.com/geoeq/geoeq) | - | 170+ geotechnical functions (SPT, piles, bearing, settlement) |

---

## S1. ETABS Connection Boilerplate (all scenarios)

From `ebrahimraeyat/etabs_api` and `danielogg92/Etabs-API-Python`:

```python
# Method 1: ETABS 2019+ (recommended)
import comtypes.client
helper = comtypes.client.CreateObject('ETABSv1.Helper')
helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
EtabsObject = helper.GetObject("CSI.ETABS.API.ETABSObject")
SapModel = EtabsObject.SapModel

# Method 2: Legacy (pre-2019)
EtabsObject = comtypes.client.GetActiveObject("CSI.ETABS.API.ETABSObject")
SapModel = EtabsObject.SapModel
```

Note: CalcTree connection scripts get `sap` (SapModel) and `etabs` (Application)
injected as globals. You do NOT need this boilerplate — it's here for reference
on what CalcTree does behind the scenes.

---

## S2. Database Table to pandas DataFrame (A1-A6, C1-C2, D1-D4, E1-E2, G2)

From `ebrahimraeyat/etabs_api/database.py`:

```python
import pandas as pd

def read_etabs_table(SapModel, table_key, cols=None):
    """Read any ETABS database table into a pandas DataFrame."""
    ret = SapModel.DatabaseTables.GetTableForDisplayArray(
        table_key, [], table_key, 0, [], 0, [])
    fields = ret[2]       # column headers tuple
    table_data = ret[4]   # flat data tuple
    n = len(fields)
    rows = [list(table_data[i:i+n]) for i in range(0, len(table_data), n)]
    df = pd.DataFrame(rows, columns=list(fields))
    if cols:
        df = df[cols]
    return df

# Usage:
df_drifts = read_etabs_table(SapModel, "Story Drifts")
df_reactions = read_etabs_table(SapModel, "Joint Reactions",
    cols=["UniqueName", "OutputCase", "F1", "F2", "F3", "M1", "M2", "M3"])
df_combos = read_etabs_table(SapModel, "Load Combination Definitions",
    cols=["Name", "LoadName", "Type", "SF"])
```

Note: CalcTree's `parse_table("Table Name")` is equivalent — it wraps
`GetTableForDisplayArray()` and returns a list of dicts instead of a DataFrame.

---

## S3. Write DataFrame Back to ETABS (B2, B4)

From `ebrahimraeyat/etabs_api/database.py`:

```python
def write_etabs_table(SapModel, table_key, df):
    """Write a DataFrame back to an ETABS database table."""
    df = df.fillna(value='').astype(str)
    fields = list(df.columns)
    data = []
    for _, row in df.iterrows():
        data.extend(row.tolist())
    SapModel.DatabaseTables.SetTableForEditingArray(
        table_key, 0, fields, 0, data)
    SapModel.SetModelIsLocked(False)
    SapModel.DatabaseTables.ApplyEditedTables(True)
```

---

## S4. Story Drift Check with Pass/Fail (A1, D4)

From `mihdicaballero/ETABS-Ninja/get_functions.py` and `seybaskan/ETABS-TBDY2018-Automation`:

```python
def get_story_drifts(SapModel, load_cases, max_drift=0.02):
    """Extract story drifts and check against code limit."""
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    for lc in load_cases:
        SapModel.Results.Setup.SetCaseSelectedForOutput(lc)

    table_key = "Story Drifts"
    fields = SapModel.DatabaseTables.GetAllFieldsInTable(table_key)[2]
    raw = SapModel.DatabaseTables.GetTableForDisplayArray(
        table_key, fields, "All")[4]

    n = len(fields)
    rows = [raw[i:i+n] for i in range(0, len(raw), n)]
    df = pd.DataFrame(rows, columns=list(fields))
    df["Drift"] = df["Drift"].astype(float)
    df["Status"] = df["Drift"].apply(lambda x: "PASS" if x <= max_drift else "FAIL")

    summary = df.groupby(["Story", "Direction"])["Drift"].max().reset_index()
    return df, summary
```

Compact version from `AesirX899/etabs-python-api`:

```python
def read_drifts(sap, cases=["Fx", "Fy", "MzFx", "MzFy"]):
    """Returns dict of (story, case, direction) -> drift ratio."""
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    for c in cases:
        sap.Results.Setup.SetCaseSelectedForOutput(c)
    r = sap.Results.StoryDrifts()
    out = {}
    for i in range(r[0]):
        out[(r[1][i], r[2][i], r[5][i])] = r[6][i]
    return out
```

---

## S5. Modal Periods + Mass Participation (A5)

From `ebrahimraeyat/etabs_api/results.py`:

```python
def get_xy_period(SapModel):
    """Get fundamental periods and dominant mode indices for X and Y."""
    modal_case = "Modal"
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput(modal_case)

    result = SapModel.Results.ModalParticipatingMassRatios()
    periods = result[4]
    ux = result[5]
    uy = result[6]

    x_index = list(ux).index(max(ux))
    y_index = list(uy).index(max(uy))
    Tx = periods[x_index]
    Ty = periods[y_index]
    return Tx, Ty, x_index + 1, y_index + 1
```

---

## S6. Base Reactions (A2, E1)

From `ebrahimraeyat/etabs_api/results.py`:

```python
def get_base_reactions(SapModel, load_cases):
    """Get base shear for specified load cases."""
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    for lc in load_cases:
        SapModel.Results.Setup.SetCaseSelectedForOutput(lc)
    result = SapModel.Results.BaseReact()
    cases = result[1]
    vx = result[4]
    vy = result[5]
    vz = result[6]
    return {cases[i]: {"Vx": vx[i], "Vy": vy[i], "Vz": vz[i]}
            for i in range(len(cases))}
```

---

## S7. Get All Frames with Geometry (A3, A6, G2)

From `danielogg92/Etabs-API-Python/Etabs_Get_Functions.py`:

```python
def get_all_frames(SapModel):
    """Returns list of frame dicts with name, prop, story, coords."""
    ret = SapModel.FrameObj.GetAllFrames()
    frames = []
    for i in range(ret[0]):
        frames.append({
            "name": ret[1][i],
            "prop": ret[2][i],
            "story": ret[3][i],
            "point1": ret[4][i],
            "point2": ret[5][i],
            "x1": ret[6][i], "y1": ret[7][i], "z1": ret[8][i],
            "x2": ret[9][i], "y2": ret[10][i], "z2": ret[11][i],
            "angle": ret[12][i],
        })
    return frames
```

---

## S8. Get Materials with Concrete/Steel Properties (G1, G2)

From `danielogg92/Etabs-API-Python/Etabs_Get_Functions.py`:

```python
def get_all_materials(SapModel):
    SapModel.SetPresentUnits(9)  # N, mm
    mat_types = {1: 'Steel', 2: 'Concrete', 3: 'NoDesign', 6: 'Rebar'}
    names = SapModel.PropMaterial.GetNameList()
    materials = {}
    for i in range(names[0]):
        name = names[1][i]
        mtype = mat_types.get(SapModel.PropMaterial.GetMaterial(name)[0], 'Other')
        if mtype == 'Concrete':
            fc = SapModel.PropMaterial.GetOConcrete_1(name)[0]
            materials[name] = {"type": mtype, "fc": fc}
        elif mtype == 'Steel':
            fy = SapModel.PropMaterial.GetOSteel_1(name)[0]
            fu = SapModel.PropMaterial.GetOSteel_1(name)[1]
            materials[name] = {"type": mtype, "fy": fy, "fu": fu}
    return materials
```

---

## S9. Add Australian Concrete Materials (G1 localised)

From `danielogg92/Etabs-API-Python/Etabs_Set_Functions.py`:

```python
def add_australia_conc_materials(SapModel):
    grades = [25, 32, 40, 50, 65, 80, 100]
    E_map = {25: 26700, 32: 30100, 40: 32800, 50: 34800,
             65: 37400, 80: 39600, 100: 42200}
    for grade in grades:
        name = f"CONC-{grade}"
        SapModel.PropMaterial.AddMaterial(name, 2, "User", "AS3600",
                                          f"{grade}MPa", UserName=name)
        SapModel.PropMaterial.SetOConcrete(name, grade, False, 0.0, 2, 4, 0.003, 0.0035)
        SapModel.PropMaterial.SetMPIsotropic(name, E_map[grade], 0.2, 10e-6)
```

---

## S10. Load Combinations via API (B1)

From `ebrahimraeyat/etabs_api/load_combinations.py`:

```python
def add_load_combination(SapModel, combo_name, case_names, scale_factors, combo_type=0):
    """Add a load combination with multiple cases and factors."""
    SapModel.RespCombo.Add(combo_name, combo_type)
    for case, sf in zip(case_names, scale_factors):
        SapModel.RespCombo.SetCaseList(combo_name, 0, case, sf)

def get_load_combinations_as_df(SapModel):
    """Read all combo definitions into a DataFrame."""
    table_key = "Load Combination Definitions"
    ret = SapModel.DatabaseTables.GetTableForDisplayArray(
        table_key, [], table_key, 0, [], 0, [])
    fields = ret[2]
    data = ret[4]
    n = len(fields)
    rows = [list(data[i:i+n]) for i in range(0, len(data), n)]
    return pd.DataFrame(rows, columns=list(fields))
```

---

## S11. Load Patterns with Seismic Type Detection (B3)

From `ebrahimraeyat/etabs_api/load_patterns.py`:

```python
PATTERN_TYPE_MAP = {
    1: 'Dead', 2: 'Super Dead', 3: 'Live', 5: 'Seismic',
    6: 'Wind', 37: 'Seismic (Drift)', 61: 'QuakeDrift',
}

def get_seismic_load_patterns(SapModel):
    """Read auto seismic patterns and classify X vs Y direction."""
    table = "Load Pattern Definitions - Auto Seismic - User Coefficient"
    ret = SapModel.DatabaseTables.GetTableForDisplayArray(
        table, [], table, 0, [], 0, [])
    fields = list(ret[2])
    data = ret[4]
    n = len(fields)
    rows = [list(data[i:i+n]) for i in range(0, len(data), n)]
    df = pd.DataFrame(rows, columns=fields)
    return df
```

---

## S12. Pier Forces to Excel (A6, D1)

From `retug/ETABs/pierCheckv002.py`:

```python
def extract_pier_forces_to_excel(SapModel, load_cases, output_file):
    """Extract pier forces per load case and write to Excel."""
    for load in load_cases:
        SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay([load])

        table_key = 'Pier Forces'
        raw = SapModel.DatabaseTables.GetTableForDisplayArray(
            table_key, [], 'All', 1, [], 1, [])

        fields = list(raw[2])
        data = raw[4]
        n = len(fields)
        rows = [list(data[i:i+n]) for i in range(0, len(data), n)]
        df = pd.DataFrame(rows, columns=fields)
        df[['P','V2','V3','T','M2','M3']] = df[['P','V2','V3','T','M2','M3']].astype(float)

        with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
            df.to_excel(writer, sheet_name=f'Pier Forces {load}', index=False)
```

---

## S13. Frame Forces to Excel (D1, D2)

From `keshishianv/ETABS-Python-Codes/getFrameForces.py`:

```python
def get_frame_forces(SapModel, unit_index=6):
    """Get frame forces for ALL load cases and combos."""
    SapModel.SetPresentUnits(unit_index)  # kN, m
    cases = list(SapModel.LoadCases.GetNameList()[1])[:-1]
    combos = list(SapModel.RespCombo.GetNameList()[1])
    all_results = {}

    for cas in cases:
        SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        SapModel.Results.Setup.SetCaseSelectedForOutput(cas)
        r = SapModel.Results.FrameForce("ALL", 2)
        all_results[cas] = {
            "count": r[0],
            "frames": r[1],
            "stations": r[4],
            "P": r[8], "V2": r[9], "V3": r[10],
            "T": r[11], "M2": r[12], "M3": r[13],
        }

    for com in combos:
        SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        SapModel.Results.Setup.SetComboSelectedForOutput(com)
        r = SapModel.Results.FrameForce("ALL", 2)
        all_results[com] = {
            "count": r[0],
            "frames": r[1],
            "stations": r[4],
            "P": r[8], "V2": r[9], "V3": r[10],
            "T": r[11], "M2": r[12], "M3": r[13],
        }
    return all_results
```

---

## S14. Frame Envelope across Load Combos (C1)

From `lukaszlaba/etabsplus/etabs_processing.py`:

```python
def get_frame_envelope(SapModel, frame_list, combo_list):
    """Get max/min P, V2, V3, T, M2, M3 across all combos for each frame."""
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    for lc in combo_list:
        SapModel.Results.Setup.SetComboSelectedForOutput(lc)

    envelopes = {}
    for frame in frame_list:
        section = SapModel.FrameObj.GetSection(frame)[0]
        r = SapModel.Results.FrameForce(frame, 0)
        P_vals = r[8]
        V2_vals = r[9]
        M3_vals = r[13]

        envelopes[frame] = {
            "section": section,
            "P_max": max(P_vals), "P_min": min(P_vals),
            "V2_max": max(V2_vals), "V2_min": min(V2_vals),
            "M3_max": max(M3_vals), "M3_min": min(M3_vals),
        }
    return envelopes
```

---

## S15. Iterative Section Resize Loop (C1)

From `AesirX899/etabs-python-api`:

```python
def set_section(sap, name, depth, width, material="4000Psi"):
    """Redefine a rectangular section — all frames using it update."""
    if sap.GetModelIsLocked():
        sap.SetModelIsLocked(False)
    return sap.PropFrame.SetRectangle(name, material, depth, width)

def optimize_loop(sap, drift_limit=0.007):
    """Read drifts, upsize sections if needed, re-run."""
    drifts = read_drifts(sap)
    max_drift = max(drifts.values())
    iteration = 0
    while max_drift > drift_limit and iteration < 10:
        current_depth = 0.40 + iteration * 0.05
        set_section(sap, "COL", current_depth, current_depth)
        sap.Analyze.RunAnalysis()
        drifts = read_drifts(sap)
        max_drift = max(drifts.values())
        iteration += 1
    return iteration, max_drift
```

---

## S16. Full Model from Scratch (G1)

From `EhsanAlizadeh1/ETABS-API-Example/API_1.py`:

```python
# Load patterns
SapModel.LoadPatterns.Add("SuperDead", 2)
SapModel.LoadPatterns.Add("Live", 3)
SapModel.LoadPatterns.Add("EX", 5)

# Mass source
LoadPat = ["Dead", "SuperDead", "Slab", "Partition", "Wall", "Live"]
SF = [1.0, 1.0, 1.0, 1.0, 1.0, 0.2]
SapModel.PropMaterial.SetMassSource(3, len(LoadPat), LoadPat, SF)

# Groups
SapModel.GroupDef.SetGroup("Columns (ALL)")
SapModel.GroupDef.SetGroup("Beams (Braced bay)")

# Concrete material
SapModel.PropMaterial.SetMaterial("C40", 2)
SapModel.PropMaterial.SetOConcrete_1("C40", 40, False, 0, 2, 2, 0.002, 0.005)

# Steel rebar
SapModel.PropMaterial.SetMaterial("R500", 6)
SapModel.PropMaterial.SetORebar_1("R500", 500, 575, 200000, 200000, 1, 1, 0.01, 0.09, False)

# Frame section
SapModel.PropFrame.SetRectangle("C500x500", "C40", 0.5, 0.5)

# Add column by coordinates
SapModel.FrameObj.AddByCoord(0, 0, 0, 0, 0, 3.2, "", "C500x500")
SapModel.FrameObj.SetGroupAssign("1", "Columns (ALL)")
```

---

## S17. Concrete Design Run + Results (C1, C2, D1)

From `nhniegas/Etabs_Designer/etabs_api.py`:

```python
def run_concrete_design(SapModel, design_code="ACI 318-14", combos=None):
    """Run concrete design with specified code and combos."""
    SapModel.DesignConcrete.SetCode(design_code)
    if combos:
        for combo in combos:
            SapModel.DesignConcrete.SetComboStrength(combo, True)
    SapModel.DesignConcrete.StartDesign()

def get_design_results(SapModel, table_key="Concrete Beam Design Summary"):
    """Read design summary as DataFrame."""
    raw = SapModel.DatabaseTables.GetTableForDisplayArray(
        table_key, [], "", 0)
    fields = list(raw[2])
    data = raw[4]
    n = len(fields)
    rows = [list(data[i:i+n]) for i in range(0, len(data), n)]
    return pd.DataFrame(rows, columns=fields)
```

---

## S18. Spandrel Design Results (wall scenarios)

From `danielogg92/Etabs-API-Python/Database_Tables.py`:

```python
def get_spandrel_design(SapModel, code='AS 3600-2018'):
    table_key = f'Shear Wall Spandrel Design Summary - {code}'
    raw = SapModel.DatabaseTables.GetTableForDisplayArray(table_key, GroupName='')
    fields = list(raw[2])
    n = len(fields)
    num_records = raw[3]
    data = raw[4]
    spandrels = {}
    for i in range(num_records):
        row = data[i*n:(i+1)*n]
        story = row[0]
        spandrel = row[1]
        top_rebar = int(row[3])
        mu_top = round(float(row[6]) * 1e-6, 1)  # N.mm -> kN.m
        vu = round(float(row[14]) * 1e-3, 1)      # N -> kN
        spandrels[f"{story}_{spandrel}"] = {
            "top_rebar": top_rebar, "Mu_top": mu_top, "Vu": vu
        }
    return spandrels
```

---

## S19. Brace Force Comparison + Excel Export (C1 variant)

From `retug/ETABs/BraceChecksv001.py`:

```python
def compare_brace_forces(SapModel, baseline_cases, modified_cases, threshold=0.10):
    """Compare brace forces between two conditions, flag >10% change."""
    def get_forces(cases):
        SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        for c in cases:
            SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay([c])
        raw = SapModel.DatabaseTables.GetTableForDisplayArray(
            "Element Forces - Braces", [], 'All', 1, [], 1, [])
        fields = list(raw[2])
        data = raw[4]
        n = len(fields)
        rows = [list(data[i:i+n]) for i in range(0, len(data), n)]
        return pd.DataFrame(rows, columns=fields)

    baseline = get_forces(baseline_cases)
    modified = get_forces(modified_cases)

    baseline["P"] = baseline["P"].astype(float).abs()
    modified["P"] = modified["P"].astype(float).abs()

    b_max = baseline.groupby("UniqueName")["P"].max()
    m_max = modified.groupby("UniqueName")["P"].max()

    failing = []
    for brace in b_max.index:
        if brace in m_max.index:
            change = (m_max[brace] - b_max[brace]) / b_max[brace]
            if change >= threshold:
                failing.append(brace)
                SapModel.FrameObj.SetGroupAssign(brace, "Failing Braces")
    return failing
```

---

## S20. Geotechnical — SPT Pile Capacity (F3)

From `geoeq/geoeq/design/piles.py`:

```python
# pip install geoeq
import geoeq as ge

# SPT corrections
N60 = ge.spt_n60(N_field=25, rod_length=12, borehole_dia=150,
                  sampler="standard", hammer="safety")
N1_60 = ge.spt_n160(N60=N60, sigma_v=120, method="liao_whitman")

# Pile capacity from SPT
qp = ge.pile_end_bearing(N=N1_60, depth=15, diameter=0.6, method="meyerhof")
fs = ge.pile_skin_friction(cu=50, sigma_v=100, method="alpha")
Qult = ge.pile_capacity(qp=qp, fs=fs, diameter=0.6, length=15, FS=2.5)

# Bearing capacity
Nc, Nq, Ng = ge.bearing_factors(phi=30, method="vesic")
qu = ge.bearing_capacity(c=0, q=50, gamma=18, B=2.0, Nc=Nc, Nq=Nq, Ng=Ng,
                          shape="square", depth=1.5)
qa = ge.bearing_allowable(qu=qu, FS=3.0)

# Settlement
s_imm = ge.settlement_immediate(q=150, B=2.0, E=15000, nu=0.3, shape="square")
s_con = ge.settlement_primary(delta_sigma=100, H=5, e0=0.8, Cc=0.3, sigma_v0=80)
```

---

## Snippet-to-Scenario Mapping

| Snippet | Scenarios | API Pattern |
|---------|-----------|-------------|
| S1 | All | COM connection boilerplate |
| S2 | A1-A6, C1-C2, D1-D4, E1-E2, G2 | `GetTableForDisplayArray()` to DataFrame |
| S3 | B2, B4 | `SetTableForEditingArray()` write-back |
| S4 | A1, D4 | Story drift pass/fail check |
| S5 | A5 | Modal periods + mass participation |
| S6 | A2, E1 | Base reactions extraction |
| S7 | A3, A6, G2 | Frame geometry retrieval |
| S8 | G1, G2 | Material property reading |
| S9 | G1 | Australian concrete material creation |
| S10 | B1 | Load combination creation |
| S11 | B3 | Load pattern type detection |
| S12 | A6, D1 | Pier forces to Excel |
| S13 | D1, D2 | Frame forces to Excel |
| S14 | C1 | Force envelope across combos |
| S15 | C1 | Iterative section resize |
| S16 | G1 | Full model from scratch |
| S17 | C1, C2, D1 | Concrete design run + results |
| S18 | — | Spandrel design (reference) |
| S19 | C1 variant | Brace force comparison |
| S20 | F3 | Geotechnical pile capacity |

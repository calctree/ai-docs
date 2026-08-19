---
name: connection-node-testing
description: Paste-ready MDX test pages for connection nodes (ETABS, Excel, SAFE, RAM Concept). Each .mdx file is a complete CalcTree page — paste the entire contents into a page to create the connection node, calculation context, and test criteria in one shot.
---

# Connection Node Test Suite

24 test scenarios across 7 categories exercising every connection node capability:
read (Var), write (Input), scripting (Script), and multi-software pipelines.

## How to use

1. Open CalcTree and create a new blank page.
2. Pick a test file from `pages/` and copy the **entire** MDX content.
3. Paste into the page (or use `insertMDXContent` via the API).
4. Connect to the target software (ETABS/Excel/SAFE) using the connection sidebar.
5. The page content describes what to check and the expected behaviour.

Each `.mdx` file is self-contained: it has the `<Connection>` node(s) at the top,
followed by page body content with test description, inputs, and verification criteria.

## Categories

| Cat | Folder | Software | Capability | Tests |
|-----|--------|----------|------------|-------|
| A | `a-etabs-read` | ETABS | Read-only (`<Var>` + `<Script>`) | A1-A6 |
| B | `b-etabs-write` | ETABS | Write (`<Script>` with SapModel writes) | B1-B4 |
| C | `c-etabs-roundtrip` | ETABS | Read + write + re-analyse | C1-C2 |
| D | `d-etabs-excel-pipeline` | ETABS + Excel | Multi-connection data flow | D1-D4 |
| E | `e-cross-tool` | ETABS/SAFE/RAM | Cross-software transfers | E1-E3 |
| F | `f-excel-only` | Excel | Pure Excel read/write | F1-F3 |
| G | `g-model-generation` | ETABS | Full model build + validation | G1-G2 |

## Test coverage matrix

| # | Scenario | Var | Input | Script | Multi-conn |
|---|----------|-----|-------|--------|------------|
| A1 | Story Drift Check | x | | x | |
| A2 | Column Base Reactions | x | | x | |
| A3 | BOQ Extraction | x | | x | |
| A4 | Stability Index | x | | x | |
| A5 | Modal Analysis | x | | x | |
| A6 | Beam Forces | x | | x | |
| B1 | ACI Load Combos | | | x | |
| B2 | SDS Combo Update | | | x | |
| B3 | Load Pattern Setup | | | x | |
| B4 | Unbraced Lengths | | | x | |
| C1 | Section Optimisation | x | | x | |
| C2 | Column Grouping | x | | x | |
| D1 | Beam Design Pipeline | x | x | x | x |
| D2 | Column Design Pipeline | x | x | x | x |
| D3 | Column Grouping Excel | x | | x | |
| D4 | Drift Report to Excel | x | x | x | x |
| E1 | Reactions for SAFE | x | | x | |
| E2 | Floor Geometry for RAM | x | | x | |
| E3 | Foundation Springs | x | | x | |
| F1 | AASHTO Culvert | x | | x | |
| F2 | ETABS-to-STAAD Reformat | x | x | x | |
| F3 | SPT Pile Capacity | x | | | |
| G1 | Full Model Generator | | | x | |
| G2 | Model Validation | x | | x | |

## Code provenance

All connection scripts are derived from verified open-source ETABS Python repos.
See `reference/github-snippets.md` for the original code and repo links.

| Repo | Stars | Used in |
|------|-------|---------|
| ebrahimraeyat/etabs_api | 80 | A1-A6, B1-B3, C1-C2, E1 |
| danielogg92/Etabs-API-Python | 73 | A3, A6, G2 |
| retug/ETABs | 22 | D1, D2 |
| mihdicaballero/ETABS-Ninja | 16 | A1, D4 |
| keshishianv/ETABS-Python-Codes | 1 | D1, D2 |
| AesirX899/etabs-python-api | 3 | C1 |
| EhsanAlizadeh1/ETABS-API-Example | 5 | B3, G1 |
| nhniegas/Etabs_Designer | 1 | C1, D1 |
| geoeq/geoeq | - | F3 |

## Connection MDX format reference

```
<Connection software="etabs" model="Model.edb" name="Display Name" requires="Instructions">
  <Var name="var_name" table="Table Key" column="Column" />
  <Input from="source_var" table="Table Key" column="Column" />
  <Script>
` ` `python
# Globals: sap (SapModel), etabs (Application), parse_table()
rows = parse_table("Story Drifts")
` ` `
  </Script>
</Connection>
```

Software globals:
- **ETABS**: `sap` (SapModel), `etabs` (COM Application), `parse_table("Table Name")`
- **Excel**: `xl` (Excel.Application), `wb` (Workbook) -- use `.Value2` not `.Value`
- **SAFE**: `sap` (SapModel), `safe_app` (COM Application), `parse_table()`
- **SAP2000**: `sap` (SapModel), `sap_app`, `parse_table()`
- **GSA**: `gsa` (Oasys GSA COM object)
- **RAM Concept**: `ram_concept` (COM Application)

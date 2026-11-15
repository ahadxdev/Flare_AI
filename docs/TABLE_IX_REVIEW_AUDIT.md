# NASA FLEX Table IX Scientific Measurement Audit

## Executive summary

The audit examined all **2,370 staged Table IX candidates** in the read-only
SQLite database against the original NASA FLEX results report, its Table IX
pages, and the per-test figure captions. The source PDF hash matches the
verified NASA source manifest. All 2,370 candidate values were matched to the
correct Table IX row, column, and PDF page; the source table contains 276 test
rows. Four test identifiers (156, 205, 213, and 228) do not appear in the
table and were not reconstructed.

**410 candidates appear to be individually reported experimental results with
adequate table and source context for human review:** 142 visible-flame
extinction-diameter entries without an identified contradiction or explicit
extrapolation, and 268 exact per-test burn-time entries. This is not an
approval or a claim that the values have been independently remeasured.
**Every candidate remains pending human review.**

The audit classified another 287 values as derived quantities, 2 as
approximate values, 1,379 as boundary conditions, 264 as initial conditions,
and 28 as ambiguous. The ambiguous group includes source-internal conflicts
and data-quality cases that must not be approved as observations without
resolution. The three pre-existing approved FLEX observations were not
modified.

The row-level machine-readable register, including the complete candidate-ID
grouping, original value precision, source hashes, table-row excerpts, figure
references, audit classification, and review rationale, is
[table_ix_review_audit.csv](../data/reports/table_ix_review_audit.csv).

## Scope and provenance

The primary source is the locally preserved, verified NASA report
[20150023456.pdf](../data/raw/nasa/20150023456.pdf):

| Field | Verified value |
|---|---|
| Source ID | `src-ntrs-flex-results` |
| Title | Detailed Results from the Flame Extinguishment Experiment (FLEX) March 2009 to December 2011 |
| NASA URL | <https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf> |
| Local file | `data/raw/nasa/20150023456.pdf` |
| SHA-256 | `b4f6ca983e2792c33a0b92220a791a818f426bb635b94f7fd33dc8c9c471e79d` |
| Hash check | Matches `data/raw/nasa/source_manifest.json`; source is marked `verified` |

The comparison source for the three previously approved results is
[20130014061.pdf](../data/raw/nasa/20130014061.pdf), source ID
`src-ntrs-flex`, SHA-256
`1488bbb461f2ea0f97c2c2fab6ac0a01603a6837509ab6ac6d1ef02bbf72050b`.
Its NASA URL is
<https://ntrs.nasa.gov/api/citations/20130014061/downloads/20130014061.pdf>.

All page references below distinguish the physical PDF page from the printed
page number. Table IX occupies **PDF pp. 26–34 (printed pp. 20–28)**.
Appendix A.1 is on PDF p. 25 (printed p. 19), and Appendix A.2 begins on PDF
p. 26 (printed p. 20). The original PDF page images for all nine Table IX
pages were inspected. Table-row page numbers stored on the candidates match
the physical PDF pages, not the printed pagination.

## Table structure and measurement meaning

The table caption is **“TABLE IX.—RESULTS BY TEST NUMBER AND FLEX IDENTIFIER.”**
Its row fields are FLEX test number, engineering identifier, date, GMT test
time, fuel, ambient pressure (mmHg), initial ambient O₂/N₂/CO₂/He mole
fractions, initial droplet diameter (mm), visible flame extinction diameter
(mm), burning rate (mm²/s), burn time (s), and test end.

Appendix A.1 defines the relevant fields as follows:

- **Actual D0** is the initial droplet diameter, or the diameter at time zero
  when the igniters are turned on. It is an initial condition, not a
  combustion outcome.
- **Burning rate** is an average burning-rate constant calculated from a
  linear fit of droplet diameter squared versus time. It is a derived
  quantity, not a direct sensor reading.
- **Visible flame extinction diameter** is the droplet diameter at the time
  the visible flame extinguished. A dash means flame extinction did not occur
  because the droplet burned to completion or disruption ended burning.
- Ambient pressure and gas fractions describe the test atmosphere. Appendix
  A.1 says the gas fractions are drawn from chamber-fill, recirculation,
  filter, and combustion-history records; they are boundary conditions, not
  measured combustion outcomes.
- Where a droplet left the HiBMs field of view before extinction, the report
  says the team estimated the extinction diameter by extrapolating the
  burning history only when enough history was available and the extrapolation
  was not too long. Otherwise, the report says no extinction diameter is
  listed. Accordingly, a Table IX number is not automatically a direct
  observation.

The report's HiBMs droplet-size analysis estimates measurement uncertainty at
±50 µm. In §5.1 it also says igniter overexposure made droplet-size readings
in FLEX tests 001–009 less accurate. The eight Table IX initial-diameter
candidates present for tests 001–008 retain their `initial_condition`
classification but are flagged for this source-stated quality limitation;
test 009 has no initial-diameter candidate.

## Audit classifications

Each candidate has one audit classification. The full candidate-ID sets are
included in the collapsible groups at the end of this report and as rows in
the CSV.

| Audit classification | Candidates | Basis |
|---|---:|---|
| `experimental_observation` | 410 | 142 extinction-diameter values without a source conflict or explicit extrapolation, plus 268 exact per-test burn times |
| `derived_quantity` | 287 | 260 linear-fit burning-rate constants and 27 extinction-diameter values explicitly estimated or extrapolated in the per-test report text |
| `approximate_value` | 2 | Burn times reported as `~6` and `~9` |
| `boundary_condition` | 1,379 | Ambient pressure and gas-composition fields, excluding one conflicted pressure value |
| `initial_condition` | 264 | Table IX Actual D0 values; tests 001–008 carry an additional image-quality warning |
| `ambiguous` | 28 | 27 extinction-diameter entries with specific source-evidence issues, plus the test 114 pressure entry |
| `setup_parameter` | 0 | No Table IX candidate was classified as a separately reported setup parameter |
| `simulation_input` | 0 | No simulation-input candidates were identified |
| `reported_summary` | 0 | The extracted Table IX candidates are per-test rows, not aggregate summary statistics |
| `hypothetical_scenario` | 0 | No hypothetical mission values occur in Table IX |
| `unsupported` / other rejected | 0 | No additional candidate was put in these categories; the unresolved cases are retained as `ambiguous` |
| **Total** | **2,370** | All candidates remain `pending_review` |

The 268 exact burn-time values are individual source-reported test durations,
not aggregate summaries. Appendix A.1 does not define a precise start/stop
convention for this column, so the human reviewer should confirm the
time-series or other supporting record before approval. The audit does not
interpret a pipeline confidence score as scientific validation.

### Results by variable

| Table IX field | Count | Audit treatment |
|---|---:|---|
| Ambient pressure | 275 | Boundary condition except the ambiguous FLEX–114 value |
| O₂, N₂, CO₂, He mole fractions | 1,104 | Boundary conditions |
| Initial droplet diameter | 264 | Initial conditions; early-run image-quality flag on FLEX–001–008 |
| Visible flame extinction diameter | 196 | 142 experimental-observation candidates; 27 derived; 27 ambiguous |
| Burning rate | 260 | Derived from a linear fit |
| Burn time | 270 | 268 exact per-test results; 2 approximate |

### Source-row and page-alignment verification

The Table IX candidate excerpts were independently matched against the
corresponding row in the original PDF text extraction. All **2,370/2,370**
candidate values matched the expected Table IX column and exact reported
string, and all **2,370/2,370** candidate page numbers matched the physical
PDF page containing that row. Each candidate row had the expected 15
table fields. The nine table pages were also visually inspected; no row was
reconstructed from a neighboring row or from an inferred value.

The four missing FLEX test numbers—156, 205, 213, and 228—are absent from the
Table IX rows. They have no candidate entries and were not inferred from
figure numbering, neighboring tests, or other values.

## Ambiguous candidates recommended for priority human review

These 28 candidate IDs should not be approved as measurements unless a human
reviewer resolves the listed source evidence. Their exact original Table IX
row, figure reference, page, source hash, and rationale are in the CSV.

| FLEX test(s) | Issue |
|---|---|
| 006, 020, 026, 070, 073, 097, 098, 099, 208, 209, 234, 255 | Figure captions describe loss of the droplet from the HiBMs field of view before or near extinction, an inadequate extinction-diameter estimate, uncertain test termination, or image-analysis interference. The table value cannot be assumed to be a direct measurement; see the row-specific CSV rationale. |
| 034, 104, 147, 157, 188, 200, 258 | Table IX gives a numeric extinction diameter, but the corresponding test figure says no extinction diameter is reported. This is an unresolved within-report conflict. |
| 039, 043, 051, 052, 069, 093, 135 | Table IX prints `0` mm for extinction diameter. The figure narratives describe disruption, completion, short or disturbed burns, or other context but do not establish that literal zero is a measured diameter. The value is preserved as printed and is not changed to null or treated as a measured zero. |
| 204 | Table IX reports 1.11 mm while the earlier NASA report reports 1.10 mm for the matching Run #204. See the discrepancy investigation below. |
| 114 | Table IX reports ambient pressure as `0` mmHg, while Figure 118 describes the test as a 0.70-atm environment. No pressure conversion or replacement value was inferred. |

### Candidate-level review queue

| Candidate ID | Test | Variable | Reported value | Issue |
|---|---|---|---:|---|
| `candidate-83fc6ff100d2691fc1a45a51767f16210ede36ae631d958f26fc42052d91e7dd` | `FLEX–006` | visible flame extinction diameter | `1.53 mm` | Figure 10 says the droplet left and re-entered the HiBMs FOV, but does not establish whether the Table IX extinction diameter was observed at extinction or estimated. |
| `candidate-a8a7bf8df77649cfed455c01c90f0fe82814d180d7a0ede249656a45cfa36f34` | `FLEX–020` | visible flame extinction diameter | `1.56 mm` | Figure 24 says the droplet was in the HiBMs FOV only briefly and may have burned to a small size or completion; the reported extinction diameter is not supported as a direct value. |
| `candidate-1754429622b755a9795ce4fda90c09ccfeb2e2ab46fd69c024cc06e3fbdd8fe6` | `FLEX–026` | visible flame extinction diameter | `.4 mm` | Figure 30 says the droplet left the HiBMs FOV before a possible completion or disruption; the table value is not identified as direct or extrapolated. |
| `candidate-06cc4de42bce9f0ed08311b774f0f90ac9ce6b8e482f5cccc09a4dda9cf0b1b3` | `FLEX–034` | visible flame extinction diameter | `2 mm` | Figure 38 says no extinction droplet diameter is reported, while Table IX lists a numeric value. |
| `candidate-70c58e97918fc78f16cff6463d35e0bf64cebc1c5fa53efbce3eb5006dce5668` | `FLEX–039` | visible flame extinction diameter | `0 mm` | Table IX prints 0 mm, but Figure 43 describes a sooting, fiber-supported disruptive extinction and does not establish a literal zero diameter. |
| `candidate-9a67a7238433e511d07777803bc8734252e5db5e327014c179d0a94a45ead668` | `FLEX–043` | visible flame extinction diameter | `0 mm` | Table IX prints 0 mm, while Figure 47 describes disruption and dislodgement without supporting a literal zero diameter. |
| `candidate-a23f0075f7f015131caae68654908dd9656fc5b720959beb0ade85e575905c58` | `FLEX–051` | visible flame extinction diameter | `0 mm` | Table IX prints 0 mm, while Figure 55 says the flame disappeared halfway through and the droplet burned to completion; the meaning of zero is unresolved. |
| `candidate-a4033bdb3f76e4bf58690c7f78f929063028a86ec51fa80623d80db78c69d58d` | `FLEX–052` | visible flame extinction diameter | `0 mm` | Table IX prints 0 mm, while Figure 56 describes a late disruption and does not support a literal zero diameter. |
| `candidate-ac36fb69588713c4f7b567e06baaa9c8ed3e3af8aee9292280f5c67225f3552c` | `FLEX–069` | visible flame extinction diameter | `0 mm` | Table IX prints 0 mm; Figure 73 describes a very short burn with substantial droplet motion and does not establish a measured zero diameter. |
| `candidate-ea1675cd16878857d9f82c3d70949f3a2eef3a7d5250cd9d42b1494c7a2a917d` | `FLEX–070` | visible flame extinction diameter | `4.6 mm` | Figure 74 describes an anomalous deployment and loss from the HiBMs FOV; the table value cannot be confirmed as a direct extinction measurement. |
| `candidate-93d080c2ed12c042bab35758cd7d082656946a755cc940148eb50e730dc04d49` | `FLEX–073` | visible flame extinction diameter | `4.58 mm` | Figure 77 describes a very large droplet leaving the FOV quickly and limited evidence near extinction; the table value may not be a direct measurement. |
| `candidate-003ab4236267cf5f74fc7a4366f510918699fdb7c5801d3456181f52a2d131ec` | `FLEX–093` | visible flame extinction diameter | `0 mm` | Table IX prints 0 mm, while Figure 97 describes high-rate burning and fiber-supported motion without establishing a literal zero diameter. |
| `candidate-e0bb8cd4840a4a9d73dd9c99849a913636ce600748a004ff59e1d5ef34b7118e` | `FLEX–097` | visible flame extinction diameter | `2.6 mm` | Figure 101 says the droplet left the camera fields before extinction or disruption; the table value is not supported as a direct measurement. |
| `candidate-81b2a0348cf1b42f4adaf4436fd75500c73fa7735d38a1256dded55dde291b4e` | `FLEX–098` | visible flame extinction diameter | `1.74 mm` | Figure 102 says the HiBMs record was insufficient for an accurate extinction-diameter estimate, although Table IX lists a numeric value. |
| `candidate-3256a43de0c3c967d9cc1d07ab9e6801fe35ad67d8f1dc9a32fdb725f1cb3ea5` | `FLEX–099` | visible flame extinction diameter | `2.32 mm` | Figure 103 says the HiBMs record was insufficient for a good extinction-diameter estimate, although Table IX lists a numeric value. |
| `candidate-d9c63afff7055d5db5ab3b10c34e9bce4b6b3c6ff0997bff9d41054ec89ae1af` | `FLEX–104` | visible flame extinction diameter | `1.58 mm` | Figure 108 says no extinction droplet diameter is reported, while Table IX lists a numeric value. |
| `candidate-450b6023b015fdb8e23c07df7b0e3b0c533ddf119a63b3c8755c329150ff0b52` | `FLEX–114` | pressure | `0 mmHg` | Table IX reports 0 mmHg, while Figure 118 describes a 0.70-atm environment. No converted or replacement value was inferred. |
| `candidate-ea944da8d72fb41875ff39fee0b9551658a8b594ddf94f7eaf7d5fe959d078b7` | `FLEX–135` | visible flame extinction diameter | `0 mm` | Table IX prints 0 mm; Figure 139 describes completion and droplet-material ejection but does not establish a literal zero diameter. |
| `candidate-cf6bcf808a43f135bdf94143fada206927cd61539b385a61d03de7fa2da272c4` | `FLEX–147` | visible flame extinction diameter | `2.49 mm` | Figure 151 says no extinction droplet diameter is reported, while Table IX lists a numeric value. |
| `candidate-992851a04b9246fa31efda5fd4d31efb2828255e6e65861b68ee2678353dfc24` | `FLEX–157` | visible flame extinction diameter | `.45 mm` | Figure 160 says no extinction diameter is reported, while Table IX lists a numeric value. |
| `candidate-04e366b18556dcf02764f64d9d94036254bbde442c6f4ffd6eaab24ef3b51685` | `FLEX–188` | visible flame extinction diameter | `1.29 mm` | Figure 191 says no extinction droplet diameter is reported, while Table IX lists a numeric value. |
| `candidate-fed8a128594fe88899bb13524a75e46f74516bd06c646a8c94c02014372edb94` | `FLEX–200` | visible flame extinction diameter | `.98 mm` | Figure 203 says no extinction diameter is reported, while Table IX lists a numeric value. |
| `candidate-88c2c43eb1936e719a4d4e46c92013dd8e6c6fa6a3fb92616435ec4ca060ca6c` | `FLEX–204` | visible flame extinction diameter | `1.11 mm` | Table IX reports 1.11 mm, but the earlier NASA report reports 1.10 mm for the matching Run #204; no source explains the difference. |
| `candidate-3c357742b3dbc2a26d79e13e159c5a8bc92be26e81fb302e96fefe266439e77f` | `FLEX–208` | visible flame extinction diameter | `.47 mm` | Figure 210 says the droplet left the HiBMs FOV before disruptive extinction; the remaining LLUV view does not by itself establish the droplet diameter at extinction. |
| `candidate-807d9300509b158c2ea19387334af8980ca19a47f380640645fdab14d6e64e1a` | `FLEX–209` | visible flame extinction diameter | `1.13 mm` | Figure 211 says the droplet left available fields of view and that disruption was unclear, while Table IX lists an extinction diameter. |
| `candidate-f535284e65a08d673683891d1e644b03e226ec5a6440b3bb143fa067e798324e` | `FLEX–234` | visible flame extinction diameter | `1.37 mm` | Figure 234 describes loss of the droplet and flame from the relevant camera views and says continued burning and duration are unclear, while Table IX lists an extinction diameter. |
| `candidate-41a4cb77b455ce4bb03f10fe098de04a911bcb354c571d90ae41eb5949251d81` | `FLEX–255` | visible flame extinction diameter | `2.52 mm` | Figure 255 says the droplet left the HiBMs FOV near extinction and soot interfered with droplet-image analysis; the table value needs human verification. |
| `candidate-a1ca5ea22507668012006ecd108c196cc886fcb494a1421a0ba0c203bfd97f7a` | `FLEX–258` | visible flame extinction diameter | `1.53 mm` | Figure 258 says no extinction droplet diameter is reported because of disruption, while Table IX lists a numeric value. |

All other candidates are still pending review as well. The `experimental_observation`
label means only that the source presents an individual result without an
identified classification conflict in this audit; it does not mean that a
reviewer has approved it or that a raw video/time-series has been
independently remeasured.

## Run #204: 1.10 mm versus 1.11 mm

The discrepancy is **unresolved**. The compared values refer to the same
reported experiment and the same measurement definition with high confidence:

- Table IX, PDF p. 31 (printed p. 25), row `FLEX–204`, reports methanol,
  ambient pressure `761.6` mmHg, O₂/N₂ mole fractions `.21/.79`, initial
  diameter `2.75` mm, visible flame extinction diameter `1.11` mm, burning
  rate `.52` mm²/s, and burn time `12.8` s.
- Figure 207, PDF p. 237 (printed p. 231), describes FLEX–204 as a methanol
  droplet in 0.21/0.79 O₂/N₂ cabin air at 1.0 atm. It says all cameras viewed
  the droplet through the burn and that it left the HiBMs field of view
  shortly after diffusive flame extinction. The figure also notes that the
  image-processing unit did not record every frame.
- The earlier NASA paper, PDF p. 5, calls it `Run #204` and reports a
  methanol droplet with initial diameter `2.75` mm in air (20% O₂, 79% N₂)
  at one atmosphere, with extinction diameter `1.10` mm.
- Table IX defines its field as droplet diameter at visible flame extinction;
  the earlier paper calls the same physical quantity extinction diameter
  `De`. The identifiers, fuel, initial size, atmosphere, and measurement
  definition align.

The values differ by 0.01 mm (10 µm), which is smaller than the 2015 report's
stated ±50 µm droplet-size uncertainty. That fact does **not** explain the
difference: neither source states that one value is a correction, a rounding
of the other, or a revision. The audit therefore retains both as separately
reported source values, keeps the already-approved 1.10 mm measurement
unchanged, and leaves the Table IX 1.11 mm candidate ambiguous.

For comparison, Table IX values for FLEX–110 (1.57 mm) and FLEX–263
(1.42 mm) match the corresponding earlier-paper values exactly. This does
not change the approval status of any record.

## Database and API integrity

The audit used read-only SQLite access and did not update, insert, delete,
approve, or reject any candidate or measurement. The database is
`backend/flare_ai.sqlite3`.

| Check | Result |
|---|---|
| Table IX candidates | 2,370; all `pending_review` |
| All database candidates | 2,423: 2,420 `pending_review`, 3 `approved`, 0 `rejected` |
| Approved FLEX observations | Run #204 = 1.10 mm; Run #110 = 1.57 mm; Run #263 = 1.42 mm |
| Existing approval metadata | Preserved; no reviewer attribution, approval timestamp, source hash, or value was changed |
| Live `GET /api/measurements?investigation_id=psi-flex` | HTTP 200; returns the same three approved observations |
| Database SHA-256 before/after audit | Identical before and after: `12ab4cbde620c69a8aa85a06beb3a0fe36e1f5400d7ca103effa461b07bf1edd` |
| Source PDF hashes | Both FLEX PDFs match their verified source-manifest hashes |

Only the requested audit report and CSV are deliverables from this task; no
application code or database record was changed.

## Limitations and review recommendations

1. Treat all 2,370 candidates as pending. Prioritize the 410
   `experimental_observation` candidates for source review, but confirm their
   original page, exact value, unit, test identity, and any relevant
   time-series before approval.
2. Do not approve the 287 `derived_quantity` entries as direct observations.
   The 260 burning-rate entries are linear-fit results; 27 extinction
   diameters are explicitly estimated or extrapolated.
3. Do not approve the 28 `ambiguous` candidates until their table/figure or
   cross-report conflicts are resolved. Preserve the source-reported values
   as written in the CSV; do not infer replacements.
4. Treat the two approximate burn times as approximate, not exact numeric
   measurements.
5. Keep boundary conditions and initial conditions separate from measured
   combustion outcomes. In particular, do not infer a corrected pressure
   for FLEX–114 from its caption.
6. This audit used the original NASA PDFs and their per-test figure captions;
   it did not inspect the archived raw camera videos or the separate
   electronic data/DVD addendum. No figure points were digitized.
7. Four test IDs are absent from Table IX, and the report's source manifest
   records no text layer on PDF pp. 1, 6, 24, and 312–314. The missing-text
   pages do not overlap Table IX, which is present and readable on PDF pp.
   26–34.
8. Microgravity observations are not evidence of proven lunar or Martian
   partial-gravity performance.

The exact command syntax for the existing candidate review CLI is documented
in [development.md](./development.md#extract-and-review-numeric-candidates).
This audit did not run a scan or review command because the task was
read-only.

## Candidate IDs grouped by audit classification

The following complete ID sets are generated from the read-only database
snapshot and grouped by the audit classification in the CSV. They are
collapsible to keep the report readable.

<details>
<summary><code>experimental_observation</code> (410 candidates)</summary>

<pre>
candidate-f59ef4b521b04fb173239c15c03c9c9ce336552199df7dd57c3b6bf93bcfbcf5
candidate-aff8175711b16f6d2373a0541beb7de064ce700f39ea7c92e3b8c36ffe893085
candidate-c70f666dc8f5c4a86529e955a286e1c0f0155d04baa9abe19d23216487fa5f13
candidate-578c08955f2e435f87e8442d45f4a338a5325baae4bd31f54aa26116483a9568
candidate-3f3e0eec5f3b14f210eb06723aebc7e49362efb18140fbe240be2e6a15906fa1
candidate-b00736d7715c6b02f6e36e76acbd9ba8c78ed0520ff6c9d2ef0c9a8cd3aa1f51
candidate-eb7783d5cee6b0fc923f8e5a8e2e413c20f72ae2a1bcdc199482b48cec0b2443
candidate-cf0d016bf5899fa016776ab1dd0d05f5ea2bd9a0880fa265e31ba7a06448af1d
candidate-80a97123dc67886cebad2631a1aeb0272b2cc32b504a351accc1e7b40f372083
candidate-ea77620bdb476cc9f5099de2e973196ba2e0fa3bb408bf53b7f829d1b5771a1b
candidate-dc35b992dbda374ec78d43ecee9330983e4c61ec04d53b7fc7267c5bd6c484af
candidate-a3d98e753583c34d9deaab75046dd6c16f2bdca31feb4a3272c29918086c3447
candidate-22a6d8232c3f5a478d038eedaff97e6b5b6fd115c792d295c0cd0305527bda4c
candidate-043dc7b15aeae6cb054e03efd07fe9fbb3f9402188745b788faf09c962d778f8
candidate-0493bac75ab37e071dd052af61e667b1c6876587e08813e06f1fda867b39a5e6
candidate-5cffe8ec7812317efcdc998fb841dc0d7a2394d0be11ea1c7fa571efce203c88
candidate-e0980d95d54871ef9a2b019e4599806941a97c321feff1a6ae5114029ad591e9
candidate-d2a23ed3843faea25d233f3e8e86e9bd349556f90215b70b32430f1478bdbe05
candidate-2dc91e9d4521a0cc27c5caafa350a70f332a67649d2d114dea14a934fd0fb6d8
candidate-349251041772225d5bbd086c7f8b22bde827ce8dbe20ef75dd6f87e34cd9848b
candidate-772433726523695c33652f1e4f03f35d4b1fff4b826129047d6bef3ef16a223c
candidate-066a820670ccdfe38ae753bdd0d9162a5ad0be37a86666d6cf784e8e3b9228b2
candidate-7cab7055d49128d74045d5e72c7a7c5becbad6ca86e29ed96489a36ae965d549
candidate-9ffd583e04ccffcf9f0a0a978a1f12b3f677c32293114f19687324309611d129
candidate-1da05207d24d2ab9adbae1b4e0677009f8f08a05bda5d96d871d99ec579603e2
candidate-82228ae04dcfd55c7108633bc0bc3411369185052d6eb733fe32d53d9d6f847b
candidate-31b8e88bce7ca817c147580e332c77ce440afd85a7201ecb37fbecc1909292f4
candidate-08513f5092798717e3234a002d029eca612de7877a70aef27338dc7385856b37
candidate-18a313c7d166ce37fc8227edfd4c54ecb42b745e092d25fa13c6d0fd4b32af58
candidate-53ca46c96fb9cfb6fb7bcce4d2a847e6e08c9cb54e272346918245ae60857f75
candidate-8cfedce519df7261048dda55eeb3ea1334a135b6dfc692f93455db1afbc2f473
candidate-083a16d4e3e27c873bbce4da878239c40eac6df49a667d156e2f9ff2c217781d
candidate-81b5a57488d04fd31f90d2932d94edbbac8f1d411b6dfc75f41e7c1704989699
candidate-068deb1b8b0d88102d38c298be6242b10a1508c72a007c104f5b8c1dd4478a2e
candidate-b4543ec8a5ecff2f754f4a9c6e1deda8da88f3eb1f9896c53d7acf65b563f7b0
candidate-6474c86a08d59fa4c995f8317f3ca1dd0c5225af7a0a468ed6d70f07dbd7713d
candidate-a4e994e1e2573f992f91ed70960a50671a8b86ac04684243eebe8c68644d10e2
candidate-c49a6dc516898246f7252c863ef779c054940608e75efa802889688e55b257ab
candidate-1eb157866b432a5cc23f9f6c3c5aa55693e5d8272d5ab9fdefe40a7375357bb4
candidate-1acec582ecf808283482e5b5ecafbce388777eac23c79f68e8b4a37d1d93b21c
candidate-c7826e97e7a6e06372e029bd81f64d7e30a2fdb9c3973d32742cd0e30c087e05
candidate-baf7f5f80aec660c8a8c01eea28238d9d663669d664af36e15a28cfa1ce1d61a
candidate-ff4d4db74cd34116bca7479b42f4c5e64a3e8cd0d05cc563236e58b192e64d86
candidate-a917e2f5878b612a52616300011bd4adca826ef4061e35f2ed7adccb33968b3e
candidate-38316fbb54e42dc41e2e72378c9e245e7f0377f53bfb39a1d4310b3c99faf311
candidate-80b0eaa41e7454023417f7d53995f74c957649e4adc7dd5f7af12b67b29f639c
candidate-9d64e59f15713fcc59d1db0d929b6b150219289eda3ba80d76bee9b2b3d5c259
candidate-5d782fa329b2a7e1edccf7c43b2a1d0bac5573364e45fcf80ad218707fa5bf7c
candidate-493052f00f0126446cfa70d59e1c1e83cbc8f70ad4f869c99cdc30c8aa353de9
candidate-ae6ded01bce7244596594b6304406871e675fb06afbd46255feeaba766277ae4
candidate-434b8e1df857e07cba1abf77c4361b05d1c6799f6f6ce3ec282b769bf99c1fb6
candidate-91fb0f7f091d6bca6306e9435a04c117134d10226555eaa3b4ba222749da547d
candidate-092c9eeb3231e2b45f8f62612b79c8c2f8aead735ae646b29f9fd063a0d49ceb
candidate-9e3bed8bc6a0c32fdfab69cfebf5a9018013e25278b6d217ffa5bc1e38816e1a
candidate-9e4401fbe85d3bf84ee9d451c5333a810245c15831aec19548f798d13107340b
candidate-72af8f3f0ce7c060252a129e06dfe93bdc13ab21cd681d943ee239befa7c81ab
candidate-aa93fbcaf14fcec809d654a346f3c86929c29713b3bb66572222ea9b55513cff
candidate-a13cf13ae7c087bc47569c86d7b8494134164d2f83a32d6cb2a4e014c6a7f8fe
candidate-b8592b55fd496251b026bde1b1867df452691c3b2d5564823f092fc9b6ee0bde
candidate-08fb4e51808cdb8f6083880c8650bc2dafba4e0453ea5b42d8933769be2e5240
candidate-772f989c88252ca6fed0e4e9ad8ef6bfd0760ceb76b7617c13c20aec973c0425
candidate-39e7aca5b687d06d3fe0b46e3b689d82a170595e2738488dbb6bc541491cc39d
candidate-1ade9a91178b13f779f633881b74d18a5a8d02f82bc52b3c2b8c1aaa8fbc0dce
candidate-b711331e7ddf68938b86368c3df65ea63c39b360e3df642040bad71b91f5ffd9
candidate-0c1d38b4188239d542bbb82986a217e63f3927f433e2498b9b153ff926ca8e41
candidate-d495ca791c2630c0f73e82defe83be46e569ec013f6d42dbcdeb00686f23c238
candidate-2911ab979af9034beb68425afcde86c9681efef56f0678a8d5e8af7d0a33acea
candidate-aed7ef147a57e4065b2d3fa5a053136b50680b14cbae8f05442465c7998473b3
candidate-c07b74cc4e8f889d131234b14ceddebc89d0cf964df2b3d5ef6702ba8454b2e3
candidate-a579f594c9ec88f1f20974fa3829b52700c230d71261b1f912f42938608be340
candidate-1a44ca85ac3a1169bc4e1c11c082dd78f4ad2e90e19f21d81d62b9a4278bcdda
candidate-e7c952a1cd067b56281c58beb5469382d129cea6c8e59b9b639652d81821f4be
candidate-131c50f35588f1ae31fa9ee706f19af830ebfe027c3774c8765a71033458f5c0
candidate-f812f0814583f48e760e684bbe0f39230706b77191da485f2b3f7bc9b4b0ccbc
candidate-f5981ddd7778971068d2f21436f3413a8711fb3856ac4741465508daded7bdd4
candidate-85769a3c91092d0db9d995d55ac5894208d9a786aba18288e8950f6528c179c8
candidate-472838e74a841e5b178c167cb5ea2f24f18d301f6b9fcc6302e8acb819f5eb2e
candidate-5a9264a79017a1dbba0b1b8075705cdcc4316c3e584af22b0b63056072aa1bb3
candidate-1018b2ee512c0aae160b5da76b49aa54f567c556ba1c6bc56399885e2a303961
candidate-0b73b04019b89d1d7be19564d79fc4b2ec821c8dc08134e44c718a912ab56dd9
candidate-077c3a6f90eb92b63143c2a72229c29f515f5f2033378c32f090507a177eeba1
candidate-c024388b382273e8a7859d507fe5c1a519a30ca1d3981835c0d8150acd21c73e
candidate-838d378d850dd6abeee1c7f41e4a1b513f1e3e77af992ab73ea620240ab9e3f1
candidate-4727462f6c9581ecfaa0610681a8332e48abbe68e54241edcd30e054cc7f1dc2
candidate-61a84750dc24f4c20de92f1ef8263f976a9a77ab57b677aa123845b3e406e3e1
candidate-be772e749db2ac58da18813903b7fd3ce3e81490de5fcea9b845fccafb9fab15
candidate-9d8bf43ffb6604860b37a88e2de99cc6c123b274ec7dd4499267a46a03bbb54d
candidate-3711968dbf7e0cb7e78a537c517bf195027ce7380623692d25f1cb8ee54c4730
candidate-0abd28523da87560a99a672e7f218990d16ede1138d904f50d0170a7a8f82b28
candidate-ca5c921c5b4d086dd894b583d6f467f45e65117732ea3504e3e47dfb9731b57d
candidate-3798804dff10a7ed9f5d259a1b1c3d4c230684b159deda0c7b3992c3fe675ab5
candidate-783ee12829576da8eef5372316993b0a620ea1279a089dac550394bca5b955fb
candidate-35ee4cf965951d14b9bc8f543728c6bd15b166ede1c7feb8736a23cbd779697d
candidate-cee60a48a399bcb7d7a15f810f27fe50f824e63873ac9a4dc5d12074eff0c7fe
candidate-6ad06313986dae727a2c6ab095aa9d8f5e6b8bfe6017da66e425f575bbab5bd9
candidate-a74f448b3ba6ac79861405bace52ff40e78dbdb0ceb855c8df6af8b1dee5c2a2
candidate-42cd6fe545d70b387d5a6dc6feeb1f8fdce4c156fd82efe9b83c017344225fa4
candidate-862fd63d5e39b592748d5972031749ebbc0424aa4b6d1abb3a6f8b5ef28f322e
candidate-ea4a6571274c66038149203a9860377a78d7e9a0201346af4ba35fb48febd92c
candidate-13ec95f8dede3570f4b4adcd9784e298f249ea3a45cf55459d6770ac1b49111a
candidate-56370254e7e3b4df16b0683f2ff7a5349fe6c262ac37ca5421c33391723c3142
candidate-e51b8fef4c125725f5ffb7dd2d3acd8ba48ed9c6832768a30c657c0ea93ef80b
candidate-bcf4fdb39ca2fb0eab2ca788bc2ee55001188c2134e9e63ae5a32fd56fcf671f
candidate-62b0cf256a16e72e5714ec355dc4b4dcfd525638ce8f755826180f2bb8e8b842
candidate-5be0986d58c5e642e44250560ba53fd5663807fb49126879ade0fbcd610e98ae
candidate-13f75cd4bc99d83c50165618284ba50f154bfcbad15861f225f76812ea64a64d
candidate-89dd53d97777e5a5dfa8d8becb3c6dc742334bb3dfd30881e9171ba60c37c1ac
candidate-b707e456957606ce3f0c6cce2227c7ae7720d8d59f487b2c122890a44911fec3
candidate-58f7c97a5731f0b3db1f9db4e67a5a6f5fd6d4ebd4c0f421d2e8b4947c9d4d5d
candidate-9753aebe57eaaf74c6505fec7faf4b0f0824de995d6d24faea6efe30b87f0d02
candidate-8959b269a9d6cb10d179a217fd601c236e622b5b0c9c8c6f37fc29c11588efbe
candidate-b7d1b7364f18a2d1471a167360922f9234356490881faf214d6b8a26896d86d5
candidate-b0a810faea714c57d1b3f1d283d6b48e9798cd86348b2c57ab9b3952f4e8d648
candidate-d37c743cbb1c344ac0f810e271a2c7febddc3f2ba3e16d304edbafdfa7227c6c
candidate-c6e8fc71de7e726e3b86f9a3507ba79a605921326c7a6b7326c4263ef76bf956
candidate-31dfb741c0eea299346b17156411ba6d11b42c81a248780aa271de33255dc5ae
candidate-f810ea3becd2c25c6522744532c53b0d59ab0bce3b470668b07c8511a6e63979
candidate-6c0be08125da3e239757acc90864d9e8e3091ee55662739654c3be418cd50048
candidate-ffb8deaadbad3b589fdbcadf9b30733c2e301b1f2260204b0247c300466e8918
candidate-c45fa98cb7951e5a5db3099c80e7060b96fbde998d82facc9d87ebc41fadb62c
candidate-5e676a9aeb982b6fd1827776d8df81fdde90d9408d7739addb52592983a63586
candidate-e20e3ad3d1fc284a5f37bbbd7aeb283de7def6e44fd64e5280c92de23e33bbd8
candidate-2d61f382b55e4c08581126b7939e8b02a42c4bc2b51b134172cd998ad2641460
candidate-a383693cf7cb324a1cb4027d057ab09147cbd07bd296e8af10b769f86c27b2ed
candidate-bb46dfe1a769808dfee1006c3ec97425ea2b9fdfc54f15bde434c379b0911d06
candidate-04fce87bbbd2a0a622d8526a46fd6b82ed19bf72dea4c19923ea7c7a7940cf8f
candidate-8aa9b39d6cde18774747d8853b39f7a90734b88881172cea9c8d3292404b5808
candidate-2063c5ab4ae5c49d07683abfc0a29b60a2ea16cacc36e10a8e055d2955c86c71
candidate-b1b1606167a18a046df09de83b597cd429070692d2443da3ffd7786229faa8b4
candidate-2f932f7fcfb100c824de4d6e58e062d502542d0de83b4130a6260c09d2173548
candidate-5c4dbb32cc63a4262e1a272c7ac78955b5e3dbc70aaa092d747c9001d6ec0f25
candidate-027fa953919e2d0cea28cb19b94e3ec3e669370586310b1eda47471ff588400c
candidate-02609ff5f9e42efb5b51a883d32a2f013e75157844e03d70cb38040ad2db8590
candidate-5ea93769a48a7eb983a59710a0ac4c33023f246e5e069bdabb04a78b666e71d9
candidate-9abe91b8359a7e91478e732f0c8cdd9541f8ef2991487500e9380b8123bf5bd7
candidate-7d86a3c4b401fd86d23bed7100db680ac507d30a38e3e55782158a532ffcf18c
candidate-8e69a4e8b0f52718a81a77161373b6462244f3e92164da74024b16153031b59d
candidate-7c37510f538ee6171d6c77af72a2599b1cf15d5b89ab6837a92026e6da99c6cb
candidate-4532af9f5d89b362bf78f3b3d6d8b1de0cb2efc2d83fabbdef4ebc6b1b0ec398
candidate-77f867d9868eb58248cfc3f25ddac9988f8cb47b90f6f70e8fff6f3445286fbc
candidate-391e432d2f65900a1a8883dd2fbc242b23bc40a7ec8335b7442d13a2d7022040
candidate-4a870c575a61d42546221408f9646ab30996f71261544f4b9447ffc5777aab1c
candidate-345dbc811f2568cc13f7b027c7e7763539c667a25228900441d414b1ba889e53
candidate-8eb7b5fb59487d4ed490136aae49ef8f0379602a8da0cf81a8089b8c8178bf5b
candidate-481ad4987d19f9ce28e2ada53894eca2c978d8f1d56adcf666f9fde58601cac6
candidate-5ac1bef1d66055f1c2059c0f5ba230a6a4dd4d491a5577d3620dab5efa74203e
candidate-30b2f177419ef796d1d171cc800fb6212efbd5baf5e4e2a1f72b11bc69e208f2
candidate-9ee3014105b407a364cb4107db5145db83dff37229c6a3359582d6d10d8f9441
candidate-4bf7753fe58d6f05678b74ea1a959a93e0b75fe2d8b909082fee96639ee56ca1
candidate-2b64f8a431320fc70069da4688f8ee0d6dd821cd89550042da5d63fd0ca8ab2d
candidate-2f369eca27a867e3841b1da2caa05365316dfd4d32c2d238eb3292599996780b
candidate-a527e7b2b52b1f2a670a59dfd5a111576a89259b106c44ea8084fadbb4ae65df
candidate-688fe1c716c67b629edf1e5b41f6349c51c8c1f90aef140861962f87aa36f629
candidate-bf2db9ccee32e3efdf782ccc6f6a4bc83a3a9ce9d97b903cd5942a1119522d10
candidate-1229b4623a37cfd3ca569b045e60deb6043bd903884de7202f98ebb4f20c6824
candidate-a9611cfaf4ec39778e31fd07dd601a57cf802fb6ae7e0ea94ac315649d009756
candidate-a3fbd0b0dfc5479dd05930ff734c589a4b98cf65f5108c3b0092604435f28568
candidate-3d9d9dcdd06d96ea3a6d27dc1e1ff0f5a8ff1bb8e28b1e915df63cc3b6a59818
candidate-024754c6f65e6e8940c39a557ec28c315f8498e45c9f04e8cc1f0ed64ec0d032
candidate-480951abefdb0b606545311324d13d7e17e6e5bae676bd0a863371ea9ddae04d
candidate-42942db1569f7c63672c4e81a29a62d0be33c5350340da090cad327b95c6f503
candidate-af19585b006e4984a2bc16e5007503c79087e4a2a07b2373e39e545e17bce25b
candidate-e7006c4aa529ee9eb39b5a04d0038b3498c7b69b4a6baaefcbde41086d233519
candidate-0edb4768c9139d72b55a389d3709f3aea98f64757d5f627da813356d70503a59
candidate-f6016ebec8e25b0cd375d486ef6fc1498a78f51a5dda0cf45c0df8364dcab4fb
candidate-60476bbd7f846d054a5f951ccc4ed386d5c2b30e2a56f4218bdcaceed5817c9d
candidate-553c1b044d7b352f574f3d6062248500a05a41686a22b943c1b02612b32a5edd
candidate-9cb4c2514f4c5c9491aac5f803da2834db219dd43b1a7cf4db69a5df38e4e837
candidate-da690b64dc1008e175947b15d1c8a56c3d6aed4b5796b10acf016cf5601c836f
candidate-9d7840eca47004781e900a4ad049e8f6fd78dd0ba5795be1dc212b03f5800c43
candidate-9342dba39135454a3489525a36b576adc348db25a0866dc0297273743b64764a
candidate-cd56f61f8a092512d49611109ad2bca4b968751e33ea7d9a04d424a06fa46f79
candidate-62a605aa4e74af22a1c20626c836c882679e69ee0711b2212d56e561957508e2
candidate-1eb7003515bb01906961cf7b8e3ccb17e504409465fcda15cb64dfc36feffaa6
candidate-85daa4309c9734aa569f210546fd46aa10cdcff8d21875ecbe5f3ee59b5f290f
candidate-28ec4a4987735f7e67dd4d69ac40f8879d13bd6f69aec93cefc4de35f2e2e5c8
candidate-50c506cbe49c66687ddf79a3c09b06bb49f2383f823bd76e6c644d7a8e2d3a4b
candidate-2012a8d5e4a540295f56aa9961fd3364e94d55f6ed0db3ce6e6a06eb19fdbc9c
candidate-b66d6ba89c4040143c2961be5de03978ff55984198370572b722f6863eba8415
candidate-2a08bd2f481247d690c694b56e87bb951f72aebb82ce08db3a825ecb52333806
candidate-b39a3d60d1f21afa3c20ab64b94d55029ce758d319950ce301f82fd6c3d48ec4
candidate-455d1c85a3cd31cfbc925986b3c8eedf3486ccdcfd473ecd224ce7626f6415ef
candidate-a476f1c8b11433e83c06e8afeadda7e2281f120f79a5cf713abb3884fae5c4da
candidate-ea27cf3fd9e392119d3bcede8ef2ddf57a2a0c65d4d494b208e72923dd287282
candidate-a47a667c30224dec080fb97bcbd97ff43a220d65139cdd7ecefb8363cb0f6042
candidate-91b54f7134ef8b901c863a197e5de88a7d6cf8cc1f32bb07ed16b4f926ee54bb
candidate-05a31f32687b057cc7f6673c019646388d3dd783fa0eafbc98c8dd8a95996022
candidate-e73d9e5110eb2a952ff2fe79fb2f12e44fc019437e531801cdbcabfef3ffa90b
candidate-522055a4ea278fd53a8092e5e1b0bf078d4aaac6b5898152251043d83be70458
candidate-35fc4b3e4a4a48ee85308d4dcef9cf46eb03a2be62e0034de7205f78578a423f
candidate-2168fe095ae1934093059e54b60f9fdeceaf9eb0e3c4e853cf462b6ad505c123
candidate-a80904fcd20fb9724387dfb65e94cf9eae70daabddcf7d50a791e4e0f976f526
candidate-38966d33b084c8bb255b7102ef24e316503cbc3ea735b5ca96693f4cd547e1ef
candidate-3f9a4f6d660db92bb1d7cf11c7b0a35fcabde5b47d190d77368e3a6be35c1a92
candidate-ec4fa5e4168bfc17b067aa7dd2a02151ce41a4ecae491ca270a105f85ba00af4
candidate-9b716deb18b5fb3ea34301ba3ee2a49c717726b17c4c4735b9ce84fd9a9cbcba
candidate-a920519f3bcbdca373d1f35cadcab77fc221cf2ce9cd167a381e55eb4d82680c
candidate-8d4d452c662d7e4d401849f6223bf0216952cbf848892ed005d70da2c0491014
candidate-3c90799a399f66c3de3d838c1498ea7719a96075458718f8c783cbc7e3d83923
candidate-9db55204952f3c82347d2d5b79ed4f904ec6655470e1742fbcfb1a82ed81ec5e
candidate-150f8882758b0e400bb36c6020966fafe0138cefc8b477509cf505db76de3c73
candidate-cf40305682381851f4f14c074208b6a4ea11cddb30f0690d2d088e7bc2573073
candidate-1da61066900e0219c6f7d0971754563827500a598ed50cf5872ca3eebe91a2e3
candidate-bb01818e8e6c3205e1483f5f50ce945634ee9c80c81b4d15288f3fdc6f82d17d
candidate-4f9accbfeaf458c7715840f754dd2304bbbc2f6564b0e89f008bf7d969ae2383
candidate-d0ddc7e740725006473a2cc84049107b34a25e4de870828ff13ee70841733a3b
candidate-c33b1b4fbeb2b82b853818b64391f712efb0b73ee8030e9211e9e197545ecfd4
candidate-bf16e2a5795083f1ec5c1ec8706034fb065ec22d8f4f70192ed5067f60b3b0a5
candidate-61c8711e7f60a1f8f267c0f52091066da9530bebb9cb918c57ef4ba0e9d1b7ec
candidate-c9f388fc952c682370aae37ee43ed72a0a27d5207e98f9e99bbeb283c0614908
candidate-f1b58ea845bb666bf3deaabf9f7b2cba108bb93f432dd80cc7a2523967cdeefd
candidate-6e3b5ffac02c7969226b19d263ee8ea0876acd0dd7b623203faed6ab3bb6ca53
candidate-321b8a463de34e68c85105672ca0fd9257169de1819694d8995d5e4c7fa98304
candidate-b5981bb39228523e872f6da664d02780d20511957c24f3ebd5fa5960756e5fdf
candidate-f6df846880dc8b41d8ad4f6887062fcc94f5799b96418ee66f9a876c02a46fb9
candidate-138ce6d902c799e738fe146947cdadc317f05d697fcf948f98a16e4218d990f9
candidate-0f8b49d4adc494df0de5d7508b9935c3e1066354608cc74e12704e3a46132684
candidate-3511aa903729159d32a79b53a244d91f42b00c43119755d332a2833a45dc8f29
candidate-5275fd60437c5ee4d294186f0f10cbaea437547cd68a9fa2f7b5f200c88c2cb5
candidate-9cf8fface6a5d76fc088b5489f1471372fc5daa8c0503d990ca66aa3855f9ce0
candidate-3f07b16a76706258cbc426e7a3650afadbf6c3e0188f7afc1a04734a50ca4a89
candidate-071b54b39f6880c40f75bf199b95450a14d08e2f46379a2ad9b6505dbe8c7ff7
candidate-f78b823ea8d64bfae631726578a10711e56c0d19d7b6738a1dd8b2c9ffd34267
candidate-d0f6da315ba25252cb82861bd59b6cc60a6640ac607d66f1e07c82f079517711
candidate-086d78ffcf95229810119d04fbe758d8565c3f7d030820dbe71290fa462952b9
candidate-3e0b745cd9d3be0b5d590cdfa70b76bb952b85218a7b20bb7fda1fc9e80f814a
candidate-3afb17de0200b6007a5aa4b0a0a73942c8edeed029d1c23ac7bfd6560c34db57
candidate-07c8f31e691a025dc999b0af81dccc5b04bec9f813c4fa365f9a8af42e1be979
candidate-a00a81d38718ba16d36da9960dc0f303febdbd20a1cc2e69e0ee7605fdaea0e1
candidate-8bb19f0fc695616d9fc99bdb4dbf369826cabad9633d149d716f0effa116d28b
candidate-cdacc1d2039147c2b9f1ec7325067c2fa8e216cde17f86b9129268c21964f574
candidate-6191fa6cb2b35b0130ca1d187a13876eb08a92abc279516b2d1b49553aa914eb
candidate-566d6a93b61ae65e52f44a476f09d41af3c14fa8ca6e48f0cccd343fae69c0c6
candidate-dfb9e1c8c1b88f0722fa2adc8c8e865cd710a39d85e837f287c3bbe81a915d03
candidate-8242706bbba8f9bdab4ce62e3d12488dc8daabcffcbe004ef4d8dd63092f52cd
candidate-d091a62e76c66b7cf8e2eca3aa65fc1d0922a06c0ac46cf170210c9bd38550ca
candidate-67b29a4837b4b1504e144bbcbd2f19772fefe265c35ab93f91ee5fd19c3af11a
candidate-f52b7ab472344c3f12057650a0a9efac75a710200707c60571af7a9f7f46f755
candidate-6a11e07a59d89db9e07a4a826b6518ba9617438a4f226b443fb0062b0147eb8d
candidate-96bb476de71ba55d33042265c6fb4a4c01f7378d6849aa99d5c68e1951cba59a
candidate-5df337522227418e7f8bc8e0c6ddfd7aee2dcf998b69d7a1430258cf7aaa7ab8
candidate-1e91b28e492cbbe9930ccbc7751f807c3d6094b0266973e35077512cab443660
candidate-3b114cb70fa2729ef5a48723978278c478f6f8882c51e0df15276edeb8577545
candidate-3fe4819d908b1216d69ef83fab15a040da70fe5bdc9afd6ef7a1fc89bb0f41a4
candidate-4f66972434a886a4ee17143f8cdb12643432716499bbf8a8bf4e691514f0a24f
candidate-8aa2e85f92c7c904f38ec1c5cb9a2c285a7ad3d629859da237b54386462ea703
candidate-442743443b1884a0b8be1af27e07e4e72067ff4b169bd18b3ae19beff8d78dbb
candidate-0fad760239a2cbb5d88adca3922dd26aee3dbd5af049c3f568def07e8966a7c9
candidate-07d4b346035ce2de4bb39e58b3927f5da418da68d6a116df612fb9c1f9a7ad81
candidate-7977936feac536d4e34e78b7cedc6ea904732c9beaafde7dc2b848afc2808b81
candidate-b3a0d97dc2da2bb46ea0b59226dbcdb623e8497b08ddad7b7d698bd224b79ed3
candidate-05623c684f8d4d6dee4f912176bb75979ca855b7c10e1f83b748542589fa016b
candidate-b8b0c05f597c533655325310450b8115506aa78cbba7b1f3b053200ade982d26
candidate-b47e65813582a3f47de08c146cec7bb6fdb89befdaafb324a2a592ffd311dcc1
candidate-f447c2ad5ecead8fe536a4004b22bbd2222c1ef7cfaf3c55dadc538ddf610d82
candidate-fa7aa78a5dd73cfe7c398ee9af0cf8730b4c433ab072df5432a9d8cade3ca7f4
candidate-9af9978344f8a962fa456d6dc119e2bdf0823461dc027d7a1a87066a60c00b30
candidate-bc7d753f7ffcf5ed8220024585db51778eeba8c22468dc085544789ec93f9442
candidate-ed4e20330ebfbc9a9b99c68a82adfb1ab48e8dda9dc11465e6ecb3058025c8de
candidate-84549987fa6222c066b1a36e4fbe5b8616e9101179c3b622170c05d44154e736
candidate-8efc6e6870272adf292c5670f6c4ea22e1bc5c845bf90b2385a5b1ca278d7573
candidate-84d42d05079d11788604caf1cc3855df90b07131940314c180a381e3d494c9fb
candidate-9936f45cf3f8e819dc9d2af2dcc15e96bfb9ae11e899798f4f23c49839f141c8
candidate-0581a9c55692c8fb9d860d35641d0b06cee3e78ae4920a12cc692492621b7e56
candidate-999591c49c8ba11d19127c3554967b17b9beeef0b3cd2d6c3d18b384d0597257
candidate-280fa4af546ed00083a2dc69afaccdc45312df375f231b368c27284d99a28ae8
candidate-1d9e9e5d8d3eda7c8e5766a693c1695f1c4b90aa0a1e753476f80fd877431ccd
candidate-30f025afb1d02028d07ebebbb9564d675da08371c47934559c1cd21e9a139b5a
candidate-1aea6069881376d2412e005bcb459853f9a578658b349987ab8ed595d4e0ba79
candidate-50d721c656d4a9c17aab02c767c39be9f8663521a5813b1282205ad569f5a0fc
candidate-06406c83fc3c98d606038be72948cc51414b4d70c49d1f1e8b8df18ca5ff9cf8
candidate-c13bc224eba0a2fafd554904f7cd9b1ee56923587c856d5578a066c84664e51f
candidate-440098c07bd290de7a09e749c6cbf81bfdaf66ee29bd255b0ba36e3889d818fb
candidate-4ee2f025f820f8fb6f4efb34b2d9b8c9bdaf41ca6b856593aa2d6f889f6324b7
candidate-9b1c2762dc2bc71d7d97da41cb4fda7e45e9b557aaebe60fb1a80c34518439ac
candidate-d70b3876d87804459290f42d85a659623061210ef1de919a939bdaf7fa99e8d9
candidate-b8b6ca9ab767b0078cb32af1855430d01075f7f9113f86bcd53f9d1832e967ec
candidate-8f85f5765eed95cbefd8a4cafd9558fcf8a693d7a65c9cc032b903a4153a358f
candidate-2e693b1f92f3ebb330be24607b6b3cfcc6e35ebecb2e0751ad1fb4fafdb58f72
candidate-5860aa3112c8a4c4dd5badbbb402c4a2082207ae5869a4c0795f12ae1c476bd8
candidate-1a85aed2628d76119b28537b7badd799bfe2bbff7e3e70886790b17ade411c19
candidate-18c27b4d6be25af620d9fca4b813cb6b475cc21330650e0f453295595f6ccddf
candidate-f05fb9dd7d16eb942702d8afdd86a3d50becd8931f4b6234c10ed2825dd5641c
candidate-72c5632d37abfe3f9de03595d47e282c8bd403150f384c9f794feb4bf3554ef6
candidate-8b16abad046fa74f93be97106e5aca144ef55af4f1f3e564ef7fbe2ed31a5dce
candidate-ff0cc85a9515396af93b4a854d8742348df36fea203fe213e6961e91091cb020
candidate-f202851898e99cf3e5795946fa6fb2221a391deb2b28359859aae43beb43065e
candidate-ad484768bde40f25093f2ae105f908d4ac9f2aae0c235a543330d99f3bf4b286
candidate-f7c746af671cdf7e4e94aa8ea98e27f88daa97fd9d17b24371fda9fe83400692
candidate-e3abee2dc89d0c54fdc8cc0a27e2718cfafe8782112a98c2453aaa35f3e6c869
candidate-0bb8bae397349f5dbb7263d1786e3702901326b681ea77e6152136b374ea4dc7
candidate-7c27e5f70beb16e4b7a4b3a38e0ae56d6d5240d3f01d12fd5062255ad16a2193
candidate-f43ff769dd21832a4c29776bcea536285a1b7b873f5159c7f6a00b2d71a8173a
candidate-cb1964f853c5a71c650f56d3c06add100576a42429b07ce00a176d9b2ee009d2
candidate-e175861ba937b6bd8302c44112be01ea59dd2910434afa8b500fdf6045fb44a4
candidate-778479fb9518efbc7d75a1643e4b120477ef05ae0b15369cf09babaa1f302a6e
candidate-342b3aba4c03493cd43030308ed2f3237b20313a4a864099d625163e3d9afada
candidate-4eb70b950af175c8724b74c4c76743f6b6b44b59dcfff3e044d856a093d0df15
candidate-f4057072251b36215951801b8557a9f7dfc725a978bcaa6c24fb25f3d1f2ac84
candidate-17727163d4b2105b41b416bfd11a08efc875c06b4451cace9fabde667c6c7165
candidate-9c883c17a498b602e2bdf213fe5042cf42cd27be1ccc1d94ef3bb3092cfbb53f
candidate-e1f63eb1fea56e264e637772ea29d6e7668e9d926520faae664f22abb4d8566c
candidate-18d81b04784a41da652effad07cb1b201071a3c124104fc9b72f40ba2d986e70
candidate-48a1faadb2917848917a0b8ce46612d8286e7fa20042dd5907d67bbca31d1425
candidate-e588540ea009abb3f307c6faa6cc26d9d7485738019eeef2525df2aa1d755d25
candidate-881ec45f4c09f1e17ec1ef4e9e979e978e3be5b9506437ddc45939907d733152
candidate-0d9c0cededd8725bb11397c4598c7658691d17d4d6d8891273415194c8d75c3c
candidate-62dd587073268d6c2d1d73e0eb7f5a5e397f780149f5726a32032f5b069bea66
candidate-f48f3072e490f0794cff581ad3d09718f2a7d01260c7863c7ce4ca8ce714e21d
candidate-05068ebe63331b70100eefac4f476a73165b58fed13c7175e7e9f925b875af61
candidate-ef84fdb8d77921b7906260a804bfe9955a0a8a58d5a24a5cef48d96c5aed946d
candidate-d47cedbc3945fc74eeaa7669832d4cbf4bd6b4e564cc696c1849b8c5bd1014d0
candidate-11810f33e8ad8a2d442fc73fd18bb25398cd3de3a531a341dc98b9a40e5446bb
candidate-0e408fa85fe480ec9b5abcfdd05a647d31ba1c5bdd9ce5ed1ead6229661d61e4
candidate-40bf4bd8da9270a050b5540301839cf0283ad4d4e39271d6b09ff116bb511d45
candidate-0c71df0e77a11e180f78c907299790b7f73112672ba05984b866cd4ab3c68042
candidate-ecd77961e775e4216314b35b739ea75d1ef5730bd0e570a1ed485562106feb37
candidate-16708535db659038594f746a5b4532c2643627990e9b2b70866800ce2e870ab7
candidate-e7c0aa0ead5e94a6ee2ab5c9740c211ed8cf4c5dea01e402f7bb314b39ace4a3
candidate-ff0e51d7e179739592ca720144531fbe9c9a33c485324690b2570dbaf5bed6c1
candidate-1269240c2155c46b9523016cc806d696e9cfa607701a3507dc75169a31541ddd
candidate-8420477429203dfdadf6e390399d3b8335c00eaa633f28ce6f03eeb5d8b6e301
candidate-b025e605d14d1f4cd629c7153ae94ff2a135edfc05c2dc029fe5e950151b4a56
candidate-a471287cfef2f6a49007ef3bfaba236a394f215af47379925d080f4fc8ee1dc6
candidate-18d4fad0f15c4ce6e4b743719aaf3e3366f20432895313ccbef2f571728ff376
candidate-7aa7160f53e2ee91eddcf0e31a9514eb0b79cdac7a36508a61b32c19239576ee
candidate-a8e1cba3918cfe17ca977b90f7b80a292a564e133d056f444472058a6955be64
candidate-f9fd87e91f72961bcc9e53389054ff4a4851b3e36410223637f2e35355f7a10b
candidate-000425778650f898a1fa5c72676cd1dc1033a716693a1c59a8d7cf5536e81b51
candidate-8ddbe29c3ae7fe5f8f42552bbf2e9ba97997776e042ddaf372bae7326b94c599
candidate-bf7a90981384b528d1ae9d4e4ebc6c84eba6e1c635162ba8480aa58d64f7a30e
candidate-9dc597d3af292cc324c998dcaf92e8fe85b52fbf0f37ee78a01f1c0f83fbb199
candidate-dd4f275ad700b2d3447d15929dd62f5d1ad6fab67ff92dde2f4121aa9b86a09e
candidate-30e0cf2e380bb58b3e0ae26ed49768904a96fda01c4cf9f985cfa56831189934
candidate-cd8280ae168fdabf9f103b90ab974bd004b77fb08a996c6894a60bc7c8e816fe
candidate-7cbe0db83d94548a882c7cb8e02596a849b8e1feb9cb274fe794859b006bf210
candidate-729e63df51fd5b98637e8fe9561ed1ef5486ac5d98d822965d403c12f0a16a49
candidate-97e28070943919d2582bccaed60c3fef3f0c90686b4a6e2b8088834562984176
candidate-bc56515f50f909ed430b6473c5459c061b6fdb1650bdacd3c10254e9128fc136
candidate-67be81d8582a23e45169a0bd473e3a8cea023661027f2337192a2dfacc3ecc60
candidate-8a1c9cc8b865bc8a9cb83b05f2be8e19d465bb31e4e5422c6b1f5d0554235946
candidate-244d6e1f195e15968b2efade1c93e5be0c9acaf8a4831353222621c77d0005f4
candidate-66eea25206a85775246f846ce11b8cee0a1cf328998ddcd80d5e759a7733e312
candidate-0ff459659230d28f9630ebf3cf831002717a028301c6623001ca754479efacc8
candidate-fc5db1fc6ac1ef6709dfe7913cc18066ac614ee939fa905091bd3ad2f8d5b093
candidate-bac8827f1aafcf476bda034412c0bbc3ea0092933d9eff0e78b04b8160a6da33
candidate-9d84dd283c096dedf7c421cef51273d895ca26a9acd5dcd760b770444c1e88b7
candidate-25b7846951c6426483201bdcbd1b2f584fbb7c712c8b3940e997c129a5a34646
candidate-eef2730e061915b3dfd8bd432f50326d21d19baa897bae5839343d1bece9d32b
candidate-bf4df6afc5c539068a6d85fb3f675bcdde754ec4910027ee77a73df07160a72a
candidate-874112bfb1d7e41f42ca3591adcc26043ff50379f7c5e3ed7c98c9e1db497d59
candidate-ddb86ecc3540c3fa914a697cc9a84501520b6b64b4f88b9ac5baee62daa1c305
candidate-e2c6fbf1a365b43bee1a75d2b606302e1fc80dea003bc5cbfd7d10b2505a424c
candidate-94ed9bbf69976d3a7a2a6a4add2d5d27d75270ef5224de8781a14d65d084accc
candidate-e8ef46eae0f4422791fa4a3121bc5be14a78d825e5d36dfcbc8d76d6192156cf
candidate-f57cf69708ebca9aadb11986fd700f6db1453c7ada2e1b5892e8e624ebdc3684
candidate-a6977e7bead56699aa4bf29c6e538e17cbfa960bf4be902329f6b362e6099525
candidate-4d77820244f6ec263ff4f773bc6456746339e80db508166b1e2fb0e60d6070c3
candidate-76f7302ca94e3da7ba2b4114090fcf19b2c4479056878122d56dc2dcc1fefefa
candidate-23905756bbcc0a78bc1d7daf33fdc1a3acf6633b2e6683d4107b7b3b3eb2eefc
candidate-d511f227df9a9e00202f9b14f9ac2302ab3c944d9d6e404a606285b5a5a7fc63
candidate-e62abb4dd5dd0456a2282b2f8fc5420e93d6019b19adc8fbb0155f6c0a5c5cd0
candidate-9c285af63c620e69812b4a2d2381f02c7b946770887c8fdff9e6b52a699a5a70
candidate-2888774d8d1bc0495200d4d37ad1322d50514287aa49ef52d24aa0b182ac8adf
candidate-1e97915fd369eb86b4298acf61582af6a34373a957a1094093f486df79f3e144
candidate-301b49d5fda6ccd55d7c59898f83306ae6ddf07ed8a31aea893a18cf5ec130f0
candidate-e7a83d16acce41de7fcf74bef61418c79fde0c531c803861d515d17d916d58ee
candidate-983000d6fa33228f1834e7ac816979940cd6c06971320c41633244c72eef45d3
candidate-ab830996085868e5749353b42456a0075f4b2040245d9ef97474a46702ac74c0
candidate-a37451680b196d4b772b7c9f80c51ff57c8dd4be95ebf81c417fdf0dfd847b99
candidate-e20d368ef665b8b74c4b716defe2d20ba22e271507ad532c2f3681b5d87cb91a
candidate-93213e12ec936d663d356c6ee0309755f7b57322c499f880a7b8b1ce8824753d
candidate-f5d635597dd903e89abb71542e1c140ff55d582f8df0fbc782efae6093b451f6
candidate-f149571f78aba26d12ad411ee7520fc7a5a0a6b5826ef497edfdf1de4a6b0609
candidate-3bc8b6bf3faf1d788aa0263c6ced1b649175a8b49c130c93398dfca130d1c18e
candidate-3f90ba4896b78a95ebc4bc7c76ad564d939550011a949b30def22fbad1a6a2d9
candidate-0a603b2c1a7d40623184c53857c83ff71d18f7f7922edf143a495b5c7e88c437
candidate-5df3f56e0d290c02e823ecdf673331c8d1482402cba3c0a3c5805884c39ff054
candidate-6cf796cf0b2b6f1fbe0cb98c73e6221b7e1f171a189675e340fd24d170cae03f
candidate-27f4407315a2fc1cfd65f4d24a7b67e8f2bb84f255f605330fb706a359b668a3
candidate-482d8706b2f43a75b0fa758cfcf11fc357ddc8f19880b677d25d61f18e309ce1
candidate-399b0bcdc1fe2df0eddb9e47c8dd2daaef7aeb15c217d8ab790c9e2bef11198b
candidate-dfd747417a446f292b00637e871d460ed04782c8a26ca4845a699cf8b46420b6
candidate-1e24b9089a2f3b9d76cba962ca60fdbfbe12ac9d3f38d0a1e7c6d7e1c1f51376
candidate-6580d82021c0eb49159090cf5c0ced69eddcb994d65285c61b07fb70f4fef588
candidate-27c47ecbcf8279719771aead7b2e8fba62cd4032226de0bfce6538094adf456f
candidate-4343404cf985791991274516d5ed36ffeca5e6805d2d1da21ca492eed12d7d8b
candidate-99c8f9b06cc213c517c87b8f0a5acddf600ebd40cf745faec198c2cbd721cec9
candidate-768c94f1dcca0bb15d466a9bcdef3191b9179e028db60010c8e0807cc989ca6c
candidate-b5a305d8e497b6073c83f524bc5152579c87bae1334447523a28df7ea15c4579
candidate-33641f99344804e9825120cfcbf1fc364c16d45c1ce1d1c606c3cd1bfdebc7ea
candidate-1b7f04dd09f4b057d05e5e9b3f7942a1ceda2d394e6d60a827d99c2479b18565
candidate-4f3c492a0fd1e86d93c684be7c7db2281fbebee6387948e74eb2eab227164f47
candidate-849c4a55be811decd803cf58da22a102a25c9caceeaf0d04b4cd1890d1933d7b
candidate-7ff995f51c8a8a53a74c6f24a716e58ee5c23ba3f4ce67a1538fe406dfe52582
candidate-f7938da15a3d058a4dea003e62e0c5978d7130f5cd7e1d51c88086fd6cbc63a9
candidate-ba296c89ad1188fb56ebbf4ce765ab04ae97a9bb9b0b9c2e2199363662d75371
candidate-8fc513fe46bf58a7a8fa2b7d86409402c90a815348b398e78ada474b9fa2921f
candidate-4a3e719bc353aa7fea984e99ab77a568f54576432aad9f3f09863ed7ee60a451
candidate-7f819742c2a30b14fc280931ffedadcda527df237d0da7e48321cc940c3e042a
candidate-fc2af23c197d7e2e4872788c13990fdc40e94cda96dea84b02a39a02ad1cf1c7
candidate-0d9ea1788ea1fe50b4360a245a82ef4e0b3da67bfe5172f06d81911572654844
candidate-5fa50a28289a8361e6b20cca9e8dd2cc9677d407027accef0beb91ca2fdad39d
candidate-1cbb55082d6550903df5d77df123b6f8e27ff61bc1761228b352b2a693499da3
candidate-646bf9b74faed84e8b68b226d8e66812be4d6d668720874bdf936831046bdd5f
candidate-f8cc25986783456cde3345920de2c8d8893694326b841c80b9099f0cd07a4636
candidate-daac268501bc34504fc688ee3788bd45b5c1310c32ba87278534ed49a228cb83
candidate-9b07b02d745e07deb8b51a1048a31c160e31ef11dfc16faeec1919edc6ce2851
candidate-079df20d957dcda099d6555d135b9944b7ac8bdec0d8f69d52d5f52dbe24f478
candidate-072b116c50c35f7898dd51fabbeafdef985d85365d5c7f8fc90e44161b6c9f43
</pre>
</details>

<details>
<summary><code>derived_quantity</code> (287 candidates)</summary>

<pre>
candidate-37c6ddcc56b62e39533b502432d0fd37bd0c5637b9ec988bdcd91b85d2b73126
candidate-d7d1331d2e7a83ecfe4d2e56f4228438d6f82718c7dd4dddbe4f5a6ff3fdb6d1
candidate-a1f1a5d2d80f63397d4d9ee26d4c7bff910670b5270b87dd0357a4a9e0f8792c
candidate-58b2462e858626469e98e649c2b20e72c9e4a0fde545e2e3ecc9c4b174fc9296
candidate-e0388f4ff3f2c1e2d5a0fc5a2945b7e40c972eed41ec21a9c5803d4e478de100
candidate-bd1e6c9f4fb5bd843a8776f1c2b77d9552d0e68ab88980a736c0295db0831567
candidate-c4117cbd0fbb98a73d52f579fb4dac33952f47114b8f89944c5bd17c529b95a6
candidate-2f9230a9a04436a9e8eead460d106f4cac69853cbb8615d952e3c52f1e3f08b6
candidate-7a994cff38525caed8462edb379a4d066ee2e3ec7e34c4378d72ffee1cfd0d8a
candidate-cc4132a0a7ae8f0a9219caea20e321ac2d6d30d42016e8295f84464085142a01
candidate-ea11ed3973504c4191b5d94693045c6ead825ffadb21185aca5397768da006d7
candidate-e5267806408269805d34b91e6950585c9abc710693e922b53d004831add9843f
candidate-bfb80c0d26a191f40aff188120894cb893a43997f66aa3b8261e9bba8437b1f7
candidate-006ed1fab2c5bfd1e39946e1bd63b922c09ae6b6449f6719e9284fc394668ef2
candidate-158bf43a248e27f6f6cc2a8690c0aff8c89fa68200efc7847ee38e44dced85a9
candidate-c3192e62186d066aa02ec03603692335b527152b35be6547b9fbe5ea4ad6e34d
candidate-c372f37d83bda234789b97ac71c6c732e43545b88eb08bf9c177e848edaef20b
candidate-f9560d795a058d76210fb10fcb1260f5f0e5bb297cf578d1a29e675ee745da78
candidate-d16c76d5338ec71cf759a9725bb4e7ecc8477416c3b5004b68f095b4a8fc31cc
candidate-165d9f9c31e841e54cb168e4a13ddd2043d0fa502724496224a70df5ca0c4cd9
candidate-d095c087bbaae5788827f5892a3726609cd2111ab9fd2dcc9485a29b78001708
candidate-a77d428eaedea05570ee673eab047ba439cf28f65d2be318cfd8d518efb9ef0d
candidate-8edb42b6938d08060d8c0bbbdb7a8bd47d284f2ed79a8d21492e17acaef59847
candidate-cfc5cb5c57f237fb59d3ecaea2c93c3b8b9e1055db758830c57a3641a67c1d71
candidate-90df61c5f6f88ab0622304eec4aea2e26ee89d3731411889e9fd8b2f6e9d5d60
candidate-477dd31991642e4423c93f91e67891102f808aaa2af169aaafa36180defecf3e
candidate-bc33c9651799226cae2a6ef25ad894374849d5413121f2e87f0a8364cc8b4a45
candidate-bd065a5f37895894796ef8c42b4e0786c26e34fc02ba47d39f417d60c73936f3
candidate-3798d0e87554f7dae437b9f4bc9240a1dfa41295cbb212e3676af8c194d3bf97
candidate-89fab6bc7fd401acf2dc94c204f2932c169c47c925a25139a20c0e7d8bc828c9
candidate-e8d584c35e1384fc88ab57a0f955279adf4eb6b5d38433ca64ec167d2c908eaa
candidate-28747b21e6067a27f4560d1772964a4325f6affa6f52bc0afcc8aa9822ddd7fc
candidate-de6c2f4642d9a3b2f9597ed46d7b572d8bb9750ea72dd117e59bedf47891ac29
candidate-83efd720d9297327a78e5c04bc9e6907e05d9e40c65054cb06c294f552d5740f
candidate-4d32fcd91e4b13ee8d8273ab6ecb20bda9b16342ac7aa98f9d977f51738eedd4
candidate-0660096a756e5816eeaf94c455f4a2d69eaa5f2f71d455a99843c416a631384d
candidate-41e73b1a6e250646bf969827eba3b0de0a69cdaa548cf7a386868f62b7950242
candidate-7565469a6f873531236062be3f77a47e1870e8036a15c4e6e0493f3fa880c12d
candidate-e7ddff9ef2dff1623c63507709b0c6d43dee007f727b4f60cc471afa4464e091
candidate-5becef6ada0a4434492f65c25f3ab7bbb3d7ec65c29a41ff18aa18c1f56067f6
candidate-40b3470c82e3af3e5b79fc98286a4237bfd6e69c77495178ec3b60750572829f
candidate-8d16faa19c9539bf8f8630441f65b41259e8c8fa7da66b6f7679624e4b98fce6
candidate-c2d2904dd624230b24468aa1461f2cf2290e92cd87904aab28b73adb6a95c426
candidate-37c327b7fb3b380905ec4c2565098b7e52fc0c204887a302298d1820ea4dcb0b
candidate-ea9ce1f97ce30a4cbd1a8a5e0320838a7a3190f47e465dfe90760e86cceef8bd
candidate-30e1005cc9ea86bb29ce04eaeeb6633bfb80f51cc67fd9f6a6acabf0b33dbd89
candidate-3e8008311ebb6989593865882edbfd19c8310ba4fd75e9db1252bb1dae8b24f4
candidate-a755350e035d91778f1039b2422866b162adf4ac6e41c6067a9035880c431397
candidate-df09b7114cdc01087ca6dc52e111118d748fbb15df4e2c2bc39fd0f7b202a4e9
candidate-021ff0205dbc3a5c1c5621135abd9aa032e65b02879332870423c370cc5f1872
candidate-d07b30f28baa193595eb93c5e320c73ece56fd06ac704cb53b78815205741ebf
candidate-0afc3ce75560b51a5fc356c9ef0f7e67c4e7fae37040f7810b521d3c57fa255d
candidate-6dac22b9b0d813523d203ca2903a4bbf29e5569b7f4c7d03dab878b71d7a6364
candidate-d301d3c468ebb30f82976871e04606f43a0767f26552317e6a075ff16a28cd6f
candidate-114cca77d20ab0ddfdf2aa4b4024a59b159246c85e7a38eac5db1680674cfb9d
candidate-87bae96bd7146ea109ab5c28b65e46403de4bbb6a6c8a65d8300c068233f4a51
candidate-377a2ba9ba6c409179ed98fc84444126365d2b2d31452e159fd583d2e01e6911
candidate-1303582e01fbfeb627e0db7771671e9075704566534a82b4107669d86e663704
candidate-8db0644623985eb0a10ebc2f703979527468a04067d085e60729f335458a58c2
candidate-965dd43c2f7add079a811f6d969dade5fcc5d606a12a44d7eb34b39bb3ec643b
candidate-766d5ef1febed44a69bc096d65afde271a78a99654f19f61f4d8cfba4cfedebf
candidate-a4128263517279b6c53ff406db9b70e1e3bf7804cae641d46d620675d5dfa7f7
candidate-0d4af587bf680a574b9809dcd3885a82d8ca172074904d2edf2e374cf5a7967d
candidate-668ae5205a14321ab308fd15043d3ef95ca8a19af677a55f2be37b6936016949
candidate-933d63289d60b625d4757cf053adcac23aa9a5524e81a5c9492a12193991fd1c
candidate-f70b9adb90a6b1f886cdf5a998998024fe1e2b0b3a467f06b5c96e27c209df1c
candidate-dbad2d48d744ff873db50ac657023990888b6afcb7a49e3bb89a09a477778565
candidate-7e4e58296ee5ba0186f04a2c38252e570fa7bf747746d530f3d0320edc6dfd86
candidate-cfa64368f7e4e70e38d99762ce1b3b7babddf330777f78bae128345980b6f233
candidate-86b6be154f09b5ddc1e888e2c8694a4ef3e9360d2bca777442f643edc2f8b6ea
candidate-334c8bd7d4e1bfb9c54551e39b6f9a2650692389af3a592ae9c396cecab017f7
candidate-09929e3fe99c049074d127a73961e69b233adec231dc9123afb93b675f815215
candidate-0e2e4e995c886fedb67bb0cff1fdb5b25eafe6b72f4e1ba2a412e084b8d95a58
candidate-dc52a4406433b9ef918a5f894839307be8dcff7ef5707cda4ced2865f4d5082e
candidate-896dc17e48ab90f20e2376c8a6d3c011a269f8b4510674e44ff859b197f3ca8e
candidate-6db19953a0abb79f20148c0bb01c5a4d4f2c635589affcd11c55b88735837e20
candidate-cf1d839af33123509dbef62f42fa90bc51252d17d7ec310785d09f2222e54aef
candidate-428356556c03c046f51151238bcfc9d3793eed1ca9c0de34213b1b513d3441c4
candidate-bbac067813f8bdf2568bf0e7cb1601bfb0891883f16e08a7e6daa527591a2db5
candidate-f9227e41d2a5f9a4eef54c6cec30f48f89188d861613857a645a5dae6323bf66
candidate-5e98551fd2b51418f6f6b57e815d7bea7c8bd79b3d4708da662c5e66368aaca6
candidate-e523c43c8d007dbc28d0e0a08462128b967a09cb21c8ef52f4c5a9e4af53d2e5
candidate-15eaf4806dab5ebbbbb391e28cf5518c980331a217ec72ef9a55a6cbff09b868
candidate-8bce48975b18701c8e8c9388b5ff27d4403c014d6b1a661f13f360518d619208
candidate-e4f5dd9d2fb0fda9e2d2fc0b0bb9c27941933164124a8b1a9061810672382fc5
candidate-8923c32c075d7da919acaf5ef946e36017e0b2f6cbb25053608f3384136f3e99
candidate-3abfdaa22ccd015811bdb348119a9190ab9857764ad0035edd846fbe4865bb5a
candidate-26012d2bc35806a8fadd1dc8fd48321f129e9a71851cb58d809e740217c70197
candidate-d959f5ae53e5bae24e0d25c3cbe338c95ee46c2626e8589d826a51a4ae0903af
candidate-5ab2c0a8163201137208bd6a74d4355e109d31fff4d5f428db68203f5a5d2d8f
candidate-908753b2ea86c3fbadbe8bece8f59c795ec6bbc591ac42574f7aedc2f05e3515
candidate-e428773159541ee860b0be01437bf26701fc5be49c50d64439c88eb3fab062ae
candidate-25c23db1abc50948ef64af9cf5f10ea5540cfaabaccb00cc448a5c3edce84a16
candidate-151322b94506d563df2b4250f3a7671b29f1447d9b6026e2039239ca95af6794
candidate-a7b991826cd0ac418b7f71ab2dcdc76746198d308f06e43173fafc523baf7bf9
candidate-5256ad593202789561dd21d5306811c3c655982f272202175375e19170577638
candidate-a65a9bd874d0f2f7ce7ca38d4ac2ba227644315a870cbeea1f7a8152921aeefd
candidate-ea853670e1d447342d76745246fb51f1a97fd2f1a1439c287a963cd4a21a5e2f
candidate-a78fa546698459ede3df087817d5cc1c274d791befacefe66e3b9d6c9121e909
candidate-c1a1bc178a3e9c8f176c563555a064c71657b0ebffb8f8a289448d39969ae4f8
candidate-b5b1eb5dd06ef41a001d2ec4de52527f6f2e21a47276c7adb18d6fc6c8efee14
candidate-8170eed48bd2ffa82ff8b06ecd9d6ee294fe2c3a286caa80692e2717a43edae8
candidate-5af3a477e214944c14dde7cb2848b9121bb4c651403b642fe2e32c945ce0b679
candidate-121ae9c6bed80e3ed5b2fe886a339b06bb80d906abb77e39b38bdfcb16a20b27
candidate-4a468db0813e58fa00200c7e214eca9a2323db3ca5f9249f64fc0a362881145e
candidate-0ddb61948ceff9a82833c1e9198645d4d5ea3741a69ae45c1c44db87dd3cb327
candidate-eb6efaaece2f121f5991518d5a684b9963095ce1350f9ba1dc54b743e389f2a1
candidate-00b3502f85d00807a6156106e13ce599a2e79569fa5d79187df3230d1c99a65a
candidate-28051e28dd21bbd7f68d2c21d1714d62989b326803830b854af054ca2a5e7c8f
candidate-a7bdd96fa096f6cb8c0e88047f56c7e1c88f99a481b2ad425f1b3e451fa827b2
candidate-d5a0c4ed7c71168357b76e8c2c13d93cfd4241bac196310fd96090da72a4b2d6
candidate-09d6aab3c24c06a0251fa565e7c90bffbc36f7c4bcfb03e2004144a68c87ecef
candidate-bf0a63843c513f8acb06a596e3f8790fefa0ae009543aabd056ea663ae058bfb
candidate-ddf9d455569b251b0be336ca1d03eb67e0c93d75ae5d15320de579ea47d5af62
candidate-4ffb2e2fcc45e09b99734134321d4fb4105aaba17e4dfe096835497ab646deb9
candidate-37f767fafe93e82c081bb58fbc862500f2c2cfdf0db6b8c1ba7d2734d9da1005
candidate-36df339b4874574891752ee7874bd34be296af515b9cbf0961468d1a31c81bbb
candidate-5cb69d01dea5ff76fd25cc2ecdafc63c0eb92d0bc979b7dbc6718d0dac6b7149
candidate-9b68b3e08151debbf5524ea7ea35f936f2e40349ed406648877c2c3ba2680cbc
candidate-d4a30c447f7e4009136ca15d196c67bbe12a58059a440a82ba728b01f63a6550
candidate-67d182b924bcc82abee28c80cc7bbf6fcc7a439c39cc17fe8ca03b7d51bd8975
candidate-4fa06643a91b0e47ef7d927adbf9a57d358c9f81cc1dea9f0c703790f3192ae4
candidate-80e43cee95d22037e1388b6f0c7173c70f863cc2c33a54ea8cf778f64663ffe4
candidate-0814f33a7f863f2455708d7f3b5da8589c571ad29192a15c503246d1ad925a34
candidate-6ee33ee366c21d6b4db6270b58121a846bc7630cda00e3549ed58ea1050ada67
candidate-65107ca8e4790a0cf9029abfce0cf7442642b97f3a1b5e0ebb8978978f9414cb
candidate-32db5349236e1fc15430842ce6821c831dedf5ffc4ba3c1009c3970f017eb126
candidate-e70a6d89189abf5c93d74c88c4e2033350c15fcf343def9345f5ea27b0558855
candidate-b0d2413c4144ec03c1236e12aad9251067044884868a566b3abaf04d9ea329a4
candidate-5d196a83f04ab4bb4ce08eb5dacb47a0da717e64dcb84ad9fdd5bdb6a7aa6a55
candidate-651fe6543f96c94dcd451ac8b5f3b985106ac694223d68fe01ced2da67b9ac9b
candidate-f91179f4217b968ce67f4fdc807b139451cc82a1cfaf03a9a864d6c4e57b2923
candidate-9be91e42175f9cddcfe0ea0446a2d42c3183600fc318ba710bedb2eeced226e2
candidate-48c7e6f7e723df650ccd9805d704572118beb16845eadc01e832c01be17fee22
candidate-35f292d0923871696fbdc5fa3e1ef4f69886a5a10c92c5aa76224f8349a92dc8
candidate-15a46786cc2f107f988ddf416b992612a967ea3d1fe3fc26591586f147e5e2c6
candidate-5419a2f8e064381d19ff2bfbdd8bd5e4d6d0b701ecbbb8d9901d5424f52fd8bf
candidate-1ec8179a9e80abf3a5cdf1b2dff364a869647ef9373824478156f83cb5e0e054
candidate-137881ab27c7e914e5d513fce8b4479657896f2baac8bca90ad6a240805ca215
candidate-196ea5defebb8981328be44496427688321dcf5061465485cfe21cabcd58a995
candidate-9474a3ca7006f02441ad352a73d1fc0e358b7c6e10db353e168042d7d1b9cd18
candidate-a0685adc07ba7a20986c4448681f4fd63bb64109512aa2d288d4179b5f6c831e
candidate-5d1b1d93f98652358075900c778dd7d22fe862217a2b77554c88d5a86feb39f0
candidate-537a1a97fbc5d91f682da2a993fc5bfab853cd3d328c2af0d6763e66ecbf8dc8
candidate-a70ee2b983f51fca8ac95918f516d2572e6b33c39f770993c62dcad2f5a45c18
candidate-c2f9f21002cef7fbec7f4a3eeb2cb50b305fec2d375adb65e7db572b3ca55dcc
candidate-07d938ebe4ae2e2111e06fefcd19cfcb8ad2ac97bf02619d9c56ad7b59e14904
candidate-3b49d8a4c548382fd8fcb94711359270ecaa4097bcc85d2ef7b2fd16455e379c
candidate-61dc4359df6e6483767cfae957a2a57733c3c96414cbc61601ace02ad84448f7
candidate-38e413679c3bbc40ab76aafc482abb0141a81ad84a7817f229c59fa30753921a
candidate-f069425ad32017349d3b93da44b362ce0460536639666b2af5731b86e50b8d43
candidate-65d3a024b0873a0635285970c38cfa2560ab345a3ca4cc9febccd366f41ab1ec
candidate-2f844d62048f33be5cd9b2d7b3080a4c3e563520cb98f183ef97f60c93df95e3
candidate-025c9c5b2c38418ee4b759fed9b7e4fc9271486f8ab071ae1e3bea6df92bf161
candidate-8f8973aec79b62c3664563aa6d4cf7795e184640dcdbf640574f86f19957e1d3
candidate-8755091dfd3a0f94fec61a25686905d6e8960d97c0b1b2f7faf3e5d8a5252e4d
candidate-1c11e47562041edc0103d50b33a697f7264b934bd36e5849555999633769d159
candidate-9e542d5bad188703a4d58e559a9af4c89ae0c83b3c30625c69e939c270621bfb
candidate-8e740f8f8722170a89f36b12ec06d13af3eee5f1051ecdae6c648858609df1e0
candidate-ff44a5720e7edda7188c4a2ade802ca69fe92ba1e191c6a8d35ec7afec100a63
candidate-37666da625bcb528f48b7acde34e5bd8e55e79740c3bf23a0f98b7a68bdddd2b
candidate-f09630796a7c3169ceee1ab52f64f1347362560abcbf7f432a41c218dd372145
candidate-d93990fa4552919989826e4ca91bc64169a0e3ddf7cb0a285fc17d722916961e
candidate-6490cfa3b46cda03e7922ffdb2b2dc80e0b1bcd02958c343d637e7718fa36390
candidate-7a436072c1f65fa2279dcfb1c75aa334a2540932ed625b5f892714fe575d0a05
candidate-a2a7359e1cae680496ab21b0c2ac988af228b39d12f32ac743df6c88ce6f2e44
candidate-019acf2ac43e8eb558aeaf1c22991b72ca612dffda4215a64985cdd0815a5613
candidate-6e75f081a22ef253c441e2e0faae06f8704e73eb84cf6dc7f6bf17e1c45bc1f4
candidate-22ebe11c76e9d048d8bc7a230843279144c32fb39e6099e75739d830ea486342
candidate-2c18e089dedb008bdefb93ad3e70a72c701a1c6e224348814a364ffbcca8e7ec
candidate-304ec052c569c6583a29c096ab57e77d714c9b22d120b4576846f12bcd76173d
candidate-327b555e358aeed90cc3dab0498d38a77425378cf4a6415083dd54c2257fc5f0
candidate-2638b8eb891d8c8f8c23ac208c1c125fd7043a86b114eae1f2b1cfc7ec876dc9
candidate-7935fc3b51331aa3eefe3e295425e557a85c40ee3923d6abff836843ed5f3850
candidate-f1ca306656d2b31802872d725a8df0c9498715906546000073fa5ac1daa02c54
candidate-8326b33ba76239331650f4085185c305ff4043453eebb74ca8753b15a862f7eb
candidate-04a1947ca12ea1a4d856a17c2d78b019ac5c1b0db23173923ee826f28709e407
candidate-91ef2fcf9b5c3ffd0b278d8a8cc1c50b3aa1871ea48a320b5c8f3e7c00879f09
candidate-185cfe4de4368910ce6a088c8b5804481e5e4f4240f2bdb71f7224c1416b0529
candidate-e2af7738e6f3764fa3aeabd21e5a4e3c4416cd7ff52926e58c5ee3306e46386c
candidate-60d3d6601768b6220c965a432b0c8cfda85a26b81bbc25175a217f0a22f9f7d9
candidate-687f5a8e222e66e174f26d87f2100b1cd73c06e9bd1f03bdb877f28d5e1293aa
candidate-79a0f2bf22b20bd4f38f607bfea40413a209a5bf2925dc77dd4439fa971f0c90
candidate-a226b89791de30ca19bea43d25af9502bc4ee173395db8f9c35b16033af9823c
candidate-c0906436d280c56fa8552d2bfd9d2c000182a394c8cd9cf7e6235a30c0a16892
candidate-90eee94463c2a31abe709cef30bf5fc3c4604aa07537e3334adaebbe05157542
candidate-9ac09639ddfa03f395cc78d0a47f68173a513b6f602b02a0d1b3503e1cac5380
candidate-4b721ea96afb6adc52d1fd1d0bdb4495e19efa01a26803fc3fc6408da4134205
candidate-f9c23969a2e68e62789469e8d9609824ba1a9fd4597e2f65005cef05488491be
candidate-9ce99351d5f1bba33a80836785ea1a84c4796ef3e12de3ec6541ad2a5beb1e19
candidate-cf311ac51de188eaab11b8bb674da070e4e49282f6de469370e0938c84737058
candidate-adbe03c1de354c690530062355e8e14e579bf0e7d09f79959df468e9e82d6006
candidate-6851923a792f41e1ddd23aab6376378375df0edd5406aa4373751d0f39831fe5
candidate-1964a7e718579d714f9692cea52872e0be9c5cda891f511d5dce249aeec9aa99
candidate-6705b8db3085e3cf821b4ee2f4c70811cef8b137f621d787a90fceb81213f9f6
candidate-d13c029526ede986c23ec5877cfc57d3c2edddb9c157e097eea9610b05530de5
candidate-296c169ce34a2a0d9d10e165a6d024dede0e52c8df0e09a8d20a022f2afe2121
candidate-57706aabb21af2d48261862c555234a7eea6b8251da7225eb365eb14552aa0b8
candidate-b6f9f62e14d8bfdace744aea11a946c38855f2a924d114e61cfeab0a11b201f6
candidate-ca904cb3447a2848602ed60bc3508ffb065d58e3c26f726f4ae14abd1f682ac6
candidate-48de6fe0f68d0abf36c32f626ec2d196e3e1fba99b81fbef12df96a72a7eb64c
candidate-57e87d05f91c5702bf71f66c1116cb5b251ab023637039430adeaf4e9d638416
candidate-2139c9fa97dc5ead64d00e6e21e21d5509491304cd26d2c0c4254ab61e919cbd
candidate-837c5792a7540a08f5bb2d9517c122866570ccde276e6dc5ad7ac71aba16cbfb
candidate-af93701484f92be6facd53af3d4f8ec6d51b5db58cdb19802163b6cf6d3b01fc
candidate-b836cb179d70aa64c53bfe5f05bb8173e756d932fbae3645284653406aec77a2
candidate-2df9fe2ddad467d46114e3f90c216be594537a57e654cff9b0374fcfec19d8c2
candidate-8fea5e2e38aff5b964bd8368e557802f7873f52e04ef5de9d69dcba6ed9e1858
candidate-e6f2bd2f4902aa4d4308a1a49a3067f0f8550284d7f309b8ccc9ec259fa69d76
candidate-09f5db4fc93540a833a3dfb933dcdd76dc298b5889a349ef1b39b04fff9b3de8
candidate-ebc5183d2dc98f08fe9b54bffc4cd1c98004f4cec8d3992d60f8488b91c0ebc2
candidate-1c2876356494b85e7c2c063e41263f583133bd08ea3110c030842344b5c1b15a
candidate-b2a716732e4446f6dedebca645038495682c1288513b08d9ed609e24e431782b
candidate-f63ff310e7df62c1274c906f9401576926e01947df30a9bd25a2061ad06f9e7b
candidate-f4cd006e2f318fe5701e1a532fe38257520c977e0c68036208e4b2fdff1a4369
candidate-73641c5102556ba3767e5373f7a0b5f803f6556fe13762069365bbb0e61f039e
candidate-c41af76f7a7c606e1119ec5629e1501bc0911041caae703dd335d9a28535e559
candidate-2854e8281c1162dce1dfcb07cb19746397dd14723aa76a9b8fecb68d3a037e9d
candidate-c827025523aad5fc25a7401ad43c2e18d5b5cc387bfccccd801d2abed275f314
candidate-29b5f582763f13e8b7519296817afe81e0bfe2bc77d2862e26c8412ff6769bff
candidate-1ca8ece7fd19a85109e09a1e11b6b26294d75918a5edc33891e799e0a77a62da
candidate-114c16af37ecba35c08670505f17ec9075fc4bcd7981036633067b5de128ab90
candidate-486ee07e38e709c06404b4a5e00f04f5cd4d17b5d8580caf2350692cb2989b8a
candidate-33876fb536d8e92d805b4510701104f60aa8efa7112776347f201c7faa731700
candidate-547ffae690c8266331c5586ebbaa0e20b67afcf059365d0daa0e873a6f0c1a19
candidate-b8f24ce803d97c48d006f460dc499863c20f9735bc8461892b84c63ca988068e
candidate-80088bbbe8a346d0925a1ae623e7449befa86c264fcc470c8f816d1eff64e1fd
candidate-954a4e1ea8402afff6257290cd2035d5ec744bef457f7386d63c84517f3b3d0e
candidate-83917ba53c3314a6896b1cf8fe5f990138e4a4072cb78f4f9cf195afc9aead07
candidate-714a9c9c92640ecbff3d2d9f1af0ccd92ccfdb8d662ae3d84cec0f70e15bedbb
candidate-4b057198cf18a0c3a4783dcda9ed310aeba1a32712dfb173ca916e16ffb560f2
candidate-268612293bb6bae3decce01ebf163f47cac4318510581131143a25ce41731ae8
candidate-1ede5994cb32c3f6eacfcbea14da4b1f04826b0cc5067f66f24432c801a66f4a
candidate-39423e5cc9ae9c5633d0bf4dfe02935be0f5771031c14c590001c5a703c24667
candidate-eb0e2e560d5d732375aaf31095e1c1d0f8b7afbe30a37af95f781c907db27424
candidate-3a91af397d3b76a1bc336f01b0aeec2edce2d9f61c01d950b64406766c581f90
candidate-7101e307dea3a7098a77bea3fb7e0ad5c069e3555ca8d8cb668522650ffed4d3
candidate-315eed6e26b65bd36249adb0b4056426242433621e2ccd864828096dbb28c6bf
candidate-cebc4496a14647636047ed9b1d1593484e1d90ecb9afe14f5c525dac4b8aa87b
candidate-11089d38a9b00a434e9f36304f294886e68108d9b64bc1ce839fc3396fcd2358
candidate-c971a2bec5287bbee73c4d5fc1bd52602cc13b52e62c51eb2107ca453e80060c
candidate-4b21224301db297c4b6391c62ee49f8d228c7f1ea9c5dd65fd778bc2afdc09d0
candidate-851693ba26ee734c1871d322b8f0bda11c68a9dfd7e060223bcfd51e0aeb2cc4
candidate-65b46ed8296fe5c095980cc424d5ce3b383668b104ff7fc1c6562dc3b1f96aef
candidate-110ad01041b362c06c12a50101fc126d3e4f7e37cca746933e307d5bba56c292
candidate-e6f53961cc57ccd404796193ae7976a2f35c9d91acb4c0d10e95fbb037e7d053
candidate-213b49d3c06e4ece1de204f017bab13666efc6f1ec2e44f49de58cb31df0a13c
candidate-3c4363d9578eb597b9bcb5a74e169f2e8107ecec3961e44161cda90685690244
candidate-966e862149bd9018946fabb3c77ef3afe1805780a1f590930a4edcf00dc6323d
candidate-91a3ebe60d393d415c392ed6cab8bb412b89f0ca88685888053ec087cb87cddc
candidate-85cc74df05b47b752527cceb9904ec2dac64b88fec70bb21af8d164ffb544037
candidate-65304d2c7d172c3f733450605163f91063283a214e36d67383019bf35facdd8d
candidate-426b95aa790375e7ecfb3abdb1fd34731e38c0d60b5dacfc14906344729dc757
candidate-421f7b752cbeb13bbd332d6eca8280be77444db42ec00a4635088f70577b58bd
candidate-3b4c076a7146a7179130f3e149eb9fbb5f2790edb44991f2f3e0caa712089705
candidate-4a47d1e3e0e2e79e56366cd2ee01d1600039b909ae465d2dd26c4045461f3297
candidate-437df6892dd525efc472173f4baf3eaf7f91b0ec1ce09f9c8febcf608757cff7
candidate-477f5930e4182b61806395344cf7e6428f95ca7a80056bdf7644661faafa2ed4
candidate-e7dbd95eabd54f28fc3c4735f474ffa4cb3d54958ebe67b2abab0dffbe6a9d49
candidate-426b2be729e35af7568f3dac49eb22b1d5353172871888ac36894ab9e240ddde
candidate-a0256a1ecc3ba8bad6c4679bdf478cd083f0bb55d9ea44d2664174b2ca072973
candidate-91fca5ee7a1d96968f53ec8b00cf586ab1a0a3043d3684ad7a4a959e9787f20b
candidate-00d3a14ca902a2ffcc1d98dc1d423f26d068b58f3949ea920a2a4f4cb1a0295c
candidate-5c87882c290055d84485dae5348210cea2d0ef103ef311233850e173c3f2628f
candidate-3ff530e69e189dacc4dc499d28eb02ea47e2bb85e49491afcab0acc7f8d89b54
candidate-3b093167b41b4f5108661d0290840524640fd41aa09e52a3fbdef126184f719a
candidate-bf09e6951ba6fdfaf2a04ed295abe9a8bfd8cf01a5794ad628c236ec578d20d2
candidate-c0d6169a837715ebfaebebbf83d312bde5dda5badd40de47d7e1649a59046e0b
candidate-6af209a048e394065c0672e480a387cddfcf4c3abf8a63d1eb1c0517336c058e
candidate-2dc4fc27cacf65bae76d5fad321db254e0d5d173d211e5261b8fe0069c4085bb
candidate-1dcf7ee7950bdfac42c84dbef6b720c3f4046bb95288847cd6a628f40999a470
candidate-529495b54410db9c531310fd3b3f21abaad9842546225d60b0fc7db5ddf677ac
candidate-55f487d92f5f737a1e7c790f29b5adfd2e6a1bd6c62f4f06c75cc093013274cd
candidate-2855a9a854f539d09bc949795154d4b068a45d386fd6224c46b0f8d16b7d4e37
candidate-1ca53e4de27d47d93a7b74d2746dd4f9da4e0893b93aef903fe312982e508fba
candidate-3593687699471dd5cea87ebf149d459c36d2200f6d877d2b167767dc9007059f
candidate-62228293a414a5f729bd784067fb546b3809cb2de7b2fe2a9c96a9060ecbd3e9
candidate-c55ed7a992b94df4c07027648840b99f285dfd17cb2161d0ed5da590105ca7e1
candidate-8cb75b24ab77dd25df78cf9a164b08925f705959da4f08d478b732a1d9f5b04f
candidate-782e94884337ee0eda56003a285d64997f2aa055a00e861f61a192ebf46bc7a7
candidate-4cf2a13b630e1293e7528f1c84551c36b69d25af240c003af72cb8a61ee00788
candidate-2411fb6baedf7ccf9a019ca532810e239c0ab12650965f2def1bf30e4904ff6f
candidate-b8a6681d45e23a443c2ceeae27c197a805b3aa2b66dde7616cf1571fba9e416a
candidate-cb4835c8ebde53ac61481bb4f429ff6c96354ba2fcc0e4187141903e73d8092f
candidate-4d0d12d4fbc6716bc05f9cb4616d5bd86497fa9062683b7896588c6d817e9e4c
candidate-1cf137e8895b092510e1def2cac84990e9d6b9398b96365b140d97753cb52d41
candidate-2e7b9d9c1b55e3a4b4a87fcf8c30009a3f47cfb6934d2dd640710cb5a8be0429
</pre>
</details>

<details>
<summary><code>approximate_value</code> (2 candidates)</summary>

<pre>
candidate-7e8f7da2fbe693e5d26ba498452e285cd47bed4983535d61525fdb36930063bb
candidate-0a625ab2a6a33039d7bfbc01760edb9585f6f0f8b91bb716e00a2a0d78d4a47c
</pre>
</details>

<details>
<summary><code>boundary_condition</code> (1379 candidates)</summary>

<pre>
candidate-ce32551e400035d49d7a4b46a5ab01276eab35951df7fa552a61767a06cad928
candidate-ebcac6ec3894862ee7018ba6648b80b8188fb8c7cc0b3c64f1a6c4a91b969935
candidate-9b15c182a30d47ad4fe169b63c57ca798d0889a80a199ff3532bf033675b05ee
candidate-9ce8fc99cf99a27c2014e6b530f3e302f560a059bf24986c7f3a44f6b504e978
candidate-fe50a117d5cae5b880723aba2bb13a99f04927973cd96aff5c37ab2d112301d8
candidate-57fa44c88ad05cefb2111ab18242748bdda7d1e2b046de3b622b30aa17fa04f2
candidate-92250321da5650d761cb74afe2409dfbbabf2324e0a9e63cca304fbb82f47dd2
candidate-f49b628bf17cb6c57a632201d307d3afc3fde4474a02608070b4f700b4d7a877
candidate-fbeef70574c2809028db85d63cf3921715bf3e05895643703e558129250db02e
candidate-2de1f85a3b626c6da88b1e845fcb93a9f5b86e0c367d561b80908ccbfa6e5599
candidate-4221062d5e6adf48d146bd143437422ea107df0a3b48ccf0d85dba13b9faf2ad
candidate-a26cd5cff4d520a01fc1881a467d56faf87bfb2e26de303abe7cd230055c5dbf
candidate-75633c33926f20c1a27b617aa94b23cb41ab58d471c7ab6ada4e660c569a1adb
candidate-3d5466324b4d097a4849122f9b9071b700423c2c248d5d4ac3806eb401f83b7f
candidate-2674124d0192f40b15be261c8394eecb1040ddb07ced22ffe5defd36655d8b27
candidate-3475d2adf1f5d683c348131446a986cc9dd91fe16123c8b7305bc9a757ae5701
candidate-2944ee241f1bac8b6c65877944c8dc9c38d8d479ba367892a6dcc271941a1b32
candidate-4cf99508183c8d8644ec8cd78196fbc1853d84efcbf2af831fd0b402bb2ee379
candidate-f9daa6241c5e59f8168b28e3a03d0309fae00d228c4639712cd13572c972517d
candidate-ec4a94547af37fbe2450afe7c98654041e973da190b7e94adc96ef3d6bc92a2c
candidate-d5a338f52b4ddcb1e7391bd8b6c3fd27b2a8757226a39f68b114bb4ab72a8f01
candidate-b3505ad477de7d59405c4332f38799328c6328338224f5657f3b02051a932a2c
candidate-1a86d72c70682769dacd81a3d4e3e82bbaa7cab3d04b5f63ed5fb7e0df63051c
candidate-db35d8af0e1a2903b41883a397e7588a2ace36e309861cd71a4a4cb6e4ea76cb
candidate-0fbdb30bb209098b5500f9f1879eaf545eb6902535e8ae40b092fcd6b64f7a51
candidate-103f361f9bcadf502e4225e805b163fc319e5efc6aae6460e3787ef58a25d5ca
candidate-58a51fdbb56e5a5b42b0e08e25525c5bef17409727f5c5912bda822d1cac25d3
candidate-cf299cf0306a88827a89e02330da9d9b6ee21ca7286c73f3b4ab93ab550bf6b7
candidate-a182ee5899b7424aa983867588919db57d8ab9b9e557e7c0c3804b96d554a0b3
candidate-35af1acc3d132c246c11c05a52f1af878fd0889b6f0f14bb7b714ce08dd418fb
candidate-2f48f727d559a4712eb38d2024826d7065ea3b93fc97970b39febae71da111a4
candidate-518ffddfa35f30b105ed23c9ae2559ee2a02c6ba76f8a40125cb722a18113cda
candidate-e479e3be3b2c8b2944788ae05c037bdb9b4e2efb5f14e2352b8147320b6f01d7
candidate-9a19beee5f57984be28be732ffc65af2f8a52d051770e547973f1f8f2f313ce2
candidate-11e6a78d4a019f348b29cb17ddff9b6943f214a1e4d277bb043b0d2df66b2504
candidate-acb5744030655f4eb1c6172f26a153f5041f823641ca94fa6cbb8bb87799579b
candidate-632de39613d261498840634ac29af28347fa8330381955fe42f6b12f3aa58d97
candidate-823fc35cd37319c59f0f2983feac7750f431697bed8fc3a301a8ab7b01fc24e3
candidate-9140a26498415b1379e91bf2c0532a8318847d2412be6ef3055531cc3dddab00
candidate-30e6d180b6b9fedce830779328125b28b176d6e921caf57ba633ca5957f54725
candidate-f08ca19d3a2151930f45eee0b7ad168f0aee97369f22a58fbd7492847cd69f1b
candidate-d077907a57e9f75cf839919ed06d14544be02d69d48270298d198c6d0fe8c1c1
candidate-e96b105f399cb0b31f9ffe09a87f0fa45d29b3092e31cd1979a5f7271b39834e
candidate-c4e63114f0afd3bc7cfd42dce162875de466f706c7f00946d9f29b13968a203d
candidate-acb31d8ea0e848444a5fce3d8e80d2e459dfb386c3f9c3690968bd7359318543
candidate-274879fd53d0ea5fdf83483f6af38eecbc2db1adb0ee1287610ea3660bb2400f
candidate-fa294bb5f0e8eae2131ab79f878290ed1ea05cf34042ae26cffdb72059742bd4
candidate-d85add3089e30ba7e9c7c1572871a1442bda5147eab8385d8b0d1fd49ef0bd40
candidate-6b5308d94fd70180006ba22919585f2f93c26cd79c055d79c5f3742ccc9c9aec
candidate-92f419ec7f713aa4e906d8cb292ab35fd8fab4d3a3472c8d7becf07804e62788
candidate-cb374b8fd5f0ca88362f39dbb3256d3b2e24b6d1318588afce8ee0336285d04c
candidate-78f315489d2718df270c7caafc64bf790ee7c43fed642d27c361ffedcd3dbccc
candidate-a424c52c906ec46a8431d359830dd100912891f42fc7bc26d0a65fba70e59c0f
candidate-cb58b49aa177503c7b2d75b266396b24978c87249dfbb0c3c40d789e4dd7b748
candidate-bceea33e06825c50757c972e602be49484c023f41407b7f6e6713982c27412a9
candidate-44b2efb669533ac29a1ca891d7ad6c8f9042d8378f6724d9642935929ab6af77
candidate-f610f29469f8b5bc661a809c4c7d817800367d728c707c074c4f55eabcfcddec
candidate-6904e515d560ffd6cbba742acbb0d85f2d029ba86000149f02cbcbfa89907e9d
candidate-f8fed71bb33265b4a130b4a6cafb3ffd7cccb25f7e6075a0af61a3b19142d42f
candidate-d4affe2c25a4b3e318636e2d8f43b370b1c29604362cf55c508a1794f752f92a
candidate-c8a210999d901c18b7a5f44b742ef2b37f7dc587de54b8c54e744a449ba21e7f
candidate-28fe925d4be6c655d658462d113b35b82040b2ffe99433b0a75e8093745a80af
candidate-ad916c76a5def7843e62deb532d744b97a98ff347d3b5b9e7c30d76d20c30045
candidate-84e475c1f235e762256d2b4417ca81b4500080730c1034e76c508888222eb3a8
candidate-0adf9b83297ac4080dea0934b01d88e14a168db729d84402950fb02660a6163a
candidate-b9eb7e9dada379175df7941b1e6d1ffd7df4dd92601cc6e7cbdeae3a99f5806e
candidate-eb3a3c1256b57dc35e1f402329294a7a169c7a3a5997f98cf4e2328c26f538cb
candidate-3c7f857b8f435ff63aa26654fbab71739b1875bd330e6a31fa8c5ff320fbb74d
candidate-ae52a7ba292dda9397a34300c23b916d7fa0f5903c3885c1dfdf106157b758bb
candidate-bd81d236eda35c98fb5273b96f11ac0d587b977fa6db47c12953229fdde3ab7d
candidate-1a2dcdcfa552759e75726baf3bf02d6041b9ec1d90fe6de55ad49c06cbc4a563
candidate-1c266acc44c98d6bad5548136d045130b34cf3b42d94a0d8809c8338f7e1c631
candidate-8d284f572840a8a8dcefb1ef535e9dd10b9bab73f097598b908f9f3b919edb26
candidate-61d3b72d212d954e20b45c4588da8f16a35215db120f1e71745a9d28cadb2c8c
candidate-8c950f5a8d088c90a4793b067b71fd8714ebbe14179131322ee7ff490df14afd
candidate-cf0e341023fb800ed14976dd9338ec5563af29dd8085df3591941584f794f5a8
candidate-6736916096d81352400df12f8afceff979d8c9b2e08961721585f5db953a2b32
candidate-0b28b17889d42014b50e82788ef07fd1fa255cf87d6e4ee4f030d82c10c65711
candidate-028eef093dd95a180ec62a0b3ef31cfa2e41002061ce59cdb043514349cf6b12
candidate-a173eaeffb06b4675cf849820552292d006e4ff7df0ba7f02508098cb769cbe7
candidate-d2fc2ddf46447eac7042fe8e1147e2da006977f1306a2ff99bd7b825737eac96
candidate-0753e5854f039d91a0663259ac99749d55e5531cc61d906c7bac7fb9607ae3b3
candidate-2acd7b6536a0b5f793e53fa485c138851b4642ccd6261b2f3a9ba28c3cc001a4
candidate-9bf891b5f8463c203d0ec0ae82518a4ad6d851c3180bd6240dfacc5a95066797
candidate-738ed0d7269b32aad52e64b1b05e991a2f558c2fce57dd495357e11dce3c4c15
candidate-19b38355bdbd21860a2605a5c9ce36464dd76b2d34f63c7b69284af99c11a3df
candidate-e1550c571bf0c3210019e0fec4049fa02dcde8069652ec1527dc9adf14b5f3d6
candidate-2177d23287af3b0998dd999fe3865860089c116f9c1be93b1d6550116ae8165c
candidate-dde4ca393389fd0840475e1dd6e4b8a3987dc3734ecdb3bf37b6bf0a1701b892
candidate-093ae045c11f14f66157bd0356bbeba4f515a26a425bee5df1805cb26646b1d7
candidate-d1bbbe39e4495c9699229c015db4599a337fbe09989a474eaf535e54bc93597a
candidate-15b3fd60d220f4993ae59e955b64ea1b71804b2b4c4ebfcff1c63dd11202871f
candidate-ce8c856e0be0206304ced47b584e7a38830a774ed5a85441990dd281dad12c70
candidate-8f27a605264b90bbacb289750879101887493f408ba2ed38467c14fb65d45043
candidate-d91570f0084a5e9322729a4d576618c92c3030e88765c5b25141c13d08990620
candidate-fbd0d88c31164c03575c21dbb914afdf0f8a3f5bb0aad0b0065f985a4deab7a8
candidate-ba511cb32604eed86216a236a1a398cdcd24a9d3afb551343f0fb4825662b223
candidate-5fca27b2fdb6f28c103b53738f784135769619b0c2b167c78162622563c2974b
candidate-0b4e1b3ec05ec772a3e67a4dfde929967fdb3e04a50b26d691d1fc23818ad36b
candidate-39ae0ad244f7864cdb5098b68e2f75004bfdff3c674d7af5ceb2e51a7285858f
candidate-6558e16c0a974d3863166db124aeb5d340c9486111945af3720da0ed5673ad0a
candidate-a75c7688a17c997fe83760a46c0c80252fa9a0958d8cefb0063fd3f67738f2da
candidate-5eafa15fd5453e6b6fda8c3ac576cdac202ffb26b7b4b9060dfc819fcca7b23d
candidate-42e5f9ad7c81527917e0db23602b6ff7e8648dd81398541ee091621897e78b70
candidate-62d79c25c4658de132084984611fa10a3e3623a951f5138b8b04cb52c0c72f81
candidate-7f65aa2fbf9d57635ca79ce286b2c5c9b1dffe112438c2a3bce56142dbcc6382
candidate-b9fd20aa91b138e35783b6280202167285f8dbbde383263da430382300d0435d
candidate-afd3b7dcdf32b61eb61a55af2a121a86415ff0df7619bf6f6130b29822273f1d
candidate-7046ff01ac5c6c6890ae1108eae7ec5c16a770012d33a88508f5fbefc6368f38
candidate-34111156d45b641067820be044c886b8b6d903c9577b1d2752916055dc41011c
candidate-e321cbefb5d1f4d515fb4f2e50fb64bcafe02882c5e1e818a2663f9445c79402
candidate-d0a94184c7001b85aaac2fb76ebbc15ecf02a303a6619d4b738e3be649f7e5e7
candidate-652e7d8dd04935246b976a7aa07b905d1e4b720243a7646dfe4d8c4ca1cd0b03
candidate-69d4cef33ccb384d7f7dd4ef623be8452636bf87c25a2ea4ebaeae8b52068a09
candidate-c197be07de031eb1269c400d42cba540fefed17c0debcd65355fb27267e2d4d0
candidate-aad5719fa4593f24845322f10185373bff6e65a08c3038f52ee5a0abe3fdcc3c
candidate-eb797841e9f8e7daea730cbec467443865882c71844f06483267dbf4090b9cd1
candidate-d602641444ef4e014ecc135c67dc1a35a5d91dbad3ac72245524f824a7998f1d
candidate-b30f61276800409fd10eefca843d858c760b473bdcf169ac770ed7f2a073b6c3
candidate-c1a86ced9685628bff01a426e06ea0e4b198326437d670e8b2f8e3c72df65dd3
candidate-a7ce84082d81f848d2e81a1025003a5444432747529c3fabbef04f8ba06558fa
candidate-871819d0160e4836910f2553e63e24bd5cf52e22cfdc67df8dd99e56ba6635eb
candidate-e329249d0ef1b1e6507bdb37c29b9ab3aae0af1717b501598032222e6b034e57
candidate-146fed548584454fac3530af2355b31801fff2f9c1b5fbbe42c850141dec38c0
candidate-fe77726862bec83957a68ffc35e7e869377f42b747633f9b1a6f791e5a0bf508
candidate-eaa38f5c4561d6973671844617c50de84a25e9c9b56fa2bea92b921d35301004
candidate-52b60b24a065735944313cead0be1554475a7c857854bc7934b4571bd957b152
candidate-3a441dfbc6a8fb34eded43a623a3dbf3894520f974ad4613766da4811347b1be
candidate-44aeb1a52dc9d076ca949891c5231d4def23add2301da97d1986018f391947b6
candidate-8a58762e7db6578d3ad96184e6bdc520271c4303b6b7da4ecb19ffaadf8f2dfb
candidate-8e5b67b9571421a79b8a83136acc2c962828110c8bfac2df98eac74552a5d58e
candidate-b8a509b85dc3d923108b223fb33ed17491b5a84b605b4a37a128b860b278bb4d
candidate-cf1d88751aae1b2055e144fa30bc98a776e5f5c69b2176172705ced02febcb92
candidate-4314980fdec2113f6d1ab121c04d670697d41f2fcc7a91bb35d12083d6d27e45
candidate-750120578605a4125d86e52ed7192cb40cb3d5b2aa415f0a5ff400c09ff6057e
candidate-49c16d1834dc09c86166b526cdb85ef66ac492ed72e1658f6056dc21e61c5501
candidate-6bbbd723204f03758eedc5886bbb5b266a118e13bc44c4c001d8c10ea679c846
candidate-683fde7333a259c6ff2f081a4746b410f9cd411dad6b66e5f7ee8d1f1069e8a1
candidate-9b19039576d6cd561d38b6fb09ca0a599c81e648a52293cc044688b26f798b6e
candidate-34e768aa7b49ef8e2ee302a0d6e1a4948189169de35ca80e06ff6c90755a8058
candidate-212c4c2c1714f0cc8a631f8e2c7a1c4279936bfe8039f7f9ac5e4f7db404576a
candidate-82d6c81312a0034ef9085b8c6c4c2b24bc8b9ff8f0cba3166bcd4524d1edd54b
candidate-1c27efd83ff3a136c2793efe1c7c17f8aa95b1748438ac3f2f3406d93c0cf6cd
candidate-72b1a38d09c3352589d6ca3e6f6ae6d79c4e84bfd96c9a4257c808a1732e63c9
candidate-03f14e884de138a3f31038cb32a1893a8a21cfaa250da85e1a182048e8ca2e64
candidate-0cecdc3ec05a6f993e40dc882c46f822a80052f68923a26aec1b8e3985268941
candidate-bd84029cbcfa69437a6612bc7adb010a156f5aa52fe3cd643991374d73c119ac
candidate-0e13915e62bddcd6f2b31cd6bb8c4eb82f43968d566e04b3b8590004f1586744
candidate-6dcd5b67b3405bb8a1b96c5245e930f0a01f5f5fa8b95178baf412d705aa21bd
candidate-4efad21fa7415ecec23d009f1e5cf49c812d120a0179ac0559d6d34530b67dfe
candidate-f9482f058bade0a60fd727b5285b80e67d66d49cd2f9118bedaf5ddd85e13b65
candidate-eba475c06bda48e52709cbe2ded50a051f0ab8d6c51dcf3b6cef8e62295c48c1
candidate-84a27d620f6bc55f9f250139a4a582ac92f48d46a36c13e027f7d9bd1e19bc67
candidate-237e0928b124492982a20ac522e9356de40e25c68a62920040246ed45eb01a29
candidate-b1d731485b9dbabf619f1bcdbf4de6132ae52c296312f1face7fc2418693702b
candidate-383842850ee8211abeff532224e1332d4956ffc8bb35390d53d9244da1708e3c
candidate-412a2c5a7a3e693c97d800c710b2337ebe3d743d981ce9f88a58935ca462a43e
candidate-770354524253fd97e172e5d044883b04bb8bcbea53249c3dae2221d1d9c59178
candidate-63ca2be008c2d850b66194875dd573e3e404cb0a91f5f02b07a29988975c0602
candidate-59072cbb24ffddbdac1734e05193286a4f414de5a00162e1b1f7688a783b4a60
candidate-74d7b69dae4a84ce3c1f79b3afb904ac6d9824eaa906a27eec0ff088c3e7369b
candidate-a72dfaeebbbb8d0068b0fb52803335d3e08ed9f6c856c3185624291b43029fdd
candidate-f2cd08ee02185dcefa3dfafdee5dd4318eca7e4288e664595d4c8d68a8546da9
candidate-14094cc0ddda71421fd48e0fd974e7abe94a38b37df7d6fe31b9faedc1de20bf
candidate-aa8b00b46449ea3cf7f77f50f9c37cd1d1f686e1b6d8eddb2c9ec7e155c6a8c2
candidate-2ba01c3e1af1704b3ef38f17691d3b5bd9efb260fe520b0888015ab94666fe59
candidate-4f189b091f47f8c0d3fe84b116906f879ace97879e4b760485717b9308b1c0d5
candidate-a8e2fc499083ea49518ea72565d03036d2c4d461f2fd2e7f2a9f53fd4ed26761
candidate-08490791fb458ce73dc3444f600829a1bb79bc623e0fd5d0bdbcecfae62dc47a
candidate-61e70b7aeebb5c034153a43ecb49ddd67111c6562b2fae6a7a9902f447a1bed4
candidate-3038a97e884888af8a87cbe2ea7acd3f40ef80f6b0915be322491dcd12097d96
candidate-ebb692f9d8aeadbd1557d4ba7b34a2d8204c98e58d65b94d68859d5c0becd9c7
candidate-c8aacc6cbcc02a3cf6d1e0fdaa70a0c57f8d25045a23fa542a98cd5a7c283718
candidate-134f223885c5cca462a1aeb6faf8e57b6e19806c0d205613257eb897c5cc8649
candidate-dace0c5f5ae3a2374560e35b53e4d19e9936f1bfa07af2444c201fac145c75c4
candidate-0e9feadcd335abfc3a5a232852403d2ad54ffb7d296a93db36653a607824c602
candidate-ed6d65a65f3c4378123e8a20ea6b296cf326dbc0df3af142bd7757605c328160
candidate-3140f37a36a44ec371ffd32b84355b0cd45b081e023f88d857d90afe4fe45568
candidate-88d2d9c99e13f322048fb572c8bce1497d2bd6c1386b43a9c67696118c9d4be9
candidate-10321d30289366b9d41ab76b3a8b5e9163b097044cf7f58e9143fcbba4131815
candidate-8571c6d725644ada8f67e03d3d0f9f379c39ed91f79059b98222a3685f332d3c
candidate-8bccbeb02dec9d546ab06bcf6cc361753874ceca2c413728b3be51cc4798beb7
candidate-eb0196c336597c5f7e23f591d394e0fb41a64bed7c27a8126fda2fb2269881a6
candidate-0e31ebafad0f8a1389e3485f0ff963c9c1af8cf51989d1359bab41d0831575fd
candidate-ceda64b16b8f6785c0edb7013e877afd347e827e96cc8afe8b5b132edb3510b6
candidate-499c4ea0e6d0d6837799b2b1d58896874d0275c8346b5b2f7b3c2fd271d710eb
candidate-6a7d597d41f964db0f8961562381ba838e222659c6bbcc6059465c0a760f5471
candidate-b971717ac2ad0e6ced26e2c39402f7c1856b09601b4d90747226bfc2f4d432af
candidate-d44063cddcd7451ff79e9f58face38f873fc6ff1982ad945ec8e4be9a3722f5d
candidate-40d4f0e18791541db98f693a03062e4d292baa738215d755f245fb1616023cc3
candidate-cca1a30b8a94d4be9dfb259519cbc7a81022f14425402af9e8cc1cf49b12ce36
candidate-be8caccbc0487c90d6464cac3fce797e462501f15c43aa53f821334d8c0e3c47
candidate-3bb596598f30985888657d39b678f76238758e49ac2400ea1652b0dae84742c0
candidate-69ba3e65bf3f4c287d8e694cc23dedf24c4f5df14e5a7ff132d4c4dc88035cc9
candidate-9eebe0825a638ad91e30d785590d4555c3500dc9c02d0e065b94478ffef791d4
candidate-71abb1980b2b4883bb4945343c8605ed38bb116e949f7c6873f437499e39e93f
candidate-22430c6a5ab7845a1aadd766a93e9629922b72e43f7160ae4b348063ba3c632a
candidate-dcfc6b992313dd12b28def3ed0557ab3da5c6772b2466ce78bb3f0c636664441
candidate-3e8f85bbc8493a08f3ba20ecce1e928b2b2e4bae1c430acd5140189fbf4d48bc
candidate-557f6c2ea9341fed551b1f91e463790d6f46218b8a444b3a2ea4ca83229fac5e
candidate-5eec6f6ece0ab03728e6653ab11a0f3a2e914b302e56651c77ca6d9142c09002
candidate-b0471ddd0c52fc860c1c3598cc9f57c28d042423a25d36585b33d77226b51c8f
candidate-eaefc0ce6a24ec3ddf24c60222679762d88a365713b34b4bc8860da8c715aad2
candidate-b9f0984305aa7d7d6a41f7d782eebdb2efd4185c3505faf9b2cb85af4cdb045a
candidate-5ffbf7a29a840581ad8510fe759c18c0a47ef3e643e887423732b2c34b7077fd
candidate-6f416298557ff8c5930466a595c142caebcefe8660c108f2afb9f332439de30a
candidate-ce3c15501271ec4d5b5ac29f357c800481b3ab1e4060547b6e00edb3a15b6878
candidate-31c92be6b4d9725f88f90607b812d8c4d56faf4fd92c35108bb32af1582835a7
candidate-86e8cde368877282431c17bfa722967dd62ce3daf07089c91b6a6a99a590ec73
candidate-43d1fa97e7ca04f58ea018ef9d3d9d6854f5a8f92281fea9c0ed8ccb907e847d
candidate-d3081331c63bbc4c57a2e3cf41b26411510d1d8c522f733d9b4d73607df53114
candidate-95e93984db814a19c5b4cd3dbf307eb86c29efb39ac4ae8245c6bbf445f6c59e
candidate-1cb03cbb45193ed36161f00139971a5a590c4395b49d59c990be809520509aba
candidate-67de228e973224d9a3227cc0226ab05dbac804c3ac8414c696a0c667d334f0c8
candidate-cf79efa4528b9d434f982d31d45469edf6f79e78e90e7d21e1b8e0fe05344bb2
candidate-a17a96fae946bc07a4d88ec23488a4a8a7464b469094150ea1ad0394ab2b9fd6
candidate-125b9c4f7c24d58a4d43749a67ccd0e9f2a19d71a7cf5a5cd59fa4c5d176819f
candidate-0632cb5dc99c7eed9df922e4747118880f1bbc9a1b9f7f55b71124b9f8daa9fa
candidate-fdff2a49be3ba3b04dffce343d938e7a09771b4e81d8d43edd93e1aecb40804a
candidate-73b01f944a7a20c6a000f9f1b0af58d307cb3956a05f3f7ccf727ae56fcead89
candidate-1856457ea8743b0a78defeda9fc0292adb965c14effb3bc75e44db88b60c4644
candidate-7a389471a37c2fb9e9ffe363ac870286c680838340b558d47abc01873e88d90d
candidate-124c5eb8c17e079f69e3c18f09be24591bbc1d69e3caae4210c16da4cc0e5ef4
candidate-fd77f5a7ca4570b9cab64744e84414a71e001f16e4da8ea6daa08c11bdce019a
candidate-84f5e53dd820b703e0a4d73b0efa685c743d15bef11b1bca9167e6e85aa4aff1
candidate-66da0f26a5651789c0535bfd3c9591140a7d5b4b5f2c84a33853ddfeae5e5daa
candidate-ab7ff28c8b96c05fa2e68d50f0547759690e7afb3eba6c1d7c749fc124d0bf9e
candidate-67c1f7f31505e64bed4e30988f22fa6887f70109e200b989ce499a4fc1d1c6ff
candidate-53fcb842ff2f7947158dfaa8955724deec83030fce634b7f4785efb7bb14942f
candidate-c987a0df6b0c779fe7fa3aee20d509880a8eda63db85181e8b4a11eeebeb7bd1
candidate-388aba681f8255c352bd076cebeed3f04f82674c5b6e81f86f2f0d41f84dd484
candidate-eb0f3c924e04be44c4a76beff66f6c77d84acc2b46f302605318fcfdada8fd8a
candidate-445cf1ae3cbeb0d06b48e8630a60358bea1413b5166b80d1a7ebd04db9793f58
candidate-7c09fb8d146e1c4cbab223abb09d80d078f2ba2f1f27fa9fc379572a0fe44e37
candidate-976755af33a6ef8f281731a364903d97f25e1d89444e8eb62d0585f0747a146b
candidate-d2a9aa62c12e156e81b9dfa92f9afa9d1993554317d2f6b1ac1f7be9e11b16ba
candidate-3a745f965f90ec62a7cef6841f15a8182c902df1f6573620af60c1dcc8ccd878
candidate-b8c5b41e017fefb37691b38ac8dc970456c85c35e02b125ff93374310ecc0785
candidate-294d1d63dbab3efc27a2f38a7a8d2ffc723760697a5dc450eff58ebbfbe9ccd2
candidate-55f5b13a989dc322778b7869100f20c02a39b81df9396844fffda364a2c08b34
candidate-f72e0b7dc56b18fa5dc6e366bbbd0c88b9759fc248543ec01a2736c45a73fb06
candidate-5bfdba07ba0601f61b7beb70457da188c320d85309639419452b61803c62f8d3
candidate-bf236cbde94380b19ccb7a6aa1480f637a6d7b35ed153ce796f6591f18a635dd
candidate-2e1790a93a28acd8f1e2ead093df88b26fa3c843f8905899d1868fa5481883ba
candidate-dd53ab5e03fc8ced6a9de3d552d4f3668036a943bc83910e240bee76a5d93cba
candidate-95586ea78e7daade31fb211ce31dd6f34c67225ed06cfe003579af1f23297d5f
candidate-66d44a082f5e547dc70159b1d89268ce76741e2e9e73fadbba0aaa04d81d8262
candidate-208e70ec2fd424bb7cc88030068925a22f74ccee798a34fa9e4de327be6dd0ff
candidate-5d18362fd70406b1745c25d2077dae706a9d921c66979cc87afd82d6d3498f08
candidate-a7dfa268b54d3c96b509b20e7bf94b852db1eecd3ca8404a5a3919dbdc0b4264
candidate-35233301b0eb1b2f9612c8531da3898c30123a6ac22f993f9ea1e7f342322ed6
candidate-a5baa8997e7ff38cb755f152964b61cc49be314dd2859f9c583fbb329fb8d99a
candidate-9b748b2a0f745a4ff71fab6ce0f8e296fd9b4c32c0518d0753c36efc2163eda0
candidate-38a2456e03fff830fe66f225bb675930849b72878d3e5ddd7773028f31bd3414
candidate-358ad1dbbbf527b5fac2f39b385333e7781faa037f246faf8774ed060ab9605f
candidate-fe808efe2cea01d7468b1307b460631430685334ef5aa6f807af81053c96e1b1
candidate-6a9a88bf40ab7f32ee27923e5e1db2360426e5be3e49026be5a95905b622f174
candidate-d366a574db3a4c844aa27090c2ff3d3c0672f9f1e0fa08dc87acea3468b29b3e
candidate-7c5976814fc8ced4ed58b7b7072aed6be5e832fa629e0fc970421de636f69db9
candidate-74d3d369e2893f6db88b7fcb0665c991ae1eb89f924d3d22c602c7ba98d44eae
candidate-dba4ee0c1a37389f422c383607a4f4be8d4143dcd1f7bd3fbe8e7e2440d35516
candidate-3e13b2c6fa326817120bc53faecec207ab633945bf0d9e7b56c0ac6765a1dd6f
candidate-057d0a4d892e4ff4cef883eb01d3e929b79fc1dc96c877ffbd3bcc6e279304cf
candidate-662ddd7fabc237f7333a9dffe4da96ab73cf04cbd70e27d026a048151cfdf31d
candidate-6efb850140b29528983637d1a84c9ebcf15f89164cca931e522c5611b3a96b8d
candidate-f4b1763012ed67fa893f6a8043f8186d49bc9a11e1480b53c32cff42db9174af
candidate-9eef43445e7e8a4da7549655b8bff0a04b36f4414f2af054cf7efc23c037c0bb
candidate-893c1f50f76088256c491b9077dc7bddaef4f8a9675c7ae09ec03babfd517dbb
candidate-c9ae4bf620639d7202ad794d9745ebe636d8e603c31eb6e1a9d6dd26aa0aa32a
candidate-d826e82b7d8822f4ad84509178097f9f7d1ff532e223c8bd6df2fb0ad5be9eb4
candidate-aeccd689e90be2c55074e8041dcf971a61df4c1067fe4660ac2121455c524262
candidate-9c761eb1627057a680fdc66d2a13565beedcbc3cad6b386b71702a99f0330843
candidate-56f6c6797e0f7df73cdbef89b6a9326c370d749713637f949e6d938984163592
candidate-c041d1428ef04884ba566d676ec2056249b743bc893ec21bb5c0804db1ad7098
candidate-6a228736f7d8a7e5ea096c83ccc9aafe10541b54a5c618a57967747918d848ad
candidate-756ecf475348c1d06e7ceb35310e915b4255090fe2f58a90647e413d37fb3644
candidate-5cdd1849329834c49924c83846a0cfca8d7a6eb2b8bee8ddba508dddbe65159d
candidate-fe3eabd89cd33eb857573bf3a9abc3bb6e15a9a4ee718566cc9a01697ece60ad
candidate-fa2b7dd9d6a9348d00f7bf2fc7f2771b7b730091d4c8ca4a24266bd46fe3103f
candidate-6581bf69c5143de11f4cccd233ad029595a18872c0b890d947a1f1b974e30d2f
candidate-4d6cb475b8598150a57c842f43e1ba7082f07143ea920bc3fbdb5e489bea0632
candidate-eadc039f80022bef4a19f5754c4875ca73acaf5c616a20a9a0d14928c4b94977
candidate-9c3ab2d266a1e76809845f229e2bb3581804fd3dea0f2c19a55f39fd911180fd
candidate-5e60a25d5ed6e22a6245880384c495bee9ca755d938ae2fdfb7fee98241b7e26
candidate-79d6c6fe67174c180b40035fe2dbe2d5e40dcf7eda4154861b08772ef6e7e4fc
candidate-5160a20fb59819a5b6fb44551b85f18c89a398a2111494a72772b6e6d6154cbe
candidate-0d84a686da4779aa0e80a919f3c452c05683b52e0b1659bb4d6097277fa2ac4e
candidate-41d39fa1c88d14ef9a011b0cab4775024e3e5273a52f32e1a6b778c3fc0db5cc
candidate-550071f1140f13fe580ee037160405ef6709f5102fdef801ea9817d463602ab5
candidate-7c98d30f9e51374e9ad59e01f1276559335005a45d3aea6ef8b39c998a301a92
candidate-2ec375a6d2a8c0d44843dd6214ec31c902526553f92004d383b1b83129cdaf6e
candidate-bb353f66f301be4704e6e64edb4ceba9ed35fd1dabcfde47e12af516a5806739
candidate-c8041a2b6a49eebb9b29cbaf16d6741ff5459609ee6d09432e911a955c3f68de
candidate-b728fc6abc4db0b49e0fcf3376c6314872446f2ab0f520a1111f30abb6c857bb
candidate-80064f4c7154e69698c6b9eb636f9517d9b1962ad06ca6b3ef45a19aff23495f
candidate-b1cc514176e80cf1e65e9898bdf12a8a9540bae890ce6bbfa12cba65beb83fb7
candidate-e3a957a4ddbc885d3d6ebba44e94a9a9f7713518ec015322b480223382e3b352
candidate-d7a648968ad5974e346095e580ffe0d921cf44ff2b88ba0a0f761f49168db09d
candidate-b1d8f7b0758df00955613adea0cf866cd09c2d8b6e37690f17f4d13b394fb20e
candidate-077326cb09440f019acefab2c40180a2c154ee7b4bc531af9964d022b8d44378
candidate-2f9c7584bad14a34e77b6e1216cb5b9dcd567f778c89fa293230e1e3d391a031
candidate-4a009b118b2d16ebf69c4dd91e427228db2806a96f6d42dd0e3909a9950f3ca3
candidate-df9d1fb7ebbc3d0e125252770c21a0c38e876c02fece8c3e702cbd22692982cd
candidate-34b8aa720aa82d84b54a2b1ed625d1c15a93125826e70254eb32df632467e50e
candidate-ab2477263bfe9d3bcbcc8b24ab7f1ec565585018256bb0a98bf31e9ca36c5259
candidate-2223e9326e915a27b0a6333d8ce9d3a9265bd88cad9a04923321aa8829ff3308
candidate-95d5b3df40399b3b60008929ae25a8cd230419295ea71086500479ec4170c36d
candidate-eb1e770eaa6d0a63f1450e21410ebd3ca0538c707cd32727c99affdab1370aab
candidate-c09ccc12cf4ca8e21180763e9292f8cc80039708b1edf7ce1b4b6d03c0e39283
candidate-dba17ceaa482117bc383d409e2e4568e8a542129519d16051e7c283da7a4dbd3
candidate-3cbade0bd857d3e3b9a7bc4850c9f5fb4914655ecff4165b05deb0d04b436c32
candidate-da03f4a54e1f4823edf37fac836d3e8327edcc0c3590fcc3b6eca61345a3de4e
candidate-6296b2331605cf1ea3b0645f6656c78498a9e1396b2bb8bbf10c92fe91afbffe
candidate-5a10d069611301a7014a671769f848666f76507b7ffab42c32d93658ef95927d
candidate-707e76219e664ce38e29613882c31df12b7368d19c22cbe8abb1a01b70dfef68
candidate-53b0a68b9b494f7d48a03c7a51ff6ac2832bd97a192b5e5f763bfd3ba2615d9a
candidate-47804b50b0f19cffd0dfe25604d87110f29df44277d8881fe2f0e717c78e51d5
candidate-ea6635e304e08d3d9a22d0d3c677730833847444720019d4a4ff090abd90cacb
candidate-1127e63ad7b68be563b94a2c6da37eb992815c4ca755dce9548ad47c6f51cd01
candidate-225dc072eb2e8cbfd36d47e76abc0746de1d82bfb6bb10506f63100461e21d76
candidate-4420ce6a8fece4949b322282b3814f416f94bbe5282c1df5ed744749eba985c5
candidate-c4ec72c5b63109f4d32c7060777b018648308b6ce2ac7431867a832c87ad5cf0
candidate-ed392c0847df321123252a8b4f6d0fd16559de4bd6dc00b2ac936a0d375fbb7e
candidate-ec37ce13321ed62de4da683941ba40dbbf02abfb1d8f164d34cd755be7927cef
candidate-311f4d6d29a00f6209bfb9a14e44b20bfdc7020d0569f2c5229bbce9130f1986
candidate-3560eae9d396000f963dfc1a84204ae0a6ac8af4eb3d83637c9f5aef668305cc
candidate-f4da26d52c592c5e500de882ac61a19a7d33e28f95c5056f9e513ad3b73818e2
candidate-d236d6faa5f87f86c1bbf418f47a286d7c3ba15d2a65f44a394f5c8d9f8937c9
candidate-613ff165f43f94692d3be6949890b9ec0ecfb019afd030dcb7efacd646c1696d
candidate-724a850a715d7bad5c4602dd25f9ac3067ff78307bb24b940c0d160643c98f79
candidate-e96012f80113033962368d03a5a3f42fbb879cfe17e8a07d660d83dfd2fca60a
candidate-93b151031bb6a0bab13fc05bd967a97490c65561a7ce122269546049cacb0897
candidate-03ff86ce7cde7d3b61f9caffae8c8a1b35233b5d6de84db3d7864cfdab658013
candidate-6e84ef3487f4a9065113a1539c3632b64f5ad09bcdf073c23383efdb81c85a1f
candidate-04e14f642b0273dc73479d4eaad5334eb341dff5f57fb6433359f1ea124296db
candidate-0d1870532932c3bd359924f94c9cc34c7c40cc7479764a78df1e00a712f4580b
candidate-2b17ee759bf83233e7e7497aae6fd70f4f263aacaf2950a953e84d84470f1445
candidate-436a756cbb07df6aee74f2ff93cd34b35b5078fd972078d47602fd460f2493ca
candidate-fa09b4d92eb36482fb8938de0b65b328dbd20936d2552e7eb04a03740d4555a2
candidate-008018b359c1d8cdf3718f29fc2f8270b6baa835f0c3efbaacd195beb4407692
candidate-e1f18d398bb1a05e52984ecc246678d05f8423d08e7259ef333c7705600343fd
candidate-5e42f5f14d7440e00c9ad90333aa87de4d822f01f484c32404488999e4684e6a
candidate-c7a743d5456f5373f714334c51ddeed29ac319a0ec3d65eac3766b8bffdd3c59
candidate-6b2c0bd1e4232347f67f6b34d4e2efe9d5220b30f3ed7383f2e88dfed207de4e
candidate-806bdf0463469909d27fc3e0783e6135fd52554be3f1f138a0123cde0b519710
candidate-c322f9ed2c85b6f2cc90bade44a9c0912ae098cd8e94d25b418522bc6b163012
candidate-68818c9c53eb0f5786d86a785237682c056b7948d2a5206f2dd24ff0fe9058d9
candidate-dca3ac4759da56ca773654bc959f25ccd5bba8020e54e71d34ca19ef83abb7e6
candidate-e52639d7b7ae2d9bc3d71ae576d41526af401a81585fb66642e63c93c03b00f3
candidate-440df87dd97cb332d17af3b0f3a38d71e395fcb76cbd06d8ec23f0e6aa9fe0c6
candidate-bdca11cee74ef2a2290cfa101743cca2442e5912c225357fe9a86b517d90fc20
candidate-5f5f19b0d9a52029261dda6346ddb9fee763ede8784e5f98970f2538a4edf606
candidate-67122f35a22b0142bd00608ccadbf0c9ac8dd4b2159aab270e7d2c5006426f4e
candidate-ca828c90b6748f287a2c6ba0dbb0ca472ce82ecb93c07e5df7b1a47c0d2681bb
candidate-844a362e7da96b3a0b1e62071e47962ab4f1c59faadd400f9390a551eae688e8
candidate-bc6f0fd294845113da9eee4acbe5cfc159586cdbc65039859a45235b282f656e
candidate-839da8fb0357bba2dc45e9d8ce9c713c51762690bd1f60c7931fd49030957571
candidate-17ce43ad96331b7d71a2cf71b6398494f4c8fc2db707fd6a3f52b541cf04fc66
candidate-cb03b6ec7e66d906167b39cfd157e1e189518129f107a11c0cf798408b009597
candidate-a14496102548fcc57a9ecda96cd4fe7eae41b66c3251d19e1007866ee706dc38
candidate-4999ba5f95a9f89dd1eefc93e6379c0b002cc958cbb5ce99bf6968670c0ed998
candidate-181ea89c7cfb3f89fb50e5e14e1463499cfec2d60f466abc442ec5b4b41b5838
candidate-8df2a2f961e36a6e11c58e139a2023dae0fb910f960b0c19e1358d4b674bc046
candidate-fcb171541170dafec42c639c4d2dd8811393825da78d0893fb2db8f6f02f5e0e
candidate-df9cbef1298ed12cbcbf2a073e7dfd90d9cc901fba502f6afa6933419fbf15ba
candidate-0bdf1e13c46b8662335c6920f844cce83ce1680fa9ef769403addf338644afc0
candidate-bcdbf79341acbccda77c286475fe2ab606cc64aa9d61333d11d00c8907285e56
candidate-d938b4df930949ff82746caa5c11be4f08dd97862d23e4a8456c8eeecd5171a0
candidate-f99e4c68d7ecd5efa0759b529c03ecc1c6efecfd67435bbdbd3316baeb7f832b
candidate-642a0e90cb9c5241977fee675527dc65e5d33a85d9769a15d6db1496f353ce3b
candidate-b19a7dec0011baff442176baf63bd3f3a7404042d4a62cf118351e6953140ce8
candidate-96545434fc7e615195f7c92f3e629da7fd8337cf0e1241adbf00aee296ed17b1
candidate-059cf2a7a9f76d6e91f7e652c10c04137b3d29c190f5008e79209fa66c9f6207
candidate-f8b3276085419a95c8fa80d57555faba4f940019a7ccea0f9999550f5222c3c1
candidate-33f43dfb57f459a9c9fb50a108819b09ec6a51eeb36854199b7d585716a72a5d
candidate-fb836f0853ff970f4042ae760d6994b540baada9688b137949d837eb8ed9b2be
candidate-1f7bbeff9de8e673ccaa9be80e35265fcdbc0798dce35fdda432211003cc7d04
candidate-ef4777503670332d3025d7b71c217956020b670457884c08e5c806311580e449
candidate-867dd43e197337aca0cff3665a391c0e5b5320e3f25d7909ef8057d738c50a3f
candidate-22cff00b8e0cfef340421e12df10846138a11f1257a67273ca05648f0b884de9
candidate-90ef72b3722d4469f568c022873711176de7bb6e919d7eebd1fa0b14e56fa6c5
candidate-713ecae8ed1ff95cc55f07dc50e8501d034408e41999796da5dcd488860e2246
candidate-e5688886b290e86d402168a6cc6eccd5f1c37b2e74936c156aaac6bc806692de
candidate-279c7cdbfc6a2308d9ae713ff15872f2c0fa3ec59d26354c05a58424ab5280a8
candidate-92067493cfad5020e01088223ed954ebf7abdfe5a2f37c6fb99ae8e7423d8480
candidate-0d8183d9a64e50bb21dc91914ae7e77b20a0a094f2d3bcde4a934fa3a515449c
candidate-91c9b87a913ed715e4a5d26e86a95966e06df7421b2d16fc153f9bf2a6c8bebe
candidate-f12f93999252fef6ec2de37a811b7559571d080677d9fbab6bfb1117fcc97573
candidate-d7c061e17e37ce7da319ef29433785a96729c1d2711b89a8222193a0d0ca99f1
candidate-12d385923682e99928765c0620eb43153b4017ace5cef7e3188057abd5419f2d
candidate-c264a4290c4610b60ed32bda0c137009651b0a52bcfef64187ccc124037cc77e
candidate-be72f64ae14cbd8e98933b00bc7ac79b5117ceca97d4dafc772934bae06206cc
candidate-c228d6a47014762b6a2714280c04f35401580edb279ff70bc47e2be410373c9e
candidate-7be8c629f5dc0d3d659dbf31347aedb8c1f2644c73a940d15acc9e3f305dee43
candidate-ed6276809a4450a0d0b90dfc6fd0ca74ca34575d4da9ae5f3fe79c5877281c31
candidate-3b63285278e09da2fe30a01a3092543c2532b256d0962ece627a2bd65ed44da7
candidate-affa4a282f13317a8a81a985da7e36c52bd1b004ff241b8b8bde002463c353b8
candidate-22ece3408c09b18d46965d3c08bf98a53c7dd273a1e1df5262f67b9a42fec7f5
candidate-129a35184092718d5f574c169e95ecd575332b97ceb9042f5950878f853b5063
candidate-cf2ef3fca8eeaf436536c18850ac6b37603b9149e6386169213714da36c662fc
candidate-e88a24fbdc6d11203778ef67eac823a5330f4008a6a110efd2426f2c54a52ad3
candidate-ed78f14fce859c55d143484227bd83a6239cb5e012f322e0647a6f1248290d81
candidate-50ef8e5c1faad037fc26dd5d6c105451f9c9efefb9db2e066d0001dadea61fe5
candidate-4a390203cc663c2df850a45c723d5c2f14f8243dfc31f853df51446d23ac6211
candidate-5cb7b05cd840be22a512463ea195ac840bf706e052c0ba76bb5fe16ee9e29043
candidate-f9dc4b431beb591935d9c4b47790d441bbfc89812e583dbfa06d35bfc4cb88fb
candidate-7b82b519b5dd6197e16dbc35844a963b27618aa6eaf273721c6b635e8156a195
candidate-e0fce9438d619d8b2d11c1ce38b4ee2c6b9981ab30bbc13beecadeded2083892
candidate-6e2f4e9d3279dd29c866e0feff9b15af68ab89156fb18c4bd7e49a9b01a8b145
candidate-89b615405be30187a02197604c469ee653473ee1ddb996644ce45581ffeb3cdc
candidate-0aea1c6feffd5f9508de36c7565b56db0179c7707af428a6afd4b4fb0a4a0bf4
candidate-e4a89dda466b5c2c569404d68e887bfb3b1ea8f43b401d933e48f126f5457571
candidate-9b38a5f13eb0abdd0c372cd3ffcb6f0e630bbfa690cfc0468ba0b63fa3534b7d
candidate-785b71e717aa98873589cc4bc0be181cde2acafedcc8c18efa42a73b6cfd7ed8
candidate-45a1412920ad5aa78548106befe1a9d1a81a6d8fcb385d03e4a6f3592eede931
candidate-e5ab29d901053fe8d92c2f51892e042d17c1ae3c930c86c1d5742f6e6bbee128
candidate-e01e451aa2e60f1019400d6250e37d958f74421c4f5348b81d30bd229b8186df
candidate-4cd238b5a69859585141e35571e1ac51121e12e57374845e8c572d311623ff46
candidate-d381b8bff3dd3dda452531245ddd01c7716c951f14ec456c44be0da1fc83161f
candidate-ade87e8102decd90c047c2296f5a68269569b576e140077e1019f5c6f822dc60
candidate-fb66dcf68e9d3516204f4f0462152101aeffbd174d72f80c2af4d6b3594f6621
candidate-6f86c6ea166a7f86167ab2b440e8f0ed10d3188e76ce9f1c27bf00bffdb8f5e5
candidate-cbe414de87d0e278ede1920e0f35d79c344c3e660c28dc2a7c684daa5ca9ee48
candidate-d762a9faf6b31b7840eb51c0f5e2314a9609b9f41b87436538b3c0fe718e6065
candidate-d2b61246730791e37c0d389a0b345f6ef1abffd32860e64d2a4494d7a87e8e3f
candidate-9d1d466b19b345bf0d1586b63347f9e1264be36bb546d28f73359bab893de9b8
candidate-d12c9e3539ffd355abaa352030da5b5923e525bf4a29d1dc9e0271e73e93d43b
candidate-18374c93cd072783705b0cd7a677b25b7bcb9c19ef4cfc1215cd52e0bcdf09fc
candidate-95f247a7b3412ebcd4627ba850d86b53a9b992c552495a6e3a5208c93e01f7e7
candidate-72c5fd17b7628fd796b69310cd2737b80605a79f51659a4b166258163c981b9e
candidate-dd82f70ef2c6ff4bb726e77dc074a62c2e2ad5d93abc72e716d2613ee23cb85a
candidate-071470af61067bc24e003883b1485531e157fc61ff7b27a7e6671c630539f432
candidate-9bbe67ea6b24499e8c3bda96a687812663ca52c982d1530350b93366b7d46b6c
candidate-e673f53045e95007d4dfe95a47929e1d22a835e54beeb953babffd1b3405c01d
candidate-a413a95f94f07aaf74d993d01e496f30b89559ca31806374d01e09cc951c7cd3
candidate-e91468d8e75d9a4835e8884105b4739d74160edb1a18fd7f504cf81dc31a9eac
candidate-b801bbf8e3f05ebd3c67761ca906a516316d123f7200c658f8188d5d28f67a48
candidate-3a59df03bd17c7f4f4d4086bb9adfa62d096f3d452e8f4f5c38c895157e0d56e
candidate-e9f7ede64004a60c7fb18432f4dbc793b96f50494ed1de55a7fcd2094e56ccc3
candidate-0c5c0c8a491c01b609443c4c5146499233bc5efb594ce7bd4edd4c5b8077fdb4
candidate-d714d0b4383677e87ad985016068cb2c471df33b0adb2bd904a8c721efc1511b
candidate-deb8009ff25a59781011b88e8274c4b10a2961b18f3898ce83e5e9aad652fb95
candidate-1dd4f534355138740cae5d9c1c439148ae1152f22fa2d29a64aae69f92ff6125
candidate-7333a81d5a37a9a8c9a24dd23684350e5a32bd2030d08f143786ed7383abe45d
candidate-8481454484ffef16b950fba9d2493e3616809ddf299a07338b303b562fd81d0b
candidate-f383cc95af414b10c38a7518593ee32405adce93521d4efce0d9d3b94857d778
candidate-55796d031f6f2f4fac8d8ae9095ff2aa1d3940e1e0fcffbcc3f53152da9ee4ba
candidate-44f9fae1aecb1b92d2579cf12e533548e00e1cd103d5754a24d4319cb15e78f6
candidate-ef0b92935f17c0c7d2badb517611952741b9dd9f42783234fc1c3659b09cb307
candidate-08a925c04431ccdc30a09cf16c3ddd94175eda6cd1ea6367930cce208f58c698
candidate-21a7c3406f210a1d0f616b50b0220d1585d370b2b90c146d1833f82a170b1f23
candidate-fd2f3ca711a64f17ef92e3e62beeff8f8dd5edb2cd5fa3ef4594ccc4c3d482dc
candidate-d2b1384e90514c4512aab4f015248c5227474646acfc9b961eb3dc56e1cc35d2
candidate-e3804a8c513bbe9f5d1025d6958be7e7b9bc0e91df5f1b10e0bc8fe160caf2cb
candidate-0a209fae2ed230781fe4d4fa9d46687cff240fb0ef062cd4d632580c75997798
candidate-354426019265c3f36f46332dc4676903fc7c815dbbd091ac11c4c0406ec08fc1
candidate-7e0c1fabac62f0423c2e66aeda85f03615585f9576491a31789ec39f5f1ce6e0
candidate-3ef1a0ad73fab2b3d96640500cccbd5b49889e20c94b0899add0fce20eb3ff5f
candidate-087da9180728904c1e9303d56050dde77bda3e10d672a855f9e36464a1c197b1
candidate-7b71aa655ce8f221ab3986563c5359b2125197f6e1072488582a4e4d1c27dec8
candidate-0ba53f92bf52142eb70ad6e7dd394439021b19704272cf9af36636acab0a672b
candidate-a88698d345252ccd951bbee441093d3e1f3892ca85ec5d68f441567d53faf05f
candidate-c4640b265b0e1c5111ab429e67129acabc7995d9d91447a36b3eb661052d7f71
candidate-b66f1a28dac9d67ca487776d3cbf663618fccf5b22ffa1e8ae5522e0608bec24
candidate-905f81f85e7c359bb564af974139dfd352edf7beef440e2f1825d224cf519101
candidate-f400c5f2a18847110dc1dcbea5ffde6e57bbb76f8048bb85c5f7515e5a551f9e
candidate-42baef0c33dc4c94226eb1b4c5d2b1b32218e14cad2d230787b5606ce64b8d34
candidate-bc1ac5f0f082fddb0be72a6c5b9c76e9f86096e4338742eba2b8c0fd1d028ffb
candidate-68c43321a05658d95ca3ef5f2ac581c9e026fc52810bf99e21139c7cd7b544f3
candidate-64d0380018cb454fd4b69f097c5ac2dc66680304a5726a050a3851aad756e702
candidate-4872919c6cd7dbae0b00d671fd4484d7d2249dd4c4f36e27162b8d44f7689eb9
candidate-c229d64fc164ed76d7ad982799025342cbfce7583ed6d8fa9e9bf0fd91c7e514
candidate-4b9f6a28a68c5cddc9a1e8cabace0413b9c3f1acbbfa220fd3030a29d291ec66
candidate-68afcf00755175722a3cb5393dbdd0d5481939d7ca044dd244d7e5dadde10dba
candidate-d0400ce6f15b0244f009ab79b96d41686d68b11be3aba0c9492eb18821b1cb3b
candidate-315cdbc2dbef226fa1837e1954896b20d475c5d2a2a617e7d42f15e87c1ee157
candidate-960e49df09aeaec11b7ddd0ae97b71ad7c0e71af3e63ef836050e59bc86b5e92
candidate-9ecb9acdccb5ed391540640c3760c2ec7e787c323196ff313713cb1a11360180
candidate-d380a118ca6a6bb119c4f29c57acf4a4e9f89679f01aa7714a8b9badb4c4ed71
candidate-279bbaf37bbdef5a6a52d56e828ddb44e0bd94e0356010996a7805100f987c85
candidate-860ca12ab0b85dda2b2bc4c9176090135af3c5503e3f04506a696e6375d04d63
candidate-1b7c239ff538d8c49111c0544666598ca759d5622757bb439b6988053c22db86
candidate-3cce2be4c4c5491756726f3de50bd06b8b6cecfc88bcd92412555fda5ef1a44c
candidate-ea28149b3fa75c49d63ff647dba88324c1fb832a3fc3f226aea5a46562a44f4f
candidate-2597b9409c793f2fa27288d028868f8dcc237f91e881c8c8e21861f1e76f196c
candidate-f1c78568a10e8538a1454e68bfe1778f210c9eb27f1b86ec4752bf80f4615531
candidate-350e0fb0d2ecc45ed4e09842f22672d66e37ffbf8ad91b2bf50cae30afa42e88
candidate-3d9917ceaf2f594880077aa8449d76da0491b0b7075fe49bb0f6f392444715b7
candidate-37c03ba03e5f5d7d5ee8cb03942091f72f1b4d3b2d903e9582b9e9cd13a7b26b
candidate-0b153b29d8e9d8166d3e0fa11188ec21a4bb5d6aa40b7e964dbaebd328f9a10c
candidate-a428247b200639e7ab420b91d90376f9c6986db390c60199dc47ae87362c34b9
candidate-efd439b0dbe5ee3053534a02d5e4f67b06241d1485408aa62e61a9efd3bff495
candidate-582759606d188b77c757fed68c8e67345396afb9c6adaeb3f2bae9a3aed9f55a
candidate-8862104d00549b09753f928bbb4ac2edfd4354e103891fce1a7200fb48e4f6e0
candidate-8d23b650d8fd2dd30b31ad8f024c5af92210bb17600d0325dc572e5ef646a07a
candidate-83e5f581db1f7d88fb95b07f1a455ed1bba2b47f6d3ce63aa93c1ac22c3339f7
candidate-f3c97bc1482f584f6187947b9b0cf0cbc251aa52143049e287aa9b7072e9e415
candidate-f6f0e10729d860df1ddad1a1298bb64f82c3f683790f849ee22b87238331b367
candidate-f51c01608cc0da79975bf4007dd7c0346eb00034426d02844ea256f7ae227161
candidate-3baf5a9f22b55b226a36f2cbb369c7d9b8c1a2394a0472d47de98990baefa989
candidate-2e9f2817592cb82e5a7af2ceac9b551bffeba2343b34c8345e3274cee14c6eff
candidate-a410cc87c6cd15f70b910a0f37bd7ea32a9b7a9f40e89a0f54a93044226c4d0a
candidate-1a3dda38a4d10c36095990bb78f133171e20a44eac14bf15a6731b78756c155f
candidate-c550863d1277c493794e7476e5b613e9a0be209d9c66c2a83f1720e496420882
candidate-81691d27dfc1953be05488eda6fd5c72907e6809a3a2bfe219ed9c58521f902f
candidate-80c184a4ebbfef02e64c3a44ff4646877c3e7422d9d8b674549bc8f3da7ebdd9
candidate-7022b8c42a723606f96ea49a8635f5df4e6f36c7026bdcc283ebdbaa61c73f9b
candidate-a2ab2c4f4cd1c86741594362a8ed3f5a9e298000df4f633c7061d8064b2722a7
candidate-ef0fd4dd85c9fbeada6a3e60752ab3588544353e5e11b3587b91d32edac059f0
candidate-495cedcff618639ea01db0ce62fe09272662dee1576ec1318eacefe7d9c63b7a
candidate-4d736a6fd5eb5d2681f56c0a16889b376049038da497c38edeac09c8ad8d60cf
candidate-bd18d95ebaac25c509787bfaca99b9f3757c37d912c1a0129994d056dfb3149d
candidate-16b0bc6e7d33b552f16a1c22c0e4ff20c560fc481fd04656187f5eba76e7e3d9
candidate-56e1e95ca14a492ddcd25905d995e47959bb249e0d61e3bdc1505ebc32fbed48
candidate-44222a0434f81e98b505f9cbc7c4e09ad5dc994006e41ce1bad27a40e38a6785
candidate-19a151f49966c70c471524adcc30ca6443083688ae49c68a31a41e242c6b6988
candidate-d3b3f196c4bd8741892e8e1eeffcfaafca17d84ffb11138dd090b7eab9fcab5a
candidate-d89330717f0a0037efbc0000c89f2a5e847baaa040f56c89a6e73172a7abf498
candidate-785b0fa2328b63795dd68f870e88517f53620461a8b32c0d222b4006a0619ef6
candidate-a2fc4af39d5d13476a7d7141d32191f25b08fb8b12614d83e6e81e41d9d7ff19
candidate-96eac1314ba54f2f440898bf76b40b9317d4d0eb2adc755da0db6a864a7feb65
candidate-457e9ee80da376fe2079d510baa82114fb4c9065ced3cdfc94dd8547f98d75a0
candidate-d5522fc017c1f378710604490f02e46c71c3474fc13ad80c8ef39649b13d7fbc
candidate-c20ac70d5578a28549b055d0bb4ee24f9363e6c81c8048bb444e2e3e21e47ae2
candidate-356b2514151a765f18bf3a826024d760c9528d052ec5b1cd94407f9c9368b6d3
candidate-db3f473a4f7ca298a005057ca777a605f18b8f32ab1e700581de7aa3d366a778
candidate-c4e66714b4361e17bfd49f18e61d7fafd74bd0153e7f8771dfa00ecb20caeebc
candidate-79b2b2d08191e65887692763d86e8cfd35afaefbacbac39e75b6e5583b1def0a
candidate-e131a59380a762a8aec430e43fa337d01e548087334e448ed7ce9679389572f3
candidate-76f9c7f8832154d35bec17ec89f0ba4368a7835ed6708a87184c288eea53bdc5
candidate-c66ceafe3e41c93b29bbe0705e87da3a3f09e423472ec75a3318da570bb40069
candidate-7da3d5e3edf18aad81b20006098429ca72b3b528afef065e5ac38851b9fe3d09
candidate-ed33edbca1fdd4a6f2ff7c3301bed264d9eaecaee2f33be828c53f61fc513e21
candidate-5b94830b0a34f28debb4d453600847f05db1eae274630d1296038e9e3aeff5b7
candidate-5eec3c3640e29907435e96fe1e8aee365c56abb127273e9b72bbb5ac9ed99b6e
candidate-41d416cf1f9fc6956a356d1fc69f700188ec1b357f471ff2e130ba2614583815
candidate-2cfba47ab80acbb8a8c253dd7ec76d0232a76e18b68feb9fd358c7fa9346926d
candidate-25bbc1022e5e1265cf62ff1645ecaa6bb384a551ad55fb9f574d93725d34ab74
candidate-1c4916ede08db63b849667af14428efcd2a419dd8458d94819c0dc92902cf1bf
candidate-461f79b1c4772aa39cd612d1bd49c136d442acd415d8d8a51c062dd277a78ff3
candidate-dafd934a361633b8edb5e6eb9d22009ee12cf5ada211446229ae5f67ca70566e
candidate-38cc4bdf085700f780c7968ad7a6f42cb44342cae16bae92310d53cc7ebe5f1b
candidate-d1155ce3fd8a6dff8c826aec645cef1471728d8f7126a041fcd8d327cc354ed2
candidate-d609aa93027b9b355b775b2b5bf6cd2284170f271d076a4a1d67402992a3f30d
candidate-75ec5f9b03d14225e3282a52c78b953085961958c8ef730e2cb0e9f6061c14be
candidate-b0773d3b1523f016216d5878a2f3865d4e07b28e3673acace37d3a223bd0842f
candidate-a35be99e3a09c6e1ae87745ef93021dd682c7803d5c637f1f8d2fa84aff4dbd1
candidate-db54eece5e96643352e15bf6caf09c7acabb769019557aab1afe869429085556
candidate-5330ff7b9873f7c8df244cd4f97cbec08fd99f6f914d0849f547663bb42cb02c
candidate-03abaf80d87ab7c96f8ae048620ccfc1c716550e4edcd7a475fa7e04a400c589
candidate-05669482e83539111e7e1ce231fbd193cd8a403453c85a2aff54e1c1dc1c9f73
candidate-459bf0d704ac866679c6c9286c653a61caee35b43439d9f4e75f2a2d6811aec6
candidate-2d5dc07dff49707334046eca8b832f7f5ff99ff468aabb23be056c3541a1b078
candidate-9edf0bfd190b5f2c09edfc97b6b087336bc11f2f20f961c3b95e6bf6e4784513
candidate-b94293200de91b302f2aa0350242a65b928a23aef4186cb9c0726c2f5a41042a
candidate-1e818f7949b6de30f49243ba026a89f9e7cef8db903ff933aa5c7c1c2c0d8c0b
candidate-15fb89fae173b6ce8b79d94c38a913b800e92aa725b38a7539a925bb4d312796
candidate-fd5d17d21b757ae8836a402db54af9172254958ec61c1daa89a6237d3875b294
candidate-09f0b2408b36a043c68e8927853555c437fffe3055d2d08f0ae5fcc3046b4055
candidate-db27995842c9a3aa5c6c73e43609a377d6ec24a79ebac237a05002061ae9e4aa
candidate-170da6b860a8780196d6a7044f26f689488a61a0389184ed747327407ce47906
candidate-63c214c37fa89264cfaf658d93e6031f01532a994e6747352152ce65abb598a5
candidate-23b3472bc6a84b193cd249fc13015c602374687905a3f263f96afc9745e38331
candidate-f1b5625a41ff147d34e3107fc5e0daebaffa278e6047c80678dce1aea419859a
candidate-99b7a3d892c28c3cea4bd995afa64eb9069d65666bc91b0d272557ee7ba0777a
candidate-7f10c45ec89f14deee3c8784663cd295adf1eca54e177a7187e3398fb5af70ac
candidate-9d1eb93095218edbdd7295911da19013cdc8d7b11c23f9ea702d553ec5bb270a
candidate-a427cfc43670cc8f7c66b052e39744ee288d4bc7357608fb6065ccc4feb1c5b5
candidate-7bd7bae3da38b4cf48264d16a6e8b6dcd616c1c6941edbd8bfc44fed77cd0393
candidate-e20c822a908952fb894d52bca49c64a3f72f26d33cfea3ca6ff2d94c5c6630a1
candidate-5dc4c8dfc9c297e72c5f008af964a7c2d24a912c41a8b7dba78e7fc08627f71c
candidate-b848d7ea3504f2a7341a4826f4cc2c18402c43dd32473c05701cddc97ee26c4a
candidate-389c4b2fe87e1f24a9e44e72873504da39c390771117dc3bebecf1195b43fe32
candidate-d2f3eda8e69f77f46d05253b3f5ed31cf7e52ddf6132272924026b4e43203e6c
candidate-bebc18c8667424890ead3be03869b3d4134e008008145ea8b91dc56a589f4afb
candidate-e8ea0ed2aa6562b12b5b56343a57abee6a9b8ee086e08ab871eaf49637ad7525
candidate-404f34d46d1045cd759f3e4288195cdce8f1a518ce34adb24ad38ad6635d0eff
candidate-e087f363f89eda40bcae3b366fe22d630690aadf2e62654e819a9c45a14ad5fb
candidate-09034243e759e7320ca819d426da316ca8d866f28c2692e2d7db3d5f0d11a1a3
candidate-9281580905677386ede1fb481055a72c8ff845edff37233ca5d4b6b0c4f9e0b1
candidate-97e3aad9c54d4b4c78298cb6bc41ee316f3fcea42eb166c663437d7935797f29
candidate-907b676e0d4885e431573602e1a0071d82da67809f0cfdc02b0414dc28161900
candidate-087f3d58cc6e66fdf4539e564c5c9f700c4678801268ffe217563ffba7eab062
candidate-404e61ed1950b7bab77f7aa607de6c4469ac153f35260107fb5257c21420540b
candidate-2382552feb3925b37a579ffe5857f20575bf3275301e0b6549de9ea79ad62695
candidate-d7173d7290a233cfcd6a2c9ef1aa7183d4d4c30d757bdfa4c1b1afbd7e0aab50
candidate-87b6c689dccf959559ec9115957d91bc99428a67809d55f545cb181d85f63f04
candidate-120e1953297d99bef80e3e962dadaa777b677ecdf05462fdd74c0a36ddc2cf12
candidate-4368ade60df96d8af7a8d77bf699f84435863aff3290b24c534dc1d423b208fc
candidate-f44c00236d2355782692b7da7c0a64d517eb74e25bc7b5587d7eb803f6ca61ba
candidate-28e8e68eab3df46b69f1ffafaa2a6b35c81a234ef7a43701d0e967e0c79efdb7
candidate-b17617972a17cd015989ab94db9952b03d6177c0498a341d2196b11d8ac98bec
candidate-3200ef59f0b783f9a5f523ccd11dba5dc36a8455b7f90f39220cfea5c8e50cf2
candidate-b64f69b97cda725f6d8904532392ad415684ed98c3d28ce72fdc6f0b7af76da7
candidate-4c6e811fe6e3b171a1145345de06258fa37a6252ba31e2e524abb2907934097b
candidate-d6e3c226880fb1240fc8f3cd6c2805766c3aab7dc064dd22a3fe7d3ec7262d64
candidate-8455b98e695eff2594b81f891d8a81a957c39f341af2785184d855d4560575c2
candidate-5aa432b5df01fc90b429efdb01d1334e19c60882128ff3f57846dd2f54c65079
candidate-f437078a851689b084548ca41b4849a89e5cad9b99d69459ba546a322473eda4
candidate-b138ebadd171ab6655bdb41dc3f4ec013067bbc14b7523e43e83decac0fb7fc4
candidate-91e0c32db694db6187339f8a45d7e59b7453f99e3c8abf5b90ae99455ccb6c28
candidate-77b70fcba320408168517d0c2fc07262aa42d123337f6d005807f95f593fda76
candidate-7afd7df09efc6824704305dd7fdd52c7afeb8f9f223cabe25224d44ccb30b1cc
candidate-53ea398f952a2953c047a1e907318e18cb08a91e5c1cdac307a2c55b63abeea0
candidate-2a1972a4998ede12be8644ad68fb3f5cbf2e4af9b07b739bb3bcb614869732c8
candidate-2feff5354aaa584ed8d132036aa4bd3f26beadf5ae35607001eabedd2ef9ee73
candidate-4569880eee8b3b5583df08a6711c0e91bc9219d8ad1692b4f1b484d3c043e001
candidate-616efced15766f9253ae8260ae0843d0c9c0ff13e0de1a79859953b454bad976
candidate-c3b8b632afd90ee9bbab955c319fc44b613cd75aaf4fec548d1e2d0c891330cf
candidate-98b0472ed527eaa843f21b3c8d17446b02ce26d85ff6208c6548bcc7402b9fd6
candidate-da6f41c2a9db1184d55ed274bb73416002eed1bb4b12174c1dc1da4c2ea92234
candidate-75fee1407380154c8d750788baffe76f03de3d4d11de02ed058747cfb4a7c40c
candidate-a994980082aed74245e7e6103e2608ccba2fd2feccf2f3977477cc07ba951ee3
candidate-d1595573909e472cd3307714ed41094b0942b1996cc8d6106c33909c7b4e5544
candidate-b91fdc443af2f2ed86db59bff839360f0f46735e5c21ec88d1097764b289f79d
candidate-b4d8f2139d0057cc5e8743c9bdca0d7f05351e0d2ef918dab84b4d9398837761
candidate-a603c9508fdaf1e0a8b13dccbc791334749b668a266b358f036409c60509e4f2
candidate-27979fc349304658688766bd21fe5dcfed210e461ac09e944d886e9a4b262497
candidate-a1ae260b781da4a636f12c383540c397d0065dcf49064e886d62b81c720ec377
candidate-3bdec7653d3b4c22f2f2b444f18b485b3c602d9df451c8b874c5931f86d10534
candidate-540e1835745f670e86c8d934492a3cd69432a40285e13a75367795969c48e827
candidate-54516f63d4acdb7caa186e406e69e21d59fc56906f00accbb73fc5c4132dd7c3
candidate-7cac11c87fd5666cc101888157502a766655260aaa559bee45ab629ea1748024
candidate-1b79ab8c013ba7f61d1c82680766dd6a2ce0aa6e3839eff0899ae2d217618cd2
candidate-05769ffe51d4dcb029becad94aeca24a40ac2c822bb42c8ee40eb87105dcaea5
candidate-93e26795fca10282739fd477d41d26c206d542d5bd348c243003be896f13a8a2
candidate-afa4d684638389b4bc673540555f8d6166ad1cc29342c361f66591dc8adc11e2
candidate-a6d0a80c6ca0b69ec274b117cbc9ad07c000fa0c8cd011a76c7e562463a36dc9
candidate-7460783b26ef517abd1ec4f4dc5a9524892d19b0f4cb02ad1e61bc85ec5734ea
candidate-c7cd4f007a2c80cb5b3f9985495febbe97867d1fd3a4fbe9ec701c42472faf8a
candidate-d6196c9d0b7472be937bcb1c85b5c351ba4675b8ce2388d7e01556e9bd78075c
candidate-6619ce1fe77809bf4ee530f6ba529495fb19c3a817e9137a268ff99c3df12074
candidate-dffc8ae1911b8ded71c3d7a90ac195a0fcbda4b07be87bdba6c572b67eb6d27d
candidate-3dc93c3220da7d2c30b82e7d1a082f59ec82d3d59f659566a30972e749721455
candidate-99f4a53914cb64620460501063c47f4aa5d10501436b4a3e7a99a015b414b730
candidate-e931db095e4f9f7b3051f5590b4665b36570ae972e6bd9714cb1b47f02934ab3
candidate-0975839228594260d9c8391ef6156a92a80d3b01a99edad8f6ff60e7dcdf1f1c
candidate-4b245214d9a4d492f3960dab40011c598cabe5a51f30b454ae184fd63b8791e5
candidate-2f9019bfdcba4cbfce809b303bf39b5e15072e9146d99cee09a73a9d7c352000
candidate-130fc5a3c905738aa46efcffe31e6d7c257f7329ab7b7bed83eff7cafd56925a
candidate-832c9c0781991d940baa8fa962915a9b70bec1505e212350d3496edc2dd9c441
candidate-df21e3bdee0de5be9ab1d4b054b647e5a1be5806674aa9aa25a65c3019ac82d3
candidate-5bab513e2dac53dadb173be6922433443650dfd437d9584638950c36c6c34830
candidate-08852dfd1569b2aa290eaa68ad26e8229a1325cbde915dda8ffd29428d2306ab
candidate-97e8924c80055a8f920c529013d526d0b708c7e291c755d4e0479415d50d5abf
candidate-4fbaa09340f7ab4d30e5d1c33d29c7303bbab08c5c6d07ae927022381ba71135
candidate-d815f261d997db19f51e71b8dd68d89b99435ca157f4621d029832502d856f1a
candidate-c9cdb1a0ef47837111dea5415732951fd6740ec969ae6181d4782fba9a9dc7d3
candidate-1b36c210a6bec790fbd2b8b33d62528fa74785a6478a2be42e0fc469ecca276d
candidate-5ba0257130a346eef25accb87672794e81ba137cb3382bd6a4d5a06b697aed4e
candidate-02217aeafd86090a54a945a554432f228cb790703cf058d8aaef09ecd567f411
candidate-51482a459539ebd0ddff20f812bcdb20a69373251dd8ff1ceffe12e643c6c425
candidate-5a8dd86ab1e43f295c5e1f37fa8aa56d801082cfc1fc580908286c125e504c36
candidate-f38635f2281a274cf4e7e97e0ac1cc2d1a84cc0cabe377fdc9a2df54b026083d
candidate-d10bb735ee5d1a646370c59ec97ea3e61ec14111b66b1424f9c43d35ee648c78
candidate-8fdff7453d59192fc1cafafbccc30e0365d8ce16f1fb01b3c7d1bdcb1a650210
candidate-ca73122f9179023e1e2910e64e8983fdc12db991354b718e32fa3fd97751359f
candidate-7b99e8687b9e099347fe7794938fb370cf9ad7783173f196d9c8230118726f22
candidate-45fcd0511e007d3558bcfdcde12092e5830a0c4dc417a71d97c22acb79720c6a
candidate-ec92a4ebb72e912b77d68927bc2e6b95c0479da6f1daacb8219ecfc980a5dfe3
candidate-f590b25898774c82804276b5c48e048be6a373e34f3cef498fe4b516b7d08ba3
candidate-6a1665c81439900e76ce37a74e7ce3e5b8eb5dc10f225cecdbdf2539f492ae33
candidate-c86efe9793a206592b2b212c0af14fc2b6ea4a3e51818ca4ee4855c3849cc446
candidate-4d5d17521e6bd1abaa9ce325b58d9365d19e83ada2680d5fee0f8f1b663b7cb7
candidate-9bfc8df55cab8a37b1e3c44636e342af27ae1dd16c2dae458bd4b7fe5dfbc590
candidate-486ab664d139723ae36977eabbf55fbab887b0ca9544f525bb78e1cbd1f29cfb
candidate-4d92220e5f9ddc817e450d327ce5bec6e2781ece3432f1da993a9f86622afbb3
candidate-ec209f20981456cfdc3f4bdd369c697cf62292f4529fa9588f76adb03ae24896
candidate-909c7d53baef64ea9efd6b8269e84e03b0f1339bd47d816103e5187b1e15cb1a
candidate-2af4c1abb524b967ef362afb3be52448ebdb019bf52c897107d9018496badd4c
candidate-11e7df15fea6ef2c8cf2a181978d353d8b43646d6eae94585f3504c34be49597
candidate-36825ee4145d5c3f2eac2a0a9acd4cdd38045368f77c31f96af13de33b085018
candidate-65f66fbc4595a166082f91aec08551eb96f85dc4e50c6e9a12337f5da2cf82b5
candidate-cfae0cf7bc969e6cfd2997d2e1170009f940748f3d638d10ba0205ab8b4fa857
candidate-6c6a5a09c72c9504f69e0cc34b2e6ed06d1227114081a586c13730d081582ab9
candidate-0104168b072713265ab3277340387f1b1977a72334a3da2b13e71d1a182c3116
candidate-cc2ece6c3fa250f38837c6d8d3caa5a64980fd74b850c9e79878d142325144f5
candidate-5c93fc0688c13cd91fcd255e26076bb9d5edc7b7f5528cbdcac444824c44374c
candidate-bd845ed8a6e04b69b09323923c2c090ef0dfe60e0661b03c765c2570d172b98c
candidate-f48daf2cca61a8a27b02c08ea7704172e8a603ed7591750678d0b2518a8c0e8a
candidate-ec4f13766b40ad6ba350208c21fa47f521e3fefcf9e0bd1e1da5ed36d7ac348f
candidate-d4aa971d892d24b384c7ac6c73d547d07875aa1c656640803e9145df1eb3136c
candidate-979933bf377025bd1de27c841bd0ee5e34a880246347d7f68211b64d2a0bdeb1
candidate-bc5606c87c30dd6b52dbe86bf362b2ce4a90b7ad67881cac9aaec0987b9b6801
candidate-d3ab9cc5fcaba1f0ddcf7d4653e74daf5745a8e3a4d5ae5066f83980edda8176
candidate-262362c1130f2ffcbebcce6cbe83a984c409d50eb8dde6b47d41d560ea0fb735
candidate-43489acdc9322a2e0df782c7a2e9de13572b0beaa5e881e0946578e1a735126a
candidate-7038a3a28025b769fe2dd5b06d6045aee6e676ae1178831697ffffdd8b996c21
candidate-313aa5300cc150837246144fe0ce4659475fc06dd2d269f70f8606a590ad80ec
candidate-149a120623eabc6fdc76e3b3a7eeb66baa58957ec60f92a39ca6876041a1f039
candidate-a2a19498c0121a2c115b30c2feea063372eb972a8fbb1f0bf4e476c88f212be1
candidate-77a262e5a16bc94ef464a2c00ccf59513b50828c64cd5b72cd65f96a4724c261
candidate-843a5b336a23429f1f90345de35bdb72f3caa938d5b6c55829d5e8358af6f687
candidate-309f28ed1f8a4dddb6ef1a02e7eef058c01a13bd0944cdc8adb3407489cfa861
candidate-6706149afac72894548ec31f57b216cbc717d4db9225ae409198ceea46cf3550
candidate-b4ee989077c4516210dd794f31d5b16a0e6a9cc4ee9aea0ada4ce529cc08199a
candidate-0ac08cb0f69414f330e6bef39406058c94847b334ff88ad163df41e6f3f05e85
candidate-1a3ce28fecde7fc76a5412d892b5cf545b53325225da117c103ab3498f85e524
candidate-9be3d65b478e6448590397e6797fd44feff6f71f70a19ae0c0563d26b30f97b0
candidate-122666c6cf71021f6c24c2c1c07c09bc6d7b3a37f32e98ec1c01de63695789b2
candidate-1d25dc03625700a8a5043ddfac319094db702557358abdce465063b8a7f4af8d
candidate-37310b0599dc129f57e7d46bf52841705ac19fefd650d0dbdebda0ef6464d5be
candidate-3367a060dfc28b73855cae100218ff34c75a300d4548c2e0d6ff3ba1eb57de6c
candidate-3f79d0132e9ba83c975e60b2371a2260797e17ff201318e9ff5bcf8af2205b75
candidate-8622dc62860ae64c7957e4e6b7a803f0e775dfe6f01bb70dacb942405c1aa344
candidate-6647f66b06d845fe47acf3aaa6bd558cdde2594318f0a1b85e0283253b5b2c36
candidate-730261f3790147ecb3e8e9acd0814e2afe37c6ad53ae27206dcbbceefaf3e451
candidate-310fe4898a1109886611c0cc161c41226f62328b205c25d674d5f5e1ee6b9ad5
candidate-ef2ab6bb71f770fd74876172c044329934538d6b13b7d2f29c0f6f9844f63768
candidate-f9b90e816d1673fc68d85cade8c7e8639189fc44fb202ee0ddc6b153d14182aa
candidate-fd43867131b1e531bc968350430e51dff0a5c62a82d314c501a19fd740d10263
candidate-832267461a2df4ad9e4a86e8628c87a7367eaf78fcfb0bb1f3a9849a7cfafa87
candidate-dbb217a772b1168dc5e5714cde7c38cb7cb9ffa66ee2cbeb3efbf9832b45fa9e
candidate-d47b8af040fe4810ed0d01979ce8586197e15a919e76869ee8aad2dfd4880059
candidate-79672392684d42d02b1ca96f1efc1f6ca354e939e17c059f9433234664b4e966
candidate-cecaaf4a950be8d781a600768830c1eb969db3d4d9984304257605914ebd4ce9
candidate-933b316582f8e532d9a5ee53ed5d6eb0223951c173b5706eb4b9d1119650683e
candidate-65f4920346694cdb7ea40edb535407f30919544f6327137470159cf323902177
candidate-fb7b111fad19b58fa31b56af75e332a41aec44dea179e638dd4aa2ccc19de149
candidate-c40ff67ea225f8f0c45275ea9682f1b2a55bab6eb624445edfaa02dea21d842d
candidate-4ca3208332d4a5f449534c2d7f1c15534cdc127208637c9ab4af40029160e9b9
candidate-5bef0a11a1d3c37e95f628250d0c73fd60593557b9acf929616c6a114a200178
candidate-fa9c8e31d88c1b9cb98808d16f8b6430a367807b481129897fec1ff8ae167072
candidate-1746296260263c50bb087609ba2e1c9a267d0775307be42032e90c2e21e20532
candidate-d6df8245652e987a4ac45c13e1665521a9aff8d4f8e890560cc09534764c08c7
candidate-c0821e1937854ff0d130d2cd12de9eff09bcd687bd95c81aefefc5b48d0a4953
candidate-4067753cbff64b539dce6fef3ec775a26a69d2d28365af743d12e1551bf8fca0
candidate-ebacb086264ae823970891e0c0431b3fbbb845f262550158cf7793a500eef222
candidate-b027980c3a9c89f28eb62024d90c75fe61d4f607349cb0567b3924e1e103cca5
candidate-a84630bc3b1d27112b5d6fd5be8ce8120d7bfc63330ac8bb3ed0706ed5dc949f
candidate-236ba4a4c12e318c581b58d7448fee20f7bdfedefaa4c59831532ef442665c12
candidate-d29f28a070195dfbcb5c5cd4b7771d39c8e0a124b69f53fde819d7e41e1641e8
candidate-8a97033524d4d1b86f01c5fcc4f854e22c376a38500ad831f6b930c9c9b04a99
candidate-26a4bab59d39e8ca98b44d14b51260bcaddcea29af35b436a8f5078f4a51c199
candidate-f77af4577b2e6d6be2a675dc081dda7a65beb1671240ad5494ff43bea7c196df
candidate-f207d8c7091392be22e12aae302460c2339da1b7d87ed9aa2920546b9f1e01e0
candidate-abeb5df8b395cda6e7198e2b4289eed4d47e194820ce199d66841166551c9172
candidate-119b9b2c19756eb83315c2816167fa57873e1a82204fa331dbdae77aaa339353
candidate-60328416c6f53834a544c15b069287ae876a69954e00d86bf1658a275b511a25
candidate-9fb2f9fd607b1b9edbdef362a10ae69878e854428710024941736532be3a8758
candidate-8c1776e46c3bee1ba026f6d898a05a8b74d52a7b53bcf9c82bc80bfa8913e6e7
candidate-2bab0f49211fcd18318c7970b44dfac3e877222b27320a166eb2008232694b16
candidate-9c141d8d89d24693f4818d70463ff07d1025d1efac76b541a87ecd72014bbbdb
candidate-2c8b3bfa0a9cbf327606bab744df7c2557c902163a7c366a80b12c9b36e7d339
candidate-202116b768bb4fb5868f47f8e89393eb3ec1ca242a4360619bb3de28e1792ebd
candidate-13050cd3d0d0c42cfb959c2c3356c0c7901ce2caf493b54a8b4e86901ab7bd14
candidate-61fa6780fab0bc2caaaa25b0fb19a20e9ecef5bee8c57d77d67cc06445227323
candidate-38d9bd6538aeae13b2cce56054b51ce4f03125bcd9cb335ff084ebd097669ae0
candidate-4b0df5636aa91cc6be92eb1e053401eb5135e79d570d6293ddd096f807f9c41e
candidate-25dfd7a92d41a82460c52aebd3f1e074c61c4aa21e1a5904f2659856b8a3c78e
candidate-44a6c4daf01f1f3b29de3dba9358f564deda1b13f8f5f8bcace1c2d2405f8c27
candidate-66ca32de3c1b55552bb14eb75b73685fa7d024f0e27eb6256e375d24d31fb4d1
candidate-e65417bcdfa55c27aa9cc4cf68a14759ad8806305f23c6ef480bdd4417709eb8
candidate-1d8386ef71c5a8b26be769342dd5ac6321d979db82381fe5064a0e8d8dee71a4
candidate-2dee16fa2ae6d9ce02a7fe9f7757a212e7b459acb5eb8d0c50f87f13fabd6315
candidate-fa1c9a34a2466dd0b95e7e3cb872d1adea5bd41fbbb55613e58d7e6c3dbf1383
candidate-6ccfe81996c49e841a9a4d3c085d6b457840a5a7036400366f2cddef418490fc
candidate-e1b02df60c7a43e0368d05816b2e4b2acdbd0a3088c85e2330e5f79124b68103
candidate-292beb01784ab63e046646b096cb479dd19de813e0f5abbdf115f1126ea09d2a
candidate-c21033dd5261e558f515789c86a93b9038bf2728871c943ded6316c2a1fda1e9
candidate-62a86b158b34a864797b482b07e67ef64688acc4a7b542476870d50bb60adda7
candidate-9aef1865d12d05e2487ab8472f0527862e60712f40236b7961976a61bd7beedf
candidate-c882ad86e7a31ba018abb0fbfbde6f9159c9eb04213fbb63ad04879e4810ddb8
candidate-cff9a16b2d798e6eb4840e2a12f9a617d01cefde94b30230aa9802814000dc4e
candidate-9237c4d9c36dc39e5e8002742eece30b208124aadcd69d8eac34e4d31a95da55
candidate-28923b0206e03bc8645c18ce56e51089cdb1e8c833fc58dfaf03e0b91ffa2769
candidate-db0f375ff5234e02015112058c3f36304e865f8afd39cb372f301a58ae3ef402
candidate-9e40ae81dc8263e12056f23bc981123e5eef3178ecada6a3be5ab94965fff1e1
candidate-c1a828fa3852fdbff039a2bacea25d21358a3068acc74f06422d10ec23e43b7e
candidate-d913c919d7f77c568a89f715719b7b4059a6486abe9f5f9ec5b58c23610cb6e3
candidate-9b7b11e5282880b132f5921af9f2de2c2a284fa66d96cc44eac8e0680ea8af77
candidate-c26148a79a7ddfc4f4393ccf110b80cfb2cb91956377909e59b55747ad455ab7
candidate-c8e1d2c68d7614503cf783118c053d32570c19f1964ab5f4156706d30050f332
candidate-d0e9543429c80d581aec16cf428d3620152d0548de66f6519e8e57338d49c5a7
candidate-c269168356699095bf55d01c4e4a943f49ce6b56b810130f8977802ba765cb7a
candidate-ce744dd2e43c99018b901e1bddce267ad0de1f7558178b1c40bc40da2ebc5fef
candidate-cc1851ce1f7f5e2f4175c342af31c4856c2d7637da287adf967e3e141ab1755b
candidate-1e4d5ab6f58ac9d64403b202e2a05fbcabf2b8e69ddf9eba21beb667b1447605
candidate-2c639061eb4132118794e8fb8f00fdb617843a097a9ad87f30f3c0fb0b0b9522
candidate-3b8200d5ed5c7f2e9c880debec01220ea2bf427e89ffb4c546f6f1c5b136512d
candidate-9b10f90ba7f460760304b473a2cdcf885cbe6a645449253b9946b268249b34a5
candidate-b40f23d2f322e6a3f797847a067a4a222f51a0894b02a9a2c1f94decafd6f52e
candidate-0feb8f6210b7050e81dfbb6a44b9b13d89a5a0f77e8de112ddf3204631e41aca
candidate-d1fa040189ab2b59e2e027cef4ffdbc1725f8f6f4195fb52a1f4c650e81a8726
candidate-137fd7aa5f69504b6ae53ac5a2e714511d5dded07b347760d879cd77c61d5143
candidate-59aa7297817d856d0aa9dd941236ef00c479ab1abcddbe63157fcd594e3d2f1f
candidate-35d73f59981eb244b99f5a215562d1879aebab7c02c6bf57b40b15191d424076
candidate-99c3efca0617160369ae540a364b867b151af60c433593f26e6284fc9e59af24
candidate-062d51c429d3a9e466e76a7df228a00131630286e9de95ce8d416220b5648e69
candidate-89141703747cb22bbec3d6b945ff6d70616317a525743ef3891111142caffac2
candidate-7d42687bc243c6bf6a647d2d53ffeb2b33beb0a7c794463fecb097641592a917
candidate-b78e59d638be3368b01d849d6e774114505e9859ba83d831ab6b03c2d3768910
candidate-a09df68b398af5b2a1833a9491453e024fe95906f169975859bfd781c07cff11
candidate-adc17f32205e2f024b595e0c1a89c309e6533d2bcbd89ac75ead0dacac51b31a
candidate-9dad7d36dfad1a477f4d886d2f0ebe1a82c5b8b2ca0d6a75d8120cb9966571ce
candidate-82c7e67ba662050c87d627084256e7c5a744712ae28cae1856298600f41c9abd
candidate-3cec784850b52a3619d4ad54618b72a89c2ca1f87c75037a074b8b83a747ae96
candidate-c0a0feb23c31e2ea4f09ad3735a0e7388a30eb6c38f66180caa530f4c4949076
candidate-ab4534d7973a3af2175880a07316d1a112b6a5714d9cbe1d58221c0be9ae5ed9
candidate-eab8d893c40ed41cc1c4a6ed0c9340cd374326926bb347eefd66155d49490ed1
candidate-538456490af7cc81d9e079d0020c9d6473badb3e349ececc76b06936c62ebd8b
candidate-b9ee14ee87ce4be4788470f59496d27635568a04efb75019ffc52402ea90f6b3
candidate-9ffd743fc82392ca7690bc562cc840ae04e9938b0ff8e33da31e97a0d9bb3e31
candidate-96add75497b5c7d19be47a7ee458fe217cf41e5693d2e2f7d5ebd8af294a9bf2
candidate-a72c9d5a8313d006a66799cc6e8b6bf529cd144651e92d0cbe972206326d1162
candidate-44bfe68a78fcdbe8d4f2fc0027718a5e7d417f22fadcc96b28a2099f53ac667f
candidate-a3b0e90083ccd2420316632e40ce993042fbb5138e76faf65807fdbd7bafee48
candidate-3856b234bc999fffe310bffc8d1a9a83b84d8afbf402258486c1a2267c109150
candidate-09565d40d90c8b94753569631c6400e2571be6dc3106868c75d9d4f2e22489da
candidate-1e8ea09b29fce74c1c66c82d129e8a00e0ff18fe39ca41a26fa46aa280e43ca8
candidate-2db809273ba292e00bc91b26bfcb8d787379507048b9a5eb7022901c85d32adc
candidate-611ebeff0bb6ba0b1bdf644f473eca2905aabe648bc6d798726c0ff7243a6742
candidate-30eb5ade7dc909f076857f7c1c07c4c39f50fa6915b56e533fa60c2d8bfcc2ee
candidate-65cfbabfc16e5a0eba5d75b14af7ef6b77a4bd83aca6e42fabdea26693ac57b2
candidate-6b7810e8e591c2475004b75e7e0fcf001defb082b9e8a0891c3c9f5845e49657
candidate-acca66c9e42e122f4df20c0a1d4607340acd059ef413d1bae8ebcfbed21f1777
candidate-a9d25cdf51beabe89518da243d5fc0500b74014a3e88de1e1d3051190d25c48c
candidate-9ef50ca011719cd003f15a93378d6383bde924061f1bb26feba5faf7db1c0d80
candidate-11659d677f8b5e1ee34a5913bcdea3feb35ca6e2c27710b959a4e28c24bbe6c2
candidate-7f3868f434109f826d00922adb00b41687f389a86b426bebf59a9690d5f22703
candidate-14507a2b0e2a8c447c9599fcb430306b11e0b58f3b36a4d5f5e0e8300e8395b5
candidate-c3670863e88185df3aebb4ae07607c11ecd7fa606802993cb9e7f81501cd3505
candidate-83e9f77934f7ad02268b7d2f48102ed7082574ec9ad25b0738838d28fa249577
candidate-fad49742f2f18653562be1257add412b1ed929a16a3225134456ecb884c43478
candidate-e3b5ad3e6514b87d66b6f5407e467766a0d0e2f07caf57fe914019413c89abc3
candidate-85c143125fa45fde764da7c5c47754167a2387449bd6d72cbcc5229a4dc69f50
candidate-dc3f3c99621f42ec6fd100ea986f5aa1029c582c0458656241b8e03ec6f77276
candidate-90106702454281d0006d05a5b5ce544c254d65fa8e158e7406492eede6793487
candidate-9b2a970aeaa287813ea7a494eda97cc52809305ad6aa220a8ce0d296d71fd4a5
candidate-4f7dd31ce0a6c5cd2e46242c6eeb33518249cfac3df5c3bb2b68c3da9ddaeed4
candidate-f4c7f9e584255e087e357bf05b152f65c6ffcf3bf533cebe21346c9555de8e21
candidate-8f888c525defde7579e59324cfad4ebd3e5aefd16f8c2f2fbdb9cd7980e44552
candidate-b01fd543e7babcef055dfd03ebc71259bcd1083edefb012651906a0c9ce40747
candidate-9a9593f2e72dadbdd5a8a41125d7ff6d707d1641ffd9e54a367cf6230497e9aa
candidate-cd13e7819fde44f97009b9e37a118e40cad07aa25559e99aaa470f7b2e76c18f
candidate-4b46097e54b85fa22c237ae3a955c394b470ffdfe32eb68051455f2ced9f7fc8
candidate-baa4a9c4b5a72c787f2bbf018729a186c0030d20b5161482331724cabe341105
candidate-32e62c5ecae54a44128cc9b51ef69835f707394453f3be5e961af6ba1101a643
candidate-bd01106bf1f4330ea5279d0f457b380392b13194560bfae83116fdb28189866c
candidate-2fe4c0dfb66bd02dce66a5eec1f595fda02ba99b272194f209299838a10d2f8a
candidate-03a67a05c8036aec99d40fa6bbe8d1599524b9b01002d5cb6761925f31cb575a
candidate-9040f1550d9ea0df4e9b3465675c0adeca723912be7162d7a49e71a9e924e992
candidate-8c5b0140256a4994c6a422715882f98bb26d38e304a821eab320d769dc52084a
candidate-3fb378c944745fb3edb842848803d9502e88fca12d2bb61e1848fe538ad38ace
candidate-92fadc2523cee0636c6d0cdf8b76f37c437c284c22b8cd2ce1a096d5250d130e
candidate-50ec7d5a45ba5734eda4fb1fdb3be411cd5650d2fad44e0e5b9c2fa394470e26
candidate-b055be9ddcba4ff1c83a20325a716e51394962aa44e4aa4b431411d8ef9aa7d7
candidate-7f2414d7ff9d9bc0532a55c9a631f7fecc3a68ac88101f35c2621728bb658d5a
candidate-a6fd5540870a401e63932002d59f15b71cb16e8dd73ba8dbc29e312e1656d461
candidate-b716c112f269f5ba30b45315e41b1d703287d4fe6fa41d77d296ea98582b4453
candidate-27c23a0add44c5f36cc5f449082abdf4bbcd1fd943c4a305abdd058d7d61869d
candidate-b10c1456157fbe43ea10c37569a66541c0887175de0b0c2a28d59fb687774e31
candidate-785d92e473cc03125189fafe9687ccb0e995fdc0bc53ff82e8ecdbd1fafc7780
candidate-253e364b2a01bc8cb3d51cf708650ce86e2faeae661a5ee3f7d033a441c58acd
candidate-47013839d93f671e126d5dafa05b8727f30799a591bcb66fdbc2a1cf12f98ff4
candidate-147697168d66279e0e0d5b590e0c23acbf3930719c81e5043c87e17b5fdf7b39
candidate-c81cff40e4825ee04c59a6e945d888f507a62552fafd38c561de2a8005a29f47
candidate-a795d95e745782fd4a0e9b8ef9b199c75b1a6555a32f58f3f9696dc228d6ebb7
candidate-10be6c50fa92b4850b5a42315e9e7daa0d3cb586a64c8c23d440eadf6300d6b7
candidate-6402f68c505ef316121427428846157a84040ed2ed9638c0325a76b170c73e77
candidate-ba188046e20b093025d8635ddd345877bb6ddae6ac598742e39463639ff87991
candidate-d0e25aa2c992bc971fa21647eacbbebbf31c4158cc2cfeba8a089bfb099a9434
candidate-600148ad26d21fa7b5dab0025ce90842a4391e1d2ef4207afe65afa4715691e8
candidate-7cbeec8d643b3ab8f706eda4dc3d5cc3864824d3dd302412144a57717ef61107
candidate-e0b19e0bf762210f499a2619d122346d48636c842a3ce16b7f65678e1158c347
candidate-ee358fac28813be50815e120219047f6d1734a87b445d6577b8661da6b044f55
candidate-558767585be9949ee4f1c75ed17ec06784ab74b1f8a991f523520fb84bb77644
candidate-502d85867b4b699e8cbf410bc744d6473561cccd1378d30d0df44ad2ea47d588
candidate-f30c86e8c06b2bbecbf5f761e0d18ba3135ae081e6c4ea8ddacaedf3ed630a3b
candidate-8a1ce5ac7521e6671435c66b70f77fad8a1e2b921688d8b08af60a5603819716
candidate-70c0cfd14ded57a8d4375e497cb456ac0c0da73147a105b40e519285fc439bb2
candidate-1d10dcafbd71d81eb17bfe21117ae7001ee484b2d92b9f2b661ed5ceb5af28da
candidate-e333f28bd315eec0177be2f2494d924de7133454758137d37307afac317de431
candidate-75b96fe37d41c3727356df2e64c340a8262e9adc0b8e8d1a4171447b2d7c9a25
candidate-8162d33d111198ddfcf5f953c399d59e24fadf2dfb1caaeb350a3fbe8a426608
candidate-cbd0a53376f176ae6bc1eba9d4884c8ef777299a8d95d3d8fec57a0137881b06
candidate-c0734be56c35db7be6bfe31e0a21c799361de6cf66724d32aa9dd0b539c8fd28
candidate-8823957610bd548cbc54b44a0df5d196131a256c63113b2eb5abe3fed506efa0
candidate-c7f00f728673b6e05df225d659d72bc2d26da624931598c12b6068a9458e0ba2
candidate-fffeecefa2ad4b869e08bb200383beab0958a98146d8c7acc928e9aca4a0bd2a
candidate-8726ce9448d3b306b10205db3185eec3ca79b54fce0cba724e81ffbd7cb5cd32
candidate-c0aa8e5d65e6f3a21f0572518940881f68576ec9e1d477a913ea2dede63adbb1
candidate-abd92a04296f19d878a8589ddb0111a4419c6f1a523b65b0b9db2196fd98a40e
candidate-850fbafd2496846715d843d343ac1158d72e08a859611794beefaac150f05a38
candidate-afcce74a5071d127d4ab121bef5e50ac7b43af13a38a0f0836f39f0948f21058
candidate-0cd045ece61218ae541bb6641a2478d1fc1fadd19b9ad7f7b1daee25002b157e
candidate-6e5a5f44e638d6c31c9a54dd82545a99df324cb55a054e068e208d24055d306d
candidate-5d3adeb20006decfac8551658cc24ee77bff55a686e712a5f25b7d330d0a0ef5
candidate-c2343bdbf348ecedfb7f0cfe0b933a302f1099d19e726e0fcd9852722e8e8e9a
candidate-890068769b1024067a4824c79353c5f3820c19787c86d3aebd32b8ee0252bc0e
candidate-29791c77768ee7f1d6669cf7e89922d0be254e8792b5f423bd180cc3b95a5bcd
candidate-83197d29f0f7ad9f57bd966f91f9a81c1bd00686a057cdf326d7e159da07480f
candidate-06373a55e0a0f567e4ee9571ba055d1d10e05cdbbb2cbc8d4c17343120e78359
candidate-01a2aa10cc2f7adf8559379078dde40c80a71ed10e06793747fca7812091ce33
candidate-9e121935a39bd4543899fd77b4e5095468065db3cc85005ed42c26bebaace00d
candidate-297f3610dee4cac6ccbf5abc171ff19e70dd2327470665f4237438e40bb9ee63
candidate-e29d4e9c19aa4cda2b640cfe0eba1572f0d3710ed8011971bc90ba1dc097264e
candidate-c1ded87436092a1fa7740ec75b67c36ae0479a8780166f9e61620c633107ed8f
candidate-3c5dd78f44e76b2f00878d619b0ef27a720ee6f381a4c72bb05145178172ba2c
candidate-3f5ceb5ec75dee554bbcde895a92828c3a574a53ce01cdd8c8c9321cb26489e0
candidate-70c7104ecb0bd150d4580fed7e43ba0e6c941b4321d2e6b0b63a083016adf7b0
candidate-28d3afe68d350571000d7589deba7522d3cf9e4c1bbd4ed9d99302fe1e740e6e
candidate-101bb0ca7271f7af2278491d3edf1b70d9798e0c9108761e127ad2dcca729112
candidate-6393ff7d959877368c811e1bfd449332cb0bc61cd3b220fafb1f8e06344f1f55
candidate-6be7ae111960279a7527c280bc1bab308b1606b7e6c16f8b2c3355174eb0ce9b
candidate-81244f7668b83c7ca8b310aa9fc8ca5f063bf864a54acdd09702eea0f1e9f589
candidate-99556b28bea057e2e1d0bc9165b5da651a8071d27c1d6a95e0841188d40193db
candidate-66b92c30c0993623ed9939370d1414ef21cd252c7941604520c334e339b06dd1
candidate-529a6a2c463bd835f0903d47596439e5b7f79c179c893a1ffae924a9ae70d35c
candidate-63c7dd533157054d9aeb0ac1573ff034b79c76719e0fb9f24f0c6e2bd58d16a1
candidate-48eb99521e6683d681075b7139f8eb7751e6c6e39989ed84800b47a97fc2bda9
candidate-bf1e0591ae761d8f1d96fbea2bafc1757cc3a368cdfc12aef886a2be877daea3
candidate-99ac8606baa63d35fd2468500d4ea3c7ddf8d4cf9fa2a637e49a1f5524a31cbf
candidate-c9aa0ab27d37242f208364783e870910fc86cd1da6889959b8365282fa727378
candidate-c2c0a342b1ac5126d349cde468e97260c75f72c9f2d46eaa536bba62e33a14cf
candidate-234691d21e2a7d3c66ecfb3527d08ceb55824b44b25ec3667c0c5321de218710
candidate-29480dee36fc07cbfc68e222061ebddd69b78c622b094259a220d0fcafa64c60
candidate-cabe88ca220995775112515d00ff6facb871766fd9da95971d9a092ab852bfff
candidate-f646222991c2868aaf55d4095c19f0241e46510885e5c28fa6555046a3f5bf15
candidate-72f6fd58d2d362d9b0d2cd7979640af65dde86f642b1f00606f452d29889cfb5
candidate-559ca7bd627e7cf4167909b3e3b156052ab881433f471b28a78dd00d29df6153
candidate-922f3bf57a11d70e51d62d3190d25dfe715b5a674018166efd3596dd2d4dfcc2
candidate-8eff7e622c2f6a2bc6ed432d9fec27e024ab36f07eb42ac51ef7d51affd2f6ef
candidate-c68e4d76e0917080fc4f1f729e0bdec6747d7980ec4d4a03aa9cd1418465cf06
candidate-d54fc4aa7d97f8de5e9223597bc83effc87c725467d3c0830a854024df2c0437
candidate-5f9037d36ddf8c23e6a380c367022b90364c12d53364efc6d43a8f94377aca64
candidate-698ac83a2166b7e8df60a141d0a26cab0b797dc57bf8ab0a26faa9c6782fd858
candidate-716af60d875173ee96c6c67f3b793cc5ded7aef8be398c06acd2c8925e48e8f9
candidate-9cfb233925bca20f7dbf095552263955e14f2db1b37fb838fca14947d6d7c6c9
candidate-d4de72ee315510ef563813b636a5c7d5588787eca926afcdec01d9e54b020d19
candidate-95966450b31df8d419c867a86bf7c0464ebb232bb929cf232ba490cc74d9ab82
candidate-487201627f1ce0dd91fa2ff9c7a98caf9a882c4f2e042a4d49343fdfc8ea9f9f
candidate-c0a236c1c13dc4814501c6bcb62e70ecb1635410934f76f9b2d2a56023d3c971
candidate-54cba2cfdb2519b4550d5db09900192ff9e0ad955039307034aad057d1659fde
candidate-cf81aa076af2622e424a7fd09c4efdbeb10fd5a3a7b17b569abf4d84689c272f
candidate-bf33e730725ff2dd97a6ff1c1f48f5930051df0e254d9f2b3b49e9a91fc5c1a8
candidate-a8cf4890703e5b3a8336e3bcd36797caa80e08553f79ba00f773a8a8f7e9f2cf
candidate-366534942cd62a7cfcd2740206c9df915fc600ca595f503df986268bc66f3d40
candidate-acb74c3675d12d813dcfd1d99069b328c14fc2d2a4b7bccbf14d01a800ec956a
candidate-c679e1d82e3857ab20d0703f904bc2fbbf299d6f26242fcc70dd44c7f63bc8bb
candidate-4fafa8583505324b44aa9400c80d0a9b3468c4957a718a4d3a0db7917611f2ed
candidate-39637db495d092073ed8649f8972a90e6c0daf431646daea54f5d084cd827b7f
candidate-be5c731dbebe8109e312de9847024e6f29eae65ac67e33d2a9acc6125d487964
candidate-ab44de18d54494fa27ebfe72b2f1e27a19faaf655510afd8977a735ed6b4b920
candidate-0e4b7697b39b117cb2eff2808fa7f9bdec8965fd4fffd9e2a5e690a19b124e3b
candidate-751212f2a0cc7b138d92e478970b8af9930ca3e87d48891af8555858a0e2b389
candidate-cc64be2f67522058020f37b914f1adf9d331b3ad52b7eeddffa44876a84bcc43
candidate-8171090b77bbaa7e5c9ba0972e45733e2bd771fe4f691f4c92a896f63d6a9c06
candidate-212f9772ec5a4930045358f19772c2102e34fb16355786676a34ba7365559853
candidate-bd5360e550cfd20dfff5c81c5965a55405d9c298587c2bb08ef0650922aaaa64
candidate-47f13a39931e3e98dec1e9d0714453bb081c60c03a1e35eb7791bce630a66bd8
candidate-3fe21e33b15002dd887026f58fc71bf79af7b98352ccc1eb1b1f8b2f0d5cfb4f
candidate-da5af771c76fe37326e2467178bd6567b499a8a67abded5c05c38bc9f53a25ca
candidate-45f7e1ed2a51cd4344b8238940184e00e0f4d2e6b831a77caef5fd7a49b692ae
candidate-562279cedff808c737ceb7196e394e37daaa4a90e506d22a27834210a8d24e28
candidate-a2dbfdeea5d6781b08f290fa0ce5e458d1e8f50cfa68b042f17e7e132be12fee
candidate-2c6cf2ab95f8e8c537919085dc56fd7086e451668bf754ed0c1062b57778406d
candidate-357aacd3abe5bc48fe4720b2f32a3b69bd992fe5694199277864f971e9d8abeb
candidate-eb2df0957f52f8426c62b11bf6486753520ed0598eb114f967c593aefc63484d
candidate-bc4788e8d19ffe7e035b7a37bcc9d653d0311104d627ee8e1152155f08c0f4f9
candidate-114b1e85b7aab47f4730e4a5baf2147c217593905fc043df8b5bb14a69f075d8
candidate-b8175456ad14c7cd115701dbcbc89bf651041f60e8971c3c3fbeb4dc222b698c
candidate-d513cd794a80a0349d231a569498e33b1fd7a6153088ad14b8bd6ff46578a954
candidate-2ddaf176ac5c472fe3050ca9a1bd56b321582d9b7b0461426fa74329b3b66de2
candidate-fec675244d34df7d6e542ed457fb58601afb199b6977882fde536731dfefaec8
candidate-621b4b2f6a53130edabf9632dea7aab29fd86c13d852529dfaa7d95535458e5d
candidate-7e93e036bd77679b185bd81fb681120e1fdafa7b4b9c9142a19b6349bd158df2
candidate-28adf490a390a2927a1afa5e2fa995fcbaa9900dc7676cefd9906382f873ecd4
candidate-c56be346a0f320158f0a19c5f202fa03835c0935d2dbb5e1d55d6ce3a896f78b
candidate-9a90364bb8519ee7f3230050a5d30c6b7688bb3683c1549ae5754b9749e6a93d
candidate-e206fdb784efedaf5bc22da7763d62628fe737352c506fb2689a062bca9f3b9c
candidate-632753b94ac9305d5c3717bfd233274dea7924ed1bff3fad844d7a8a6a7e649b
candidate-5d9daa47587ab1c5136673c2550625e66d818be00ae7c7e4a41ba73fb06a8d3e
candidate-d20d971520ad06f00f0e9dc93e773e0d8749e17319897ad61c1c891e129928d7
candidate-3203a3a16ceb07899d16d879e982ad6bb3fb56376e59564e2bacdd08b4a40c61
candidate-c4465b97d2a864c742d6afd0d1a9700d9a4fac5a6d4b6fa68cd24cfc25301d10
candidate-9a81d14e461e176036455bdab2258c3c40f38d1af66e451c09917ce0658a9c51
candidate-e4e01fc60b5f1c208c3190951a53e51291304c964970a5f75d89d63effecf21c
candidate-fc19f441837db1eb1eeafbb2bf7ecf0238937873573dc9fc7e9e7283f20224f2
candidate-96f7364ca318a41b86a5feb83da2d1e0295e54d04bb032d89edf54379403e3cc
candidate-db70ebbb9ee894f8f2e0a125494f63b9d4f7213dea4f16147ec55a3323ee3ee5
candidate-2c7de21058e8ea781218722ba24ba7e2f1ebf54c16218d8a7cdbc1a4d44e7de9
candidate-e3cb2fa70cfdbb926a51522a6a5c4e8f10eafde82926ad7507d054f587f9a7a1
candidate-37c69569ce3039cab664a21bb28437fdd8660b8a195dd73027d216d4280f9d9d
candidate-2d1bd143671ca6e4d1e2c47253f4ef8bc9948f6169aa3b90a557bd783700b2c6
candidate-974b3421a9f78fc0fda0710e69cc86ee089ae3720b04f82e74929861725d09e4
candidate-3309eef5050eb8aeb02270ca47113971a3641bd5c2520986a6865da28e57ff9f
candidate-91e765be482351b073e6e411d1d29a8572c4d2fcb6c12345e6071d2cf58b421e
candidate-3f6da313a93879e1cf038cc0bc3833ce165474263fbc132bceddcd1b080dc0f6
candidate-760b74ba0993e1c31085be90d2bb19890397d066a2fcd86fe151cdc2a88d8bf8
candidate-5c6770d2fac1cf5a477e5a50e454a1bcd193090c663030b59a0716f1ef530911
candidate-e5566af7181a14efee13a29e674e1796f02c80c0deb8936c7eaf3b7dd25afc41
candidate-28b4d0f70fb51530bf9c8e430fd811b0d69c566e77f8d1e9973ecf7a399e2265
candidate-049e80be458e23b22a390be243356aa89650843fd0665868ebd97bb05d61923e
candidate-f3073d20f3e59ad933cf6274e90b74fc19e1358a78668201f8b2196262a09ef0
candidate-5c9bc2e36608950efe5c359b86743d6898fe58583fae4ed30f7477e812982431
candidate-fa8c2aa3a1641939b6896ce915857c7d85a71065f7ec949285bba92498a251b1
candidate-27131fbeb1356748e6112bdbf3e2636669edc793f7e55b7acc75306f13f94e39
candidate-a52196369f26f2218c34e531379e8209155468741b36ba196792efb8136d9c52
candidate-520f812488081661a46546db47184de2beea44286ee84151cee3ab1818a20d1e
candidate-2ab670aa79bf0ba3c24164c089b94bf3937e2bf169bbf0e8ff85055cd37200d2
candidate-590cc42d5848938fd492824b85f8c4ce475c65a63067aa3baf5d281208f6cc33
candidate-4063e46b8903fbb4d1a93e61af21cce187c1dd59f76cfd0c34e3b076eccb36dc
candidate-403e45d24f3aa76a96c63fedfd1f43230b29b3ad573e8b1fa0445c25abe8dd41
candidate-9becc55fd051256cb6f8dd082922eaed11f843efd2ffd68a1dbb5620880bba5a
candidate-7e8ee7f04bccb3c554eb6fff5e390753315d86915f281400dd776bdabfacd95c
candidate-50a2f23787c6ed9ff62c83f3b4c4994d9532e6731780772692e4c4104b31bbc7
candidate-b0f65b25a3ae4d79dd6e8d0f0153f55abe3e999be709e7e06a8b2e961993c323
candidate-e28b7a23b2399dbc1e0fc0828ce620d637dc77df0191a35371ad7334d7fc3b5d
candidate-b787a9db0912f9a22aabd87bd5ce56d5e0d879913adf9cdf92e5d3cbf742eb77
candidate-e4fd5835b1fb72f031265077d30a3a7c138ef0f669510a3badabbcc30cc1d62d
candidate-2705d3a992640aa6b40c5c3c7d61b44599264fb538cbbbe7b52286384487eb23
candidate-5fc6ecbdd900bab204bfd1c09b22e58fb1999dcef23ae3bdd238b3231386b621
candidate-40f6ca21df9d0ef1018e4986c9fb5f0df82a8450595e8a10a39367450a8174db
candidate-5ff4f5a1c1835d5f08cf20eeaa7fc68e5b47237844c5ce31d828b67d65573a70
candidate-727eaf05410178320ad6ab69994b144036d690dfb19b608a5d41cc5f1635c9cd
candidate-34c14914aec3fe2998bec65aa9e15054fffbb6b56eb855c1f7e9c3816533b679
candidate-0ff0654d9f77cee7ab11dc0c6b635613051538863c96436e260effb2832ea4b4
candidate-40b69750e4087a3588d8cab0e824d142c4f918e55459567f6f4e6fd64b46eb5d
candidate-c9d236b51745dbfb692ba82b89b8d59db2ed3ca01e748d92c0b4787cab0d0878
candidate-7a2ca53c83711ee695e28ede0f0b2aa4c97112da96829b59637a592c3d777fa6
candidate-07e5cc639cde3726752c7550d1b02d123ae18f9b5c69120c7c35f9a6303108fd
candidate-d704286541bd66f8f01f1454044827a14723fb1e1c70ecb2e85ec8b1ee9e05e1
candidate-a7a85878ac32fc92736347a660205aaa41cd3a7b71b965261e7df4ee81069e9d
candidate-9a873fdcf8c8ad624daf4879816f859ed7e002af9f025d0cd8fa0c0e40d3b498
candidate-1d61ca6b9ff076787007888439fe090e4b3db18e6bdf6dbd413a89d3b798d1f3
candidate-a1a0e845d346676765b6c81237b73224589f17b3e7031495f8e9a836bb861749
candidate-4b3d6f34d71d6308d0bbe1336dfe99c41818cae51c110e84c4ad38ded24228e3
candidate-e1a4703d2ba30b28797aafad8be42e2526715efe1e34186c42ac0655852ea13b
candidate-4241179fb997c0bc335d4f65f24fe039546cbf8d3fbb16b3bdd984f8dede2584
candidate-f84dd211fbc03dfda4785f47a4dcd5848c6ad3d92c5ce87c68ead75365a6bf31
candidate-e08c7e708b01ac6e44e3c3cb9f06f498939671368ed68255b98036979b520856
candidate-4549ce2da0761a387922832196593c09e66898ebfb8ec3d0ced003649039db28
candidate-478971de9e130efe4f1e249220c03db105a91d20f535a304739196d72dd5f3d2
candidate-4f092e23d3893118909832847b17afe21d24f524829e7c02578788634e92ba4a
candidate-5c5ec57cf1edebfd149567794f436ba085003949ac30de21619cef12d45487c5
candidate-0cea11dd2a42f26bfc44c2d6b08c3c891aff63289a92143d3efe8457d0ba1704
candidate-ca3419cbfd8d2dc5bcf6fe136f303bf120e206f2a3738f67c22d4c0fb49b7ed7
candidate-05e0de2f24ab4bfc25799e11b193a68e1c3fdea8c4911e525358ff7abdc1176e
candidate-f06aac51f2f1558296651f7915f259dd7ff769d6f4d5c15e96fab14251d509ff
candidate-de2c4e27eb3b5991f8f7da708d0e232bdf37dbcb28795437a743e060dcf9f731
candidate-2aec28ec87d37bbeebc901240b9fe52e6f947e9853968004fb23a3619f4dc82c
candidate-b8bcdb8bcbd4c807dac05d905caeace1a792209926d893403b28d73a533f85f9
candidate-8dea3b97a78f17898590beba67e1f042f8e40657ce8810359d8b41df71666701
candidate-fca149081b2eb5546a5f1af32edd78e9da21910768db7786a5c17d74ff10437d
candidate-ab2ad0a701e8cae5c93c84a4d9fda8a0658a2c303ae187caca13c38396415fb4
candidate-215c8524ef51f91082a04a02de9e61209b140e22d03bc08faa98ffbaf41b16ee
candidate-49ba607c871fb896e0a2735dafcd8ee57b76dd593ae082afafbe33e624907411
candidate-892fc006371bbf061a07be22ddb082625b253132c0d50ebf38895b05e0304dbc
candidate-4a594ee562da179297a08e107d0e837bdf948430b7e5225c9d4adb5d8e6ef338
candidate-5685debda7f33380f72f910fa4372adcd310ca63bba981f8ee0959ec89660996
candidate-785d4f37a3614364d6cb684ef1777d2a3714abf3ad10edabd1d98839969f392e
candidate-62276f111e7305fef5929d676e4dd90618b296dd30595a495773bc84eda0f9ad
candidate-d3f07514e03203a1a1cd43e1dc92aff182795ba25348c75fc0485e21626b61a7
candidate-219d608aa59c8cc094ace73ea508ad6d36d865e448cd377a61fb1518d8b5a562
candidate-08eee53b6d0ac6c4a96697b40d2bcb16d659aeecafa79c7b43d27ce54dbf1aa0
candidate-47e5d134228aba9548df25a14b1a0bb7361c8743c81cdf1c2e54210d17e905cc
candidate-1d201742d740829f570f91599543012fcfa68a5745c7deadeb011419490a6da4
candidate-c2656f9e2bbb89878be4cbebe42fd59be2ad836eb07af8d862c91473c4994810
candidate-09bf90d5b28317faa7b63a11f4233dad390301e495edb0804129820880e037e5
candidate-f666b95b9669443153358f90e7cf59ecca010d41005dcd99d13284b618b0c444
candidate-9c52424ce59911045a98247d607a51f5b3d7b5e99136489fdc7a6b06995b3a6e
candidate-f505bb88c8aeb7fb69e1c0f7c8a3d607262668d389cd83c4b1ee3146a034be5b
candidate-d40df91e3b18b9f596c4bee493918358b504412fe09907c5d136a46df1ba4faa
candidate-37b3b97fff3fa2c18b58d239e28bc3e6a4b38d71c1d464056cf42a9c5647caea
candidate-3039830f8f0d28c1980cbec361cb9b4b05de1ff37bb4e14f1a63450949d809c8
candidate-8beffbc4ce5a3b7a9d963e4054f9bd41dd6dbbcf9e4292ab57eaadc2a98464c9
candidate-e6bf31d2b94844c03c167618a5e959020f26c72f19d76117167d407b353c0008
candidate-932f434c767ece93ffa457c9450397953d2f7f46ac1ab75dba21b2ce50ecd8c3
candidate-e934f7743d9fcf901d3dba4048428bf29c8084f8a35ce61b17527004a8e63963
candidate-15124dd544724a139dbb0d874bf3e0c34db1cef0f04d03d42114912666fc9e8c
candidate-af03e28c479dd11fdebacab1166a9e550c739732771f2691a4c2624fced37c13
candidate-442d51216fd22daba05c2ff9758cfe783771bebf6e4f843db32e782ea2a1aa54
candidate-ed4bd6411a07cb9bd1a3a6e9828a338e0fe3c38bce1b434a637eef5588f8def5
candidate-f9a58e1a8589e487e94ad499dc680a27723bae45cb01066737f2211469939ed3
candidate-3369542449a2c943d0d4bb48b2d80882383dda0c1cfbec94a47563c25462e48d
candidate-42bf8569bb11395d0c4f74097e0df8ea459b223820e6805485c41113ba0dc394
candidate-0e53053df4b7fc68be6153812373fb20e4482a5623d631168a810f87e316eb20
candidate-10cc9b297530fdf145f5d7d4752a19a8d9cc964b0c5c29018513e2c299cea31d
candidate-181701441066dc5f2b23822325d63af7041ca2d484251673621e50f576192a53
candidate-118b0a004b9522ad8aebc9e909f3e7c7eedbd82a868010b545268dc6723be6a3
candidate-5ab52b5fd401617bc3cede9862ddc4b092e70e11e5f80fb0d333e1a649a7bf14
candidate-613b636f3ca159a63423268236d295235bd3a518628ed7cf2003158e95026bb8
candidate-f0909c1fc948d3b39ec3791c5a93c110374a75ed4f9c8ba379b56b284c966158
candidate-4ef052ad368894f079dbb31c1702a7fe7c1c07bea3f8aac110f8c68151ddffbe
candidate-239204d1800fe16225fe0c339ff875ba6eba44e822acecc6e04aeae1d9c104dc
candidate-5c14aa95648c41123c97231a94dbfb8ffd8850aa765bef2ce17043b3bb602854
candidate-04ef42274d7def8efa3a649bf719674eb4a9324d0181af5fabcf6dbebb5cf3ce
candidate-1e3726291024ce27f6c8c4afbaa8ef7d7a994d82255d421ac651def9110a2976
candidate-b98d45283a02725db50a694bd619b24292c3261b7183f4cd5623ae4797b25e3a
candidate-ad9c3bbc6c5fa2cb19103195b9dda1fc8d85427bbc9c72a0531fbb8a0406cda2
candidate-46e09127ffae701bce44708b19b03a61bcfcd6ac04bb8a26b01a7c5f8761261a
candidate-0c68367747d0fbfa3a1ed92869a41eaccfa9dfc6b9f599afd387f82b693aee89
candidate-39c88b481e468717627d30a7c2a7a666284030c2e07cf6fc45c3e85fefece17f
candidate-d71ebc65bec29aa32c6ccc8679bfed1e6dc2784173f204f65582104ed3c30142
candidate-e020d846fc3fa4fd1d7fad789626b667fd70a122ceefff301eb6a7ebd5de98b0
candidate-d18aba5ebd6633a903ae6a56681198d18423442feee6d367a415fbe3b57b3796
candidate-9d6830a855bca87ff4d4f4222b3287a522179e615a14517a8a6aa75669dd55b0
candidate-e42e927ba220e841a2449201932ee8c32f81fcef46d6a262e2015120f90fb78b
candidate-5a07543e994b78f5924d8c5117bd55b7acd255c4477521f3221b97f750e2a18a
candidate-9689f4fbd2b3a8ab528a9824494fcdc59a9739e4e3751b7f0fe32a0a0cc19628
candidate-8cddb307ecdd8d99e872f4b453052a9d85b177f9ed8ad48ffbef96c2f0eff65f
candidate-72ec5419363336ae90846e6f87467cd733d7f01d86794260fb9674bebd23e4b7
candidate-f03107659220c3eb2d1c31858d2c56acc80c30a73d4a79dbda28a72d964c3441
candidate-41ed2151b32ffcbe1533080d10166522f58a55582d889a9de495390988469592
candidate-2ab88d1fc1839f8cb272ed3d6c6f33cc21af4484dda2c6892186f50ae5e5fabd
candidate-a61c29c9bbfd31070f3c5bde48383bcbacfc20e75807cf8fa668de6f601477ab
candidate-362134c11c24d83ce25f5b214a29e5f347e46c96af192dec8043cd0636d4e17b
candidate-3b0401bb8d519d8e4644260e0e1d02c05024ce5f92358e79d6ee332f40888700
candidate-c5b39737a7b7e0186bb0c13d7a9102ffc13d8f003cbb439ae3e8800b5ef29d23
candidate-06be6c41eeb2b8de58e72019be8675fae996256439b1d7b4c3f25051151d9238
candidate-0188a8b48ca484744326054b36b9b3acfbed86140a665bfdfc32012945ea8996
candidate-1fc0d3f899efbcd9734ec68b0ba143be3c861626b952be1a13ddad0e65f3cafe
candidate-1972d5265e0712ab667d1240a456d882aff3a445011bc06dbf4a4303e1c803da
candidate-394eaf85f51d1062489f8c6aaaf76914c7e77568a8dbd01b1fbab2220c7da045
candidate-42346e8f965ed6d727a520ba834bb6ec90a9a12c7e8078084fdca28e72b23d89
candidate-eb845ae741b32407aca5b7fd163fe572514d77584ec46926d2c9b46624a6fa2e
candidate-c72903d9f8d47c6da95f7c94da959553d98ae0395f36da5f6a63028d96a27fa6
candidate-27ffc19cdb0c3fb3e8cada6076deda3e21c823506f11a9edd2106be6fe4d3b5e
candidate-8917a0ccd7ea3ffe0d9465f5622fe7afa393c8d750d82682165a359bf77ed52d
candidate-759d340171c1acd015badfc1ce2a6daa0b547696138e6b3d2ff75b65f4ae9a8d
candidate-7ab5abd4e02219cbe102e742eed1a810592ea54d84a54d64e7018496d96ac701
candidate-ff200ba1dc9e444a6509a579cef5b45bc37a774dae5f4fa53875365c89f20383
candidate-69ab36dfe5b0f41de1479898ade43622b7e451c21edd300d08295e0faa324ca1
candidate-34a7886824723310b55925562faa091dd3bf66654ee0878983af88b3f5544972
candidate-e4582936c0ee3ca6b872b6b45beeecb07d4b4472646918def583dfdb837f4688
candidate-f6eea7144f590a7d340778915d225b4bf5f7e33f61d8f272a5e88d858e774475
candidate-d82db69c60f6941d126a14d744052d8751e73d4ad832681ac5f0a1b37d5b4efd
candidate-52f5a4585e83592e821541d82c88c40500f07cf5f98fe1391ba43e54cc3000ff
candidate-d16c045c2150d738bc9e1503b81d26e108742b726d62746675259dfd378e956d
candidate-503b91e971be74a948f0123d7160edff450344e18755aea277485e51e5653d5d
candidate-65615da58ecd26956fdee58722996500ba6925141655094402a08b8185529ff8
candidate-d2a457877e203f4c749026ffcdf5354abe67ab4a7ac75fc89053b220e63a1258
candidate-01df49970813427c6a782264629f950d4647c8ed9231202b578565e8e8c6edd9
candidate-7c4823fa77166b3fd4aa7a9ecafe4044cdcc268f92fddbf3da8b9ebc13e3b327
candidate-f509c8323447265447c6efbc41d69c08a95de82dbba0e87c1be84c3fd6a7a528
candidate-5ee742793dd722649dc0c65dc5cf1867225d03dcfb94670935432696117a4533
candidate-05e8b3d0a8f2e6396f5230175c597ed163b3644c1b51ca8bfc677f91be5f43df
candidate-ebca0e6db7a33c7b16d4fec2611b3c31077dd115c5abae9757afbfb01ac24911
candidate-5cf3050ca1c1fe2e684e13cd2a66ef7cbab48406ef4bd1f7f5fba74bab940861
candidate-cbe100aa1e9294ef892ce8999eca426c2a74317001939ad996446c533f6f0dc0
candidate-fa7b02ef9c6183974a3587b4b912d103c1fbbb78666852895c2084a6db01baab
candidate-8fcacbb9c243c576f036c0bb454ba3ad1bcc2cd51dc28b8b93fe31f33625d2bb
candidate-59026fee9041e28f919780d37b32d212f88aa0026a8eafa6fd5d7de5c9dd4b51
candidate-a0591689f9b1c0ea5e17c37f3aad34283f6639d0a388e3fde7c7839cfe636e4d
candidate-948ab99144bb0ed3f3de8e30488404dbdc7fd8044917081e98e9012347e2c2f8
candidate-855d5d82d3a627d3be2abdf214a193fdc3adf315a1a52f08f7f2b46bd40b8fca
candidate-456194e5f10ddcbdfc43c71d9ee26705d20f819ec278ec4ac719df82ea80fdb2
candidate-aba520571ec5e514347a5905351b24b078d597856e157ca919b326348a5b2df4
candidate-feafce5b00c7588ddc75bcee678a5e569f5700b6f162672f4d4df6256f5d24e0
candidate-7cef716d65df0a1ab8bdfb1b441f36bc7b7047d4ff99ff26e9d5ed8d873cf506
candidate-cab34138fa46d15c7d5da7b969fdec1930d52b6add5fe886cbe20ebc5f9f08a5
candidate-7d51af030f87a14f83fbedcc5d931194dc53cde69956df5f4c9a01878b4a6af9
candidate-551138ba26108b347382ec1541eb8660ad440ee9cf8649bc210cdfbd7a1ad08e
candidate-6bc4e4ece35423edfbd601c0806e4c2222b3a43aabd1d8c8af048c9a5ca476fc
candidate-a4da68f29c2f47db055618642b40232281c4902a0b4df34a1d837ad585f67d07
candidate-d6322fb47a6c344a04e2ed869ae252d712b6f9b5523b9e79004367b4774f6fc4
candidate-bf88ee51ed12c1b03d4b25c3f59a71d61c027319c0ff65bbdf2665b7ed3f71fa
candidate-4b5777d42f1412d16389337683f62bdc0c0120536a7f3741cad3217713682c7c
candidate-1c5e2064ed125d877c71d7397d13aa2bfa0e9b794a7defcee75a617fa6a1d9ab
candidate-f47299ee359799697751c8a81015e26da97849ed46eb8ddd38a83c22f5b25d4f
candidate-3454c0abe8bc2faf612d3c8ec4a7153eeac7b2dd583504b4f0f56b5c86f14573
candidate-6f9f12a092df5c4626c86027fd68bd1a499892c8f3a020afdc02218f5f369eba
candidate-b6e3c1ad75558aa27c65dbf9ab8aa3323c95b03d514a4ee44ac8cff7232d0f96
candidate-793fcd044011c90949fd616e48b948d5211d916d4c88dbea9d3b4d082050865b
candidate-93f03272ffdaf3d8209715698fb55b472b8aec739c5acaeaf70545ae547c94e8
candidate-d62fe364b9566e5ba4126aea81ec42de0af6b45d92a31b4455b0c87ce25915aa
candidate-b5379742b8b5b3db21815a2b7a40cd2591141a62c14ce7893a069e011824f13b
candidate-22c61b0e60c7927708f8229521dfdffae1594944a738a0a0630016a1d272db0b
candidate-47ce480064d9c52545669f318032b11840051122f391fd404dab1226ba4e0585
candidate-27bb669f0a4f321989b52047c39d6be929813bc3d667b19d0a2c7223464030bb
candidate-41cb64335a9a68bf4f43d2cdd1f008654687b64f264c0702d6777fa053ae5433
candidate-be27d60fee8f77f3f5d4e992cff38bd8778af25c0e4f738451cd0dba84b450ec
candidate-7fcad191281f06deb6abc4a1cc876043940e5d1a52ceba40bbc058e55c4747fc
candidate-7106d5d3e559906fa8b33eb8bfbbdd22d28fc081a11da9065d8b05a9f57089b9
candidate-856789b1d607779af84e25eaddd5ae2ba117eb09a99302ba75161129eb152509
candidate-eaa0f4ae373fb08d9609374c44eb74ebfb1e06b73dd9872251c4f37d98b0224f
candidate-2f76815039bdab3dbbab195e7ca0210d8c138fda11ffec5d9585cd0e70fbead1
candidate-5594dda2f6c64f72ea9b0ab7b8141af301eeb750981c4ccfe04d746296407ffa
candidate-b406b5c974373483753300acabd0f8add67e973ff457bdd3a3b91382915465cc
candidate-c3c93eb3aec19f01d80639db4a9a816e95e50bcd7c05318a9d6f84579ee46cff
candidate-f4c4f08bbe0d68889cd11162258c7427ed9a64e6430a8d387df86adcec5064e9
candidate-facb13de7700f65c0a2720c8538b818c3585fc3605e0bee75cf32e80002598db
candidate-93489365f05e46249342e7d9cad26ab2cfe8a4df324c77de9c282858a44b51ad
candidate-4efbe6041ae129a36c5eab1b9e481bc524b2667d70541388599210ccb351b1db
candidate-55ea36077f2907f42d4c47debece062d0c0969a5617451e7b0d97168296e16fc
candidate-0e5570894af9f271686cae7ce548bd0e2176d1049f0ad7625882bf3ae42c7d49
candidate-72fa5e74b48732939edc3e201b94ea6bb1061502034effb9664e7ea039f5052a
candidate-d24096cbea4ffe44878838af0aa9779d618abcea3896d340133c2c9d1f036786
candidate-b6561ca49d1824ddf2ca2bdec8a7c18c7cc996334e0fdc7dd61315b2a0503a1e
candidate-3d847c8bc686c7997b30af1786d873f78512b31c9bd1305c3370da7064c2c9b5
candidate-58d9b107f8e29f2c781fe989465ded16e330ae533810889badd8ceb0cb04fc51
candidate-cd71175992a84a96d3474985f708ac604695f1203c10c9c262d00be4daf4bd7c
candidate-2c1c57c1e0a9a44a87ecb19c63ba628bcea68fdbde1f76cbebb355436488943f
candidate-91a31d7b75e7448a66da220b7257f43fd45cf5efeaa714810bd8c1ea3762737d
candidate-6b75ea8fe7bf51c3c0c9caa35f061f2defa43609a52d66e9ec558bc6e49c543f
candidate-9c1b4c98499b7da6d7320698d46bb4b2f59fe1180fb1a4f673bfe66aa20b98b2
candidate-837c493b93e2cf46bb2349ecf1dc303bb09fb04d4f233e8c04bc991f08d9a7b6
candidate-ae8eb59572b3c34cbb2c55aaa6aa5534442c3418550b458a75914ecb1eb2d2ba
candidate-1afb53cb05c7688c67cb6a61f11d241e13397b908c51eb63bc479d89aa2ec2a8
candidate-e997f67febbd2c225564ef808ee229fc9dafdfb0b92433f8995f5563dea38988
candidate-3610cedea3a38e2ccbc30ae986a822302019c5288748a327cdd89c1b91252790
candidate-ca1f7f4d5b18312429e03cd07af38ad615b1680f00d03519f1fa38494aa99344
candidate-41de47abd6537b9a846859a445f2fcb62e48d3bbd272e803245b47e6801a0a2a
candidate-fb01a5a84b3e9723fb00cc4f92e25a0af5b5cf2a5c7efd095e7d846ab9a4e614
candidate-80ad9ebd0eeb24fbedabffdb9c40077aa19805700e0028f5d56fe8b627bd667b
candidate-c90e8b78cd62d83fdbd35fa1ce1ae16831cd26da60ddc57ca403222d23717c13
candidate-ef59b98c7238cf792ba928d615f729cd86e0fba06f2a186d735666119e617e85
candidate-41e8cbcba5dadaada87b3d7dd1b8406a4701a17b465de062f29f5b1852ea52f1
candidate-eaec2748fd0cef87d02514826a293411b3a1e37e1ab2e6df0de0549e3d757e43
candidate-04549aefb4b9d0d3c791e71d8afcf023c127a21b6bcdfc45478cd6c111584478
candidate-b54214f02c33b7e121930168738c3ea064b5ea1f7c02ce94efec7e866dc6d4f2
candidate-24a445b0ff68744ffc7c6918b22a509807412917c73e567078c399d32c160f02
candidate-bfdad1cdaa5d40bcc8a8c61213e3194a1076a27e83f6765ddbba60784ba6c37a
candidate-1c0fd2b915796878c7036cc50287ec2f9b1023cf14d3e5e42ce5658ca966ce73
candidate-d93460ac7a06faee32b6285103405b5e2611247e4c27d922648d8399f71bbeb6
candidate-1b3fdaaa16c60306e9e65d30da321f8ce131699443e9b26df14e4b62ddf14c05
candidate-b05fca0167430e39c593e642ad33ea4cb2715aa987212d94cd6e2f41b772b250
candidate-35b00ec8cd4fa09d255c214da934f90697d9c2e5c85c20112415e16a360f0622
candidate-a7c84ec85a39845d9922d05b4c233f7f0c66f5410c24397cf00ce15974c25417
candidate-630919f8b9821b9854c93b9cdc5e4edf9238d7bad45caf4c330c885a77c5982f
candidate-4eb7c3f78c7570503a603e252f8df15c495538894c6b48ffcdc777c9a3bbe850
candidate-52521b5550a725d147db2e219ecbde3df88614976e500d327bbf2f88237561f9
candidate-76a2942cef6e9405fa837577ef87f2b64163c4ca9857cc714ff17b5ec600c932
candidate-8771984a3c49805202b508cf20d8a6a2301798288cd3a38c32c3899483fc7071
candidate-94dfe81dc569cbac83a583bcad2f549933711b9d3de6b9d0457d88224dcd686f
candidate-c08ece92d452763fc25e4d1ce4aa16a32af1b825d2d7ba07701249b90f750695
candidate-b0ab5ae77e3d04865d91d35ca02fccb2063634808dd00559e30fd946fa3e8c8b
candidate-6df68e6045f1ff9411d05b6610700553f640bef6ec923c7d3f1982dc596472dc
candidate-4031eec660517f04cf65eea023144ad6d50be25157cb1a627abacf9b1700904f
candidate-fd7d1063935d337521cd096098da99402460c79504af3509ffb650eff587fec1
candidate-7fcacae529c46c95c23cf400ec7258fdf314a7cd86e0bb84e174a35678528c75
candidate-3269be8ec89eaaaa4a3afebc64a519867844c7a72a989aa6584d1f2560d7b8b5
candidate-780dd4184179f8ee8b1662a529dfb0a384e165dd6a70def718fc4b9d78b54650
candidate-d59e8f86ac716bfb29c2ee8b4a5508195bfa3d59a7ca29d46dc4896b56233847
candidate-959b123f0011a13de973f9ebebd48465d71abd19c917445eaf6c7c233d85de18
candidate-ebd5bd149a684bb2337fcd92bbcf228348da67988ae20a2ddf03c2be882c2746
candidate-352a88985c74ef1b841504057a3165026b2a6e27acc912582e1cf013594599d6
candidate-60d9abe15f18b1ec91d4992df2081892cf18e3e773577598129d93e01f9deed0
candidate-d1459ed271764a3799183bb1b60ff0996be87919bc617b05a996c2f7596b58d1
candidate-1ae607acba039782a79910bd60fcc79eaa4033d3b9f92e9bbe051f5f3315e67a
candidate-a8581715e46548234be36c083f9447d5d6728299c64d7d38a61809cf9f30edb9
candidate-3d503951f4c2eb34dee3a877c1cd22859946733b20dc7043fd05a1707a71944a
candidate-c32ec859208815bc7d86b707aaccdf5cb753c675b12a8bdbd8bfddeac37886aa
candidate-0ec9087d70ce8cca9f7b3135ed51efda1adbf8325439b030d013c02e272e0da3
candidate-dc1d746a629481c21e1ecd8317ecdcef33e6482ad98776824a0775822b89c197
candidate-fa7818958627cd1c3fc63f073333506787018c178001b0ef12ce2acc7b18aca8
candidate-5adecaf9af4f7e56baaf15931c101bcbb015b95613822845b2c997902740b5f1
candidate-4e8a3b8e95e0f05428f5b63e70ffb6afa374a11e3357c53c5e2360e99aef7186
candidate-858a371c21a02f298d3cf113672015300fb2070679de9f87c82a5f89a7bf131a
candidate-3c495b9bef9385975d085f752c5f280a682650039d528697dfa34e08640867a6
candidate-ca9c4788d5b7b9da7c7a28fb0f8c1e690f1f7845acac440fc33765f0cedd2d59
candidate-63ede401c04c7192345f8a421b8141d173cad3050934383568fe686b70806639
candidate-d026aae17c46277fa4a330f59ce705149b164ecfe050f6e213434382acd97a77
candidate-e65719e2f5a168de689bfed6ce9440aec3795df52f81dda1fb682790ef9090dd
candidate-841e7e626e0a0c010fdf50b3a0ed3c8fbb76844a5e4e390761c47aa6b72bf007
candidate-cf84832e24db6fe8bab3d74f7f4fe5b9d7a26b68c3212b1bed43ae78113e2be3
candidate-58e79a944240f5bbf35fce9680cc43321565b257d1bb3a161d5287cdde0179f2
candidate-2795dfbe6471789dc5b2554b3e62a5faa3f12b47c38e0dd032c528ba6cdbcf32
candidate-a74c652e83a9959f40f47bda8c983445ccb1321c53db926a2162bde9ced7db9b
candidate-9dae2f171b0dfe5b52b1b86965b510f332ca18d1fabd61874ce33859ea5bc1ff
candidate-244f42537e6a3f51eb956e53df8126c300fcd5920d3a7a9d8486b86ac8d28d36
candidate-ae127598963ba6af75816c08a45bee52f13220ceb97289d50073f07bfd834445
candidate-e2342e63f2b236be66db07a1a22dd31d8c38fbfd8539eb0d6667c83af43e46d8
candidate-4c895ca08eab22afe6d5f97980cebcba7101e8ed4ab09a724a9c71914cdb8d33
candidate-3f2904176204b200b438bf4ebc3abe52e03ee71b147b8db73f5891e58fa4be36
candidate-a7d8a9d1c1888564480d683ae8922c5178c7c8aabbcc6ffb5f9f70d581c71250
candidate-22adc3dcc1aa0e7928920c7d2b31d2e4142eab1cb19dd5e5cc1d29f4e52768f4
candidate-3aa64e9b2389330574fb333579f4562b4899b3244b8f6996ec6103103273e585
candidate-fae211e51da78534e00d779ccbfb230854b6a8739e20e9e4caac2389bcf0280f
candidate-aae8dbaef553c36f6725638f79fe8baaf7540c0594e2179e48b3559f0ff4e7ae
candidate-db2fa74088d81b121fc32a7878d94652f36c087be8c7e26a1b12710b305d8378
candidate-5cec9438d97bdf5e32de261c16c4f34de758ca91214415975b3ac079abf745b9
candidate-0d27dc78a7d193fad5a96c50affe52b4ec5f0ba9193c346488f085e837b015b4
candidate-b675e4ca35ead102d4b62bf95372e5571faba0499ff96e506cb37c0be6c56b82
candidate-8f063ef7abcf9733ba74f934bcae0437309cba2b59bb763e0727453c3db8c3bc
candidate-065baa1be687a130643f2ac884ba2c194dece985f23536f803a972428ab36f1d
candidate-9c8d8a6e1106c0d0bc7d320ce01ee6efec56bbd95acdd6e53026a084300f2a34
candidate-a1b6a763898d91c2618442ff7fbe5fbbd58fddafc0261b5a691fbac54843f7ac
candidate-5a4cf09159e0063452b7c7e9b13705d4dd4a2398c9fe27e1967be4fb1465a8f4
candidate-f5ed3213d28833ef577b3043d06a73b63f614ffcd3f56b56dd6bc4d26c573eac
candidate-e51770215b9a578cd489bd470070f00ff6935b4b527ccdad7edeb23a97d4c70e
candidate-dd5bf7fc5401965f6804bcdf8f63fe339e12ed45e11f4909409e0d38c2ef802b
candidate-0eb3fcfe86271ee16a74d1420c7962d302b9acdb1135cca44a7b0e251edec594
candidate-37751e455fde92a38c387e5144fe6fbc961735c3755be179e1d91f6734247d99
candidate-3d6cd8df5c1152fdcb33e0099585213c6d5619adc070b9eb997435a7f0c01137
candidate-da85f0a2f2a8175b804323b7dc1afcae42122ff62d154fb78f03be4b42523971
candidate-047d9ca4c68f7ba4adf9f25cf1bda427b68a8b9a2f4377533049d3525e9181c7
candidate-19d7aeef79b8645b0ab2698c1e3bb9cb26e012f46950d4c15e079d8ea4108360
candidate-b0639ec194d749fab39a0df72a7f7e0e608bdca6d869699bb434f9d4d8d24c63
candidate-14679a4fee989e503935d0931d71432f84df78cab3a3ca76057a1369d358db38
candidate-6ec5aa64e16d0eb11344abbe5f4c53b28397639110e08dc83deb421d3a15ad73
candidate-18a100a28095e5db98637c0e5dc2e8fc7b91f77ca909655f0b302e18d043268c
candidate-d546c44805ad528408fbd03dbd53140135b604c1d15be6b4fc60eb5d80065dea
candidate-3ce3de7c573989f7b8c91756054a2565cdae1714fd32bcd5a7fea74de9a0d08a
candidate-baef5e23dd55e65b581ef3eb3db0622967bff1021fbfa0820a27f5b5a78cb879
candidate-8a4d24ad4b75d4f924396f09365aaf4b9b16e8922557d84c0b142d56bb0ccae0
candidate-56420ad42a92536fea1b4fae48d2ff872312bd96900d5e968b86935f6e01b468
candidate-4a0f4a9ae0b58336d9a4cb4c4c5be8632aa5531169a8b01e89c3864b056cf244
candidate-053eca5f2a6b013e3cc2304e203df1bf65748487b6d0d3727a435235b216694d
candidate-4a67a67bf83cb029be96d1587df7d5fc4a74af0c085016e1b9bf1f82f2a9c3df
candidate-bb1e030b180e3d05791edf8e521a299ed3b5ad1c70550336518a4a24c4a4bccd
candidate-24233acf634bb81ecb8b7f1bdc264d10c8078231cb4049433864586575b5a633
candidate-5374687968fcf03a31bdd2fda77ce5004d052cc998efdb6577b975c6512b7064
candidate-a8af99ba0dba0479ebd659bdcfdd5fefac5e4889f54fe38275f60b337f1808aa
candidate-85306059105f22036c68725758b4baa22f266d798cca649d87a0adb82c4bbe63
candidate-5a5d3e8823726ddd13a51d0ca3e2fa080505331dc520a1499f64e6d135973684
candidate-e876afa74e172eea62de5b5e38a9fe9fec77b95921c9ce661a2364f58029fcee
candidate-608dc06e9e3b1c782083de605d873c17f7ff2435eccbc214779b333958087edb
candidate-4184bc5c4f69ad7d17fd1047b82d0221efc7d347851861fe9766a1d068091f78
candidate-355980ce683eae25ca11534b6fed542739b32712f23986a6a5ccc8bf97db1cb2
candidate-ba3830d5e7277e7d8c5a2a6527ca0925942320ba19990283dd6e3ea1a13037a4
candidate-fd8e6809d5baadd70f027fe76cdba972b722df118b22f6bad3e39e2dd25f9ece
candidate-07eb8048f09c435b0a81b15ab44515604b52106c671e3cbb3b53d2a9b22c500b
candidate-312bff314e2c12d452b66f7d67f83abf4d60a3ecd77fa4bb19bbd0e6917ae6a3
candidate-f45732a25824ac9b6a45a0c15a4796d4879b854617e213a65cf5885a75fe2b0e
candidate-41c2eef22340ea7bd4efd60e1bd18147a0a1aa02fc8a4215e9f0f05a2f8a5c93
candidate-d753820ff6119e942420d7bd20e63dfa313593d2e84855421387d0fb40cedeab
candidate-1f115f02be96e92879bf6e21e6753fac6b3f7e8e56592b4366239e9ae9927505
candidate-7187447540f11cef74bbff14d44da936288b4c63da63094455e5ce2cfe05aa7f
candidate-96d251620dbce3e4b143f5560003244987897de9fb362b2f9bd8f7519591dd4c
candidate-c9f0b0f33f233d546d6e1b83bbb50745b214959b4449da3028ea2403314b5996
candidate-19f3743c75982f5474a48d7d5302914213d4c2e72e0460eb82a276634303774c
candidate-41175d1424ac30819982b4de538e682bbcb501e8cd948e61b46d20708c281778
candidate-57edfd5b493c61f3df98d23f9a97bf49a191dc5162b809e75018f46f072c10af
candidate-f49db8ea04860036679d3fd7d767c569238805d79e66597c8bdc720abaa41767
candidate-5a3dd3960adb8b5e8d424c4c41f894201aa0b4fb45fb1c63f1903a4f0a8fe16a
candidate-a3916ff21bad99cadffcfbe1b0557a9ec2890bc3227a10e722adfebd4b7199cf
candidate-92b507a6e8b12a6c81a359f6e2aa8f42f536ed0f60a3c1f568d1c61afc626234
candidate-fc7f544767b7b85bf4bcf2a748181d041bab48d64ea18a47388a3b7d9941b46c
candidate-0245e5f9cd74921fa10f7dd51d28b462765185228808be555b7e9bbf4f041d18
candidate-e0487fe4270b7d0644e53bfc592cd8b2a4fdf9a42fa0edfaa4413fbb9889e254
candidate-73c448d4e2f1d659ad58ac8eb36323afda4fec16401277e5614e780e80ef15d1
candidate-fc1aa0ebdf24ed7473694787ae7c0940e605d7dd2bffcca59e63f74888e8ca11
candidate-08e4b576654229865ee9b14e5dc3b2ee153b0109b38fb6bf5a0fb8e19c686e7e
candidate-0b0d3414b1a80a75992c285f41da099475db4535e1867b466ba51d856dc225c6
candidate-0629189643b6f79e098de29fe26c3500e327aece79b491f5ce4558a9ae435784
candidate-d0f4b458c308d5f82fd18b6db101cf99bd28e406480ea1ab5cfcd1ee90bb629c
candidate-d05c8f84b6bc3c33110a82154890aefae2df676aee38d02613acc9cbaf383c13
candidate-a2f95542c67e036769af3cb57b36cca747bede7984a64f2aa70b1b1249cf4b57
candidate-bfaacd23a2e8c22d64f3ce41db5eca949ae333435d87a8da7dfa12c5896c8ce7
candidate-962f082b142f1c071409b3222a20f245efeb29fd988727d5a6a20c27689ea2c5
candidate-fb16174630194973fcd99357a07b75b235f57c08e28863cbd72b220e32ef8016
candidate-9e9ccede56c5bd76e8758fd8e429076ac97687e13596ef10d8f3f5d6cbe85c45
candidate-cf7fdf35431bdf3719cc60b15261ef50a1a92b259a6ea3e7079eaf561c1b3854
candidate-5d646589cb2ec47a4038eda65723ae55b2a1807e4980da7a36e29d425559ecc7
candidate-9a5da08137d52b3e1c736dee8a88dacb1714f597cacfeb1bd5cb79847cf85536
candidate-77fde7659d9ecdcfc440c82eb90e96881305f3e6af3124c3ba370b8a604df867
candidate-ab38d0b5dd89925a027dec529f4ca39d55daf4a464f3ba0cff9328950fee2fa9
candidate-5747afcf570f3b31a3d2c13b65388765f09ce31c809e596a1a7620f3f61320e8
candidate-dbd35518a51aecd1264d06f310982e36945a2952618a590391aadae850882d25
candidate-f5dc0928a3c845f2184209717934aa6f8d34d815d1bb6b2ff2f022f8e1075d50
candidate-f82e014870e9b9db2b3c96c79fb048aa6ed1b8e0d4e2ca5afdc9bb4d76ffea1b
candidate-f819a9f2d0680c9de59f2f226e5b2b243b5f514f218123750209b0b58816cd1a
candidate-c5b9f40a98aa25bd676351a7abceb097fe098438d62552ab6ee07b514312f158
candidate-4e81c5e65c88b4d9fe6cab7387dea3a3b16be66b73e29881e2068faa96298a5a
candidate-7bb2b2a463f22add455fc2d2979733085d40851d689fab9f337b0305283f1f87
candidate-2ff46a5ffd0aeb8d6d8e3c9b53268abdd305ee436842fd6d7f53d4dad05d8576
candidate-224ea69f2c312ed8e2b610bdbad88bf86ab7b7993512619dab1e23714ec944cb
candidate-eb4fa2b8d951d32a53d48654ac42182d2bb9aa94b03e4db6ce1c051aa3241f76
candidate-3109bbcb0d55b23df91965734b835e171bae7e7932ba3cad26f9ebeaf562bea3
candidate-5aa11ce3c9f3b6146e6b9ab8a3ecf7bb7efd6f62a7e277a402256d438b0d6227
candidate-8c83029a00fc274d901080bcd489121ac4f2525cc80c2646fb8f9148f8f37a3f
candidate-112d5cf3844a16b624ea9c7f53559431797dd5482cc6ff931418602304bb17ed
candidate-95d4291d964437f5721435623a23fc074b90d97499186c6d7f5987d4ae1865df
candidate-6d59e03fff773535700554216899df4a5f6b7624c812d55a06186ea669a41892
candidate-2673e99ae6ac5dc317e012defee2abaa7c4c593e0d4e296b81127dc88e4a3104
candidate-6315948f1b9260a7d9259f6a6e13ce55e6442c17feb8b177c7832967969d9513
candidate-b6909fe787e4e12d963b094c468e4bb0776088f890960f21213f41c0bb5aec92
candidate-a6e2f082864f95fb27d73132cc03bef68dbf8900ecc07fee17af9ef5b713bf08
candidate-89ab64adedfacde78ff0dab549ff10c01e6783c9a30a5c6fa0a58564c5a6b770
candidate-b746c69182c178b7a920e1d1f73a0002eaf3e32855828021e622c1b87e9c74fe
candidate-ee846da127a3556ba9f815912a57e7833c728b7f19eb33827ac38c28f1c584db
candidate-bd0b59c4883e6ab834b05e9fb5bbefe447141cf3c7819f7a2ac636fd7b51a8c9
candidate-bc2221bcd769bc0110254bf3d7ec5be35a67dfdbc2f43f7c564e7e7141f6607e
candidate-1a9aa414863d38154427672a12e4165d7a5b348f7cc3e3653a54f9c8c6c15328
candidate-233d66525eb7de211e52b3fa607fe28556c15f6927632f209108b312cca4954e
candidate-030ba17a4ec67420186ea73ae9c158626a31bd3566cd1cd94d70b538b685187f
candidate-10ee4bf7accb16036682f396c6b5df7434505ecf861ddd44b17ab1a7cffa884c
</pre>
</details>

<details>
<summary><code>initial_condition</code> (264 candidates)</summary>

<pre>
candidate-89413567598a7fab08885a832efa5dd70254959f65caec74ecc58fa7dbd28df2
candidate-d7e0058ff99768ac23651af0abc1c0ec05540a573aab4bdb47034ea6a40e88e9
candidate-1b409ecf3040d223dfb603b6ec0bf97b194511500ec0c089d69831b66404c9f0
candidate-a4d9a6a921c70941b27dcd4a05d58a4bb62c80780ac4845d9775950d75bf71f4
candidate-b9e005305dc6be4e519b44c415ad2b1d4b7ecd1424cbf850a8bd8a5b4babba6e
candidate-afa4f35aad3017f47b9990b02a8989d52b0cf9e914fedb28eb396f675628e05d
candidate-4ef9648f121f63f769628beed2930a7d5a8468bd72eab3f3dde7c41b2a081b03
candidate-7dd08c1d5d5aaa8fb9220cfbdb0b141c6cd265302f62723b9e556f24876a8017
candidate-d66e9c441a32f55e5b04ed20c25bbdde25cae35dd92b0f540b6fd9e908c74be4
candidate-8d5528d080832e4ae5428ad84734f16eec1974c40b20c256178b5981b5838975
candidate-ec0ce130a2ac98d0650d02948a7743766bf468f063636ac0e5d4de838d223aa5
candidate-bfb660205d66609a7232a304d361a59e35bea7a5b585a9a1af90ba39668d797b
candidate-db354957b1d370ecc3539edb4853836a13cbac79227bfdbde04eb0b10394ef82
candidate-22356390da77678f15ba70bad6521037d421384f8d5212543bb1f3e75b5b83b2
candidate-b80699a2dabbfc96c959ebb1c01af983a0f3d1670a671cad7abe476da2ae4dbd
candidate-567370de861e74fca2af77ab5690b7cb0d1e8395d41cf76c865432796eac5c36
candidate-ac9dd356b15cd25dc10e007971ab530766805bf1d14f123143201ee7c3d82636
candidate-c14ec68786d13c9ffe773b7597cb441a7b21506ec86b53ee24b6c2cf4166680c
candidate-d4470d3f043962f7cac96bef45bc124b885030246244d9ac42a482e690457823
candidate-6fdf072225aec2458d44ab5cf101048e17cf3abefd1ccb19b1642aecd7ca2fce
candidate-a02dc556c40287e57264876b0227b894d0c634eb00462515a165cc17a7cf2b18
candidate-dcbb8570ab0480ca86589b80ea35d14b70bb958b0ae3ff73034c183956fc98f2
candidate-7acc408f1ffd9073e521fff8d0b6e479978c85ade513d35e95f351ef1da1eccd
candidate-2a528056f34744c4e0069b7ef202d4896521569398a1b82945296691480a025d
candidate-c4154b3519b5f813afd6242ad3eb0b1dad74e6e9a5a45ac3310d923b598a79a0
candidate-bc1eb2c9f501968520dacefbf3c5f2f56a2a8db73d8de124eed4fb0dbfc49f58
candidate-573e39cb289ee2b62f31e0ecdeec7bfbd657eda338b010ea5fc1bb6b958e575c
candidate-f0a28243092e359725f8582781cda5a43896659db2052b3eba08bff4a23dfeaa
candidate-f92520c755f1f98088a25951b7c2fea144b2d712a4d9656196428a51db809be0
candidate-b353debc1c3eb2f010ed230c97637edb6ad868d3c852775b6d8e108023caee40
candidate-2f72854b01b38eb242fa8ed01f4535e82201837e64ef2b698e89cecbf2b66250
candidate-4e231bbf2d2c1220589c231fceb2a15dfcd11f78ca9e5088911267d252b35227
candidate-93a43e6c27b5a0d8953a42fd5f98a89f34d25cadd9a5ea9309fd07768c8a7467
candidate-9ccc6086a3a94e606e9264f750a372ba489c3b326f4a1431099f9788523edb62
candidate-2149fda71dcbf4ab0b22bf4eb410d74a2d968fa0b3e5091862c706f81a6e1c2f
candidate-1ebe36fc334af1a84893991d1b86b36c30925b4c4431c6911195851c0a9b66be
candidate-d914650bcfd799caaad7332db0f8a1bfda94caf8065f68482d5c7835bc21f0b7
candidate-07b03caa196e20a587481fd61434c35b251a447f987a4855bf0656afe4c5c32b
candidate-8ab1a7d004be69b7c436611156bb08da5bd9c9fa6aaf6c5633b8b877d82f8fe5
candidate-8d0379da87345c5e82ead05fee6b9870ff56af8f2b693bb8b0574f3a984332ba
candidate-78588b3f88468b93cc93592f19ebcbdb67a29608d43979af0aa85a6226ded3c6
candidate-a075f9c7acb6f624b4d9830f264dc6d8e55042a058a937d1730d6949751d991f
candidate-2cfeb8171312564f9fc75cd5d2687e7ea492e6194e8b5e6f841abdd7a52b9f8a
candidate-ebc83eae915293d494c45927e87faf44b566f2e2a8c369b3759c0c9173c45b77
candidate-e645cfc501f3af508736cdd2583dc2ffe4534734e7f60c12444bdd7ab505316c
candidate-7b815fbd1d6c389ab2780dec13e1452339db9418ac7e9e94b469adefc2ae991e
candidate-03976a19939167dcd539c5000cddfcb9cf4fa9dad66660a0761cc9c14ebdab4d
candidate-0a321e69917087323effbc7fceadf57caf1dfb945e147027ff8c92d8e67c3417
candidate-bd5cbfe2c360672932fd25eefc0dd20ca0d1a1a09f5ed4e428dd55476c4905ae
candidate-25326903ba1007c22e971befacac9c74cc3bf4658c9f6f2e9c5677921f81ba2f
candidate-318a08e3009273ed861d87a267bce7c6d216889258cb275ed61d47f1ed50666d
candidate-6dd13481460657452188161d32abdf3dff8463512f31573a9f8bb6a843344efd
candidate-32e960f68606000c8d9f626ae685c6ad35fbdf0170f10e248b198be0c8c6ab29
candidate-8a68cf9086d07085a03acae1bbc28e7da8a7400bd494a5ff44e501624aaed2ab
candidate-7bf48e4b5a5662953b6d5d2598968cf0d52b2d0bc8339c312ada211d73b254a8
candidate-8edb6ba7515b2c6760c1e7e45a6053a8ae82a48a8ffeb012c0a49f2e0f0ff971
candidate-59d96d6b03a4bc6cef1afa6156ca62376d16e869038c04843c12e4e962f70ea0
candidate-1b6b69876d9913fcb28491e1845d68973a82c8605b77f79264fd3b92ca464e47
candidate-36fa21957e250ee4e0e6b72d467b327e170c44192417ccb316e9a0bc4b0134ef
candidate-b26b51b55a28af4c809d9f906c8b7dc564c49fdd586fd476b5edd5f22e880b1f
candidate-98a2973316b038845f1ff62b7f56f53e6ee49fd76fb22670a496151eab533e22
candidate-4e28afda2db740be2c09c2a79fd201de21064bd5ef7061f7fd8ad5082efb1e96
candidate-326d2124edc1a1f7327048d69efac4e89c736dd7c736e1734f32285056a9f3a4
candidate-033c9c473ea9d60b33e67842beb783f7f2c2f4f0ed5c585acab7fe1bb8c394a8
candidate-33872b1158630be22d32d828519c71ad172d628f8890af2f6b8a8e9cccd4ac9f
candidate-a544a345b72a8fbce409be29e8efad4b7728ce70b9a2902f1fe6ca253ab7c70e
candidate-019f0bf3f00b14f03a697409a83e0c13a287532cd2b4cb85eb7ecf80ee9d6069
candidate-c588238fa090a09a04a37ba18ab0ca99a65ba504bbdb1b6df527a701ffacbc11
candidate-537d3f29ba4fd5248c4f186c197fd95bd3a84970e3d47f4d29e862d571f6494a
candidate-c1d1408a3859b923e711329ef3f687d5c64bb33caa334523b89309cceba99a80
candidate-b89c77be60a54c6c32087e6dfd9961c05353da110bd67e2f8f9658f06fbd2ce3
candidate-39fca829f9c844e58df73ab539441fb9236aa9315c3819162e52d977446936fe
candidate-abfda7fd9c527df4313d4998af2a3cca34ba03270ab7d593a6c7034124d9d16e
candidate-600223d33312caab195e3332a0aa72867744abb7d9cb170a0c116c013d715bf1
candidate-00bd37eb65d6e01a7e59ce862bc9e1191f9c46d8c1a973dbf4731f5d06417230
candidate-a07ed576954e761315dd01a5d1b1cb7ffe57908c586ecaf7fb98dc113323ec86
candidate-14d5eab09827cc6f02637440cad51cbfca734a13fb107b918706763cdb693684
candidate-463ccad5755d7a1f78fb7a106b91f01d5de5ef159a3be544d2fc174004027dbd
candidate-93c7a9f34f275c60631650a54b96fcd83a69d28127bd4d023534ba9c06e21e1a
candidate-89da2d70b96167a959a69d13ae96188366aae2852e28dbb54d84592db523268b
candidate-7d1537c6cd0ecf30f215422340f1171d5bf006a71d96c807b6e1509dd636fc53
candidate-4e2f722fce6d38ac57a56349311c4589249dae0398f8e3e10a32d76928b30772
candidate-e624aef026e9d59a74c50ca4b0d26a6fd974ddd1ddd4e783929ede84bf35263e
candidate-97992bcfeebcc29b20e1024cb7a45884fbb29a7d0d0101e73da89cb1e8bf113e
candidate-7ed1e4a85a686cabebed93439f322fcc762b1b0857f44337a0811cc6a88ddf44
candidate-de3effd109f7c9dbb5036f8c98b7858eced3b2ec4b376c3ba5163c9e6d16312e
candidate-ff5430c7710cc12569d6b5c4c6001fd0367d6e958ac27f273cfdc7d58a4892c9
candidate-bd37882ef21e089a8cf99262eed0394610743e9bf1dd6daf23ac75e4590caf70
candidate-ae26162d413d8b7c755773327b7db9ee728c273c1ffa3c8668cea123df1e3e41
candidate-a0904f2a9f5915b9790dfdc636829a9eac2b49c803ff5c3919e68b61a02cc693
candidate-050f1c98bbe3cef1daf405363bf8f0aed71acce0eefc0a1ede1158c4badf6641
candidate-8fd7cfd7a36c045fff373c8d2a50c918e36ab66853281324e516c7eb1c7e9ec6
candidate-53ec22ee38a01b2db7d399d66b64a8717984a9c28cac2ae254b0d4512142ce0f
candidate-8352c89781b7d4f580a8e9af8e8d38bb6f7974e1d61a48fe55355d9c7510f486
candidate-6fa6d006a296e2baa3c859c386f9e0c6642c3713ecd78342f8f1fa8280b9e7fe
candidate-3418d65f233c6ced1fb750caba62dd6c6d2197eee6cf2c14065ecd694269d3b2
candidate-caf5d130969be37e0b12bb9e67506894e1ff7d2c22e01086095684edd7399075
candidate-f0e4acbecceee0d74d0efb07a70bede852ccd305593174c65bc9e21c99cdf5e8
candidate-2ff6aa9ba52bb5f4d5bfb849b0441be99c90ed0d9ce90a31714046888aa91267
candidate-271e8971f1becb6ac8f88293ea6f5d1ae5f83147aba562e648b6a0c448aa73ce
candidate-98e1bb2b5c9fef4668718e8bdbfdfe3a54ab702daf2a269e8a9f9692608df506
candidate-df9063548b890348b5f26c536b33ead34fdbba564802fdbc587f580eac4e3feb
candidate-277d75f3ee986034a6ebcc83afe88c7af00e1ae017653abcd7c90a2ea7f12aa8
candidate-fa51065284cf38243b750701ee4b5ff5284180a1004331d2056df273d212737d
candidate-6ed8e8694dd84d1b249b80d142962240ccd0d2f3169f8f519f0db3fb3f37b923
candidate-113887a14e2f083b362bb3fd89d9508f7148f5d77f20f37a98f1327be5111750
candidate-0506a621b03d203acbc42f282d168e46bfccb5d2e2471d968479ddcd36b2e238
candidate-b46404b36a6bd1a719db2fee9333dfe2935f5954f84db0400c42813e862722a0
candidate-3de0f4335453ac9b97ca9e8ecb9556f76bf56974bbe8e72aa1c890353d63eeab
candidate-85945f6d7cad4b134a9049e2a489a3a4d5096c6e2c310fc2c630adfd520be129
candidate-9eea758b1e9298e5913b467ba192047f0ac9c1d3468ceaa21e0ab8a8ab4c1f79
candidate-216936052700f8076d7a61cd17f76cd2f5fb780e8ad3869529e5a3f278760330
candidate-efb470acbbd0871fb4a68bddbb39a6fc350a4c72e255e8ddf194b8c2e22ebbbb
candidate-1891337e46481e70a285cb49d14c12659d7bcfe7b39fd2d763868c8bc5fc3f5b
candidate-e8b918654a5001ca5545cf95c0ce482edeb83131395beb2f908512b8110d27ae
candidate-d46fe4232857eb9af7128eba351a78eb802810063c261a963f08c4fa6c141114
candidate-c793c5acc2f7e515fb46a3f7f58c14415083da9f749482fe92cec0ac4db9f607
candidate-49a5395e0f3b26c66988446994c5d9acd33557a984a9b60d212e96d9e5614f80
candidate-91728d12e87970f8a37e11c41ade5d84d82038c6bf4b11e20d1f258c7d2aa538
candidate-190d4f56340aab882f20ca037cbb5ece61e87c32054d5de30ce0a00f3089d792
candidate-2a5a6d34807a366a8e23fc19d739b1bf5295112e109c8dcb481b1c67314ad6bb
candidate-5433d1c67e1dd87d17bc944699ff2b68a14d1fe7a90f8e5f1a74e520031a4231
candidate-e87892700bb073f73fb0a520a4f99d36c9fc6b322bb0d668309844128b9fe609
candidate-d06a76b2ed57101f6987b2930c47d349fe313a7d485090b9988772aa5ab2c1cf
candidate-5139381f365862ecffb4237b55882ee7ef03157e14067f63eee51dbbe606b1bd
candidate-cf374fe9a495f9dd9185104793b4edaf432b926075e8240bfd0a6d066113ed67
candidate-d50bf03c2193ff7981e8bd425e843b6be11ae8091d2659f84fc9550e90726cad
candidate-40e68e437cf98578adbcf30558363fb42bd4f2afa6fd401b9bab7aaa2ad7f344
candidate-cc6f30724a723e599cd89be50c5e2ee1fd7337187047d27092329b65a29e423f
candidate-357983262341db65d4893cf322c08ed21bf9e8e63a42525c1d707f0ffaf7824a
candidate-a23164b145935616ca2d057d73489a022c1c84254246e0f5f7cbc396481aeb25
candidate-7967c25fe2afb51a9b3ad70ceac42279d0f3ca5abd823eaa51b22434ad9db510
candidate-9cbcdcf8ca79b097c3244e7a02de5c2c3a1102429c31d1687e39d7fbc4f62b97
candidate-886f77b35aaff126e7cdba34e7e983989dd6f9ad58e366017a7c526103d1e9da
candidate-b2b8b9b4dc9a71b88110af60794643fb51c6c06d62acb9de23a0e70f018a92a5
candidate-0d7f3576f0c485a4dbc5b260b95609b4a8abe873248269c23a81e6fa2a73a119
candidate-5c13986674e94d83263b1dc4488a556fcecef4de772225eef6b65976b867556c
candidate-9d2246aa9255f2140da0f484e35bd0d859d73f94560bd686d65255b158f3c640
candidate-82a23d12e8a9021fcd8f798f5a541023351c050a5b12e7a1752d559f29deec9b
candidate-02fb18f538714843db855d1f7235f6f1769d01bcee260737ac4aed04a771536d
candidate-81a83f7b53b74f7ae849e15bcb58833aea7ff722af5a022fce5d77daa9a6bf2a
candidate-90af314755cc4db422e431c3c4d1531611902cfe709a9b816b540d1d91ea029f
candidate-1b0843af3bf5ff5cb886b1bd3a763643d628d4e41c37bcaf3401bfc813bde25c
candidate-9571c671f6882414e15a773299fffc765924de4f2916ed77acf40cfbb0ee1c03
candidate-1cd8081dd3668594608eb45dde80181700047cc3f1265ef7d76b82f9c2504596
candidate-12a2bcc446a7fb382a26d2799bf5c53e2e3190dcedec3372e64c2ba5b809e42b
candidate-273231807c4ea80d49b79b9f1ae2f1ea58be843d8e346de41cca9fa3829cae43
candidate-84a02c987bee05cc139848dcbbc92693355b07dbe57a097c35e68b308863a3cb
candidate-fa050497aeddbd21df50a588c1094e197039fa440f81e52d9d775ea146e469e3
candidate-bcf4999ecef7c58549dd8375050433ffc04fcc9118e008ac40e9ea947ea5ea54
candidate-e0063c66855c459805d89691bacb0d5529ea0b9f0e69e90c2fac153ea6e343cd
candidate-eba490369bb80932a1e99437168c5fd175a94d2e90104eeae41773d0fbf2f47a
candidate-43e1c3b6343d24309616becbe42cbc77bfba5562c012e8db360574dc118f60fa
candidate-eed59d396fb1407c3d4524a6d0e9798e5b94df1b39f96292841cc15324770540
candidate-d48b720ab6616ed0e96d87f3cb7c990e9dedb9ddffc3bbb9b9b69d55fc3b0c27
candidate-ae5e20b3c1e524b9826bdd4725bc2ec7e65b2d3123f9ed27fe8c50967d416866
candidate-a1c3fb272f82fdb50d9abf97afb2b538dc877c06930236a663b930cd46986f9f
candidate-5c59041a034936e7d3ec57088b1a7fb9fef294ab1614fb2185e61339327d0ec9
candidate-190b37c67d795b65e37e9ebee1ee221e3079663b2e3d97bb62b9c1957475b344
candidate-f08894b27f7cb0936cfae3db4fc58039720ef8224e622d56963d0ecf29923017
candidate-c0b0587ef927748fe4e90ed7d7cd48b77e2e134c0f58a56915cd90fd75b96fcf
candidate-003a45d10d79fca55e770ef3f18dd323667021f0d970a3b1a5714afd59ecad64
candidate-66b7c3cf79a50a9e1a58f96919d3e403d3723f4e4e1477c11e2df0e2a66014c4
candidate-b9ba115795ecd61936b360730e622de9da61afd4b65033305f6609248c17aca8
candidate-858ad0afdb0914e1664db89e31997332a55a506115fe5c20763ad8f5fa5f58c0
candidate-76de110825c90c3bd03efc69f0a6aa7cc7f00223a56b5d66ea12697b7be946d8
candidate-b2c3f5ee7c5ac73b92edff39dc0dbaedcc2cfcbef583f85b4ba62e90bfe91a31
candidate-a2b938b6b43e2f58d4ff92e94bc0b21a9dc7fc3e720ccc058ccb9e377dd8708c
candidate-1479ee2b13bafa1f888a73eb0c9f9cfc6a827d7ceebf16a3bc306ea95890ed3c
candidate-4921de89633dd6f1def5314d23fca52de73961cd1428d07c678fb3b7ce633cd3
candidate-3aa2231e7c2d0cd19f5f859225059a5f0ec6003cfd353a17b13f6dab845d29eb
candidate-4f00de01712d92e3a06353c9ff27d363ceca9c75bddc46b8680f64b21e2fd6f4
candidate-309ef0d64be3f016e804c8c5f34f4482b3e5e7f6b1cacd65cbb6816fd9bf4e42
candidate-622c9771d4277632844e684cf4b903f30aed1abd132b33014873213397315fa4
candidate-cd1d25b8f6e35284fede4f92c36eefae16f46b9844414b32f7d4f20f2f06ba84
candidate-80d7f855c928d5389dc243e7f04d01a566bcb91fefad2918f71e90b3b4d001b8
candidate-000881f9e154f52486a7d8adb2110ee6bac7abf4f132d159b04bf3474c7012d7
candidate-9cd58e1cbf2cafcc3152befacfbfa3c6cde33c30c5ad673ea61f54983264cc9a
candidate-d1dc0369076b17866bd2b7219331e3f6977b61855c4872a80570c660862176e5
candidate-4805911588e2a9a4d8d1c2beca6771221b14b24a41af15ab414b3cc16b05f410
candidate-3f465312338ec860d5610c62472759cf10a4c5e01589a86aa1c2e870cd82178c
candidate-21de7028c7d26918f0b0dda8357a883b7aad0ef64f2fcf681ba7a0b4d4c33a13
candidate-62d9862c6bdab3536330da2dc116eb3aa150b0070f3a9c66fe69f2abbe144ec0
candidate-4ef424d36102f7fc47a27aa1ad97517a6d560e5ba48fb2c79952fc0d48df4b2e
candidate-afdb2bca35f7cc913076a65074172728283da0734ddb11e06a98c3370b1503e2
candidate-e8f56ac44bb334df0e66183ebc2ac6c794274bb5d221935b15dd30b9ad44886e
candidate-56faf227dcbd6fc7aad965186e69a6a81d1b8bbd18b13ef34cb0f2430a184af3
candidate-478c8630d88c0600beb4f59e5edff80de59677096891ec27ca7a342ee41ad535
candidate-74989fca30e1ccb89638e8e532837a2702643a0d63778004c13115a8685988c0
candidate-e4ba8326048dbe67935e4fd5f5549b90e3ac32044d715e6e0ec7e94cf8a16bed
candidate-7aaf814f219ab80d414f99f598e2d9904ebe326ba1b0fc935e525134faf428bf
candidate-1b109dcef87bbcf20766f4005287c186609ea2031bd3a202ac49ea15ea3f0c26
candidate-2773022a18aa0fa8b248bbe71eb5e505396768e54ef66fe7adb7ce6e9ebf8c14
candidate-146cab988f579ee19f3b103258c7b211363bbbc8f29d8383a4a74c77623820b7
candidate-c141fd79b7a8c9ed6f57a0311b2b367eacdae1addf589683c11105380d5f056c
candidate-935e97d7100d670fdf62790c3ba3383a691c06f3b00501934f3be7939914e575
candidate-c44c4d61b0d1b3ddc05238baa71f89124b9e6b2005f68623025be13b6524b90d
candidate-e53f9694497ee91fc6f96107738cc2fba51b2eafe1369aac2ea4485274ece524
candidate-876b22965c1fd07270b2f236e8811f6b01911c55d418475aaaea75118601357c
candidate-30e1ea150f9885964cf82860c27d3ce31439360460c5d6c9776dd3db916d0c5c
candidate-a1e4aed7bd4404b74c417fe661da147586d6005ba0d2af4a046784cbcd73dde9
candidate-f0c3662e21b791b2a8cacd924f6826be98c8a9200e91d6653bd0f852cc30c125
candidate-dd5dfffeedeb9277fd1136217445ce398ae985c5fc68867c4bad7c3a687f1973
candidate-ded95977d67f977d63f50439c0da4a5c2f58eaa4275b65b2530a2ea81baa7910
candidate-9e461c1f354ab36de6283048db1615ce7d44e2e23767da66f31997283e22c42f
candidate-6c831b1a7483b6db05181e51bcb280d34457e2b1ff581342780c10434c835bed
candidate-168d37342f1529135d51374e1229ce621c2e5d4c0f23ea76a02781b4d94dd333
candidate-a5cb5683f146dfbdf19872adcb75a9aad4a3275ec334f86712375e154ec16145
candidate-e1398fe9da321ddd97791b11ae7129cca58f86d294cc20e7c6f5723722955be9
candidate-b0a98e28f9867ac7255035b7d0c67a0b0eb2be146ec22225dc91588ecc4648a1
candidate-df12e4e202ec394b7fe9aa1fc9fcf8bfa8d2b9c71ef465400339df636a722dc6
candidate-03abdf54a3bb80e0c56a22d6512c5e65a6a143e33471ad1a55039fa37adab550
candidate-1d67ec6c5e1da960f946309becdcc3a407f468fb9c9202e1b9b71fa095179139
candidate-2fa80919c98d8d31b99d923156cbb7639ab6669b907f7cabafdb7d9dd4034b4c
candidate-90a48a8b18dae67566b2937ad2e06440731b9bbe204964cd80e0b9d3a3aa04a1
candidate-51f686daa3766386fe3a78fd008c364dec783a31bf6542cff98b866cf8813ea5
candidate-99571d900f54fd2a48c17b686736a57cad7e9054f8300adc5933b4b43436ccce
candidate-34a975bf39ffca3c4d8f85f7b971258efea2cd3c576b684bb5595c1f84ce554e
candidate-f8c54581c55312834bcfd6a0a0381a74e546acb31117ebb01a0212e1c9c8f8a2
candidate-511873ba6a88ffd22923c973154b2d48e738be1f08d6c707e234665e3fa8321f
candidate-010e544f99cb9b61bdd309e64fecea9fe15d8cbac9cd0d3d5f9273537eff23a6
candidate-8ed26735dbbddfaf6214b1e067a46a9872679324831216ea95a86a558d4f7981
candidate-4fa1268dcb606f4d4d1bbddcda0a231fcfbdbc8fa189ec510fac603dfa65184d
candidate-9c1987bf85e77ba92b2b771634a77ea29eb50ba2b3812a23056d1b74cd90aa42
candidate-e0e808ce64d66e4eedb99c91c1b7416597da902e44e773139d427fbf758b2b7e
candidate-1b3448eef6dc74816cdc4ce2838e6e5d79c1e8d534c14a398154ff0d9e6f7709
candidate-bf455e1b26c95ec0677cb9d6e7a262f2fe7e20d27edbf3df672568042d557cf7
candidate-b22f93db9f95e9cb68e66ab2f5249ed5841d0f39b9376e2d451ebb1998fa8a36
candidate-a0b15d07ed108e3790c5e8adc956239f1056222c5e287175c7beeab84ace95e7
candidate-f2e8dcaae42b4b4c0bce60cbdaf6244315255416be8b5c282fd4f50d5e40bdd6
candidate-8e04e7fe952e0a117abf7a1bc12403c5058fd8f65df48e5ee7be5e607405979c
candidate-603feed980014956fa6b4f353386fd2e819f60efa7fd12e75ae3ad1e5cb51594
candidate-fe0f5d60f5ef17522c3bba877c0ec2809421163cfdbc04403c04dee54a96cfa0
candidate-67bd8273df93f1728994e7199cf30f22e7a2f234e03570b3a90df203f902334e
candidate-f8a61d8939cd3b99246469807f684d32ce5a349c05b696c0ad8688921f9ac4f7
candidate-15a5463d5d96814f6b20d700ee4e46c76496b141c78ce2546a1f5f3988a123a2
candidate-1d4e63b4977a8f108399956ce752965d9b849dabae377139e6ee0f72035c4939
candidate-fb72235329c57daf8ae9fef90c1af54416d2306a1cb23510544224f262d5a216
candidate-a3e6b66b5bd67aaaec7361b18866edd6bcc3e4bae4383fbad969673749c5b097
candidate-30030ed32c81a2dc5354d214ae7a8a3b358f818879415dc57783ccf8caffc436
candidate-b3c7086de1029e29f82a32e40ce8e155abe71b9190fb3b84ae9b6f16aebe08ab
candidate-91438dc1d07efac7309c29f151e8d4fe01d04e497a342896889f5588c27422a9
candidate-fef63914b47924b8cb70ca93e50a5b329dec8b4195b8affefaa3cfd4042e45c9
candidate-250901349c064ef68d5ffefa0c6ddd0151fb5e1b8e4ff8b86555ef7ca0eecea9
candidate-8c57ac5feb20785ed50cda7ff5c7b834a87550f3c49e3552ba78dda329561b63
candidate-c180623ac3cfcb1550b82c4af7a4d3e1aa0e1c2f3efb4c69b119272e90ecce33
candidate-25339b93c1ada5735d88c2b9010f097827f682fec46aaaf3a325d5d23ae8121f
candidate-a7803625861ca47b804edaff83794380e71fd5a3d09fcc614269d27bbce2cc24
candidate-98e1a26e1bd3b3ce26760ece02158919bf7ff9e1f5fd65616e2dcd476fb370d1
candidate-fb418e58c8e340524d1f7ab9adb87feaac3ed6165349868ed19330382810ef5f
candidate-650126f1aa558626735b3e5decf758c39a12d6f1975d2558c4e67f4fa9bb5e39
candidate-815ab664487dcc850f1fd54e8295bad78cc43026b0b8a9ef70f560103ac71d60
candidate-d3c8861aafcde01340b2e5ac46766d4b68c2053803dde55f07eceb60daaa818b
candidate-5ce79570c93880aecadf678bfd85d01e63a30e199796bd8581814b87161173d0
candidate-b47821631cdd2e39c3ac2d9ce6729b4458eeac740ed5aedfc3c4585c86e56ff0
candidate-9e567370641841d68a52f5ca146ed0506f9fdeac6f58c992aaf51c9df69faff3
candidate-4a0ffc9c5334c2c23b0b7eb74dcce6bfd52914adc7e9b5b554e9c53e2731b3af
candidate-bf10b1da9d07ebbe586458f26a986dafc7a0ce0e97f0bbb58ad8482a59a983a1
candidate-de6726c117ad22f8e1ff2f5d94cbc22e482b9ce08a744fc6c794d4cbe6c39397
candidate-ad4ab293177b1e4a0f69293ba78590db92e58790c38c80116559c1c39e7f24ac
candidate-71e8fe479faac744008df24dd9a16ab981f1a8ef3f4e290ffa3b8eb59d910006
candidate-2997042cb708386477e31105d52b096b6abd1c035b8cd13d6268a3697ba674e6
candidate-484157441b62b42c67794964d168c93082ba7caab084976586b40ead6b202a22
candidate-b6ebf362591cad5ed9429c144c5f77147e54371500257747a40191f6d6564557
</pre>
</details>

<details>
<summary><code>ambiguous</code> (28 candidates)</summary>

<pre>
candidate-83fc6ff100d2691fc1a45a51767f16210ede36ae631d958f26fc42052d91e7dd
candidate-a8a7bf8df77649cfed455c01c90f0fe82814d180d7a0ede249656a45cfa36f34
candidate-1754429622b755a9795ce4fda90c09ccfeb2e2ab46fd69c024cc06e3fbdd8fe6
candidate-06cc4de42bce9f0ed08311b774f0f90ac9ce6b8e482f5cccc09a4dda9cf0b1b3
candidate-70c58e97918fc78f16cff6463d35e0bf64cebc1c5fa53efbce3eb5006dce5668
candidate-9a67a7238433e511d07777803bc8734252e5db5e327014c179d0a94a45ead668
candidate-a23f0075f7f015131caae68654908dd9656fc5b720959beb0ade85e575905c58
candidate-a4033bdb3f76e4bf58690c7f78f929063028a86ec51fa80623d80db78c69d58d
candidate-ac36fb69588713c4f7b567e06baaa9c8ed3e3af8aee9292280f5c67225f3552c
candidate-ea1675cd16878857d9f82c3d70949f3a2eef3a7d5250cd9d42b1494c7a2a917d
candidate-93d080c2ed12c042bab35758cd7d082656946a755cc940148eb50e730dc04d49
candidate-003ab4236267cf5f74fc7a4366f510918699fdb7c5801d3456181f52a2d131ec
candidate-e0bb8cd4840a4a9d73dd9c99849a913636ce600748a004ff59e1d5ef34b7118e
candidate-81b2a0348cf1b42f4adaf4436fd75500c73fa7735d38a1256dded55dde291b4e
candidate-3256a43de0c3c967d9cc1d07ab9e6801fe35ad67d8f1dc9a32fdb725f1cb3ea5
candidate-d9c63afff7055d5db5ab3b10c34e9bce4b6b3c6ff0997bff9d41054ec89ae1af
candidate-450b6023b015fdb8e23c07df7b0e3b0c533ddf119a63b3c8755c329150ff0b52
candidate-ea944da8d72fb41875ff39fee0b9551658a8b594ddf94f7eaf7d5fe959d078b7
candidate-cf6bcf808a43f135bdf94143fada206927cd61539b385a61d03de7fa2da272c4
candidate-992851a04b9246fa31efda5fd4d31efb2828255e6e65861b68ee2678353dfc24
candidate-04e366b18556dcf02764f64d9d94036254bbde442c6f4ffd6eaab24ef3b51685
candidate-fed8a128594fe88899bb13524a75e46f74516bd06c646a8c94c02014372edb94
candidate-88c2c43eb1936e719a4d4e46c92013dd8e6c6fa6a3fb92616435ec4ca060ca6c
candidate-3c357742b3dbc2a26d79e13e159c5a8bc92be26e81fb302e96fefe266439e77f
candidate-807d9300509b158c2ea19387334af8980ca19a47f380640645fdab14d6e64e1a
candidate-f535284e65a08d673683891d1e644b03e226ec5a6440b3bb143fa067e798324e
candidate-41a4cb77b455ce4bb03f10fe098de04a911bcb354c571d90ae41eb5949251d81
candidate-a1ca5ea22507668012006ecd108c196cc886fcb494a1421a0ba0c203bfd97f7a
</pre>
</details>

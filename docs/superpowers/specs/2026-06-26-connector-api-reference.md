# Connector API Reference — Workday & Eightfold (for mock connectors)

> **Purpose.** Verified field/object naming and payload shapes so the mock
> connectors (`workday_mock.py`, `eightfold_mock.py`) ring true to someone who has
> integrated these systems. Synthetic data only — no real credentials, no real PII.
> Sourced via deep-research (adversarially verified; 22/25 claims confirmed).
> Confidence + source noted per item. **Inferred** = shape is illustrative, not
> doc-verified.

## Confidence legend
- **[V]** verified against a primary/official doc (Workday Community, Eightfold apidocs).
- **[V-sec]** verified against a secondary source (integration vendor docs).
- **[INF]** inferred / illustrative — plausible shape, not doc-confirmed. Mark in code.

---

## Workday — Recruiting (SOAP "Workday Web Services")

- **Web service:** `Recruiting` (in the v46.1 production API directory). Operations
  include `Get_Candidates`, `Get_Job_Requisitions`. **[V]** (community.workday.com)
- **Core objects** (underscore-CamelCase convention): `Candidate`, `Job_Requisition`,
  `Job_Application`, `Job_Posting`, `Interview`, `Offer`, `Evergreen_Requisition`,
  `Position`, `Background_Check`, `Reference`, `Questionnaire`, `Recruiting_Agency`,
  `Veteran_Status`, `Attachment`. **[V]** (Recruiting WWS v25.2)
- **ID model — dual reference (the signature Workday tell):** every object carries an
  opaque **WID** (Workday ID) *and* a business ID. For candidates the
  `CandidateObjectID` types are exactly `WID` and `Candidate_ID`. **[V]** (Get_Candidates v26.1)
- **Candidate shape:** nested data groups — `Name_Data` (first/last), `Contact_Data`
  (phone, email, address), plus assessment data. **[V]**
- **Get_Job_Requisitions response nesting:** `Get_Job_Requisitions_Response` >
  `Response_Results` (`Total_Results`, `Total_Pages`, `Page`) + `Response_Data` >
  `Job_Requisition` > `Job_Requisition_Reference` + `Job_Requisition_Data`. **[V]**
- **Auth:** SOAP/WWS uses **WS-Security via ISU** (Integration System User) credentials,
  XML payloads. The REST APIs use **OAuth 2.0**, JSON responses. **[V-sec]**

## Workday — RaaS (Reports as a Service) → applicant-flow / funnel

- **Mechanism:** author a **custom report** (must be **"Advanced"** report type), then
  "Enable as Web Service." Field names are **whatever the report author defines** —
  there is *no fixed applicant-flow API schema*. **[V]**
- **URL pattern:**
  `https://{host}.workday.com/ccx/service/customreport2/{tenant}/{username}/{Report_Name}?format=json`
  **[V]** (format selectable: `json` | `xml` | `csv` | `rss`)
- **Auth:** OAuth 2.0 or ISU. **[V-sec]**
- **Honesty flag for the audit demo:** stage / disposition / EEO-diversity columns are
  **report-defined, not a documented API contract**. Our mock report schema is a
  *reasonable* applicant-flow report — label these fields **[INF]** in code.

## Workday — Skills Cloud / Talent (SOAP "Talent" service v28.0)

- **Operations:** `Get_Skill_Profiles` ("export all Skill Profiles from the tenant"),
  `Get_Skill_Profile_Categories`, `Put_Skill` ("adds or updates a skill"). **[V]**
- **Model:** Skills Cloud is a **relational/graph** model surfacing connections between
  skills; feeds job recommendations + the talent marketplace. **[V]**
- ⚠️ **Corrected by verification:** a per-worker `Get_Manage_Skills` operation was
  **refuted** — do not use it. Skills attach via **Skill Profiles**, exported by the
  operations above.

---

## Eightfold — Talent Intelligence Platform (API v2)

- **Base URL:** `https://apiv2.eightfold.ai/api/v2/` (v1 deprecated at
  `https://api.eightfold.ai/v1/`). **[V]**
- **Auth:** **OAuth 2.0** on v2. **[V]**
  ⚠️ **Corrected by verification:** a claim that Eightfold uses **API-key** auth was
  **refuted (0-3)** — use OAuth 2.0.
- **Entity rename:** v2 calls it **`Profile`** (v1 called it `candidate`). **[V]**
- **Core REST resources:**
  - Profile — `/core/profiles`, `/core/profiles/{profileId}` (GET/PATCH/PUT) **[V]**
  - Position — `/core/positions`, `/core/positions/{positionId}` **[V]**
  - ATS Candidate — `/core/ats-candidates...` **[V]**
- **Field naming:** **camelCase** (e.g. `profileId`, `positionMatchScore`). **[V]**
- **Match/fit scoring:** surfaced via a **`positionMatchScore`** field. **[V, lower conf 2-1]**
  ⚠️ **Corrected by verification:** specific endpoint names ("Candidates: Get Matching
  Jobs" / "Position: Get Matching Candidates") and params (`minStarThreshold`,
  `filterQuery`) were **refuted (0-3)** — do **not** invent those. Model matching as a
  *field on the profile/position*, not named endpoints.
- **Integration patterns:** Eightfold consumes partner systems' APIs (e.g. SAP
  SuccessFactors **OData + OAuth**) rather than only exposing its own. **[V]**
- **Unified-connector view (Kombo):** Eightfold normalizes to `Users`, `Jobs`,
  `Candidates`, `Applications`, `Application Stages`; each record carries `id`,
  `remote_id`, `remote_data` (raw Eightfold payload), `changed_at`. **[V-sec]** — useful
  shape for the `remote_data` passthrough pattern in our mock.

---

## Mock payloads (faithful to the above)

### Workday Candidate — for Demo B (decision packet)
```json
{
  "Candidate_Reference": {
    "ID": [
      {"type": "WID", "value": "3aa5550b7fe348b98d7b5741afc65534"},
      {"type": "Candidate_ID", "value": "CAND-100482"}
    ]
  },
  "Candidate_Data": {
    "Name_Data": {"First_Name": "<synthetic>", "Last_Name": "<synthetic>"},
    "Contact_Data": {"Email_Address": "<synthetic>", "Phone": "<synthetic>"},
    "Job_Application_Reference": [
      {"ID": [{"type": "Job_Application_ID", "value": "APP-77310"}]}
    ],
    "Skill_Data": ["<skill>", "<skill>"],            // [INF] illustrative
    "Assessment_Data": {"Score": 0, "Rubric_Ref": "REQ-2031-rubric"}  // [INF]
  }
}
```

### Workday RaaS applicant-flow report row — for Demo A (adverse-impact)
```json
// Custom "Advanced" report, &format=json — column names are report-defined [INF]
{
  "Report_Entry": [
    {
      "Job_Requisition_ID": "REQ-2031",
      "Candidate_ID": "CAND-100482",
      "Recruiting_Stage": "Interview",          // [INF] report-defined
      "Disposition": "In Progress",             // [INF]
      "Gender": "<synthetic group>",            // [INF] EEO column if report includes it
      "Ethnicity": "<synthetic group>",         // [INF]
      "Application_Date": "2026-05-12"
    }
  ]
}
```

### Eightfold Profile — for Demo C (internal mobility skills match)
```json
{
  "profileId": "ef_9d31c0a2",
  "name": "<synthetic>",
  "skills": [
    {"name": "Python", "level": "advanced"},        // [INF] level field illustrative
    {"name": "Data Modeling", "level": "intermediate"}
  ],
  "positionMatchScore": 0.87,                        // [V] field name; value synthetic
  "matchedPositionId": "pos_45102",                  // [INF]
  "remote_id": "ef_9d31c0a2"                         // unified-connector passthrough [V-sec]
}
```

---

## Sources (primary unless noted)
- Workday Community Recruiting WWS: `Get_Candidates` v26.1, `Get_Job_Requisitions` v19,
  `Recruiting` v25.2, production API index.
- Workday Community Talent service v28.0; workday.com Skills Cloud product page.
- Workday RaaS: learn.microsoft.com RaaS guide [primary], docs.getdx.com, docs.workato.com,
  Oracle adapter docs [secondary].
- Eightfold: apidocs.eightfold.ai (getting-started, authorization guide), SuccessFactors
  integration PDF [primary]; docs.kombo.dev Eightfold connector [secondary].

# Deliverable 2: Corrected Data Flow Diagram

**Prepared by:** Emmanuel Shyirambere | **Date:** May 2026

---

## Overview

The original QuickLoan data pipeline contained six categories of governance failure. The corrected diagram below replaces every flawed node and connection with a compliant alternative. Nine annotated corrections (C1 through C9) are applied. Each correction is cross-referenced to a numbered footnote table explaining what changed and why it is necessary.

Nodes marked with `[Cx]` have been corrected or newly added. Nodes with no annotation are unchanged from the original pipeline.

---

## Corrected Data Flow Diagram

```
+---------------------------------------+
|          1. User Mobile App           |
|   [C1] Minimized Collection Only      |
|   Collects: national ID, mobile money |
|   reference, income, loan amount.     |
|   Contact list, GPS, device logs      |
|   REMOVED.                            |
+-------------------+-------------------+
                    |
                    | collects minimal PII only
                    v
+---------------------------------------+
|          2. API Gateway               |
|   [C2] Schema Validation Enforced     |
|   Required fields validated.          |
|   ISO 8601 dates. E.164 phones.       |
|   Malformed records quarantined.      |
+-------------------+-------------------+
                    |
                    | validated records only
                    v
+---------------------------------------+
|  [C3] NEW: Consent & Validation Layer |
|   Granular consent screen presented.  |
|   Timestamped consent record stored   |
|   per user per data category.         |
|   No consent = no ingestion.          |
+-------------------+-------------------+
                    |
                    | consented, validated records
                    v
+---------------------------------------+
|      3. Raw Data DB 'AllEvents'       |
|   [C4] Classification Schema Applied  |
|   SENSITIVE: (none remaining post-C1) |
|   CONFIDENTIAL: ID, financial, phone  |
|   INTERNAL: loan scores               |
|   PUBLIC: anonymised aggregates       |
|   Retention policy enforced:          |
|   CONFIDENTIAL deleted after 36 months|
+-------------------+-------------------+
                    |
                    | classified, retained records
                    v
+---------------------------------------+
|       5. Preprocessing Service        |
|   [C5] Defined Handling Rules         |
|   PII fields masked before feature    |
|   extraction. All transformations     |
|   logged. Completeness validated      |
|   before ML handoff.                  |
+-------------------+-------------------+
                    |
                    | masked, validated features
                    v
+---------------------------------------+         +-------------------------------+
|      7. Decision Service              |-------->|  8. Customer Notifications    |
|   [C7] Full Audit Logging             |         |  Decision + reason code       |
|   Logs: applicant ID, model version,  |         |  provided to applicant        |
|   feature values, score, decision,    |         |  (SMS / Email)                |
|   timestamp, reason code.             |         +-------------------------------+
|   Borderline scores (within 10% of   |
|   threshold) routed to human review.  |
+-------------------+-------------------+
                    |
                    | score request
                    v
+---------------------------------------+
|      6. LoanScore ML Model            |
|   [C6] Debiased + Fairness Constrained|
|   Proxy features removed: GPS,        |
|   contact list size, device model.    |
|   Retrained with Equalized Odds       |
|   fairness constraint.                |
|   Monthly DARD monitoring active.     |
+-------------------+-------------------+
                    |
                    | model outputs (no PII)
                    v
+---------------------------------------+
|        9. Analytics DB                |
|   [C8] Anonymised / Masked PII        |
|   Direct identifiers replaced with    |
|   pseudonymous tokens.                |
|   Aggregates not re-identifiable.     |
+-------------------+-------------------+
                    |
                    | anonymised aggregates only
                    v
+---------------------------------------+
|       10. 3rd-Party Partner           |
|   [C9] Data Sharing Agreement         |
|   Data Processing Agreement signed.   |
|   Raw PII never shared.               |
|   Anonymised / aggregated data only.  |
|   Partner adequacy confirmed.         |
+---------------------------------------+
```

---

## Correction Annotations

### C1 — Excessive Collection Removed at Step 1 (User Mobile App)

**What changed:** The mobile app no longer requests permission to access the user's contact list, GPS location history, or device event logs. Data collection is restricted to: national ID, mobile money account reference, self-declared income, and loan amount requested.

**Why necessary:** Ghana DPA Act 843, s.20 requires that personal data collected must be adequate, relevant, and not excessive in relation to the purpose for which it is collected. A loan eligibility decision does not require contact relationships, physical movement history, or device usage patterns. Retaining these collections constitutes a data minimization violation and increases the attack surface for a data breach involving sensitive personal information.

---

### C2 — Schema Validation Enforced at Step 2 (API Gateway)

**What changed:** The API Gateway now validates every inbound record against a published schema before forwarding it downstream. Required fields must be present and correctly formatted. Records failing validation are rejected with an error code or quarantined in a dedicated review queue. Accepted formats: ISO 8601 for all date fields; E.164 for all phone numbers.

**Why necessary:** Without validation at the gateway, malformed records (null fields, misformatted dates, truncated IDs) enter the pipeline and reach the ML model. The model's null-handling logic assigns default values to missing fields, producing artificially low credit scores for applicants whose data was corrupt at entry — not because they represent credit risk. This is a root cause of unfair rejections attributable to data quality failure rather than creditworthiness.

---

### C3 — New Consent and Compliance Layer Inserted Between Steps 2 and 3

**What changed:** A new processing step is inserted between the API Gateway and the Raw Data DB. This layer presents a granular, category-level consent screen to the user before any data is persisted. Each data category (financial data, identity data) requires an explicit opt-in. A timestamped consent record is written to a dedicated Consent DB per user per category. Records for which consent has not been granted are not forwarded to the Raw Data DB.

**Why necessary:** Ghana DPA Act 843, s.19 requires that personal data must not be collected or processed without the explicit, informed consent of the data subject. The original pipeline stores data before consent is ever requested. This is a fundamental violation of the Act's lawful processing requirements and the most legally urgent flaw in the pipeline.

---

### C4 — Data Classification and Retention Policy Applied at Step 3 (Raw Data DB)

**What changed:** Every field stored in the `AllEvents` database is now assigned a classification tier: SENSITIVE, CONFIDENTIAL, INTERNAL, or PUBLIC. A retention schedule is enforced per tier: CONFIDENTIAL records (national ID, financial history) are deleted after 36 months; any residual SENSITIVE records after 6 months. An automated deletion job runs nightly to purge expired records.

**Why necessary:** Without classification, the database applies uniform access controls to fields of vastly different sensitivity. Without a retention schedule, personal data accumulates indefinitely. Both conditions violate Act 843's storage limitation principle. Classification also enables downstream systems (Preprocessing Service, Analytics DB) to apply tier-appropriate handling rules automatically.

---

### C5 — Defined Handling Rules Added at Step 5 (Preprocessing Service)

**What changed:** The Preprocessing Service now operates under a defined handling specification for each field type. PII fields (name, phone, ID number) are tokenized or masked before feature extraction begins. All transformation operations are logged with a transformation ID. A completeness check validates that required features are non-null before the processed record is passed to the ML model.

**Why necessary:** In the original pipeline, the Preprocessing Service passes raw PII fields as ML features. This means the model is trained and scored on plaintext personal identifiers, and proxy features such as GPS coordinates and contact counts flow directly into the model. Masking at this stage breaks the proxy chain and ensures the Analytics DB and ML model never hold direct identifiers.

---

### C6 — LoanScore ML Model Debiased with Fairness Constraints at Step 6

**What changed:** GPS location, contact list size, and device model are removed from the model's feature set. The model is retrained on a balanced, geographically and demographically representative dataset. Equalized Odds is adopted as the primary fairness constraint during training, requiring equal true positive rates and equal false positive rates across demographic subgroups. Monthly Demographic Approval Rate Disparity (DARD) monitoring is activated.

**Why necessary:** GPS, contact list size, and device model are proxy variables that encode region, socioeconomic class, and gender without explicitly naming them. A model trained on these features learns to replicate historical lending inequities. Removing them and retraining with fairness constraints breaks the discriminatory feedback loop and allows the model to score on direct creditworthiness signals only.

---

### C7 — Full Audit Logging Implemented at Step 7 (Decision Service)

**What changed:** Every automated decision now generates a structured audit log entry recording: applicant reference ID, model version number, input feature values used, raw output score, final decision (approve or decline), timestamp, and a machine-readable reason code. Declined applicants receive a plain-language explanation of the primary factors contributing to their result via the Customer Notifications channel (Step 8). Decisions where the score falls within 10% of the approval threshold are held for human review before the final outcome is issued.

**Why necessary:** The original Decision Service produces fully automated loan decisions with no record of how or why a decision was reached. This eliminates any possibility of regulatory audit, applicant appeal, or internal fairness review. Automated financial decisions affecting consumers require an auditable rationale under basic principles of algorithmic accountability and are increasingly required by data protection and financial services regulators.

---

### C8 — PII Masking and Anonymisation Applied at Step 9 (Analytics DB)

**What changed:** Before any record is written to the Analytics DB, all direct identifiers (name, phone number, national ID, email) are replaced with pseudonymous reference tokens. Aggregate outputs stored for reporting must pass a re-identification risk assessment before they are persisted. Analysts querying the Analytics DB access tokenized records only.

**Why necessary:** The original pipeline writes raw PII into the Analytics DB, making it accessible to data analysts and reporting tools without any need for direct identifiers. Analytical work requires patterns and aggregates — not names or phone numbers. Storing PII in an analytics system creates unnecessary exposure and violates the purpose limitation and data minimization requirements of Act 843.

---

### C9 — Data Sharing Agreement Required for 3rd-Party Partner at Step 10

**What changed:** No data flows to any third-party partner without a signed Data Processing Agreement (DPA) specifying: the permitted purpose of use, the categories of data transferred, retention and deletion obligations, breach notification timelines, and the partner's demonstrated data protection standard. Only anonymised or aggregated data is transferred. Raw PII is never shared. The partner's adequacy is assessed and documented before the data-sharing relationship is activated.

**Why necessary:** Ghana DPA Act 843, s.43 restricts the transfer of personal data to third parties without adequate safeguards and a documented legal basis. Sharing raw PII from an analytics system with an external partner, with no agreement in place, is an uncontrolled data transfer that could expose QuickLoan to liability for the partner's handling of the data. The DPA contract shifts documented responsibility appropriately and creates an enforceable obligation.

---

\_Corrected Data Flow Diagram — QuickLoan Mobile | Emmanuel Shyirambere| May 2026

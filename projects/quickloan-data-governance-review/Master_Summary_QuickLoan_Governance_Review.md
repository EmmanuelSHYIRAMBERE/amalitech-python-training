# QuickLoan Mobile — Ethical Data Governance Review

## Master Summary Document

**Prepared By:** Emmanuel Shyirambere
**Client:** QuickLoan Mobile, Accra, Ghana
**Date:** May 2026

---

## Engagement Context

QuickLoan Mobile is a Ghanaian fintech company offering instant micro-loans via a mobile app. Its core product is driven by a fully automated Machine Learning loan-scoring model. An internal audit raised four categories of concern: excessive data collection, absence of consent infrastructure, data quality failures, and potential algorithmic bias. This engagement was commissioned to independently verify those concerns, produce a structured risk analysis, and deliver actionable remediation recommendations.

---

## Deliverables Submitted

| #   | Document                    | Scope                                                                                                    | Status   |
| :-- | :-------------------------- | :------------------------------------------------------------------------------------------------------- | :------- |
| D1  | Governance Review Card      | Three risk findings (Data Quality, Legal & Compliance, Bias & Fairness) and one reporting recommendation | Complete |
| D2  | Corrected Data Flow Diagram | Nine annotated corrections (C1-C9) to the original pipeline with rationale for each change               | Complete |
| D3  | Summary of Review Process   | 283-word essay on methodology, lifecycle principles, and the DARD metric                                 | Complete |

---

## Consolidated Risk Register

| Risk                                                      | Severity | Primary Regulation                   | Affected Pipeline Steps                                         |
| :-------------------------------------------------------- | :------- | :----------------------------------- | :-------------------------------------------------------------- |
| Incomplete and inconsistent customer records              | HIGH     | Ghana DPA s.20                       | Step 2 (API Gateway), Step 5 (Preprocessing), Step 6 (ML Model) |
| No consent capture before data ingestion                  | CRITICAL | Ghana DPA s.17, s.19                 | Step 1 (App), Step 2 (API Gateway), Step 3 (Raw Data DB)        |
| Excessive PII collection (contact list, GPS, device logs) | CRITICAL | Ghana DPA s.20                       | Step 1 (User Mobile App)                                        |
| No data classification or retention policy                | HIGH     | Ghana DPA s.20, storage limitation   | Step 3 (Raw Data DB)                                            |
| PII processed in plaintext, proxy features fed to ML      | HIGH     | DPA s.20, fairness principles        | Step 5 (Preprocessing), Step 6 (ML Model)                       |
| Fully automated decisions with no audit logging           | HIGH     | Algorithmic accountability, DPA s.43 | Step 7 (Decision Service)                                       |
| Analytics DB stores raw PII without masking               | HIGH     | Ghana DPA s.20, purpose limitation   | Step 9 (Analytics DB)                                           |
| Third-party data transfer with no agreement               | CRITICAL | Ghana DPA s.43                       | Step 10 (3rd-Party Partner)                                     |

---

## Key Findings Summary

### Finding 1 — Data Quality (HIGH)

Customer records enter the pipeline with missing required fields and conflicting date and phone number formats. Because the Raw Data DB applies no validation, these records reach the LoanScore ML Model where null-handling logic assigns default scores — producing unfair rejections driven by data entry failures rather than genuine credit risk.

**Primary fix:** Schema validation at the API Gateway; canonical format contract; Data Quality Score field per record.

---

### Finding 2 — Legal and Compliance (CRITICAL)

The app collects contact lists, GPS location history, and device logs without consent, without a documented lawful basis, and without any retention limit. This constitutes violations of Ghana DPA Act 843 sections 17, 19, and 20 simultaneously.

**Data Classification:** Contact list and GPS = SENSITIVE. National ID, financial records, phone number = CONFIDENTIAL.

**Primary fix:** Granular consent layer between API Gateway and Raw Data DB; data minimization removing contact list and GPS; DPO appointment and DPC registration; automated retention schedules.

---

### Finding 3 — Bias and Fairness (HIGH)

The LoanScore ML Model uses GPS location, contact list size, and device model as scoring features. These are proxy variables encoding geographic region, socioeconomic class, and gender. The Decision Service applies fully automated outcomes with no logging, no human review, and no explanation to declined applicants.

**Source of bias:** Historical bias in training data compounded by proxy feature selection.

**Primary fix:** Remove proxy features; implement full decision audit logging; add human review for borderline scores; retrain with Equalized Odds fairness constraint; activate monthly DARD monitoring.

---

### Reporting Recommendation — Demographic Approval Rate Disparity (DARD)

**Definition:** The monthly difference in loan approval rates between the highest-approved and lowest-approved demographic group, segmented by gender, region, and income tier.

**Formula:** `DARD = Approval Rate (highest group) - Approval Rate (lowest group)`

**Alert threshold:** Greater than 10 percentage points triggers a mandatory fairness review before the next scoring batch.

**Visualization:** Grouped Bar Chart (monthly rates per segment) with an overlaid reference line at the 10-point threshold. Secondary Line Chart tracking DARD trend over rolling 12-month history.

**Governance value:** DARD produces a single audit-ready metric that executives, regulators, and applicant advocates can interpret without ML expertise. It transforms continuous model monitoring into a governance obligation, not an afterthought.

---

## Prioritized Remediation Timeline

### Immediate — Before Next Scoring Batch

| Action                                                                           | Owner               | Rationale                                                                   |
| :------------------------------------------------------------------------------- | :------------------ | :-------------------------------------------------------------------------- |
| Remove contact list, GPS, and device log collection from mobile app              | Engineering         | DPA s.20 data minimization — these fields have no credit-assessment purpose |
| Enforce schema validation at API Gateway                                         | Engineering         | Prevents dirty records reaching the ML model                                |
| Deploy Consent and Validation Layer between Steps 2 and 3                        | Engineering + Legal | DPA s.19 — consent must precede data storage                                |
| Remove proxy features (GPS, contact list size, device model) from ML feature set | Data Science        | Breaks proxy discrimination mechanism immediately                           |
| Activate full audit logging at Decision Service (Step 7)                         | Engineering         | Creates minimum viable audit trail for regulatory compliance                |

### Short-Term — Within 30 Days

| Action                                                         | Owner            | Rationale                                                           |
| :------------------------------------------------------------- | :--------------- | :------------------------------------------------------------------ |
| Appoint a Data Protection Officer                              | Leadership       | Mandatory under Act 843 for data controllers of this scale          |
| Register with Ghana's Data Protection Commission               | Legal + DPO      | Mandatory statutory obligation                                      |
| Define and implement data classification schema on Raw Data DB | Data Engineering | Enables downstream access controls and retention enforcement        |
| Implement automated retention deletion schedules               | Data Engineering | DPA storage limitation principle — indefinite retention is unlawful |
| Apply PII masking and tokenisation in Preprocessing Service    | Engineering      | Eliminates plaintext PII from ML feature pipeline                   |
| Anonymise Analytics DB records                                 | Data Engineering | Removes unnecessary PII exposure in analytics environment           |

### Medium-Term — Within 90 Days

| Action                                                                   | Owner             | Rationale                                                              |
| :----------------------------------------------------------------------- | :---------------- | :--------------------------------------------------------------------- |
| Retrain LoanScore model with debiased data and Equalized Odds constraint | Data Science      | Addresses root cause of proxy discrimination in model scoring          |
| Activate DARD monthly monitoring dashboard                               | Data Science + BI | Provides ongoing fairness accountability and regulatory evidence trail |
| Sign Data Processing Agreements with all third-party partners            | Legal             | DPA s.43 — third-party transfers require documented safeguards         |
| Conduct a full Data Protection Impact Assessment (DPIA)                  | DPO + Legal       | Required for high-risk automated processing systems under Act 843      |

---

## Compliance Reference

| Provision | Ghana DPA Act 843                              | Relevance to QuickLoan                                                  |
| :-------- | :--------------------------------------------- | :---------------------------------------------------------------------- |
| s.17      | Lawful processing requirement                  | No documented legal basis for contact list or GPS collection            |
| s.19      | Consent before collection                      | No consent screen or consent records exist in the pipeline              |
| s.20      | Data minimization and purpose limitation       | Collection of contact list, GPS, and device logs exceeds stated purpose |
| s.37      | Data subject access and erasure rights         | No mechanism for applicants to request deletion of their data           |
| s.43      | Third-party and cross-border transfer controls | No Data Processing Agreement with third-party analytics partner         |
| s.71      | Penalties                                      | Up to GHS 60,000 per violation; criminal liability for wilful breach    |

---

\_Master Summary — QuickLoan Mobile Ethical Data Governance Review | Emmanuel Shyirambere | May 2026

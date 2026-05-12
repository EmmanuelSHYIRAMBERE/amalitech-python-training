# QuickLoan Mobile — Ethical Data Governance Review

**Role:** Independent Data Governance Consultant
**Client:** QuickLoan Mobile, Accra, Ghana
**Regulatory Framework:** Ghana Data Protection Act, 2012 (Act 843)
**Date:** May 2026

## Overview

QuickLoan Mobile is a Ghanaian fintech startup offering instant micro-loans via a
mobile app powered by a fully automated ML loan-scoring model. This repository
contains a structured independent governance review commissioned after an internal
audit flagged critical concerns around data collection practices, compliance
posture, and algorithmic fairness.

## Deliverables

| File                                                                  | Description                                                                                           |
| :-------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------- |
| [Master Summary](Master_Summary_QuickLoan_Governance_Review.md)       | Consolidated risk register, remediation timeline, and compliance reference table                      |
| [D1 — Governance Review Card](D1_Governance_Review_Card.md)           | Three risk findings (Data Quality, Legal & Compliance, Bias & Fairness) and the DARD reporting metric |
| [D2 — Corrected Data Flow Diagram](D2_Corrected_Data_Flow_Diagram.md) | Nine annotated corrections (C1–C9) to the original flawed pipeline                                    |
| [D3 — Summary of Review Process](D3_Summary_of_Review_Process.md)     | 283-word essay on methodology, lifecycle principles, and governance metric                            |

## Risk Summary

| Risk Area          | Severity | Key Finding                                                                                            |
| :----------------- | :------- | :----------------------------------------------------------------------------------------------------- |
| Data Quality       | HIGH     | Incomplete records and inconsistent formats propagate to the ML model                                  |
| Legal & Compliance | CRITICAL | No consent infrastructure; excessive SENSITIVE PII collected; Act 843 s.17/s.19/s.20 violations        |
| Bias & Fairness    | HIGH     | Proxy features (GPS, contact list, device model) encode demographic discrimination; zero audit logging |

## Reporting Metric

**Demographic Approval Rate Disparity (DARD):** The monthly difference in loan
approval rates between the highest-approved and lowest-approved demographic group,
segmented by gender, region, and income tier. Alert threshold: >10 percentage
points triggers mandatory model review.

## Regulatory Reference

Ghana Data Protection Act, 2012 (Act 843) — sections 17, 19, 20, 37, 43, 71.

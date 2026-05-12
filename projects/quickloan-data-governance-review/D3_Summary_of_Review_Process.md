# Deliverable 3: Summary of Review Process

**Prepared by:** Emmanuel Shyirambere | **Date:** May 2026

---

## Summary of Review Process

My review of QuickLoan Mobile's data pipeline began by mapping every system component against the six stages of the data lifecycle: Collection, Storage, Processing, Use, Sharing, and Deletion. Rather than treating the audit concerns as isolated incidents, this lifecycle framework imposed a sequential discipline — forcing each pipeline stage to be evaluated on its own governance compliance before the next could be considered. This structure is what prevented superficial findings and surfaced the systemic nature of the problems.

At the **Collection** stage, I applied the Data Minimization principle from Ghana's DPA (Act 843, s.20). The app's collection of contact lists, GPS history, and device logs — none of which bear any logical relationship to creditworthiness assessment — constituted an immediate violation. Data Classification followed directly: assigning each collected field to a tier (SENSITIVE, CONFIDENTIAL, INTERNAL, or PUBLIC) made the compliance exposure concrete. SENSITIVE data was being ingested, stored, and processed without consent records, without retention rules, and without any classification schema governing access. Every downstream stage was therefore operating on unlawfully held personal data.

At the **Storage** stage, the absence of a classification schema on the Raw Data DB meant no retention schedule existed and no access differentiation was enforced. This is not merely a housekeeping issue — indefinite retention of SENSITIVE and CONFIDENTIAL data without legal basis is a direct Act 843 violation, and it means the organization accumulates liability with every passing day.

At the **Processing** stage, examining the features fed to the LoanScore ML model exposed the proxy bias problem. GPS location, contact list size, and device model do not measure creditworthiness. They measure geography, social network size, and purchasing power — attributes that correlate with region, gender, and income class in Ghana's context. These are textbook proxy variables, and their presence in the feature set means the model discriminates structurally without ever naming a protected attribute.

The proposed **Demographic Approval Rate Disparity (DARD)** metric addresses the transparency and accountability gap that runs through the entire pipeline. DARD computes the monthly difference in loan approval rates between demographic groups segmented by gender, region, and income tier. When surfaced as a Grouped Bar Chart with an alert threshold line, it translates model behaviour into a single, board-reportable number that requires no ML expertise to interpret. Executives, regulators, and civil society advocates can read it immediately. More importantly, DARD creates a continuous audit trail. If Ghana's Data Protection Commission investigates, or if an applicant contests a rejection under Act 843's data subject rights provisions, QuickLoan can demonstrate that it was actively monitoring, detecting, and correcting disparate impact — not discovering it only when compelled to do so. That distinction separates an organization practicing ethical governance from one that merely claims to.

---

---

\_Summary of Review Process — QuickLoan Mobile | Emmanuel Shyirambere| May 2026

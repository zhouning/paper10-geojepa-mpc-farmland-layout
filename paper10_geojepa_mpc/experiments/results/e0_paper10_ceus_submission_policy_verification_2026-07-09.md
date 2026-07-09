# Paper10 CEUS submission policy verification

Date: 2026-07-09

Status: ceus_policy_verified_submission_packet_ready

Target journal: Computers, Environment and Urban Systems

## Source basis

This closeout verifies the current CEUS/Elsevier submission policy layer against the already tracked Paper10 algorithm, experiment, archive and artwork package. It does not rerun training or rollouts and does not add experimental claims.

Checked official sources:

- CEUS Guide for Authors: `https://www.elsevier.com/journals/computers-environment-and-urban-systems/0198-9715/guide-for-authors`
- Elsevier artwork instructions linked from the CEUS Guide for Authors: `https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-sizing`
- Elsevier research data policy linked from the CEUS Guide for Authors: `https://www.elsevier.com/researcher/author/policies-and-guidelines/research-data`

## Policy findings

- CEUS uses Elsevier Research Data Policy Option B. Data deposit and citation are encouraged where data can be shared; restricted data can be handled by a Data Availability statement that explains the restriction and maps the public supporting materials.
- The checked CEUS policy does not require pre-submission editor acceptance before disclosing that original Bishan and Dongxing DLTB data are confidential and cannot be externally provided.
- The author-confirmed 4open README.md direct reviewer link is sufficient as the reviewer-facing code/evidence route for submission preparation. The missing visible 4open snapshot identifier is a disclosure/versioning limitation, not a CEUS pre-submission blocker.
- Main Figure 1 has a vector PDF and a 3870 px wide PNG. The PNG exceeds the Elsevier combination-artwork full-page 500 dpi width threshold of 3740 px, and the PDF provides the vector route.
- The CEUS highlights file has five highlights, and each highlight is under 85 characters including spaces.
- CEUS double-anonymous submission requirements are handled by keeping title-page metadata separate from the anonymized manuscript body.

## Current submission decision

The latest controlled status is `ceus_policy_verified_submission_packet_ready`: Paper10 is ready for formal CEUS submission as a bounded manuscript package, with confidential raw-DLTB non-availability disclosed in the Data and Code Availability statement and cover letter.

The remaining author actions are submission-system fields, not algorithm, experiment, archive, or artwork blockers: author names, affiliations, corresponding author, CRediT roles, competing-interest declaration, funding/acknowledgements, and final upload of the prepared manuscript/highlights/figures/reviewer link.

## Claim boundary

This verification does not claim broad 50-state scale-up, transfer superiority, operational cadastral deployment, or a general-purpose constrained reinforcement-learning solver. It only closes the over-strict external-policy blockers that were previously treated as no-go items.
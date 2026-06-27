# Paper10 target-journal fit assessment

Date: 2026-06-27

Status: target-journal fit assessment based on current official journal scopes
and the frozen Paper10 evidence boundary. This document does not add an
experiment and does not change any result claim.

## One-sentence paper argument

In constrained farmland-layout planning, Paper10 shows a monitor-gated
GeoJEPA-MPC workflow in which value labels train a value filter only after
quality gates pass, supported by the Bishan 20x16/top5 positive anchor,
source-derived mechanism checks, and negative boundary diagnostics at larger
or cross-region settings.

## Current evidence boundary used for journal routing

- Strongest positive claim: Bishan 20x16/top5 under the matched rollout
  protocol.
- Main methodological claim: monitor-gated value-label generation, executable
  masks, and value-filtered MPC form a reproducible planning-support workflow.
- Negative or boundary evidence: larger tested Bishan rows and Dongxing/Neijiang
  rows do not support broad scale-up or robust transfer claims.
- Reporting policy: descriptive statistics by default; no p-values or confidence
  intervals without a new predefined analysis plan.
- Practical-deployment boundary: irregular cadastral deployment and public data
  access routes remain unresolved for final packaging.

## Official scope signals checked

| journal | official source checked | scope signal relevant to Paper10 |
|---|---|---|
| Computers, Environment and Urban Systems | https://www.sciencedirect.com/journal/computers-environment-and-urban-systems/about/aims-and-scope | Geospatial computer-based research on built and natural environments, land/resource management, decision support, geocomputation, AI, space-time simulation, planning and management. |
| Environmental Modelling & Software | https://www.elsevier.com/journals/environmental-modelling-and-software/1364-8152/guide-for-authors | Environmental modelling/software, decision support systems, GIS/remote sensing, AI systems, land resource management, software verification/validation, and generalizable modelling insights. |
| Computers and Electronics in Agriculture | https://www.sciencedirect.com/journal/computers-and-electronics-in-agriculture/about/aims-and-scope | Computer hardware/software, AI, simulation modelling and control systems for agricultural problems, with emphasis on novelty and investigator-developed tools. |
| Smart Agricultural Technology | https://www.sciencedirect.com/journal/smart-agricultural-technology/about/aims-and-scope | Practical smart systems integrating computing with electronics/controls for agricultural planning and production at farm scale or in production environments. |
| Artificial Intelligence in Agriculture | https://www.keaipublishing.com/en/journals/artificial-intelligence-in-agriculture/ | AI theory and practice in agriculture, including AI decision support, precision agriculture, optimization management, systems modelling, machine learning, and remote sensing. |
| International Journal of Applied Earth Observation and Geoinformation | https://www.elsevier.com/journals/international-journal-of-applied-earth-observation-and-geoinformation/1569-8432/guide-for-authors | Earth-observation and geoinformation work for natural-resource and environmental management, including agricultural land, geospatial mapping, spatial uncertainty, and GeoAI. |
| Nature Communications | https://www.nature.com/ncomms/aims | Multidisciplinary papers that represent important advances of significance to specialists. |
| Nature Machine Intelligence | https://www.nature.com/natmachintell/aims | High-quality original research in machine learning, robotics and AI, including broader impacts across science, society and industry. |
| Scientific Reports | https://www.nature.com/srep/about | Broad-scope open-access journal across natural sciences and engineering, emphasizing robust original research rather than a narrow field audience. |

## Recommended route ranking

### 1. Computers, Environment and Urban Systems

Recommendation: best first target under the current evidence boundary.

Why it fits:

- The existing CEUS route in the Paper10 package remains defensible.
- Paper10 is fundamentally a geospatial computer-based decision-support method,
  not only an agronomic application.
- The journal explicitly covers built/natural environments, land and resource
  management, geocomputation, decision support, complex systems, AI,
  space-time simulation, planning, and management.
- Paper10's strongest contribution is the evidence-control workflow: monitor
  gates decide which value labels can affect planning claims.

Main risk:

- CEUS is high-selectivity and has a strong urban/regional-planning audience.
  A manuscript that reads as a narrow agriculture ML prototype could be desk
  rejected.

Required positioning:

- Title should foreground geospatial decision support or constrained land-layout
  planning, not only farmland production.
- Abstract should lead with planning under executable spatial constraints, then
  introduce the Bishan farmland case as the study environment.
- Discussion must state that current evidence supports bounded planning support,
  not broad deployment.

### 2. Environmental Modelling & Software

Recommendation: strong alternate first target if the manuscript is reframed as
a reproducible environmental decision-support and modelling-software paper.

Why it fits:

- The journal directly welcomes environmental software, model evaluation,
  decision support systems, GIS, AI systems, and land-resource management.
- Paper10 has a stronger-than-usual reproducibility package: tests, preflight
  checks, source-derived tables, plotting scripts, and claim-boundary registers.
- The negative 50-state and transfer diagnostics can be framed as rigorous model
  limitation reporting.

Main risk:

- EMS expects generalizable modelling insight and often asks for software
  usability, reliability, verification/validation, user needs, and sometimes
  development/adoption costs. Paper10 has code verification but not a user study
  or operational adoption evidence.

Required positioning:

- Reframe the manuscript around a reproducible environmental decision-support
  workflow.
- Add a compact software architecture, verification, and open-source/licence
  subsection.
- Treat performance as one part of model credibility, not the entire paper.

### 3. Computers and Electronics in Agriculture

Recommendation: attractive agriculture-first route, but higher desk-risk than
CEUS under the current evidence package.

Why it fits:

- CEA covers software, AI and simulation modelling for agricultural problems.
- Paper10 has investigator-developed tools rather than only off-the-shelf model
  application.

Main risk:

- The journal explicitly emphasizes novelty in computers/electronics for
  agriculture and warns that work based mainly on previously published datasets
  may be preliminary unless authors provide rigorous data collected under
  controlled and reported conditions.
- Paper10's current strongest result is bounded and local; the larger and
  cross-region tests are not positive anchors.

Required positioning:

- Submit here only if the full-data access route and data-generation narrative
  are closed cleanly.
- Emphasize method innovation, monitor gates, executable masks, and reproducible
  value-filtered planning rather than an application-only story.

### 4. Smart Agricultural Technology

Recommendation: safer applied-agriculture backup if the authors prioritize fit
and lower novelty pressure over impact-factor ambition.

Why it fits:

- SAT is a companion outlet for applied smart agricultural technology and covers
  algorithm development, AI, smart systems and on-farm planning.

Main risk:

- SAT still emphasizes farm-scale or production-environment applications. Paper10
  currently has no full operational deployment and should not be written as a
  solved production tool.

Required positioning:

- Frame the paper as planning-support technology with bounded real-environment
  execution-chain checks.
- Keep the manuscript concise and practical, with clearer user workflow and
  deployment limitations than the CEUS/EMS route would require.

### 5. Artificial Intelligence in Agriculture

Recommendation: stretch target, not the default route now.

Why it fits:

- The scope includes AI-based decision support, AI in agricultural optimization
  management, machine learning, systems modelling and remote sensing.

Main risk:

- The journal is high-impact and likely expects a broader AI contribution,
  stronger validation, or clearer agricultural AI significance than the current
  bounded Bishan anchor provides.

Required positioning:

- Use only after strengthening the algorithmic novelty story and adding stronger
  multi-setting validation, or after reframing the negative diagnostics as a
  principled monitor-gated learning contribution.

### 6. International Journal of Applied Earth Observation and Geoinformation

Recommendation: conditional backup only if the manuscript is rewritten toward
GeoAI/geoinformation and the data story foregrounds earth-observation or mapping
inputs.

Why it fits:

- JAG covers agricultural land, land resources, geoinformation, geospatial
  mapping, spatial uncertainty and GeoAI.

Main risk:

- Its core scope is earth-observation data, normally from satellite or aircraft
  platforms. Paper10 is currently a geospatial planning/world-model paper, not
  primarily an earth-observation retrieval or mapping paper.

Required positioning:

- Do not target JAG unless the Methods and Introduction can honestly make
  earth-observation/geoinformation data central rather than incidental.

### 7. Scientific Reports

Recommendation: broad-scope fallback, not the preferred first route.

Why it fits:

- Scientific Reports has broad coverage across natural sciences and engineering,
  so Paper10 could fit if the methods and data are technically robust.

Main risk:

- It is less targeted to geospatial planning, environmental software or
  agricultural AI readers, so the paper may lose specialist impact even if it
  clears technical review.

Required positioning:

- Use this route only after higher-fit specialist journals are declined or if
  speed and broad OA visibility become the dominant author priority.

## Routes not recommended now

- Nature Communications: the current bounded evidence does not yet support the
  level of broad, important specialist advance expected by the journal.
- Nature Machine Intelligence: the method is interesting, but the current package
  does not yet establish a broad AI advance across tasks, datasets or deployment
  settings.
- Nature Food or Nature Sustainability: Paper10 lacks the food-system,
  sustainability-policy, multi-region or real-world outcome evidence those routes
  would require.
- Agricultural Systems or Land Use Policy: the manuscript is algorithmic and
  geospatial-computational; it currently lacks the systems-analysis or policy
  contribution those outlets would expect.

## Decision rule

Default route: CEUS first.

Use EMS first only if the manuscript is explicitly rewritten as a modelling and
software/decision-support article with a stronger verification and software
architecture section.

Use CEA first only if the authors want an agriculture-specific audience and can
close the full-data narrative strongly enough to withstand CEA's novelty and data
rigour screen.

Use SAT or Scientific Reports as backup routes, not as the default first target.

## Manuscript changes implied by the CEUS-first route

- Working title direction: `Monitor-gated geospatial world models for constrained
  land-layout planning`.
- Lead contribution: a geospatial decision-support workflow that prevents weak
  value labels from entering planning claims.
- Main positive evidence: Bishan 20x16/top5 under the matched protocol.
- Boundary evidence: larger Bishan rows and Dongxing/Neijiang calibration rows.
- Required final close-out before journal formatting: target figure dimensions,
  final Figure 1 artwork decision, data/code availability wording, repository
  DOI/licence fields, and caption-length adaptation.
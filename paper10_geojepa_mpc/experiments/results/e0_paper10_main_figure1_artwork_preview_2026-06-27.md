# Paper10 Main Figure 1 artwork preview

Date: 2026-06-27

Status: workflow artwork preview and reproducible plotting script. This file
does not report a new experiment and does not change the paper-facing evidence
boundary.

## Purpose

The preview closes the open Main Figure 1 artwork gap at the schematic level.
It turns the existing figure contract into a reproducible matplotlib drawing
that shows the monitor-gated value-label workflow before final journal-specific
layout decisions are made.

## Figure contract

- Core conclusion: value-head training is conditional on label quality.
- Archetype: schematic-led composite.
- Evidence logic: executable masks define valid actions; a rank checkpoint
  proposes and scores candidates; label generation records returns, one-step
  rewards, and candidate scores; monitor gates decide whether labels advance;
  only `decision=continue` labels train the value head used by
  `selector=value_filter`.
- Stop logic: failed monitor rows stop as diagnostics and boundary evidence.
  They do not train the value head.

## Script and local outputs

Regeneration command:

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\plot_main_figure1_workflow.py
```

Tracked script:

- `scripts/paper10/plot_main_figure1_workflow.py`

Local preview outputs under ignored `reviewer_outputs/`:

- `reviewer_outputs/paper10_main_figure1_workflow/main_figure1_workflow.png`
- `reviewer_outputs/paper10_main_figure1_workflow/main_figure1_workflow.svg`
- `reviewer_outputs/paper10_main_figure1_workflow/main_figure1_workflow.pdf`

The generated PNG was checked for nonblank content after rendering:

- size: `3930 x 2222` pixels
- non-white bounding box: `(117, 155, 3867, 2099)`
- PNG bytes: `720888`
- SVG bytes: `31348`
- PDF bytes: `52666`

## Claim boundary

- The preview is workflow artwork, not experimental evidence.
- It does not add a new quantitative result.
- It preserves the current positive anchor on Bishan 20x16/top5 under the
  matched protocol.
- Fifty-state rows remain boundary evidence unless a future predefined
  experiment changes that status.
- Dongxing/Neijiang rows remain calibration and stress-test evidence, not
  robust transfer-superiority evidence.
- Descriptive reporting remains the default statistical policy.

## Remaining figure/export work

- Choose target-journal figure dimensions and caption length.
- Decide whether this generated SVG/PDF becomes the final submitted artwork or
  is redrawn during journal-specific conversion.
- Update the source-data map, caption packet, and final export package only
  after the final artwork choice is made.
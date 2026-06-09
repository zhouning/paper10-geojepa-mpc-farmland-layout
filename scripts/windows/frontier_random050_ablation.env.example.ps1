# Copy this file to scripts/windows/frontier_random050_ablation.env.ps1 and edit
# paths for the Windows machine before running the ablation script.

# Full Bishan prepared-data root on this Windows workstation. This directory
# must contain:
# tool2/transitions.npz
# tool2/pairwise.npz
# dem_slope_analysis/output/DLTB_with_slope.gpkg
# results_real/blocks/
# townships.json
$DataRoot = "D:\test"

# Output root outside the Git checkout. The runner creates one directory per
# grid row and writes logs, labels, monitor reports, and summaries here.
$RunRoot = "D:\test\paper10_runs"

# Python executable verified on this machine.
$PythonBin = "D:\adk\.venv\Scripts\python.exe"

# CUDA is not required. The verified Windows route uses CPU.
$Device = "cpu"

# Keep label-only ablation as the default. Set to 1 only when a monitor gate
# passes and you want the runner to train the value head for passing rows.
$TrainOnPass = 0

# Run the full Paper10 test suite before long label generation.
$RunPytest = 1

# Gate top-k values. A row is trainable only when one of these monitor gates
# returns "continue".
$GateTopKs = @(3, 4, 5)

# Candidate grid for the next Paper10 50-state diagnosis.
$Grid = @(
    @{
        Name = "frontier_random050_50x16_h5_seed46_f050"
        NStates = 50
        CandidateActions = 16
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 46
        TrainingSeed = 3046
    },
    @{
        Name = "frontier_random050_50x20_h5_seed46_f050"
        NStates = 50
        CandidateActions = 20
        LabelHorizon = 5
        FrontierFraction = 0.5
        LabelSeed = 46
        TrainingSeed = 3046
    },
    @{
        Name = "frontier_random050_50x24_h5_seed46_f075"
        NStates = 50
        CandidateActions = 24
        LabelHorizon = 5
        FrontierFraction = 0.75
        LabelSeed = 46
        TrainingSeed = 3046
    },
    @{
        Name = "frontier_random050_50x24_h5_seed46_f100"
        NStates = 50
        CandidateActions = 24
        LabelHorizon = 5
        FrontierFraction = 1.0
        LabelSeed = 46
        TrainingSeed = 3046
    }
)

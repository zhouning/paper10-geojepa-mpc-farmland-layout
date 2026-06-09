Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Windows local runner for Paper10 frontier_random050 label-only ablation.
# Run from any directory after editing scripts/windows/frontier_random050_ablation.env.ps1.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir "..\..")).Path

$DataRoot = "D:\test"
$RunRoot = "D:\test\paper10_runs"
$PythonBin = "D:\adk\.venv\Scripts\python.exe"
$Device = "cpu"
$TrainOnPass = 0
$RunPytest = 1

$Gamma = "0.99"
$ScoreBatchSize = 512
$TrainingEpochs = 3
$TrainingBatchSize = 16
$TransitionSamples = 6000
$PairwiseSubsample = 24
$NPairs = 8
$GateTopKs = @(3, 4, 5)

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

$EnvFile = if ($env:ENV_FILE) {
    $env:ENV_FILE
} else {
    Join-Path $ScriptDir "frontier_random050_ablation.env.ps1"
}
if (Test-Path -LiteralPath $EnvFile) {
    . $EnvFile
}

function New-Directory {
    param([Parameter(Mandatory = $true)][string]$Path)
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Require-Path {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing required path: $Path"
    }
}

function Invoke-LoggedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$LogPath,
        [Parameter(Mandatory = $true)][string]$File,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    New-Directory (Split-Path -Parent $LogPath)
    $commandLine = "$File $($Arguments -join ' ')"
    Write-Host "`$ $commandLine"
    Set-Content -LiteralPath $LogPath -Value "`$ $commandLine" -Encoding UTF8

    $StdoutTemp = [System.IO.Path]::GetTempFileName()
    $StderrTemp = [System.IO.Path]::GetTempFileName()
    try {
        $Process = Start-Process `
            -FilePath $File `
            -ArgumentList $Arguments `
            -WorkingDirectory (Get-Location).Path `
            -RedirectStandardOutput $StdoutTemp `
            -RedirectStandardError $StderrTemp `
            -WindowStyle Hidden `
            -Wait `
            -PassThru

        $StdoutLines = @(Get-Content -LiteralPath $StdoutTemp)
        $StderrLines = @(Get-Content -LiteralPath $StderrTemp)
        foreach ($Line in $StdoutLines) {
            Write-Host $Line
            Add-Content -LiteralPath $LogPath -Value $Line -Encoding UTF8
        }
        foreach ($Line in $StderrLines) {
            Write-Host $Line
            Add-Content -LiteralPath $LogPath -Value $Line -Encoding UTF8
        }

        if ($Process.ExitCode -ne 0) {
            throw "Command failed with exit code $($Process.ExitCode): $commandLine"
        }
    }
    finally {
        Remove-Item -LiteralPath $StdoutTemp -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $StderrTemp -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-IfMissing {
    param(
        [Parameter(Mandatory = $true)][string]$OutputPath,
        [Parameter(Mandatory = $true)][string]$LogPath,
        [Parameter(Mandatory = $true)][string]$File,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    if (Test-Path -LiteralPath $OutputPath) {
        Write-Host "Skipping because final artifact already exists: $OutputPath"
        return
    }
    Invoke-LoggedCommand -LogPath $LogPath -File $File -Arguments $Arguments
    Require-Path $OutputPath
}

function Convert-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

Set-Location $RepoRoot

New-Directory $RunRoot
Require-Path $PythonBin
Require-Path (Join-Path $DataRoot "tool2/transitions.npz")
Require-Path (Join-Path $DataRoot "tool2/pairwise.npz")
Require-Path (Join-Path $DataRoot "dem_slope_analysis/output/DLTB_with_slope.gpkg")
Require-Path (Join-Path $DataRoot "results_real/blocks")
Require-Path (Join-Path $DataRoot "townships.json")

$BaseCheckpoint = Join-Path $RepoRoot "paper10_geojepa_mpc/experiments/checkpoints/e0_bishan_rank_seed2028/rank_seed2028.pt"
Require-Path $BaseCheckpoint

if ($RunPytest -eq 1) {
    Invoke-LoggedCommand `
        -LogPath (Join-Path $RunRoot "pytest.log") `
        -File $PythonBin `
        -Arguments @("-m", "pytest", "paper10_geojepa_mpc/tests", "-q", "-p", "no:cacheprovider")
}

$AllResults = @()

foreach ($Config in $Grid) {
    $RunName = [string]$Config.Name
    $RunDir = Join-Path $RunRoot $RunName
    $LogDir = Join-Path $RunDir "logs"
    $ReportDir = Join-Path $RunDir "reports"
    $CheckpointDir = Join-Path $RunDir "checkpoints"
    New-Directory $RunDir
    New-Directory $LogDir
    New-Directory $ReportDir
    New-Directory $CheckpointDir

    $NStates = [int]$Config.NStates
    $CandidateActions = [int]$Config.CandidateActions
    $LabelHorizon = [int]$Config.LabelHorizon
    $FrontierFraction = [string]$Config.FrontierFraction
    $LabelSeed = [int]$Config.LabelSeed
    $TrainingSeed = [int]$Config.TrainingSeed

    $ResultPrefix = "e0_value_labels_frontier_random050_rank_seed2028_$($NStates)x$($CandidateActions)_h$($LabelHorizon)_seed$($LabelSeed)"
    $LabelPath = Join-Path $RunDir "$ResultPrefix.npz"
    $LabelPartialPath = Join-Path $RunDir "$ResultPrefix.partial.npz"

    # Command preview: --candidate-mode frontier_random --frontier-fraction <grid value>
    Invoke-IfMissing `
        -OutputPath $LabelPath `
        -LogPath (Join-Path $LogDir "value_label_generation.log") `
        -File $PythonBin `
        -Arguments @(
            "-X", "utf8", "-m", "paper10_geojepa_mpc.experiments.value_label_generation",
            "--checkpoint", $BaseCheckpoint,
            "--prepared-dir", $DataRoot,
            "--n-states", [string]$NStates,
            "--candidate-actions", [string]$CandidateActions,
            "--label-horizon", [string]$LabelHorizon,
            "--gamma", $Gamma,
            "--seed", [string]$LabelSeed,
            "--mask-mode", "executable",
            "--candidate-mode", "frontier_random",
            "--frontier-fraction", $FrontierFraction,
            "--advance-policy", "random",
            "--continuation-policy", "random",
            "--score-batch-size", [string]$ScoreBatchSize,
            "--device", $Device,
            "--partial-output", $LabelPartialPath,
            "--progress-every", "1",
            "--output", $LabelPath
        )

    $TopKResults = @()
    $PassingTopKs = @()
    foreach ($TopK in $GateTopKs) {
        $DiagJson = Join-Path $RunDir "value_label_diagnostics_top$($TopK).json"
        $DiagMd = Join-Path $ReportDir "value_label_diagnostics_top$($TopK).md"
        $MonitorJson = Join-Path $RunDir "value_label_monitor_top$($TopK).json"
        $MonitorMd = Join-Path $ReportDir "value_label_monitor_top$($TopK).md"

        Invoke-IfMissing `
            -OutputPath $DiagJson `
            -LogPath (Join-Path $LogDir "value_label_diagnostics_top$($TopK).log") `
            -File $PythonBin `
            -Arguments @(
                "-X", "utf8", "-m", "paper10_geojepa_mpc.experiments.value_label_diagnostics",
                "--input", $LabelPath,
                "--top-k", [string]$TopK,
                "--output-json", $DiagJson,
                "--output-md", $DiagMd
            )

        Invoke-IfMissing `
            -OutputPath $MonitorJson `
            -LogPath (Join-Path $LogDir "value_label_monitor_top$($TopK).log") `
            -File $PythonBin `
            -Arguments @(
                "-X", "utf8", "-m", "paper10_geojepa_mpc.experiments.value_label_monitor",
                "--input", $LabelPath,
                "--top-k", [string]$TopK,
                "--output-json", $MonitorJson,
                "--output-md", $MonitorMd
            )

        $Monitor = Convert-JsonFile $MonitorJson
        if ($Monitor.decision -eq "continue") {
            $PassingTopKs += $TopK
        }
        $TopKResults += [pscustomobject]@{
            top_k = $TopK
            decision = $Monitor.decision
            candidate_topk_regret = $Monitor.metrics.candidate_topk_regret
            candidate_topk_overlap = $Monitor.metrics.candidate_topk_overlap
            one_step_topk_regret = $Monitor.metrics.one_step_topk_regret
            monitor_json = $MonitorJson
            monitor_md = $MonitorMd
        }
    }

    $SelectedTopK = $null
    $TrainingMetrics = $null
    $TrainingCheckpoint = $null
    if ($TrainOnPass -eq 1 -and $PassingTopKs.Count -gt 0) {
        $SelectedTopK = ($PassingTopKs | Measure-Object -Maximum).Maximum
        $ValueHeadRun = "e0_frontier_random050_value_head_$($NStates)x$($CandidateActions)_h$($LabelHorizon)_seed$($LabelSeed)_top$($SelectedTopK)"
        $ValueHeadDir = Join-Path $CheckpointDir $ValueHeadRun
        New-Directory $ValueHeadDir
        $TrainingCheckpoint = Join-Path $ValueHeadDir "value_head_seed$($TrainingSeed).pt"
        $TrainingMetrics = Join-Path $RunDir "$($ValueHeadRun)_metrics.json"

        Invoke-IfMissing `
            -OutputPath $TrainingMetrics `
            -LogPath (Join-Path $LogDir "value_head_train_top$($SelectedTopK).log") `
            -File $PythonBin `
            -Arguments @(
                "-X", "utf8", "-m", "paper10_geojepa_mpc.experiments.run_e0_value_head_train",
                "--transition-path", (Join-Path $DataRoot "tool2/transitions.npz"),
                "--pairwise-path", $LabelPath,
                "--init-checkpoint", $BaseCheckpoint,
                "--checkpoint-path", $TrainingCheckpoint,
                "--output", $TrainingMetrics,
                "--epochs", [string]$TrainingEpochs,
                "--batch-size", [string]$TrainingBatchSize,
                "--transition-samples", [string]$TransitionSamples,
                "--pairwise-states", [string]$NStates,
                "--pairwise-subsample", [string]$PairwiseSubsample,
                "--n-pairs", [string]$NPairs,
                "--candidate-top-k", [string]$SelectedTopK,
                "--candidate-batch-states", "1",
                "--candidate-max-states", [string]$NStates,
                "--checkpoint-metric", "auto",
                "--checkpoint-mode", "min",
                "--seed", [string]$TrainingSeed,
                "--device", $Device
            )
        Require-Path $TrainingCheckpoint
    }

    $AllResults += [pscustomobject]@{
        run_name = $RunName
        n_states = $NStates
        candidate_actions = $CandidateActions
        label_horizon = $LabelHorizon
        frontier_fraction = [double]$FrontierFraction
        label_seed = $LabelSeed
        label_path = $LabelPath
        passing_topks = $PassingTopKs
        selected_top_k = $SelectedTopK
        train_on_pass = $TrainOnPass
        training_metrics = $TrainingMetrics
        training_checkpoint = $TrainingCheckpoint
        monitors = $TopKResults
    }
}

$Summary = [pscustomobject]@{
    created_at = (Get-Date).ToString("o")
    repo_root = $RepoRoot
    data_root = $DataRoot
    run_root = $RunRoot
    python_bin = $PythonBin
    device = $Device
    train_on_pass = $TrainOnPass
    gate_topks = $GateTopKs
    runs = $AllResults
}

$SummaryJson = Join-Path $RunRoot "frontier_random050_ablation_summary.json"
$SummaryMd = Join-Path $RunRoot "frontier_random050_ablation_summary.md"
$Summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $SummaryJson -Encoding UTF8

$Lines = @(
    "# Paper10 frontier_random050 Windows ablation summary",
    "",
    "Data root: ``$DataRoot``",
    "Device: ``$Device``",
    "Train on pass: ``$TrainOnPass``",
    "",
    "| run | states | candidates | frontier fraction | seed | passing top-k | selected top-k |",
    "|---|---:|---:|---:|---:|---|---|"
)
foreach ($Result in $AllResults) {
    $Passing = if ($Result.passing_topks.Count -gt 0) { ($Result.passing_topks -join ",") } else { "none" }
    $Selected = if ($null -ne $Result.selected_top_k) { [string]$Result.selected_top_k } else { "none" }
    $Lines += "| $($Result.run_name) | $($Result.n_states) | $($Result.candidate_actions) | $($Result.frontier_fraction) | $($Result.label_seed) | $Passing | $Selected |"
}
$Lines += ""
$Lines += "JSON summary: ``$SummaryJson``"
$Lines | Set-Content -LiteralPath $SummaryMd -Encoding UTF8

Write-Host "Summary JSON: $SummaryJson"
Write-Host "Summary Markdown: $SummaryMd"

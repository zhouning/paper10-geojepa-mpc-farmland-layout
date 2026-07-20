# Paper10 PCC v1 Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the deployable PCC-GeoJEPA-MPC algorithm, freeze its development-selected configuration before confirmation, run the locked Bishan and Dongxing experiment matrix, and rebuild the CEUS manuscript only from frozen evidence.

**Architecture:** Keep `run_pcc_rollouts.py` as a single-policy worker and add auditable control-plane modules around it. First reconcile the protocol with immutable label manifests, then inventory checkpoints/calibrators, schedule development and confirmation as separate processes, validate complete digest-bound blocks, and derive statistics, figures, and manuscript claims from the frozen registry.

**Tech Stack:** Python 3.13, PyTorch, NumPy, pytest, existing Paper9/Paper10 environment adapters, matplotlib, Markdown/JSON/CSV/SVG/PDF/TIFF artifacts, Git worktrees.

---

## Execution Rules

1. Use `D:\adk\.venv\Scripts\python.exe` for tests and scientific commands.
2. Implement every production-code change RED -> verify RED -> GREEN -> verify GREEN.
3. Preserve the original checkout's untracked `%SystemDrive%/` and `2503.05774v1.pdf`.
4. Treat the completed label manifests as immutable inputs and validate every referenced artifact hash before training.
5. Do not execute Bishan seeds 4000-4019 or Dongxing seeds 8000-8019 before the frozen registry and freeze audit are committed.
6. Do not change the locked objective orientation, seed namespaces, success gates, or confirmation statistics after seeing confirmation outcomes.
7. Record a valid failed gate as a scientific failure. Do not tune PCC v1 from confirmation results.
8. Keep bulky scientific outputs under an ignored run root. Track only audits, source data, summaries, figures, tables, and the final manuscript.

## File Map

### Protocol and input control

- Modify `paper10_geojepa_mpc/experiments/protocols/pcc_v1.json`: correct the locked continuation-policy identity before training.
- Modify `paper10_geojepa_mpc/experiments/pcc_protocol_registry.py`: lock the corrected identity and expose CLI verification.
- Create `paper10_geojepa_mpc/experiments/pcc_input_audit.py`: validate label-manifest lineage and write a tracked audit.
- Modify `paper10_geojepa_mpc/tests/test_pcc_protocol_registry.py`: protect the corrected registry.
- Create `paper10_geojepa_mpc/tests/test_pcc_input_audit.py`: protect manifest and artifact validation.

### Development and freeze control

- Modify `paper10_geojepa_mpc/experiments/run_pcc_development.py`: add the CLI, successive-halving schedule, artifact parsing, resume, comparator selection, and freeze barrier.
- Create `paper10_geojepa_mpc/experiments/pcc_experiment_inventory.py`: resolve checkpoint/calibrator lineages without filename guessing.
- Create `paper10_geojepa_mpc/experiments/pcc_ablations.py`: define one-mechanism configuration overlays.
- Modify `paper10_geojepa_mpc/tests/test_pcc_development.py`: cover CLI scheduling and freeze refusal.
- Create `paper10_geojepa_mpc/tests/test_pcc_experiment_inventory.py`: cover inventory completeness and digest checks.
- Create `paper10_geojepa_mpc/tests/test_pcc_ablations.py`: cover isolated ablation changes.

### Confirmation control

- Create `paper10_geojepa_mpc/experiments/run_pcc_confirmation.py`: schedule frozen Bishan/Dongxing policy matrices.
- Modify `paper10_geojepa_mpc/experiments/run_pcc_rollouts.py`: enforce partition/mode compatibility and expose the separate diagnostic policy path.
- Modify `paper10_geojepa_mpc/experiments/pcc_confirmation_artifacts.py`: validate deterministic-policy mapping and diagnostic exclusion.
- Create `paper10_geojepa_mpc/tests/test_run_pcc_confirmation.py`: cover freeze/commit/partition barriers and scheduling.
- Modify `paper10_geojepa_mpc/tests/test_run_pcc_rollouts.py`: cover confirmation and diagnostic worker contracts.
- Modify `paper10_geojepa_mpc/tests/test_pcc_confirmatory_statistics.py`: cover final block loading and scientific-failure reporting.

### Evidence, figures, and manuscript

- Create `scripts/paper10/plot_pcc_manuscript_figures.py`: generate Figures 1-5 and Tables 1-3 from frozen summaries.
- Create `paper10_geojepa_mpc/tests/test_pcc_figure_assets.py`: verify source linkage and export contracts.
- Create `paper10_geojepa_mpc/experiments/results/e0_paper10_pcc_ceus_main_manuscript_2026-07-20.md`: final CEUS manuscript.
- Create `paper10_geojepa_mpc/experiments/results/e0_paper10_pcc_claim_evidence_map_2026-07-20.md`: frozen claim-to-source map.
- Modify `references/paper10_verified_references_2026-06-09.bib`, `references/paper10_citation_map_2026-06-09.md`, `DATA_AVAILABILITY.md`, `REPRODUCIBILITY.md`, `README.md`, and `MANIFEST.md`.
- Modify `scripts/paper10/preflight_submission_checks.py` and `paper10_geojepa_mpc/tests/test_submission_preflight.py`.

## Phase I: Repair the Scientific Control Plane

### Task 1: Reconcile the Registry with Immutable Label Manifests

**Files:**

- Modify: `paper10_geojepa_mpc/experiments/protocols/pcc_v1.json`
- Modify: `paper10_geojepa_mpc/experiments/pcc_protocol_registry.py`
- Test: `paper10_geojepa_mpc/tests/test_pcc_protocol_registry.py`

- [ ] **Step 1: Write failing continuation-contract tests**

Add:

```python
def test_pcc_v1_locks_paper9_mpc_as_offline_continuation():
    payload = load_registry()
    reference = payload["offline_reference_policy"]
    assert reference["name"] == "paper9_mpc"
    assert reference["continuation"] == "paper9_mpc"


def test_registry_rejects_random_continuation_identity():
    payload = load_registry()
    payload["offline_reference_policy"]["continuation"] = "random"
    with pytest.raises(ValueError, match="scientific contract"):
        validate_registry(payload)
```

- [ ] **Step 2: Run the tests and verify RED**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
```

Expected: the first test fails because the current registry still declares `random`.

- [ ] **Step 3: Correct the locked registry contract**

Change the registry and `LOCKED_PCC_V1_CONTRACT` to:

```python
"offline_reference_policy": {
    "name": "paper9_mpc",
    "checkpoint_sha256": "fd3cdeeb827dc59a30e559a36fc95166db77447dc6e7d1d4b5b4c081704c947f",
    "planning_horizon": 5,
    "top_k": 50,
    "gamma": 0.99,
    "continuation": "paper9_mpc",
},
```

- [ ] **Step 4: Add a registry verification CLI test**

Define the desired interface:

```python
def test_registry_cli_verifies_development_contract(capsys):
    main(["--registry", str(DEFAULT_REGISTRY), "--verify-development"])
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "development"
    assert len(output["registry_file_sha256"]) == 64
```

- [ ] **Step 5: Verify RED, implement the CLI, and verify GREEN**

The CLI must support exactly one of `--verify-development` or `--verify-frozen`:

```python
def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify-development", action="store_true")
    group.add_argument("--verify-frozen", action="store_true")
    args = parser.parse_args(argv)
    payload = load_registry(args.registry)
    validate_registry(payload)
    if args.verify_frozen:
        digest = verify_frozen_registry(payload)
    else:
        if payload.get("status") != "development":
            raise ValueError("registry is not in development")
        digest = hashlib.sha256(Path(args.registry).read_bytes()).hexdigest()
    print(json.dumps({"status": payload["status"], "registry_file_sha256": digest}))
```

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
```

Expected: all registry tests pass.

- [ ] **Step 6: Commit the protocol repair**

```powershell
git add paper10_geojepa_mpc\experiments\protocols\pcc_v1.json paper10_geojepa_mpc\experiments\pcc_protocol_registry.py paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py
git commit -m "fix: align pcc registry with executed labels"
```

### Task 2: Add an Immutable Input and Manifest Audit

**Files:**

- Create: `paper10_geojepa_mpc/experiments/pcc_input_audit.py`
- Create: `paper10_geojepa_mpc/tests/test_pcc_input_audit.py`

- [ ] **Step 1: Write failing manifest-lineage tests**

```python
def test_input_audit_accepts_matching_train_and_calibration_manifests(tmp_path):
    registry = load_registry()
    train = write_manifest(tmp_path / "train", registry, "train", range(1000, 1008))
    calibration = write_manifest(
        tmp_path / "calibration", registry, "calibration", range(2000, 2020)
    )
    report = audit_pcc_inputs(registry, train, calibration)
    assert report["passed"] is True
    assert report["continuation_policy"] == "paper9_mpc"


def test_input_audit_rejects_continuation_mismatch(tmp_path):
    registry = load_registry()
    train = write_manifest(tmp_path / "train", registry, "train", range(1000, 1008))
    calibration = write_manifest(
        tmp_path / "calibration", registry, "calibration", range(2000, 2020),
        continuation="random",
    )
    with pytest.raises(ValueError, match="continuation"):
        audit_pcc_inputs(registry, train, calibration)
```

Fixtures must create real small artifact files and their SHA-256 values so the test exercises artifact validation, not only JSON fields.

- [ ] **Step 2: Run and verify RED**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_input_audit.py -q
```

Expected: collection fails because `pcc_input_audit` does not exist.

- [ ] **Step 3: Implement canonical manifest validation**

```python
def audit_manifest(path, *, registry, partition):
    path = Path(path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    verify_manifest_digest(payload)
    expected_seeds = tuple(map(int, registry["partitions"][partition]))
    if payload.get("partition") != partition:
        raise ValueError("label manifest partition mismatch")
    if tuple(map(int, payload.get("trajectory_seeds", []))) != expected_seeds:
        raise ValueError("label manifest seed block mismatch")
    reference = registry["offline_reference_policy"]
    continuation = payload.get("continuation_policy", {})
    expected = {
        "name": reference["name"],
        "checkpoint_sha256": reference["checkpoint_sha256"],
        "planning_horizon": reference["planning_horizon"],
        "top_k": reference["top_k"],
        "gamma": reference["gamma"],
    }
    for key, value in expected.items():
        if continuation.get(key) != value:
            raise ValueError(f"continuation policy mismatch: {key}")
    verify_artifact_files(path.parent, payload["artifacts"])
    return manifest_summary(path, payload)
```

`audit_pcc_inputs` must ensure train/calibration continuation dictionaries are identical and write no files.

- [ ] **Step 4: Add a JSON/Markdown CLI test and implement output**

Desired command:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_input_audit --registry <registry> --train-manifest <train> --calibration-manifest <calibration> --output-json <audit.json> --output-md <audit.md>
```

The Markdown must list canonical manifest paths, manifest digests, artifact counts, seed blocks, and continuation fields.

- [ ] **Step 5: Run tests and commit**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_input_audit.py paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
git add paper10_geojepa_mpc\experiments\pcc_input_audit.py paper10_geojepa_mpc\tests\test_pcc_input_audit.py
git commit -m "feat: audit immutable pcc scientific inputs"
```

## Phase II: Make Development and Freeze Executable

### Task 3: Add Typed Checkpoint and Calibrator Inventory

**Files:**

- Create: `paper10_geojepa_mpc/experiments/pcc_experiment_inventory.py`
- Create: `paper10_geojepa_mpc/tests/test_pcc_experiment_inventory.py`

- [ ] **Step 1: Write failing inventory tests**

```python
def test_inventory_resolves_every_model_seed_ensemble_round(tmp_path):
    create_inventory_fixture(tmp_path, model_seeds=(5101, 5102, 5103))
    inventory = build_inventory(tmp_path, model_seeds=(5101, 5102, 5103))
    assert inventory.checkpoint_root(5102, 3, 2).name == "checkpoints"
    assert len(inventory.checkpoint_digests(5102, 3, 2)) == 3


def test_inventory_rejects_duplicate_or_missing_member(tmp_path):
    create_inventory_fixture(tmp_path, model_seeds=(5101,), member_indexes=(0, 0, 2))
    with pytest.raises(ValueError, match="member indexes"):
        build_inventory(tmp_path, model_seeds=(5101,))
```

- [ ] **Step 2: Verify RED**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_experiment_inventory.py -q
```

- [ ] **Step 3: Implement inventory records from artifact metadata**

```python
@dataclass(frozen=True)
class EnsembleInventoryRecord:
    model_seed: int
    ensemble_size: int
    policy_round: int
    checkpoint_root: Path
    checkpoint_digests: tuple[str, ...]
    calibrators: Mapping[float, Path]


def load_member_metadata(path):
    payload = torch.load(path, map_location="cpu", weights_only=False)
    return {
        "model_seed": int(payload["model_seed"]),
        "member_index": int(payload["member_index"]),
        "registry_digest": payload.get("registry_digest"),
    }
```

Resolve records from checkpoint/calibrator contents and round manifests. Do not infer model seed or policy round only from directory names.

The freeze-complete inventory must contain, for every declared model seed, all
four `(ensemble_size, policy_round)` keys `(3,1)`, `(5,1)`, `(3,2)`, and
`(5,2)`. Each key must expose calibrators at coverage `0.80`, `0.90`, and
`0.95`. A checkpoint-only inventory may be used for the Task 9 post-training
audit, but it cannot satisfy the Task 10 freeze barrier.

- [ ] **Step 4: Add lineage checks**

Require each calibrator's label-manifest digest, checkpoint digests, calibration seed block, coverage, objective order, and protocol ID to match its record.

- [ ] **Step 5: Run tests and commit**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_experiment_inventory.py paper10_geojepa_mpc\tests\test_pcc_policy_iteration.py paper10_geojepa_mpc\tests\test_paired_conformal.py -q
git add paper10_geojepa_mpc\experiments\pcc_experiment_inventory.py paper10_geojepa_mpc\tests\test_pcc_experiment_inventory.py
git commit -m "feat: inventory pcc checkpoint lineages"
```

### Task 4: Implement Named One-Mechanism Ablation Overlays

**Files:**

- Create: `paper10_geojepa_mpc/experiments/pcc_ablations.py`
- Create: `paper10_geojepa_mpc/tests/test_pcc_ablations.py`
- Modify as required: `paper10_geojepa_mpc/models/pcc_geojepa.py`
- Modify as required: `paper10_geojepa_mpc/planning/pcc_selector.py`
- Modify as required: `paper10_geojepa_mpc/planning/pcc_baselines.py`

- [ ] **Step 1: Write parameterized failing overlay tests**

```python
@pytest.mark.parametrize("name", load_registry()["required_ablations"])
def test_ablation_changes_only_declared_fields(name):
    base = frozen_development_config()
    changed = apply_ablation(base, name)
    allowed = set(ABLATION_CONTRACTS[name].changed_fields)
    assert changed["ablation"] == name
    assert differing_paths(base, changed) == allowed | {"ablation"}
```

Add behavior tests for reward-only gate, no feedback, no fallback, single model, uncalibrated scale, no aleatoric scale, county-specific embedding, and round 1.

- [ ] **Step 2: Verify RED**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_ablations.py -q
```

- [ ] **Step 3: Implement immutable overlay contracts**

```python
ABLATION_CONTRACTS = {
    "single_model": AblationContract({"ensemble_size": 1}),
    "no_aleatoric_scale": AblationContract({"use_aleatoric_scale": False}),
    "uncalibrated_ensemble_scale": AblationContract({"use_conformal": False}),
    "reward_only": AblationContract({"pareto_objectives": ("reward",)}),
    "no_executed_feedback": AblationContract({"executed_feedback": False}),
    "no_reference_fallback": AblationContract({"reference_fallback": False}),
    "one_policy_improvement_round": AblationContract({"policy_round": 1}),
    "county_specific_action_embedding": AblationContract(
        {"representation": "county_specific_action_embedding"}
    ),
}
```

Each downstream model/selector builder must accept the explicit field and log it. It must not reinterpret an ablation name inside scientific code.

- [ ] **Step 4: Verify behavior and commit**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_ablations.py paper10_geojepa_mpc\tests\test_pcc_geojepa.py paper10_geojepa_mpc\tests\test_pcc_selector.py paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py -q
git add paper10_geojepa_mpc\experiments\pcc_ablations.py paper10_geojepa_mpc\models\pcc_geojepa.py paper10_geojepa_mpc\planning\pcc_selector.py paper10_geojepa_mpc\planning\pcc_baselines.py paper10_geojepa_mpc\tests\test_pcc_ablations.py
git commit -m "feat: define pcc mechanism ablations"
```

### Task 5: Build the Development CLI and Freeze Barrier

**Files:**

- Modify: `paper10_geojepa_mpc/experiments/run_pcc_development.py`
- Modify: `paper10_geojepa_mpc/tests/test_pcc_development.py`

- [ ] **Step 1: Write failing schedule tests**

```python
def test_successive_halving_never_uses_confirmation_seeds():
    registry = load_registry()
    schedule = build_development_schedule(registry)
    assert schedule[0].seeds == (3000, 3001)
    assert schedule[0].steps == 20
    assert schedule[1].keep == 36
    assert schedule[1].seeds == tuple(range(3000, 3005))
    assert schedule[2].keep == 8
    assert schedule[2].seeds == tuple(range(3000, 3010))
    assert not set().union(*(set(row.seeds) for row in schedule)) & set(
        registry["partitions"]["confirmation"]
    )
```

- [ ] **Step 2: Write a failing dry-run CLI test**

```python
def test_development_dry_run_writes_single_policy_worker_commands(tmp_path):
    main([
        "--registry", str(DEFAULT_REGISTRY),
        "--checkpoint-root", str(tmp_path / "checkpoints"),
        "--calibration-root", str(tmp_path / "calibration"),
        "--output-dir", str(tmp_path / "development"),
        "--dry-run",
    ])
    plan = json.loads((tmp_path / "development" / "execution_plan.json").read_text())
    assert all("--model-seed" in row["command"] for row in plan["jobs"])
    assert all("--model-seeds" not in row["command"] for row in plan["jobs"])
```

- [ ] **Step 3: Verify RED**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_development.py -q
```

- [ ] **Step 4: Implement schedule, execution plan, and resume**

The CLI arguments are:

```python
parser.add_argument("--registry", required=True)
parser.add_argument("--checkpoint-root", required=True)
parser.add_argument("--calibration-root", required=True)
parser.add_argument("--prepared-dir", required=True)
parser.add_argument("--output-dir", required=True)
parser.add_argument("--device", default="cpu")
parser.add_argument("--resume", action="store_true")
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--freeze", action="store_true")
```

Each job calls `run_pcc_rollouts` with one policy, one model seed, one seed specification, and one output path. Write the execution plan before subprocess execution. Resume accepts an output only after registry-file hash, checkpoint hashes, calibrator hash, configuration ID, seed set, and rollout length match.

- [ ] **Step 5: Implement rung aggregation and selection**

```python
def development_row(config, policy_rows):
    effects = paired_effects(policy_rows, comparator=config["primary_candidate"])
    lower = one_sided_seed_bootstrap(effects, seed=config["development_bootstrap_seed"])
    return {
        **config,
        "planning_gate_count": int(np.sum(lower[1:] >= 0.0)),
        "reward": float(effects[:, 0].mean()),
        "compute": int(total_member_evaluations(policy_rows)),
    }
```

At each rung, retain the declared number of configurations by the same `select_configuration` ordering. Store every rejected configuration and reason.

- [ ] **Step 6: Tighten freeze requirements**

`freeze_development` must require:

```python
required_selected_fields = {
    "id", "ensemble_size", "joint_coverage", "tolerance_scale",
    "planning_horizon", "residual_window", "policy_round",
    "primary_comparator", "checkpoint_digests", "calibrator_digest",
    "expert_learning_rate", "compute_budget", "stage_a_report",
    "development_artifact_digest", "ablation_inventory_digest",
}
```

Reject missing ablations, incomplete model-seed blocks, non-passing Stage A, oracle comparator, or any source seed outside 3000-3009.

- [ ] **Step 7: Run development tests and commit**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_development.py paper10_geojepa_mpc\tests\test_pcc_experiment_inventory.py paper10_geojepa_mpc\tests\test_pcc_ablations.py paper10_geojepa_mpc\tests\test_pcc_protocol_registry.py -q
git add paper10_geojepa_mpc\experiments\run_pcc_development.py paper10_geojepa_mpc\tests\test_pcc_development.py
git commit -m "feat: execute and freeze bounded pcc development"
```

## Phase III: Make Independent Confirmation Executable

### Task 6: Enforce Rollout Partition and Diagnostic Contracts

**Files:**

- Modify: `paper10_geojepa_mpc/experiments/run_pcc_rollouts.py`
- Modify: `paper10_geojepa_mpc/tests/test_run_pcc_rollouts.py`

- [ ] **Step 1: Write failing mode-partition tests**

```python
def test_confirmation_mode_rejects_development_seed():
    registry = frozen_registry_fixture()
    with pytest.raises(ValueError, match="confirmation partition"):
        validate_rollout_request(registry, "confirmation", "paper9", [3000])


def test_development_mode_rejects_confirmation_seed():
    registry = load_registry()
    with pytest.raises(ValueError, match="development partition"):
        validate_rollout_request(registry, "development", "paper9", [4000])
```

- [ ] **Step 2: Write failing diagnostic policy tests**

```python
def test_oracle_diagnostic_is_not_a_deployable_policy_choice():
    args = parse_args([
        "--registry", "registry.json", "--mode", "confirmation",
        "--policy", "oracle_action_audit_diagnostic", "--seeds", "4000",
        "--output", "out.json",
    ])
    with pytest.raises(ValueError, match="diagnostic"):
        validate_policy_role(args)
```

Add a separate `--mode diagnostic --policy oracle_action_audit_diagnostic` success case requiring `deployable=false` and a positive privileged-query count.

- [ ] **Step 3: Verify RED**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py -q
```

- [ ] **Step 4: Implement request validation before environment creation**

```python
def validate_rollout_request(registry, mode, env_source, seeds):
    role = {
        ("development", "paper9"): "development",
        ("confirmation", "paper9"): "confirmation",
        ("confirmation", "neijiang"): "dongxing_confirmation",
    }.get((mode, env_source))
    if role is None:
        return
    expected = set(map(int, registry["partitions"][role]))
    if not set(map(int, seeds)).issubset(expected):
        raise ValueError(f"seeds are outside the {role} partition")
```

Confirmation also calls `verify_frozen_registry` before any environment or output path is opened.

- [ ] **Step 5: Implement the diagnostic role separately**

The diagnostic policy may use the existing true-reward audit helper, but every row must contain:

```python
{
    "policy": "oracle_action_audit_diagnostic",
    "deployable": False,
    "diagnostic_role": "privileged_upper_bound",
    "unexecuted_real_reward_queries": int(query_count),
}
```

No deployable-policy builder imports or constructs this policy.

- [ ] **Step 6: Run tests and commit**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_pcc_information_set_audit.py -q
git add paper10_geojepa_mpc\experiments\run_pcc_rollouts.py paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py
git commit -m "feat: guard pcc rollout information partitions"
```

### Task 7: Build the Frozen Confirmation Orchestrator

**Files:**

- Create: `paper10_geojepa_mpc/experiments/run_pcc_confirmation.py`
- Create: `paper10_geojepa_mpc/tests/test_run_pcc_confirmation.py`
- Modify: `paper10_geojepa_mpc/experiments/pcc_confirmation_artifacts.py`

- [ ] **Step 1: Write failing pre-freeze and committed-freeze tests**

```python
def test_confirmation_plan_refuses_development_registry(tmp_path):
    with pytest.raises(ValueError, match="not frozen"):
        build_confirmation_plan(load_registry(), run_root=tmp_path)


def test_confirmation_requires_frozen_registry_blob_in_git(tmp_path, git_repo):
    registry_path, frozen = freeze_fixture(git_repo)
    with pytest.raises(ValueError, match="committed"):
        assert_frozen_registry_committed(registry_path, frozen["frozen_digest"])
```

The commit check must compare `git show HEAD:<relative registry path>` with the working file and verify the frozen digest from the committed blob.

- [ ] **Step 2: Write a failing policy-matrix test**

```python
def test_bishan_plan_has_one_job_per_required_policy_and_model_dependency(tmp_path):
    registry = frozen_registry_fixture()
    plan = build_confirmation_plan(registry, run_root=tmp_path, region="bishan")
    assert {job.policy for job in plan.jobs} == set(registry["deployable_baselines"])
    assert all(job.seeds == tuple(range(4000, 4020)) for job in plan.jobs)
    assert len([j for j in plan.jobs if j.policy == "pcc_full"]) == 3
    assert len([j for j in plan.jobs if j.policy == "paper9_mpc"]) == 1
```

- [ ] **Step 3: Verify RED**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_confirmation.py -q
```

- [ ] **Step 4: Implement immutable job records**

```python
@dataclass(frozen=True)
class ConfirmationJob:
    region: str
    policy: str
    model_seed: int | None
    seeds: tuple[int, ...]
    command: tuple[str, ...]
    output: Path
    checkpoint_digests: tuple[str, ...]
    calibrator_digest: str | None
```

Model-independent policies have one job. Model-dependent policies have one job for each of 5101, 5102, and 5103. Every command uses the single `--model-seed` option.

- [ ] **Step 5: Implement plan writing, subprocess execution, and resume**

The CLI supports:

```python
parser.add_argument("--registry", required=True)
parser.add_argument("--region", choices=("bishan", "dongxing", "all"), default="all")
parser.add_argument("--run-root", required=True)
parser.add_argument("--prepared-dir-bishan", required=True)
parser.add_argument("--prepared-dir-dongxing", required=True)
parser.add_argument("--checkpoint-root", required=True)
parser.add_argument("--dongxing-checkpoint-root")
parser.add_argument("--dongxing-calibration-root")
parser.add_argument("--device", default="cpu")
parser.add_argument("--resume", action="store_true")
parser.add_argument("--dry-run", action="store_true")
```

The execution plan is written atomically before work. Resume validates every output with `load_confirmation_artifacts`; invalid or foreign-digest output raises rather than being overwritten.

- [ ] **Step 6: Implement complete-block closeout**

After all jobs, require:

```python
for policy in registry["deployable_baselines"]:
    complete_policy_block(
        artifacts,
        policy=policy,
        model_seeds=registry["model_seeds"],
        rollout_seeds=registry["partitions"][partition],
        allow_shared_model_block=policy in MODEL_INDEPENDENT_POLICIES,
    )
```

Write a confirmation manifest containing registry digest, job output hashes, policy roles, model-seed mapping, seed partitions, and completion state.

- [ ] **Step 7: Run tests and commit**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_run_pcc_confirmation.py paper10_geojepa_mpc\tests\test_pcc_confirmatory_statistics.py paper10_geojepa_mpc\tests\test_run_pcc_rollouts.py -q
git add paper10_geojepa_mpc\experiments\run_pcc_confirmation.py paper10_geojepa_mpc\experiments\pcc_confirmation_artifacts.py paper10_geojepa_mpc\tests\test_run_pcc_confirmation.py
git commit -m "feat: orchestrate frozen pcc confirmation"
```

### Task 8: Complete External Adaptation and Scientific-Failure Reporting

**Files:**

- Modify: `paper10_geojepa_mpc/experiments/run_pcc_train.py`
- Modify: `paper10_geojepa_mpc/training/pcc_training.py`
- Modify: `paper10_geojepa_mpc/experiments/pcc_confirmatory_statistics.py`
- Modify: `paper10_geojepa_mpc/tests/test_pcc_training.py`
- Modify: `paper10_geojepa_mpc/tests/test_pcc_confirmatory_statistics.py`

- [ ] **Step 1: Write failing objective-head-only adaptation tests**

```python
def test_dongxing_adaptation_changes_only_objective_heads(tmp_path):
    before, after = train_tiny_adaptation(tmp_path, trainable_scope="objective_heads")
    for name in before:
        if name.startswith(("immediate_head", "horizon_head")):
            continue
        torch.testing.assert_close(before[name], after[name])
```

- [ ] **Step 2: Write a failing claim-gate test**

```python
def test_failed_confirmation_emits_exact_failed_gate_without_recommendation_to_retune():
    report = locked_report_with_connected_area_failure()
    claim = manuscript_claim_gate(report)
    assert claim["primary_success"] is False
    assert claim["failed_gates"] == ["bishan.connected_area_benefit"]
    assert "retun" not in json.dumps(claim).lower()
```

- [ ] **Step 3: Verify RED, implement, and verify GREEN**

The adaptation checkpoint must store parent checkpoint digests, frozen registry digest, trainable parameter names, adaptation label-manifest digest, and region. The claim gate returns only evidence-derived allowed/forbidden claims and exact failures.

Run:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_training.py paper10_geojepa_mpc\tests\test_pcc_confirmatory_statistics.py -q
```

- [ ] **Step 4: Commit**

```powershell
git add paper10_geojepa_mpc\experiments\run_pcc_train.py paper10_geojepa_mpc\training\pcc_training.py paper10_geojepa_mpc\experiments\pcc_confirmatory_statistics.py paper10_geojepa_mpc\tests\test_pcc_training.py paper10_geojepa_mpc\tests\test_pcc_confirmatory_statistics.py
git commit -m "feat: lock external pcc adaptation and claims"
```

## Phase IV: Execute Development, Freeze, and Confirmation

### Task 9: Audit Inputs and Train the Declared Ensembles

**Files:**

- Generate locally: `<run-root>/input_audit/`, `<run-root>/checkpoints/`
- Track: `paper10_geojepa_mpc/experiments/results/pcc_v1/input_audit.json`
- Track: `paper10_geojepa_mpc/experiments/results/pcc_v1/input_audit.md`

- [ ] **Step 1: Verify the code baseline**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -k "pcc or paired_conformal or executed_feedback"
```

Expected: all focused tests pass.

- [ ] **Step 2: Audit the existing immutable labels**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_input_audit --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --train-manifest D:\test\paper10-geojepa-mpc-farmland-layout\paper10_runs\pcc_v1\labels\bishan_train\manifest.json --calibration-manifest D:\test\paper10-geojepa-mpc-farmland-layout\paper10_runs\pcc_v1\labels\bishan_calibration\manifest.json --output-json paper10_geojepa_mpc\experiments\results\pcc_v1\input_audit.json --output-md paper10_geojepa_mpc\experiments\results\pcc_v1\input_audit.md
```

Expected: `passed=true`, seeds 1000-1007 and 2000-2019, all artifact hashes valid, continuation `paper9_mpc`.

- [ ] **Step 3: Train 24 round-1 members**

```powershell
$modelSeeds = 5101,5102,5103
$ensembleSizes = 3,5
foreach ($modelSeed in $modelSeeds) {
  foreach ($ensembleSize in $ensembleSizes) {
    D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_train --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --labels-manifest D:\test\paper10-geojepa-mpc-farmland-layout\paper10_runs\pcc_v1\labels\bishan_train\manifest.json --model-seed $modelSeed --ensemble-size $ensembleSize --epochs 20 --device cpu --output-dir "D:\test\paper10_pcc_v1_completion_runs\checkpoints\seed${modelSeed}_k${ensembleSize}"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
}
```

Expected: six training summaries and 24 distinct member checkpoint files.

- [ ] **Step 4: Inventory and verify the training outputs**

Run the inventory CLI and require distinct member indexes, model seeds, bootstrap membership, and hashes. Do not proceed on any missing or repeated checkpoint.

- [ ] **Step 5: Commit only the tracked input audit**

```powershell
git add paper10_geojepa_mpc\experiments\results\pcc_v1\input_audit.json paper10_geojepa_mpc\experiments\results\pcc_v1\input_audit.md
git commit -m "exp: audit pcc v1 training inputs"
```

### Task 10: Complete Two Policy-Improvement Rounds and Freeze Development

**Files:**

- Generate locally: `<run-root>/policy_iteration/`, `<run-root>/development/`
- Track: `paper10_geojepa_mpc/experiments/results/pcc_v1/development_audit.json`
- Track: `paper10_geojepa_mpc/experiments/results/pcc_v1/development_audit.md`
- Modify and track: `paper10_geojepa_mpc/experiments/protocols/pcc_v1.json`

- [ ] **Step 1: Run exactly two policy-improvement rounds**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_policy_iteration --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --round0-train-labels D:\test\paper10-geojepa-mpc-farmland-layout\paper10_runs\pcc_v1\labels\bishan_train\manifest.json --round0-calibration-labels D:\test\paper10-geojepa-mpc-farmland-layout\paper10_runs\pcc_v1\labels\bishan_calibration\manifest.json --round1-checkpoints D:\test\paper10_pcc_v1_completion_runs\checkpoints --round1-iteration-ensemble-size 3 --round1-iteration-coverage 0.90 --round1-iteration-tolerance-scale 0.05 --round1-iteration-horizon 3 --rounds 2 --env-source paper9 --prepared-dir D:\test --epochs 20 --max-label-workers 4 --device cpu --resume --output-dir D:\test\paper10_pcc_v1_completion_runs\policy_iteration
```

This command generates round-2 labels only with the locked round-1 `K=3`,
coverage `0.90` policy and trains the round-2 `K=3` ensemble. It is the sole
policy-improvement data-generation path.

- [ ] **Step 2: Complete the round-2 model and calibrator factorial**

Train the round-2 `K=5` ensemble for each model seed on the same round-2 label
manifest produced in Step 1. Fit coverage `0.80`, `0.90`, and `0.95`
calibrators for every round-1 and round-2 checkpoint family. Expected final
inventory: 12 checkpoint families, 48 physical member checkpoints (24 in each
round), and 36 coverage-specific calibrators. Reusing one checkpoint family
across its three calibrators is required; coverage does not retrain the model.

- [ ] **Step 3: Verify round lineage and complete factorial inventory**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_policy_iteration --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --verify-only --input-root D:\test\paper10_pcc_v1_completion_runs\policy_iteration
```

Expected: complete round 1 and round 2 manifests for all model seeds and both
ensemble sizes; no round 3; all 36 calibrators match their declared coverage and
label/checkpoint lineage. Both round-2 ensemble sizes are bound to labels
generated by the same locked round-1 `K=3`, coverage `0.90` policy.

- [ ] **Step 4: Run bounded development and required ablations**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_development --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --checkpoint-root D:\test\paper10_pcc_v1_completion_runs\policy_iteration --calibration-root D:\test\paper10_pcc_v1_completion_runs\policy_iteration --prepared-dir D:\test --output-dir D:\test\paper10_pcc_v1_completion_runs\development --device cpu --resume --freeze
```

Expected: all rungs complete, all required ablations are inventoried, Stage A passes, one primary comparator is declared, and the registry becomes frozen.

- [ ] **Step 5: Write and inspect the freeze audit**

Run the information and development audit. Verify the selected configuration, comparator, model/checkpoint/calibrator hashes, compute budget, source seeds, Stage A report, and zero access to confirmation paths.

- [ ] **Step 6: Commit the freeze before confirmation**

```powershell
git add paper10_geojepa_mpc\experiments\protocols\pcc_v1.json paper10_geojepa_mpc\experiments\results\pcc_v1\development_audit.json paper10_geojepa_mpc\experiments\results\pcc_v1\development_audit.md
git commit -m "exp: freeze pcc v1 development protocol"
```

- [ ] **Step 7: Verify the committed frozen blob from a fresh process**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_protocol_registry --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --verify-frozen
git show HEAD:paper10_geojepa_mpc/experiments/protocols/pcc_v1.json
```

Expected: both show the same frozen digest.

### Task 11: Run Bishan and Dongxing Independent Confirmation

**Files:**

- Generate locally: `<run-root>/confirmation/`, `<run-root>/dongxing_*`
- Track: `paper10_geojepa_mpc/experiments/results/pcc_v1/confirmation_information_audit.*`
- Track: `paper10_geojepa_mpc/experiments/results/pcc_v1/confirmatory.*`

- [ ] **Step 1: Dry-run the confirmation plan**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_confirmation --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --region bishan --run-root D:\test\paper10_pcc_v1_completion_runs --prepared-dir-bishan D:\test --prepared-dir-dongxing D:\test\neijiang_cross_region --checkpoint-root D:\test\paper10_pcc_v1_completion_runs\policy_iteration --device cpu --dry-run
```

Inspect the plan and confirm only seeds 4000-4019 appear.

- [ ] **Step 2: Run Bishan no-oracle confirmation**

Repeat without `--dry-run` and with `--resume`. Require complete deployable-policy blocks before proceeding.

- [ ] **Step 3: Run the separate oracle upper-bound diagnostic**

Use `run_pcc_rollouts --mode diagnostic --policy oracle_action_audit_diagnostic` on 4000-4019. Verify `deployable=false`. Store it outside the deployable policy matrix.

- [ ] **Step 4: Generate Dongxing adaptation and calibration labels**

Use only seeds 6000-6003 and 7000-7019 with the frozen PCC registry. Validate their manifests before training.

- [ ] **Step 5: Adapt objective heads and fit frozen-coverage calibration**

For each model seed, invoke `run_pcc_train --ensemble-size-from-frozen-registry --trainable-scope objective_heads`. Fit calibrators with `--coverage-from-frozen-registry`. Verify parent and adaptation digests.

- [ ] **Step 6: Run Dongxing confirmation**

Use the confirmation orchestrator with `--region dongxing --resume`. Require only seeds 8000-8019 and no hyperparameter-selection output.

- [ ] **Step 7: Run information-set audit and locked statistics**

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_information_set_audit --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --input-root D:\test\paper10_pcc_v1_completion_runs\confirmation --output-json paper10_geojepa_mpc\experiments\results\pcc_v1\confirmation_information_audit.json --output-md paper10_geojepa_mpc\experiments\results\pcc_v1\confirmation_information_audit.md
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.pcc_confirmatory_statistics --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json --bishan-root D:\test\paper10_pcc_v1_completion_runs\confirmation\bishan --dongxing-json D:\test\paper10_pcc_v1_completion_runs\confirmation\dongxing --draws 20000 --bootstrap-seed 20260710 --output-prefix paper10_geojepa_mpc\experiments\results\pcc_v1\confirmatory
```

Expected: every gate is recorded true or false; no configuration field changes.

- [ ] **Step 8: Commit immutable summaries**

```powershell
git add paper10_geojepa_mpc\experiments\results\pcc_v1
git commit -m "exp: record pcc v1 independent confirmation"
```

## Phase V: Generate Evidence and Rewrite the Paper Last

### Task 12: Generate Submission-Grade Figures and Tables

**Files:**

- Create: `scripts/paper10/plot_pcc_manuscript_figures.py`
- Create: `paper10_geojepa_mpc/tests/test_pcc_figure_assets.py`
- Generate: `paper10_geojepa_mpc/experiments/results/ceus_submission_assets/pcc_v1/`
- Generate: `paper10_geojepa_mpc/experiments/results/pcc_v1/source_data/`

- [ ] **Step 1: Invoke `nature-figure` and read its required Python references**

Use Python only. Define each figure's conclusion, evidence logic, export needs, and review risks before plotting.

- [ ] **Step 2: Write failing source and export tests**

```python
def test_all_figures_and_tables_resolve_to_frozen_sources():
    manifest = load_figure_manifest()
    assert manifest["registry_digest"] == load_registry()["frozen_digest"]
    assert set(manifest["figures"]) == {"1", "2", "3", "4", "5"}
    for figure in manifest["figures"].values():
        assert all(Path(path).exists() for path in figure["source_files"])


def test_every_main_figure_has_editable_and_raster_exports():
    for number in range(1, 6):
        stem = ASSET_ROOT / f"figure_{number}_pcc"
        assert stem.with_suffix(".svg").exists()
        assert stem.with_suffix(".pdf").exists()
        assert stem.with_suffix(".tiff").exists()
        assert stem.with_suffix(".png").exists()
```

- [ ] **Step 3: Verify RED and implement one plotting entry point**

The script reads only frozen confirmation JSON/CSV, information audits, ablation summaries, and spatial outputs. It generates:

- Figure 1: no-oracle information boundary and PCC mechanism;
- Figure 2: Bishan paired reward and three planning effects with all seed points;
- Figure 3: calibration, fallback, uncertainty-error, and mechanism ablations;
- Figure 4: Dongxing external confirmation and adaptation cost;
- Figure 5: matched spatial outcomes at identical extent/projection/classification;
- Tables 1-3 and per-panel source-data CSV files.

- [ ] **Step 4: Generate and visually inspect every PNG**

Use the image viewer at original detail. Fix overlaps, clipping, unreadable labels, inconsistent axes, or map extents in Python and regenerate.

- [ ] **Step 5: Run tests and commit**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_pcc_figure_assets.py -q
git add scripts\paper10\plot_pcc_manuscript_figures.py paper10_geojepa_mpc\tests\test_pcc_figure_assets.py paper10_geojepa_mpc\experiments\results\ceus_submission_assets\pcc_v1 paper10_geojepa_mpc\experiments\results\pcc_v1\source_data
git commit -m "fig: add frozen pcc evidence figures"
```

### Task 13: Rebuild the CEUS Manuscript from Frozen Evidence

**Files:**

- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_pcc_ceus_main_manuscript_2026-07-20.md`
- Create: `paper10_geojepa_mpc/experiments/results/e0_paper10_pcc_claim_evidence_map_2026-07-20.md`
- Modify: `references/paper10_verified_references_2026-06-09.bib`
- Modify: `references/paper10_citation_map_2026-06-09.md`
- Modify: `DATA_AVAILABILITY.md`
- Modify: `REPRODUCIBILITY.md`
- Modify: `README.md`
- Modify: `MANIFEST.md`
- Modify: `scripts/paper10/preflight_submission_checks.py`
- Modify: `paper10_geojepa_mpc/tests/test_submission_preflight.py`

- [ ] **Step 1: Use the literature and writing skills before drafting**

Invoke `nature-academic-search` for verified related-work coverage and `nature-writing` for the evidence-driven manuscript structure. Do not claim ensemble prediction, conformal calibration, Pareto optimization, or conservative planning as individually new.

- [ ] **Step 2: Write failing claim/preflight tests**

```python
def test_main_manuscript_matches_frozen_claim_gate():
    confirmation = json.loads(CONFIRMATORY_JSON.read_text())
    manuscript = MAIN_MANUSCRIPT.read_text(encoding="utf-8")
    assert "PCC-GeoJEPA-MPC" in manuscript
    assert "oracle action-audit diagnostic upper bound" in manuscript
    assert "unexecuted real-reward queries" in manuscript
    if confirmation["locked_confirmation"]["overall_success"]:
        assert "supported primary PCC claim" in manuscript
    else:
        assert "supported primary PCC claim" not in manuscript
        assert "failed locked condition" in manuscript
```

Also reject internal artifact prose, unresolved citation keys, placeholder author text in public main text, missing Figure 1-5/Table 1-3 sources, and archive/commit mismatch.

- [ ] **Step 3: Draft in evidence order**

Write Introduction, Methods, Results, Discussion, Conclusion, Data/Code Availability, references, figure captions, and table captions. Include the full reward formula, weights, normalization, block/parcel/region data description, model architecture/training, calibration, compute, statistics, failures, and confidentiality boundary.

- [ ] **Step 4: Apply the locked negative-result rule**

If `overall_success=false`, state the exact failed gate and do not convert the paper into a superiority claim. Do not propose reusing PCC v1 confirmation seeds.

- [ ] **Step 5: Verify citations, archive identity, and preflight**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests\test_submission_preflight.py -q
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

Expected: all manuscript checks pass and `Paper10 preflight: PASS`.

- [ ] **Step 6: Commit the rebuilt paper**

```powershell
git add paper10_geojepa_mpc\experiments\results\e0_paper10_pcc_ceus_main_manuscript_2026-07-20.md paper10_geojepa_mpc\experiments\results\e0_paper10_pcc_claim_evidence_map_2026-07-20.md references DATA_AVAILABILITY.md REPRODUCIBILITY.md README.md MANIFEST.md scripts\paper10\preflight_submission_checks.py paper10_geojepa_mpc\tests\test_submission_preflight.py
git commit -m "docs: rebuild paper10 from frozen pcc evidence"
```

### Task 14: Final Verification and Handoff

**Files:** No planned new files. Any defect requires a failing regression test before repair.

- [ ] **Step 1: Run the complete test suite**

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest -q
```

- [ ] **Step 2: Run submission preflight**

```powershell
D:\adk\.venv\Scripts\python.exe scripts\paper10\preflight_submission_checks.py
```

- [ ] **Step 3: Regenerate statistics, figures, and tables**

Compare frozen registry digest, numeric source data, and generated output hashes with tracked manifests. Any mismatch blocks completion.

- [ ] **Step 4: Verify Git integrity**

```powershell
git status --short --branch
git diff --check
git log -8 --oneline
```

Expected: no tracked changes; the isolated branch contains only scoped commits.

- [ ] **Step 5: Request final code/science review**

Use `superpowers:requesting-code-review` with focus on information leakage, partition independence, objective orientation, conformal pairing, matched compute, pseudoreplication, ablation isolation, and claim/evidence consistency.

- [ ] **Step 6: Finish the branch**

Use `superpowers:finishing-a-development-branch` only after fresh verification passes and present integration options without modifying `main` implicitly.

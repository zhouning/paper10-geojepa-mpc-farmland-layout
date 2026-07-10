def audit_information_set(
    payload: dict[str, object],
    *,
    expected_registry_digest: str,
) -> dict[str, object]:
    reasons = set()
    if payload.get("registry_digest") != str(expected_registry_digest):
        reasons.add("registry_digest_mismatch")
    query_count = 0
    n_steps = 0
    for seed_result in payload.get("seed_results", []):
        steps = seed_result.get("steps", [])
        n_steps += len(steps)
        if int(seed_result.get("environment_step_count", -1)) != len(steps):
            reasons.add("environment_step_count_mismatch")
        for step in steps:
            queries = int(step.get("unexecuted_real_reward_queries", -1))
            if queries != 0:
                reasons.add("unexecuted_real_reward_query")
            query_count += max(queries, 0)
    return {
        "passed": not reasons,
        "failure_reasons": sorted(reasons),
        "unexecuted_real_reward_queries": int(query_count),
        "audited_steps": int(n_steps),
    }

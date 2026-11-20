#!/usr/bin/env python3
"""Score one configuration of the matched Harbor route-disclosure study.

Usage: python3 scripts/score_study.py ASSIGNMENTS.json RESULTS.json AGENT

Assignments list task, base_issue (family in the development archive), route,
forest, arm and optional repeat (default 1). Results contain a trials list with
task, agent, optional repeat, and reward. Export only adjudicated final results.
Encode cap failures as reward 0 and unresolved verifier outcomes as null or
an absent row. If a configuration has no scored trials, include a null row to
identify it. Keep retry, cost, time and trace records in the source ledger.

Pass --expected-assignment-manifest-sha256 with the independently recorded
prelaunch digest to check the assignment bytes used for scoring. This applies
to both normalized results and native jobs.

With --harbor-job, provide a Harbor 0.26.0 job directory in place of the
results JSON. Use one agent configuration, one attempt per task and no
automatic retries. The job lock must match the scheduled tasks, and each
trial receipt must match the job and its own saved config and lock. Pass
--expected-job-lock-sha256 to compare with a launch-time lock digest.
Invalid or interrupted results remain unknown until adjudicated. Use
normalized results for repeated or route-audited studies.

With --audit-effective-route, use optional route_status fields from an
independent execution audit: exact, fallback, or unverified (the default).
The operational score still includes adjudicated fallback results. The
exact-route report treats results that lack exact attestation as unknown
over the original assignments and shows route status by issue and cell.

With --cluster-confidence LEVEL, require a cluster string on every assignment.
Keep each base issue in one cluster and group dependent issues together.
The optional report gives per-contrast finite-sample intervals under
independence across declared clusters. It keeps equal weights per base issue
and allows arbitrary dependence within each cluster, including across repeats.

With --with-structural-guidance, require a third arm named structural for both
forests in every matched block. Compare runtime disclosure with general
structural guidance, alongside all four original contrasts.

With --with-edit-hint, require both structural and edit_hint arms in addition
to the original arms. Compare disclosure with an explicit edit-location hint.
Use --profiles-per-issue when an issue crosses more than two starting profiles.
Each profile must contain the same matched cells and repeat schedule.
"""

import argparse
import json
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from math import log, sqrt
from pathlib import Path
from statistics import mean

from native_receipts import read_harbor_metrics


CELLS = tuple(product(("unrelated", "competing"), ("control", "disclosed")))
CONTRASTS = {
    "unassisted_decoy_penalty": (1, 0, -1, 0),
    "disclosed_decoy_penalty": (0, 1, 0, -1),
    "decoy_penalty_reduction": (1, -1, -1, 1),
    "competing_disclosure_uplift": (0, 0, -1, 1),
}
GUIDANCE_CELLS = CELLS + (("unrelated", "structural"), ("competing", "structural"))
GUIDANCE_CONTRASTS = {
    **{name: weights + (0, 0) for name, weights in CONTRASTS.items()},
    "structural_decoy_penalty": (0, 0, 0, 0, 1, -1),
    "competing_structural_uplift": (0, 0, -1, 0, 0, 1),
    "competing_runtime_beyond_structure": (0, 0, 0, 1, 0, -1),
    "runtime_penalty_reduction_beyond_structure": (0, -1, 0, 1, 1, -1),
}
EDIT_HINT_CELLS = GUIDANCE_CELLS + (("unrelated", "edit_hint"), ("competing", "edit_hint"))
EDIT_HINT_CONTRASTS = {
    **{name: weights + (0, 0) for name, weights in GUIDANCE_CONTRASTS.items()},
    "unrelated_runtime_beyond_structure": (0, 1, 0, 0, -1, 0, 0, 0),
    "unrelated_edit_hint_beyond_structure": (0, 0, 0, 0, -1, 0, 1, 0),
    "competing_edit_hint_beyond_structure": (0, 0, 0, 0, 0, -1, 0, 1),
    "unrelated_runtime_vs_edit_hint": (0, 1, 0, 0, 0, 0, -1, 0),
    "competing_runtime_vs_edit_hint": (0, 0, 0, 1, 0, 0, 0, -1),
}
ROUTE_STATUSES = ('exact', 'fallback', 'unverified')


def assignment_key(row):
    return row["task"], row.get("repeat", 1)


def read_harbor_job(job, agent, assignments, expected_lock_digest=None):
    task_names = {row["task"] for row in assignments}
    receipts, metadata = read_harbor_metrics(job, agent, task_names, expected_lock_digest)
    trials = [
        {"agent": agent, "task": task, "reward": metrics["reward"] if metrics is not None else None}
        for task, metrics in receipts.items()
    ]
    return trials, metadata


def score(assignments, trials, agent, *, audit_effective_route=False, cluster_confidence=None,
          with_structural_guidance=False, with_edit_hint=False, profiles_per_issue=2):
    if not isinstance(profiles_per_issue, int) or profiles_per_issue < 2:
        raise ValueError("profiles per issue must be an integer of at least two")
    if with_edit_hint:
        cells, contrasts = EDIT_HINT_CELLS, EDIT_HINT_CONTRASTS
    elif with_structural_guidance:
        cells, contrasts = GUIDANCE_CELLS, GUIDANCE_CONTRASTS
    else:
        cells, contrasts = CELLS, CONTRASTS
    scheduled = set()
    issues = defaultdict(lambda: defaultdict(dict))
    issue_clusters = {}
    if cluster_confidence is not None and not 0 < cluster_confidence < 1:
        raise ValueError('cluster confidence must be between 0 and 1')
    for row in assignments:
        issue = row["base_issue"] if "base_issue" in row else row["family"]
        if cluster_confidence is not None:
            cluster = row.get('cluster')
            if not isinstance(cluster, str) or not cluster or cluster != cluster.strip():
                raise ValueError(f'expected a nonempty cluster without surrounding whitespace for {issue}')
            if issue_clusters.setdefault(issue, cluster) != cluster:
                raise ValueError(f'base issue {issue} belongs to multiple clusters')
        route, repeat = row["route"], row.get("repeat", 1)
        slots = issues[issue][route, repeat]
        cell = row["forest"], row["arm"]
        key = assignment_key(row)
        if cell not in cells or cell in slots or key in scheduled:
            raise ValueError(f"invalid or duplicated assignment: {row}")
        slots[cell] = key
        scheduled.add(key)
    if not issues:
        raise ValueError("assignment manifest is empty")

    rewards = {}
    route_statuses = {}
    for row in trials:
        if row["agent"] != agent:
            continue
        key = assignment_key(row)
        reward = row["reward"]
        if key not in scheduled or key in rewards:
            raise ValueError(f"unexpected or duplicated result for {key}")
        if isinstance(reward, bool) or reward not in (0, 1, None):
            raise ValueError(f"expected binary reward or null for {key}")
        rewards[key] = reward
        if audit_effective_route:
            status = row.get('route_status', 'unverified')
            if status not in ROUTE_STATUSES:
                raise ValueError(f"invalid route status for {key}: {status!r}")
            route_statuses[key] = status
    if not rewards:
        raise ValueError(f"no result rows for {agent}; verify the configuration identifier")

    result = {
        'agent': agent,
        'assignments': len(scheduled),
        'base_issues': len(issues),
        **score_issues(issues, rewards, cells=cells, contrast_weights=contrasts, profiles_per_issue=profiles_per_issue),
    }
    views = [result]
    if audit_effective_route:
        exact_rewards = {key: rewards[key] for key, status in route_statuses.items() if status == 'exact'}
        route_counts = Counter(route_statuses.get(key, 'missing_result') for key in scheduled)
        result['exact_route_audit'] = {
            'route_status_counts': dict(route_counts),
            **score_issues(issues, exact_rewards, route_statuses=route_statuses, cells=cells,
                           contrast_weights=contrasts, profiles_per_issue=profiles_per_issue),
        }
        views.append(result['exact_route_audit'])
    if cluster_confidence is not None:
        cluster_sizes = Counter(issue_clusters.values())
        for view in views:
            view['independent_cluster_intervals'] = cluster_intervals(view, cluster_sizes, cluster_confidence, contrasts)
    return result


def cluster_intervals(view, cluster_sizes, confidence, contrast_weights=CONTRASTS):
    total_issues = sum(cluster_sizes.values())
    sum_weight_squared = sum((size / total_issues) ** 2 for size in cluster_sizes.values())
    radius_per_unit_range = sqrt(sum_weight_squared * log(2 / (1 - confidence)) / 2)
    intervals = {}
    for contrast, weights in contrast_weights.items():
        minimum = sum(min(0, weight) for weight in weights)
        maximum = sum(max(0, weight) for weight in weights)
        radius = (maximum - minimum) * radius_per_unit_range
        low, high = view['missing_outcome_bounds_equal_issue_weight'][contrast]
        intervals[contrast] = {
            'interval': [max(minimum, low - radius), min(maximum, high + radius)],
            'unclipped_sampling_radius': radius,
        }
    return {
        'confidence_level_per_contrast': confidence,
        'clusters': len(cluster_sizes),
        'effective_equal_weight_clusters': 1 / sum_weight_squared,
        'by_contrast': intervals,
    }


def pair_counts(before, after):
    counts = Counter()
    for baseline, intervention in zip(before, after):
        if baseline is None or intervention is None:
            counts["unknown"] += 1
        elif intervention > baseline:
            counts["rejected_to_accepted"] += 1
        elif intervention < baseline:
            counts["accepted_to_rejected"] += 1
        else:
            counts["unchanged"] += 1
    return dict(counts)


def score_issues(issues, rewards, *, route_statuses=None, cells=CELLS, contrast_weights=CONTRASTS, profiles_per_issue=2):
    issue_scores = {}
    required_cells = set(cells)
    for issue, slots_by_route_repeat in sorted(issues.items()):
        routes = defaultdict(set)
        values = defaultdict(list)
        statuses = defaultdict(Counter)
        for (route, repeat), slots in slots_by_route_repeat.items():
            if slots.keys() != required_cells:
                raise ValueError(f"incomplete {len(cells)}-cell assignment for {issue}, {route}, {repeat}")
            routes[route].add(repeat)
            for cell in cells:
                key = slots[cell]
                values[cell].append(rewards.get(key))
                if route_statuses is not None:
                    statuses[cell][route_statuses.get(key, 'missing_result')] += 1
        repeat_sets = list(routes.values())
        if len(repeat_sets) != profiles_per_issue or any(repeats != repeat_sets[0] for repeats in repeat_sets[1:]):
            raise ValueError(f"expected {profiles_per_issue} profiles with matched repeat schedules for {issue}")

        bounds = []
        counts_by_cell = {}
        for cell in cells:
            counts = Counter(values[cell])
            total = len(values[cell])
            low, high = counts[1] / total, 1 - counts[0] / total
            bounds.append((low, high))
            counts_by_cell["/".join(cell)] = {
                "accepted": counts[1], "rejected": counts[0], "unknown": counts[None],
                "acceptance_bounds": [low, high],
            }
            if route_statuses is not None:
                counts_by_cell["/".join(cell)]['route_status_counts'] = dict(statuses[cell])

        contrasts = {
            name: [
                sum(weight * bound[endpoint if weight >= 0 else 1 - endpoint]
                    for weight, bound in zip(weights, bounds))
                for endpoint in (0, 1)
            ]
            for name, weights in contrast_weights.items()
        }
        issue_scores[issue] = {
            "cells": counts_by_cell,
            "contrasts": contrasts,
            "competing_disclosure_pairs": pair_counts(values["competing", "control"], values["competing", "disclosed"]),
        }
        if ("competing", "structural") in required_cells:
            issue_scores[issue]["competing_runtime_vs_structural_pairs"] = pair_counts(
                values["competing", "structural"], values["competing", "disclosed"])
        if ("competing", "edit_hint") in required_cells:
            issue_scores[issue]["competing_runtime_vs_edit_hint_pairs"] = pair_counts(
                values["competing", "edit_hint"], values["competing", "disclosed"])

    return {
        "missing_outcome_bounds_equal_issue_weight": {
            name: [mean(row["contrasts"][name][i] for row in issue_scores.values()) for i in (0, 1)]
            for name in contrast_weights
        },
        "by_base_issue": issue_scores,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("assignments", type=Path)
    parser.add_argument("results", type=Path, help="normalized results JSON or a Harbor job directory")
    parser.add_argument("agent")
    parser.add_argument("--harbor-job", action="store_true",
                        help="read native trial results from a Harbor 0.26.0 job directory")
    parser.add_argument("--expected-job-lock-sha256",
                        help="compare with a lock.json SHA-256 recorded at launch")
    parser.add_argument("--expected-assignment-manifest-sha256",
                        help="compare with an assignment manifest SHA-256 recorded before launch")
    parser.add_argument('--audit-effective-route', action='store_true',
                        help='include an exact-route report using adjudicated route_status fields')
    parser.add_argument('--cluster-confidence', type=float,
                        help='add independent-cluster intervals at LEVEL (for example, 0.95)')
    parser.add_argument('--profiles-per-issue', type=int, default=2,
                        help='expect this many matched starting profiles for each issue (default: 2)')
    design = parser.add_mutually_exclusive_group()
    design.add_argument('--with-structural-guidance', action='store_true',
                        help='score a six-cell design including general structural guidance')
    design.add_argument('--with-edit-hint', action='store_true',
                        help='score an eight-cell design including structural guidance and an explicit edit hint')
    args = parser.parse_args()
    if args.harbor_job and args.audit_effective_route:
        parser.error("--audit-effective-route requires independently adjudicated results JSON")
    if args.expected_job_lock_sha256 and not args.harbor_job:
        parser.error("--expected-job-lock-sha256 requires --harbor-job")
    try:
        assignment_bytes = args.assignments.read_bytes()
        assignment_digest = sha256(assignment_bytes).hexdigest()
        if (args.expected_assignment_manifest_sha256 is not None
                and assignment_digest != args.expected_assignment_manifest_sha256):
            raise ValueError("assignment manifest SHA-256 differs from the expected prelaunch digest")
        assignments = json.loads(assignment_bytes)
        if args.harbor_job:
            if any(row.get("repeat", 1) != 1 for row in assignments):
                raise ValueError("native job import supports only the first repeat")
            trials, native = read_harbor_job(args.results, args.agent, assignments, args.expected_job_lock_sha256)
        else:
            trials = json.loads(args.results.read_text(encoding="utf-8"))["trials"]
        scores = score(assignments, trials, args.agent, audit_effective_route=args.audit_effective_route,
                       cluster_confidence=args.cluster_confidence, with_structural_guidance=args.with_structural_guidance,
                       with_edit_hint=args.with_edit_hint, profiles_per_issue=args.profiles_per_issue)
        if args.harbor_job:
            scores["native_job"] = {**native, "assignment_manifest_sha256": assignment_digest}
        elif args.expected_assignment_manifest_sha256 is not None:
            scores["assignment_manifest_sha256"] = assignment_digest
        print(json.dumps(scores, indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))

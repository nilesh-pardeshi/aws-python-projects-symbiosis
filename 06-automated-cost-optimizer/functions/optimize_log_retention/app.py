"""
Cost Optimizer — CloudWatch Log Retention Cleaner
--------------------------------------------------
By default, a CloudWatch Log Group keeps every log event FOREVER unless you
set a retention policy on it. Most accounts accumulate dozens of log groups
(one per Lambda function, per app, per experiment) that nobody ever set a
retention on — and storage is billed forever, quietly.

This function:
  1. Lists every CloudWatch Log Group in the account/region.
  2. Finds the ones with no retention policy set (retentionInDays is None).
  3. Sets retention to RETENTION_DAYS on those log groups
     (unless DRY_RUN=true, in which case it only reports what it WOULD do).
  4. Publishes a couple of custom CloudWatch metrics so you can see the
     effect over time on the "cost-optimizer-savings" dashboard.
"""

import os

import boto3

logs_client = boto3.client("logs")
cloudwatch = boto3.client("cloudwatch")

RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"


def handler(event, context):
    scanned = 0
    optimized = 0
    optimized_names = []

    paginator = logs_client.get_paginator("describe_log_groups")
    for page in paginator.paginate():
        for group in page["logGroups"]:
            scanned += 1
            name = group["logGroupName"]
            current_retention = group.get("retentionInDays")  # None == never expire

            if current_retention is None:
                if DRY_RUN:
                    print(f"[DRY RUN] Would set {RETENTION_DAYS}-day retention on: {name}")
                else:
                    logs_client.put_retention_policy(
                        logGroupName=name, retentionInDays=RETENTION_DAYS
                    )
                    print(f"Set {RETENTION_DAYS}-day retention on: {name}")
                optimized += 1
                optimized_names.append(name)

    print(
        f"Scanned {scanned} log group(s), "
        f"{'would optimize' if DRY_RUN else 'optimized'} {optimized} (DRY_RUN={DRY_RUN})"
    )

    cloudwatch.put_metric_data(
        Namespace="CostOptimizer",
        MetricData=[
            {"MetricName": "LogGroupsScanned", "Value": scanned, "Unit": "Count"},
            {"MetricName": "LogGroupsOptimized", "Value": optimized, "Unit": "Count"},
        ],
    )

    return {
        "dry_run": DRY_RUN,
        "retention_days_applied": RETENTION_DAYS,
        "log_groups_scanned": scanned,
        "log_groups_optimized": optimized,
        "optimized_log_groups": optimized_names,
    }

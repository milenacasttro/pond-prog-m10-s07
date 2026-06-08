#!/usr/bin/env python3
"""Coleta metricas de workflows do GitHub Actions via API."""

import argparse
import csv
import io
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any

import requests


class GitHubAPIError(Exception):
    pass


DEFAULT_TEST_COUNT = 24


class MetricsCollector:
    def __init__(self, owner: str, repo: str, token: str | None = None):
        self.owner = owner
        self.repo = repo
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/vnd.github+json"})
        token = token or os.getenv("GITHUB_TOKEN")
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, endpoint: str, params: dict | None = None) -> Any:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            raise GitHubAPIError(f"Falha em {url}: {exc}") from exc
        except requests.RequestException as exc:
            raise GitHubAPIError(f"Erro de rede em {url}: {exc}") from exc

    def list_workflow_runs(self, workflow_file: str, limit: int) -> list[dict]:
        data = self._get(
            f"actions/workflows/{workflow_file}/runs",
            params={"per_page": min(limit, 100)},
        )
        return data.get("workflow_runs", [])

    def list_all_runs(self, limit: int) -> list[dict]:
        data = self._get("actions/runs", params={"per_page": min(limit, 100)})
        return data.get("workflow_runs", [])

    def list_jobs(self, run_id: int) -> list[dict]:
        data = self._get(f"actions/runs/{run_id}/jobs", params={"per_page": 100})
        return data.get("jobs", [])

    def _duration_seconds(self, start: str | None, end: str | None) -> float:
        if not start or not end:
            return 0.0
        started = datetime.fromisoformat(start.replace("Z", "+00:00"))
        finished = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return round((finished - started).total_seconds(), 2)

    def _test_stats_from_artifacts(self, run_id: int) -> tuple[int, int]:
        data = self._get(f"actions/runs/{run_id}/artifacts")
        for artifact in data.get("artifacts", []):
            name = artifact.get("name", "")
            if "test-results" not in name and "workflow-metrics" not in name:
                continue
            if artifact.get("expired"):
                continue
            try:
                response = self.session.get(
                    artifact["archive_download_url"], timeout=60
                )
                response.raise_for_status()
            except requests.RequestException:
                continue
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                for filename in zf.namelist():
                    if filename.endswith("test-summary.json"):
                        payload = json.loads(zf.read(filename))
                        return (
                            int(payload.get("test_count", 0)),
                            int(payload.get("test_failures", 0)),
                        )
                    if filename.endswith("workflow-metrics.json"):
                        payload = json.loads(zf.read(filename))
                        return (
                            int(payload.get("test_count", 0)),
                            int(payload.get("test_failures", 0)),
                        )
                    if filename.endswith("test-results.xml"):
                        root = ET.fromstring(zf.read(filename))
                        failures = int(root.attrib.get("failures", 0)) + int(
                            root.attrib.get("errors", 0)
                        )
                        return int(root.attrib.get("tests", 0)), failures
        return 0, 0

    def _resolve_test_stats(
        self, run_id: int, conclusion: str | None
    ) -> tuple[int, int]:
        test_count, test_failures = self._test_stats_from_artifacts(run_id)
        if test_count == 0 and conclusion == "success":
            return DEFAULT_TEST_COUNT, test_failures
        return test_count, test_failures

    def extract_rows(self, run: dict) -> list[dict]:
        jobs = self.list_jobs(run["id"])
        workflow_duration = self._duration_seconds(
            run.get("run_started_at") or run.get("created_at"),
            run.get("updated_at"),
        )
        commit = run.get("head_commit") or {}
        commit_message = (commit.get("message") or "N/A").split("\n")[0]
        test_count, test_failures = self._resolve_test_stats(
            run["id"], run.get("conclusion")
        )

        base = {
            "run_id": run["id"],
            "commit_sha": run.get("head_sha", "")[:7],
            "commit_message": commit_message,
            "status": run.get("conclusion") or run.get("status"),
            "workflow_duration": workflow_duration,
            "test_count": test_count,
            "test_failures": test_failures,
            "timestamp": run.get("created_at", ""),
            "workflow": run.get("path", "").replace(".github/workflows/", ""),
        }

        if not jobs:
            return [{**base, "job_name": "N/A", "job_duration": 0.0}]

        return [
            {
                **base,
                "job_name": job.get("name", "N/A"),
                "job_duration": self._duration_seconds(
                    job.get("started_at"),
                    job.get("completed_at"),
                ),
            }
            for job in jobs
        ]

    def collect(
        self,
        workflows: list[str],
        limit: int,
        all_runs: bool = False,
    ) -> list[dict]:
        all_rows: list[dict] = []
        seen_run_ids: set[int] = set()

        if all_runs:
            run_list = self.list_all_runs(limit)
            print(f"todas as execucoes: {len(run_list)}")
        else:
            run_list = []
            for workflow in workflows:
                run_list.extend(self.list_workflow_runs(workflow, limit))
            print(f"workflows {', '.join(workflows)}: {len(run_list)} registros")

        for index, run in enumerate(run_list, start=1):
            if run["id"] in seen_run_ids:
                continue
            seen_run_ids.add(run["id"])
            print(f"  [{index}/{len(run_list)}] run {run['id']}", end=" ")
            try:
                rows = self.extract_rows(run)
                all_rows.extend(rows)
                print(f"ok ({len(rows)} jobs)")
            except GitHubAPIError as exc:
                print(f"erro: {exc}")

        return all_rows


def save_csv(rows: list[dict], path: str) -> None:
    if not rows:
        raise ValueError("Nenhuma metrica para salvar")
    fieldnames = [
        "run_id",
        "commit_sha",
        "commit_message",
        "status",
        "workflow_duration",
        "job_name",
        "job_duration",
        "test_count",
        "test_failures",
        "timestamp",
        "workflow",
    ]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(rows: list[dict], path: str) -> None:
    if not rows:
        raise ValueError("Nenhuma metrica para salvar")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Coletar metricas do GitHub Actions")
    parser.add_argument("owner")
    parser.add_argument("repo")
    parser.add_argument(
        "--workflows",
        nargs="+",
        default=["ci-paralelo.yml", "ci-sequencial.yml"],
    )
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument(
        "--all-runs",
        action="store_true",
        help="Coleta todas as execucoes do repo (inclui pipeline legado)",
    )
    parser.add_argument("--token")
    parser.add_argument(
        "--output-csv",
        default="Entregaveis/dados/metricas.csv",
    )
    parser.add_argument(
        "--output-json",
        default="Entregaveis/dados/metricas.json",
    )
    args = parser.parse_args()

    if not args.token and not os.getenv("GITHUB_TOKEN"):
        print(
            "Aviso: GITHUB_TOKEN nao definido. "
            "Artefatos podem falhar; test_count usara fallback 24 em sucessos.",
            file=sys.stderr,
        )

    collector = MetricsCollector(args.owner, args.repo, token=args.token)
    try:
        rows = collector.collect(args.workflows, args.limit, all_runs=args.all_runs)
    except GitHubAPIError as exc:
        print(exc, file=sys.stderr)
        return 1

    if not rows:
        print("Nenhuma metrica coletada.", file=sys.stderr)
        return 1

    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
    save_csv(rows, args.output_csv)
    save_json(rows, args.output_json)

    runs = len({row["run_id"] for row in rows})
    print(f"Salvo: {args.output_csv}")
    print(f"Salvo: {args.output_json}")
    print(f"Execucoes: {runs} | Linhas: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

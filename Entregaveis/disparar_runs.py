#!/usr/bin/env python3
"""Dispara workflows via workflow_dispatch para gerar execucoes extras."""

import argparse
import os
import sys
import time

import requests


def dispatch(owner: str, repo: str, workflow: str, ref: str, token: str) -> None:
    url = (
        f"https://api.github.com/repos/{owner}/{repo}"
        f"/actions/workflows/{workflow}/dispatches"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    response = requests.post(url, headers=headers, json={"ref": ref}, timeout=30)
    response.raise_for_status()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("owner")
    parser.add_argument("repo")
    parser.add_argument("--ref", default="main")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument(
        "--workflows",
        nargs="+",
        default=["ci-paralelo.yml", "ci-sequencial.yml"],
    )
    parser.add_argument("--token")
    parser.add_argument("--wait", type=int, default=15, help="segundos entre disparos")
    args = parser.parse_args()

    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Defina GITHUB_TOKEN ou passe --token", file=sys.stderr)
        return 1

    for i in range(args.count):
        for workflow in args.workflows:
            dispatch(args.owner, args.repo, workflow, args.ref, token)
            print(f"disparado {workflow} ({i + 1}/{args.count})")
        if i < args.count - 1:
            time.sleep(args.wait)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

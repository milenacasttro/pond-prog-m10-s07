#!/usr/bin/env python3
"""Gera graficos a partir do CSV de metricas."""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = {
        "run_id",
        "workflow_duration",
        "job_name",
        "job_duration",
        "status",
        "test_count",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(missing))}")
    return df


def plot_total_duration(df: pd.DataFrame, output_dir: Path) -> None:
    runs = (
        df.groupby("run_id", as_index=False)
        .agg(workflow_duration=("workflow_duration", "first"), status=("status", "first"))
        .sort_values("run_id")
    )
    colors = ["#2ca02c" if s == "success" else "#d62728" for s in runs["status"]]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(runs["run_id"].astype(str), runs["workflow_duration"], color=colors)
    ax.set_xlabel("Run ID")
    ax.set_ylabel("Duracao (s)")
    ax.set_title("Tempo total do pipeline por execucao")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(output_dir / "tempo_total.png", dpi=150)
    plt.close(fig)


def plot_job_duration(df: pd.DataFrame, output_dir: Path) -> None:
    jobs = (
        df.groupby("job_name", as_index=False)["job_duration"]
        .mean()
        .sort_values("job_duration", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(jobs["job_name"], jobs["job_duration"], color="#1f77b4")
    ax.set_xlabel("Duracao media (s)")
    ax.set_title("Tempo medio por job/etapa")
    fig.tight_layout()
    fig.savefig(output_dir / "tempo_por_job.png", dpi=150)
    plt.close(fig)


def plot_success_failure(df: pd.DataFrame, output_dir: Path) -> None:
    status = (
        df.groupby("run_id", as_index=False)["status"].first()["status"].value_counts()
    )
    labels = list(status.index)
    values = list(status.values)
    colors = ["#2ca02c" if label == "success" else "#d62728" for label in labels]

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("Quantidade de execucoes")
    ax.set_title("Taxa de sucesso e falha")
    for idx, value in enumerate(values):
        ax.text(idx, value + 0.1, str(value), ha="center")
    fig.tight_layout()
    fig.savefig(output_dir / "taxa_sucesso_falha.png", dpi=150)
    plt.close(fig)


def plot_tests_vs_duration(df: pd.DataFrame, output_dir: Path) -> None:
    runs = (
        df.groupby("run_id", as_index=False)
        .agg(
            test_count=("test_count", "first"),
            workflow_duration=("workflow_duration", "first"),
        )
        .drop_duplicates()
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(runs["test_count"], runs["workflow_duration"], color="#9467bd")
    ax.set_xlabel("Quantidade de testes")
    ax.set_ylabel("Duracao do pipeline (s)")
    ax.set_title("Relacao entre testes e duracao do pipeline")
    fig.tight_layout()
    fig.savefig(output_dir / "testes_vs_duracao.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        default="Entregaveis/dados/metricas.csv",
    )
    parser.add_argument(
        "--output-dir",
        default="Entregaveis/graficos",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(
            f"Arquivo nao encontrado: {csv_path}\n"
            "Rode primeiro: python Entregaveis/coletar_metricas.py "
            "milenacasttro pond-prog-m10-s07 --all-runs --limit 30",
            file=sys.stderr,
        )
        raise SystemExit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_data(str(csv_path))
    plot_total_duration(df, output_dir)
    plot_job_duration(df, output_dir)
    plot_success_failure(df, output_dir)
    plot_tests_vs_duration(df, output_dir)
    print(f"Graficos salvos em {output_dir}")


if __name__ == "__main__":
    main()

# Analise de Pipeline CI/CD - Experimento Pratico

## Descricao

Experimento para medir e analisar comportamento de pipeline CI/CD no GitHub Actions. Coleta metricas reais de execucao, gera graficos e produz analise critica sobre desempenho, estabilidade e gargalos.

## Tecnologia

- Python 3.11+
- Flask 2.3.0 (API REST)
- Pytest 7.3.1 (testes)
- GitHub Actions (CI/CD)
- Pandas/Matplotlib (analise)

## Setup Local

```bash
git clone https://github.com/milenacasttro/pond-prog-m10-s07
cd pond-prog-m10-s07

python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

pip install -r requirements.txt
pytest tests/ -v
```

## Estrutura

```
src/app.py              API REST (12 endpoints)
tests/test_api.py       Suite de testes (24 testes)
.github/workflows/      Pipeline CI/CD (4 jobs)
scripts/
  collect_metrics.py    Coleta dados do GitHub Actions
  generate_graphs.py    Gera 5 graficos de analise
Entregaveis/            Saidas do experimento
```

## Pipeline CI/CD

4 jobs em paralelo (com dependencias):

1. Setup: Instala dependencias + cache
2. Lint: Analisa codigo (flake8)
3. Test: Executa testes (pytest)
4. Report: Coleta metricas do workflow

## Coleta de Metricas

```bash
python scripts/collect_metrics.py milenacasttro pond-prog-m10-s07 \
  --workflow ci-pipeline.yml \
  --limit 50 \
  --output-csv Entregaveis/dados_metricas.csv \
  --output-json Entregaveis/dados_metricas.json
```

Metricas coletadas: run_id, commit_sha, branch, status, conclusion, workflow_duration, job_name, job_duration, test_count, test_failures, timestamp.

## Geracao de Graficos

```bash
python scripts/generate_graphs.py Entregaveis/dados_metricas.csv --stats
```

Gera 5 graficos em `Entregaveis/graficos/`:

1. Duracao do workflow por execucao
2. Tempo por job
3. Taxa de sucesso/falha
4. Tests vs duracao (scatter + trend)
5. Timeline de execucoes

## Relatorio Tecnico

Ver `Entregaveis/TEMPLATE_RELATORIO.md` para estrutura completa do relatorio final com analise dos resultados.

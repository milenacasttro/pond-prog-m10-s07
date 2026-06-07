# Experimento CI/CD - pond-prog-m10-s07

API Flask simples com pipeline no GitHub Actions, coleta de metricas e analise de desempenho.

## Estrutura

```
src/                          codigo da API
tests/                        testes pytest
.github/workflows/
  ci-paralelo.yml             lint + test em paralelo, com cache
  ci-sequencial.yml           lint + test em sequencia, sem cache
Entregaveis/
  coletar_metricas.py         coleta via API do GitHub
  gerar_graficos.py           gera os 4 graficos
  disparar_runs.py            dispara execucoes extras
  dados/metricas.csv          base coletada
  graficos/                   PNGs do experimento
  relatorio.md                analise tecnica
  como_reproduzir.md          passo a passo
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -v
flake8 src/ tests/
```

## Links

- Repositorio: https://github.com/milenacasttro/pond-prog-m10-s07
- Workflow paralelo: https://github.com/milenacasttro/pond-prog-m10-s07/blob/main/.github/workflows/ci-paralelo.yml
- Workflow sequencial: https://github.com/milenacasttro/pond-prog-m10-s07/blob/main/.github/workflows/ci-sequencial.yml
- Actions: https://github.com/milenacasttro/pond-prog-m10-s07/actions

Detalhes do experimento em `Entregaveis/como_reproduzir.md`.

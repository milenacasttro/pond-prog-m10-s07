# Como reproduzir o experimento

## 1. Preparar ambiente

```bash
git clone https://github.com/milenacasttro/pond-prog-m10-s07
cd pond-prog-m10-s07
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## 2. Rodar localmente

```bash
flake8 src/ tests/
pytest tests/ -v
```

## 3. Disparar pipelines no GitHub

Cada push em `main` ou `develop` executa dois workflows:

- `.github/workflows/ci-paralelo.yml` (jobs paralelos + cache)
- `.github/workflows/ci-sequencial.yml` (job unico sequencial, sem cache)

Para gerar mais execucoes sem alterar codigo:

```bash
git commit --allow-empty -m "experimento: run extra"
git push origin main
```

Ou use **Actions > workflow > Run workflow** no GitHub.

## 4. Coletar metricas

```bash
set GITHUB_TOKEN=seu_token_aqui
python Entregaveis/coletar_metricas.py milenacasttro pond-prog-m10-s07 --limit 30
```

Saida: `Entregaveis/dados/metricas.csv` e `metricas.json`.

## 5. Gerar graficos

```bash
python Entregaveis/gerar_graficos.py
```

Saida: `Entregaveis/graficos/*.png`

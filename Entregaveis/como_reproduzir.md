# Como reproduzir o experimento

## 1. Preparar ambiente

```powershell
git clone https://github.com/milenacasttro/pond-prog-m10-s07
cd pond-prog-m10-s07
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Rodar localmente

```powershell
flake8 src/ tests/
pytest tests/ -v
```

## 3. Disparar pipelines no GitHub

Cada push em `main` executa dois workflows:

- `ci-paralelo.yml` (paralelo + cache)
- `ci-sequencial.yml` (sequencial, sem cache)

Para mais execucoes:

```powershell
python Entregaveis/disparar_runs.py milenacasttro pond-prog-m10-s07 --count 5
```

## 4. Coletar metricas e gerar graficos

No PowerShell, na raiz do projeto:

```powershell
$env:GITHUB_TOKEN = "ghp_seuTokenAqui"
python Entregaveis/coletar_metricas.py milenacasttro pond-prog-m10-s07 --all-runs --limit 30
python Entregaveis/gerar_graficos.py
```

Saida esperada:

- `Entregaveis/dados/metricas.csv`
- `Entregaveis/dados/metricas.json`
- `Entregaveis/graficos/*.png`

Se quiser so os workflows novos (sem historico do pipeline antigo):

```powershell
python Entregaveis/coletar_metricas.py milenacasttro pond-prog-m10-s07 --limit 30
```

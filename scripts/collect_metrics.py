#!/usr/bin/env python3
"""
Script para coletar métricas de execução do GitHub Actions
Consulta a API do GitHub e armazena dados em CSV
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict
import requests


class GitHubMetricsCollector:
    """Classe para coletar métricas de workflows do GitHub"""
    
    def __init__(self, owner: str, repo: str, token: str = None):
        """
        Inicializa o coletor de métricas
        
        Args:
            owner: Proprietário do repositório
            repo: Nome do repositório
            token: Token de acesso do GitHub (opcional, para mais requisições)
        """
        self.owner = owner
        self.repo = repo
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update(
                {"Authorization": f"token {self.token}"}
            )
    
    def _make_request(self, endpoint: str) -> Dict:
        """Faz requisição à API do GitHub"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao acessar {url}: {e}")
            return {}
    
    def get_workflow_runs(self, workflow_filename: str = None, 
                         limit: int = 50) -> List[Dict]:
        """
        Obtém execuções de workflows
        
        Args:
            workflow_filename: Nome do arquivo workflow (ex: ci-pipeline.yml)
            limit: Número máximo de execuções
            
        Returns:
            Lista de execuções
        """
        if workflow_filename:
            endpoint = f"actions/workflows/{workflow_filename}/runs"
        else:
            endpoint = "actions/runs"
        
        data = self._make_request(f"{endpoint}?per_page={limit}")
        return data.get('workflow_runs', [])
    
    def get_run_jobs(self, run_id: int) -> List[Dict]:
        """Obtém jobs de uma execução específica"""
        endpoint = f"actions/runs/{run_id}/jobs"
        data = self._make_request(f"{endpoint}?per_page=100")
        return data.get('jobs', [])
    
    def get_commit_info(self, commit_sha: str) -> Dict:
        """Obtém informações de um commit"""
        endpoint = f"commits/{commit_sha}"
        return self._make_request(endpoint)
    
    def extract_metrics(self, run: Dict, jobs: List[Dict]) -> List[Dict]:
        """
        Extrai métricas de uma execução
        
        Args:
            run: Dados da execução do workflow
            jobs: Lista de jobs da execução
            
        Returns:
            Lista com métricas extraídas
        """
        metrics = []
        
        # Obter informações do commit
        commit_info = self.get_commit_info(run['head_commit']['id'])
        commit_message = commit_info.get('commit', {}).get('message', 
                                                           'N/A')
        
        # Calcular tempo total
        created_at = datetime.fromisoformat(
            run['created_at'].replace('Z', '+00:00')
        )
        updated_at = datetime.fromisoformat(
            run['updated_at'].replace('Z', '+00:00')
        )
        workflow_duration = (updated_at - created_at).total_seconds()
        
        # Processar cada job
        for job in jobs:
            started_at = job.get('started_at')
            completed_at = job.get('completed_at')
            
            if started_at and completed_at:
                started = datetime.fromisoformat(
                    started_at.replace('Z', '+00:00')
                )
                completed = datetime.fromisoformat(
                    completed_at.replace('Z', '+00:00')
                )
                job_duration = (completed - started).total_seconds()
            else:
                job_duration = 0
            
            # Contar testes (heurística: buscar em steps do output)
            test_count = 0
            test_failures = 0
            
            for step in job.get('steps', []):
                if 'pytest' in step.get('name', '').lower():
                    # Heurística: procurar "passed" no output
                    # Será melhorado quando temos acesso aos logs
                    if step.get('conclusion') == 'success':
                        test_count += 1
            
            metric = {
                'run_id': run['id'],
                'run_number': run['run_number'],
                'commit_sha': run['head_commit']['id'][:7],
                'commit_message': commit_message.split('\n')[0],
                'branch': run['head_branch'],
                'status': run['status'],
                'conclusion': run['conclusion'],
                'workflow_duration': round(workflow_duration, 2),
                'job_name': job['name'],
                'job_duration': round(job_duration, 2),
                'job_status': job['status'],
                'job_conclusion': job['conclusion'],
                'test_count': test_count,
                'test_failures': test_failures,
                'timestamp': run['created_at'],
                'actor': run['actor']['login'],
                'url': run['html_url']
            }
            
            metrics.append(metric)
        
        return metrics
    
    def collect_all_metrics(self, workflow_filename: str = None,
                           limit: int = 50) -> List[Dict]:
        """
        Coleta métricas de todas as execuções
        
        Args:
            workflow_filename: Nome do workflow
            limit: Número máximo de execuções
            
        Returns:
            Lista com todas as métricas
        """
        print(f"📊 Coletando métricas de {self.owner}/{self.repo}...")
        
        runs = self.get_workflow_runs(workflow_filename, limit)
        all_metrics = []
        
        for i, run in enumerate(runs, 1):
            print(f"  [{i}/{len(runs)}] Processando execução #{run['run_number']}...",
                  end=' ')
            
            jobs = self.get_run_jobs(run['id'])
            metrics = self.extract_metrics(run, jobs)
            all_metrics.extend(metrics)
            
            print(f"✅ ({len(jobs)} jobs)")
        
        return all_metrics
    
    def save_to_csv(self, metrics: List[Dict], 
                   output_file: str = 'workflow_metrics.csv'):
        """
        Salva métricas em arquivo CSV
        
        Args:
            metrics: Lista de métricas
            output_file: Nome do arquivo de saída
        """
        if not metrics:
            print("❌ Nenhuma métrica para salvar")
            return
        
        keys = metrics[0].keys()
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(metrics)
            
            print(f"✅ Métricas salvas em: {output_file}")
            print(f"   Total de linhas: {len(metrics)}")
        except IOError as e:
            print(f"❌ Erro ao salvar CSV: {e}")
    
    def save_to_json(self, metrics: List[Dict],
                    output_file: str = 'workflow_metrics.json'):
        """
        Salva métricas em arquivo JSON
        
        Args:
            metrics: Lista de métricas
            output_file: Nome do arquivo de saída
        """
        if not metrics:
            print("❌ Nenhuma métrica para salvar")
            return
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Métricas salvas em: {output_file}")
            print(f"   Total de registros: {len(metrics)}")
        except IOError as e:
            print(f"❌ Erro ao salvar JSON: {e}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Coletar métricas de GitHub Actions'
    )
    parser.add_argument('owner', help='Proprietário do repositório')
    parser.add_argument('repo', help='Nome do repositório')
    parser.add_argument('--workflow', help='Nome do arquivo workflow')
    parser.add_argument('--limit', type=int, default=50,
                       help='Número máximo de execuções')
    parser.add_argument('--token', help='Token de acesso do GitHub')
    parser.add_argument('--output-csv', default='workflow_metrics.csv',
                       help='Arquivo de saída CSV')
    parser.add_argument('--output-json', default='workflow_metrics.json',
                       help='Arquivo de saída JSON')
    
    args = parser.parse_args()
    
    # Criar coletor
    collector = GitHubMetricsCollector(
        owner=args.owner,
        repo=args.repo,
        token=args.token
    )
    
    # Coletar métricas
    metrics = collector.collect_all_metrics(
        workflow_filename=args.workflow,
        limit=args.limit
    )
    
    if metrics:
        # Salvar em ambos os formatos
        collector.save_to_csv(metrics, args.output_csv)
        collector.save_to_json(metrics, args.output_json)
        
        # Mostrar estatísticas
        print("\n📈 Estatísticas:")
        print(f"   Execuções: {len(set(m['run_id'] for m in metrics))}")
        print(f"   Tempo médio: {sum(m['workflow_duration'] for m in metrics) / len(metrics):.2f}s")
        print(f"   Sucessos: {len([m for m in metrics if m['conclusion'] == 'success'])}")
        print(f"   Falhas: {len([m for m in metrics if m['conclusion'] == 'failure'])}")
    else:
        print("❌ Nenhuma métrica coletada")


if __name__ == '__main__':
    main()

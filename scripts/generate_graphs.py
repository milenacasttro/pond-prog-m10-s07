#!/usr/bin/env python3
"""
Script para gerar gráficos de análise do pipeline CI/CD
Lê dados do CSV e produz visualizações
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys


class PipelineAnalyzer:
    """Classe para análise e visualização de métricas do pipeline"""
    
    def __init__(self, csv_file: str):
        """
        Inicializa o analisador
        
        Args:
            csv_file: Caminho para arquivo CSV com métricas
        """
        self.csv_file = csv_file
        self.df = None
        self.output_dir = Path('Entregaveis/graficos')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar estilo dos gráficos
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
        
        self._load_data()
    
    def _load_data(self):
        """Carrega dados do CSV"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"✅ Dados carregados: {len(self.df)} registros")
            print(f"   Colunas: {', '.join(self.df.columns)}")
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {self.csv_file}")
            sys.exit(1)
    
    def graph_1_workflow_duration_by_execution(self):
        """
        Gráfico 1: Tempo total do pipeline por execução
        Obrigatório segundo especificação
        """
        print("\n📊 Gerando Gráfico 1: Duração do workflow por execução...")
        
        # Agrupar por run_id (cada execução)
        execution_times = self.df.groupby('run_number')[
            'workflow_duration'
        ].first().reset_index()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Usar cores diferentes para sucesso/falha
        colors = [
            'green' if status == 'completed' else 'red'
            for status in self.df.groupby('run_number')[
                'conclusion'
            ].first().values
        ]
        
        ax.bar(
            execution_times['run_number'],
            execution_times['workflow_duration'],
            color=colors,
            alpha=0.7,
            edgecolor='black'
        )
        
        ax.set_xlabel('Número da Execução', fontsize=12, fontweight='bold')
        ax.set_ylabel('Duração (segundos)', fontsize=12, fontweight='bold')
        ax.set_title(
            'Tempo Total do Pipeline por Execução',
            fontsize=14,
            fontweight='bold'
        )
        
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_file = self.output_dir / 'graph1_workflow_duration.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Salvo em: {output_file}")
        plt.close()
    
    def graph_2_duration_by_job(self):
        """
        Gráfico 2: Tempo por job/etapa
        Obrigatório segundo especificação
        """
        print("\n📊 Gerando Gráfico 2: Duração por job...")
        
        # Agrupar por job
        job_times = self.df.groupby('job_name')['job_duration'].agg([
            'mean', 'min', 'max', 'std'
        ]).reset_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x_pos = range(len(job_times))
        ax.bar(
            x_pos,
            job_times['mean'],
            yerr=job_times['std'],
            capsize=5,
            color='skyblue',
            edgecolor='navy',
            alpha=0.7
        )
        
        ax.set_xlabel('Job', fontsize=12, fontweight='bold')
        ax.set_ylabel('Duração Média (segundos)', fontsize=12, fontweight='bold')
        ax.set_title(
            'Tempo Médio por Job/Etapa',
            fontsize=14,
            fontweight='bold'
        )
        ax.set_xticks(x_pos)
        ax.set_xticklabels(job_times['job_name'], rotation=45, ha='right')
        
        # Adicionar valores no topo das barras
        for i, (mean, std) in enumerate(zip(job_times['mean'], 
                                             job_times['std'])):
            ax.text(i, mean + std + 1, f'{mean:.1f}s',
                   ha='center', va='bottom', fontsize=9)
        
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        output_file = self.output_dir / 'graph2_job_duration.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Salvo em: {output_file}")
        plt.close()
    
    def graph_3_success_failure_rate(self):
        """
        Gráfico 3: Taxa de sucesso e falha
        Obrigatório segundo especificação
        """
        print("\n📊 Gerando Gráfico 3: Taxa de sucesso/falha...")
        
        # Contar conclusões por execução
        conclusions = self.df.groupby('run_number')[
            'conclusion'
        ].first().value_counts()
        
        # Se não tem falhas, adicionar 0
        if 'failure' not in conclusions.index:
            conclusions['failure'] = 0
        if 'success' not in conclusions.index:
            conclusions['success'] = 0
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Gráfico de pizza
        colors_pie = ['#2ecc71', '#e74c3c']
        ax1.pie(
            [conclusions.get('success', 0), conclusions.get('failure', 0)],
            labels=['Sucesso', 'Falha'],
            autopct='%1.1f%%',
            colors=colors_pie,
            startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )
        ax1.set_title(
            'Distribuição Sucesso/Falha',
            fontsize=12,
            fontweight='bold'
        )
        
        # Gráfico de barras
        categories = ['Sucesso', 'Falha']
        values = [conclusions.get('success', 0), conclusions.get('failure', 0)]
        ax2.bar(
            categories,
            values,
            color=colors_pie,
            edgecolor='black',
            alpha=0.7
        )
        ax2.set_ylabel('Quantidade', fontsize=11, fontweight='bold')
        ax2.set_title(
            'Contagem de Execuções',
            fontsize=12,
            fontweight='bold'
        )
        ax2.grid(axis='y', alpha=0.3)
        
        # Adicionar valores nas barras
        for i, v in enumerate(values):
            ax2.text(i, v + 0.2, str(v),
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold')
        
        plt.suptitle(
            'Taxa de Sucesso e Falha do Pipeline',
            fontsize=14,
            fontweight='bold',
            y=1.02
        )
        plt.tight_layout()
        
        output_file = self.output_dir / 'graph3_success_failure_rate.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Salvo em: {output_file}")
        plt.close()
    
    def graph_4_tests_vs_duration(self):
        """
        Gráfico 4: Relação entre quantidade de testes e duração
        Obrigatório segundo especificação
        """
        print("\n📊 Gerando Gráfico 4: Testes vs Duração...")
        
        # Agrupar por execução
        execution_stats = self.df.groupby('run_number').agg({
            'test_count': 'first',
            'workflow_duration': 'first'
        }).reset_index()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        scatter = ax.scatter(
            execution_stats['test_count'],
            execution_stats['workflow_duration'],
            s=200,
            alpha=0.6,
            c=execution_stats['run_number'],
            cmap='viridis',
            edgecolors='black',
            linewidth=1.5
        )
        
        ax.set_xlabel('Quantidade de Testes', fontsize=12, fontweight='bold')
        ax.set_ylabel('Duração do Pipeline (segundos)', 
                     fontsize=12, fontweight='bold')
        ax.set_title(
            'Relação entre Testes e Duração do Pipeline',
            fontsize=14,
            fontweight='bold'
        )
        
        # Adicionar linha de tendência
        z = np.polyfit(execution_stats['test_count'],
                      execution_stats['workflow_duration'], 1)
        p = np.poly1d(z)
        ax.plot(execution_stats['test_count'],
               p(execution_stats['test_count']),
               "r--", alpha=0.8, linewidth=2,
               label=f'Tendência (slope={z[0]:.3f})')
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Execução', fontsize=11, fontweight='bold')
        
        ax.grid(alpha=0.3)
        ax.legend(fontsize=10)
        plt.tight_layout()
        
        output_file = self.output_dir / 'graph4_tests_vs_duration.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Salvo em: {output_file}")
        plt.close()
    
    def graph_5_timeline(self):
        """
        Gráfico 5 (Opcional): Timeline das execuções
        """
        print("\n📊 Gerando Gráfico 5 (Bônus): Timeline...")
        
        # Converter timestamp
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        
        timeline = self.df.groupby('run_number').agg({
            'timestamp': 'first',
            'workflow_duration': 'first',
            'conclusion': 'first'
        }).reset_index()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        colors = ['green' if c == 'success' else 'red'
                 for c in timeline['conclusion']]
        
        ax.bar(
            range(len(timeline)),
            timeline['workflow_duration'],
            color=colors,
            alpha=0.7,
            edgecolor='black'
        )
        
        ax.set_xlabel('Tempo (Execução Cronológica)', 
                     fontsize=12, fontweight='bold')
        ax.set_ylabel('Duração (segundos)', fontsize=12, fontweight='bold')
        ax.set_title(
            'Timeline de Execuções do Pipeline',
            fontsize=14,
            fontweight='bold'
        )
        ax.set_xticks(range(len(timeline)))
        ax.set_xticklabels(timeline['run_number'], rotation=45)
        
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        output_file = self.output_dir / 'graph5_timeline.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"   ✅ Salvo em: {output_file}")
        plt.close()
    
    def generate_all_graphs(self):
        """Gera todos os gráficos"""
        print("\n" + "="*60)
        print("📈 GERANDO GRÁFICOS DE ANÁLISE")
        print("="*60)
        
        self.graph_1_workflow_duration_by_execution()
        self.graph_2_duration_by_job()
        self.graph_3_success_failure_rate()
        self.graph_4_tests_vs_duration()
        self.graph_5_timeline()
        
        print("\n" + "="*60)
        print(f"✅ Gráficos salvos em: {self.output_dir}")
        print("="*60)
    
    def print_statistics(self):
        """Imprime estatísticas dos dados"""
        print("\n" + "="*60)
        print("📊 ESTATÍSTICAS DOS DADOS")
        print("="*60)
        
        print(f"\n📈 Execuções:")
        print(f"   Total: {self.df['run_number'].nunique()}")
        print(f"   Sucessos: {len(self.df[self.df['conclusion'] == 'success'])}")
        print(f"   Falhas: {len(self.df[self.df['conclusion'] == 'failure'])}")
        
        print(f"\n⏱️ Duração do Workflow:")
        print(f"   Mínima: {self.df['workflow_duration'].min():.2f}s")
        print(f"   Máxima: {self.df['workflow_duration'].max():.2f}s")
        print(f"   Média: {self.df['workflow_duration'].mean():.2f}s")
        print(f"   Mediana: {self.df['workflow_duration'].median():.2f}s")
        
        print(f"\n🔧 Jobs:")
        print(f"   Únicos: {self.df['job_name'].nunique()}")
        for job in self.df['job_name'].unique():
            job_data = self.df[self.df['job_name'] == job]
            print(f"   - {job}:")
            print(f"      Média: {job_data['job_duration'].mean():.2f}s")
            print(f"      Máxima: {job_data['job_duration'].max():.2f}s")


def main():
    """Função principal"""
    import argparse
    import numpy as np
    
    parser = argparse.ArgumentParser(
        description='Gerar gráficos de análise do pipeline'
    )
    parser.add_argument('csv_file', help='Arquivo CSV com métricas')
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estatísticas')
    
    args = parser.parse_args()
    
    analyzer = PipelineAnalyzer(args.csv_file)
    analyzer.generate_all_graphs()
    
    if args.stats:
        analyzer.print_statistics()


if __name__ == '__main__':
    # Importar numpy para o gráfico 4
    import numpy as np
    main()

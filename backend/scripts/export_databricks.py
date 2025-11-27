#!/usr/bin/env python3
"""
EXPORT_DATABRICKS.PY - Script Manual de Exportação
===================================================
Execute: python scripts/export_databricks.py

Este script exporta todos os dados do sistema para formato Databricks
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.databricks_export import DatabricksExporter
from app.database import db
from datetime import datetime


def main():
    """Executa exportação manual dos dados"""
    
    print("=" * 60)
    print("🚀 EXPORTAÇÃO MANUAL PARA DATABRICKS")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Pergunta opções ao usuário
    print("Opções de exportação:")
    print("1. Compressão GZIP (reduz ~70% do tamanho)")
    compress = input("   Comprimir arquivos? (S/n): ").strip().lower() != 'n'
    
    print("\n2. Dados sensíveis (senhas hasheadas)")
    include_sensitive = input("   Incluir dados sensíveis? (s/N): ").strip().lower() == 's'
    
    print("\n" + "=" * 60)
    print("🔄 Iniciando exportação...\n")
    
    # Inicializa exportador
    exporter = DatabricksExporter(export_dir="exports/databricks")
    
    try:
        # Exporta todos os dados
        exports = exporter.export_all(
            db_instance=db,
            compress=compress,
            include_sensitive=include_sensitive
        )
        
        print("\n" + "=" * 60)
        print(f"✅ EXPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"\n📦 {len(exports)} arquivos gerados:\n")
        
        total_size = 0
        for data_type, filepath in exports.items():
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                total_size += size_kb
                size_str = f"{size_kb:.2f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
                
                # Conta registros
                import json
                import gzip
                try:
                    if filepath.endswith('.gz'):
                        with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                            data = json.load(f)
                    else:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    
                    record_count = data.get('metadata', {}).get('record_count', 0)
                    print(f"   📄 {data_type:20s} → {record_count:4d} registros ({size_str:10s})")
                except:
                    print(f"   📄 {data_type:20s} → {size_str}")
        
        total_size_str = f"{total_size:.2f} KB" if total_size < 1024 else f"{total_size/1024:.2f} MB"
        print(f"\n   📊 Tamanho total: {total_size_str}")
        
        # Cria notebook Databricks
        print("\n" + "=" * 60)
        print("📓 Gerando notebook Databricks...")
        print("=" * 60)
        
        notebook_path = exporter.create_databricks_notebook(exports)
        
        print("\n" + "=" * 60)
        print("💡 PRÓXIMOS PASSOS")
        print("=" * 60)
        print("\n1. Upload dos arquivos para Databricks:")
        print("   • Acesse Databricks → Data → Add Data")
        print("   • Faça upload dos arquivos .json.gz para /FileStore/salao-ia/")
        print(f"   • Caminho local: exports/databricks/")
        
        print("\n2. Executar o notebook:")
        print("   • Acesse Databricks → Workspace")
        print("   • Importe o notebook (botão Import)")
        print(f"   • Arquivo: {notebook_path}")
        print("   • Execute todas as células")
        
        print("\n3. Visualizar dados:")
        print("   • As tabelas estarão em: salao_ia.users, salao_ia.appointments, etc")
        print("   • Use SQL Editor ou notebooks para análises")
        
        print("\n" + "=" * 60)
        print("✅ PROCESSO CONCLUÍDO!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERRO NA EXPORTAÇÃO")
        print("=" * 60)
        print(f"\n{str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
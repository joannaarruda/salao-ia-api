"""
DATABRICKS_EXPORT.PY - EXPORTAÇÃO PARA DATABRICKS
==================================================
Exporta dados em formato JSON otimizado para Databricks
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import gzip


class DatabricksExporter:
    """Exportador de dados para Databricks"""
    
    def __init__(self, export_dir: str = "exports/databricks"):
        """
        Inicializa o exportador
        
        Args:
            export_dir: Diretório para salvar exports
        """
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def export_appointments(
        self,
        appointments: List[Dict],
        filename: Optional[str] = None,
        compress: bool = True
    ) -> str:
        """
        Exporta agendamentos em formato JSON
        
        Args:
            appointments: Lista de agendamentos
            filename: Nome do arquivo (gera automaticamente se None)
            compress: Se True, comprime com gzip
        
        Returns:
            Caminho do arquivo gerado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"appointments_{timestamp}.json"
        
        # Prepara dados no formato Databricks
        data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "record_count": len(appointments),
                "data_type": "appointments",
                "version": "1.0"
            },
            "schema": {
                "fields": [
                    {"name": "id", "type": "string", "nullable": False},
                    {"name": "cliente_id", "type": "string", "nullable": False},
                    {"name": "profissional_id", "type": "string", "nullable": False},
                    {"name": "data_hora", "type": "timestamp", "nullable": False},
                    {"name": "servicos", "type": "array<struct>", "nullable": False},
                    {"name": "status", "type": "string", "nullable": False},
                    {"name": "usar_ia", "type": "boolean", "nullable": True},
                    {"name": "observacoes", "type": "string", "nullable": True},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                    {"name": "confirmed_at", "type": "timestamp", "nullable": True},
                    {"name": "completed_at", "type": "timestamp", "nullable": True},
                    {"name": "google_calendar_event_id", "type": "string", "nullable": True}
                ]
            },
            "data": appointments
        }
        
        return self._write_json(data, filename, compress)
    
    def export_users(
        self,
        users: List[Dict],
        filename: Optional[str] = None,
        compress: bool = True,
        include_sensitive: bool = False
    ) -> str:
        """
        Exporta usuários em formato JSON
        
        Args:
            users: Lista de usuários
            filename: Nome do arquivo
            compress: Se True, comprime com gzip
            include_sensitive: Se True, inclui dados sensíveis (senhas hasheadas)
        
        Returns:
            Caminho do arquivo gerado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"users_{timestamp}.json"
        
        # Remove dados sensíveis se necessário
        if not include_sensitive:
            users = [
                {k: v for k, v in user.items() if k not in ['senha']}
                for user in users
            ]
        
        data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "record_count": len(users),
                "data_type": "users",
                "version": "1.0",
                "includes_sensitive_data": include_sensitive
            },
            "schema": {
                "fields": [
                    {"name": "id", "type": "string", "nullable": False},
                    {"name": "email", "type": "string", "nullable": False},
                    {"name": "nome", "type": "string", "nullable": True},
                    {"name": "telefone", "type": "string", "nullable": True},
                    {"name": "morada", "type": "string", "nullable": True},
                    {"name": "role", "type": "string", "nullable": False},
                    {"name": "foto_perfil", "type": "string", "nullable": True},
                    {"name": "created_at", "type": "timestamp", "nullable": False},
                    {"name": "is_active", "type": "boolean", "nullable": False}
                ]
            },
            "data": users
        }
        
        return self._write_json(data, filename, compress)
    
    def export_attendance_records(
        self,
        records: List[Dict],
        filename: Optional[str] = None,
        compress: bool = True
    ) -> str:
        """
        Exporta fichas de atendimento
        
        Args:
            records: Lista de fichas
            filename: Nome do arquivo
            compress: Se True, comprime com gzip
        
        Returns:
            Caminho do arquivo gerado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"attendance_records_{timestamp}.json"
        
        data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "record_count": len(records),
                "data_type": "attendance_records",
                "version": "1.0"
            },
            "schema": {
                "fields": [
                    {"name": "id", "type": "string", "nullable": False},
                    {"name": "appointment_id", "type": "string", "nullable": False},
                    {"name": "cliente_id", "type": "string", "nullable": False},
                    {"name": "profissional_id", "type": "string", "nullable": False},
                    {"name": "procedimento", "type": "struct", "nullable": False},
                    {"name": "feedback", "type": "struct", "nullable": True},
                    {"name": "created_at", "type": "timestamp", "nullable": False}
                ]
            },
            "data": records
        }
        
        return self._write_json(data, filename, compress)
    
    def export_medical_history(
        self,
        histories: List[Dict],
        filename: Optional[str] = None,
        compress: bool = True
    ) -> str:
        """
        Exporta históricos médicos
        
        Args:
            histories: Lista de históricos
            filename: Nome do arquivo
            compress: Se True, comprime com gzip
        
        Returns:
            Caminho do arquivo gerado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"medical_history_{timestamp}.json"
        
        data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "record_count": len(histories),
                "data_type": "medical_history",
                "version": "1.0"
            },
            "schema": {
                "fields": [
                    {"name": "id", "type": "string", "nullable": False},
                    {"name": "cliente_id", "type": "string", "nullable": False},
                    {"name": "usa_medicamentos", "type": "boolean", "nullable": False},
                    {"name": "medicamentos", "type": "string", "nullable": True},
                    {"name": "alergias", "type": "string", "nullable": True},
                    {"name": "tratamentos_anteriores", "type": "array<string>", "nullable": True},
                    {"name": "banho_piscina_frequente", "type": "boolean", "nullable": False},
                    {"name": "created_at", "type": "timestamp", "nullable": False}
                ]
            },
            "data": histories
        }
        
        return self._write_json(data, filename, compress)
    
    def export_all(
        self,
        db_instance,
        compress: bool = True,
        include_sensitive: bool = False
    ) -> Dict[str, str]:
        """
        Exporta todos os dados do sistema
        
        Args:
            db_instance: Instância do database
            compress: Se True, comprime arquivos
            include_sensitive: Se True, inclui dados sensíveis
        
        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        exports = {}
        
        # Usuários
        users = db_instance.get_all_users()
        exports['users'] = self.export_users(
            users,
            f"users_{timestamp}.json",
            compress,
            include_sensitive
        )
        
        # Agendamentos
        appointments = db_instance.get_all_appointments()
        exports['appointments'] = self.export_appointments(
            appointments,
            f"appointments_{timestamp}.json",
            compress
        )
        
        # Fichas de atendimento
        records = db_instance._read_file("attendance_records")
        exports['attendance_records'] = self.export_attendance_records(
            records,
            f"attendance_records_{timestamp}.json",
            compress
        )
        
        # Histórico médico
        histories = db_instance._read_file("medical_history")
        exports['medical_history'] = self.export_medical_history(
            histories,
            f"medical_history_{timestamp}.json",
            compress
        )
        
        # Profissionais
        professionals = db_instance.get_all_professionals()
        exports['professionals'] = self.export_generic(
            professionals,
            "professionals",
            f"professionals_{timestamp}.json",
            compress
        )
        
        # Testes de mecha
        strand_tests = db_instance._read_file("strand_tests")
        exports['strand_tests'] = self.export_generic(
            strand_tests,
            "strand_tests",
            f"strand_tests_{timestamp}.json",
            compress
        )
        
        # Consultas
        consultations = db_instance._read_file("consultations")
        exports['consultations'] = self.export_generic(
            consultations,
            "consultations",
            f"consultations_{timestamp}.json",
            compress
        )
        
        return exports
    
    def export_generic(
        self,
        data: List[Dict],
        data_type: str,
        filename: str,
        compress: bool = True
    ) -> str:
        """
        Exportação genérica de dados
        
        Args:
            data: Lista de dados
            data_type: Tipo de dados
            filename: Nome do arquivo
            compress: Se True, comprime
        
        Returns:
            Caminho do arquivo gerado
        """
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "record_count": len(data),
                "data_type": data_type,
                "version": "1.0"
            },
            "data": data
        }
        
        return self._write_json(export_data, filename, compress)
    
    def _write_json(
        self,
        data: Dict,
        filename: str,
        compress: bool
    ) -> str:
        """
        Escreve dados JSON em arquivo
        
        Args:
            data: Dados a escrever
            filename: Nome do arquivo
            compress: Se True, comprime com gzip
        
        Returns:
            Caminho do arquivo gerado
        """
        filepath = os.path.join(self.export_dir, filename)
        
        if compress:
            filepath += '.gz'
            with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Exportado: {filepath}")
        return filepath
    
    def create_databricks_notebook(
        self,
        exports: Dict[str, str],
        notebook_path: Optional[str] = None
    ) -> str:
        """
        Cria notebook Databricks para importar os dados
        
        Args:
            exports: Dicionário com caminhos dos exports
            notebook_path: Caminho para salvar o notebook
        
        Returns:
            Caminho do notebook gerado
        """
        if not notebook_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            notebook_path = os.path.join(
                self.export_dir,
                f"import_notebook_{timestamp}.py"
            )
        
        notebook_content = f"""# Databricks notebook source
# MAGIC %md
# MAGIC # Importação de Dados - Salão IA
# MAGIC 
# MAGIC Notebook para importar dados do sistema Salão IA para Databricks
# MAGIC 
# MAGIC **Data de Geração:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuração

# COMMAND ----------

from pyspark.sql.types import *
from pyspark.sql.functions import *
import json

# Caminho base dos arquivos
base_path = "/FileStore/salao-ia/"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Importar Usuários

# COMMAND ----------

# Schema para usuários
users_schema = StructType([
    StructField("id", StringType(), False),
    StructField("email", StringType(), False),
    StructField("nome", StringType(), True),
    StructField("telefone", StringType(), True),
    StructField("morada", StringType(), True),
    StructField("role", StringType(), False),
    StructField("foto_perfil", StringType(), True),
    StructField("created_at", TimestampType(), False),
    StructField("is_active", BooleanType(), False)
])

# Lê arquivo JSON
users_df = spark.read.json(base_path + "users_*.json.gz")
users_data_df = users_df.select(explode("data").alias("user")).select("user.*")

# Salva como Delta Table
users_data_df.write.format("delta").mode("overwrite").saveAsTable("salao_ia.users")

print(f"✅ Usuários importados: {{users_data_df.count()}} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Importar Agendamentos

# COMMAND ----------

# Schema para agendamentos
appointments_schema = StructType([
    StructField("id", StringType(), False),
    StructField("cliente_id", StringType(), False),
    StructField("profissional_id", StringType(), False),
    StructField("data_hora", TimestampType(), False),
    StructField("servicos", ArrayType(StructType([
        StructField("tipo", StringType()),
        StructField("descricao", StringType()),
        StructField("duracao_estimada", IntegerType())
    ]))),
    StructField("status", StringType(), False),
    StructField("usar_ia", BooleanType(), True),
    StructField("created_at", TimestampType(), False)
])

appointments_df = spark.read.json(base_path + "appointments_*.json.gz")
appointments_data_df = appointments_df.select(explode("data").alias("apt")).select("apt.*")

appointments_data_df.write.format("delta").mode("overwrite").saveAsTable("salao_ia.appointments")

print(f"✅ Agendamentos importados: {{appointments_data_df.count()}} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Importar Fichas de Atendimento

# COMMAND ----------

records_df = spark.read.json(base_path + "attendance_records_*.json.gz")
records_data_df = records_df.select(explode("data").alias("record")).select("record.*")

records_data_df.write.format("delta").mode("overwrite").saveAsTable("salao_ia.attendance_records")

print(f"✅ Fichas importadas: {{records_data_df.count()}} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Importar Histórico Médico

# COMMAND ----------

medical_df = spark.read.json(base_path + "medical_history_*.json.gz")
medical_data_df = medical_df.select(explode("data").alias("history")).select("history.*")

medical_data_df.write.format("delta").mode("overwrite").saveAsTable("salao_ia.medical_history")

print(f"✅ Históricos médicos importados: {{medical_data_df.count()}} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Análises Básicas

# COMMAND ----------

# Total de agendamentos por status
display(
    spark.table("salao_ia.appointments")
    .groupBy("status")
    .count()
    .orderBy(desc("count"))
)

# COMMAND ----------

# Agendamentos por profissional
display(
    spark.table("salao_ia.appointments")
    .groupBy("profissional_id")
    .count()
    .orderBy(desc("count"))
)

# COMMAND ----------

# Taxa de uso de IA
ia_stats = spark.table("salao_ia.appointments").agg(
    count("*").alias("total"),
    sum(when(col("usar_ia") == True, 1).otherwise(0)).alias("com_ia")
)

display(ia_stats.withColumn("taxa_uso_ia", round(col("com_ia") / col("total") * 100, 2)))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Visualizações

# COMMAND ----------

# Agendamentos por dia da semana
display(
    spark.table("salao_ia.appointments")
    .withColumn("dia_semana", date_format("data_hora", "EEEE"))
    .groupBy("dia_semana")
    .count()
    .orderBy("count")
)

# COMMAND ----------

# Satisfação dos clientes
display(
    spark.table("salao_ia.attendance_records")
    .select("feedback.satisfacao")
    .groupBy("satisfacao")
    .count()
    .orderBy("satisfacao")
)
"""
        
        with open(notebook_path, 'w', encoding='utf-8') as f:
            f.write(notebook_content)
        
        print(f"✅ Notebook Databricks criado: {notebook_path}")
        return notebook_path


# ============================================================
# FUNÇÃO AUXILIAR
# ============================================================

def schedule_daily_export(
    db_instance,
    exporter: DatabricksExporter,
    hour: int = 2
):
    """
    Agenda exportação diária automática
    
    Args:
        db_instance: Instância do database
        exporter: Instância do exportador
        hour: Hora para executar (padrão: 2h da manhã)
    """
    import schedule
    import time
    
    def job():
        print(f"🔄 Iniciando exportação diária: {datetime.now()}")
        exports = exporter.export_all(db_instance, compress=True)
        print(f"✅ Exportação concluída: {len(exports)} arquivos gerados")
    
    schedule.every().day.at(f"{hour:02d}:00").do(job)
    
    print(f"📅 Exportação diária agendada para {hour}:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


# ============================================================
# EXEMPLO DE USO
# ============================================================

if __name__ == "__main__":
    from app.database import db
    
    # Inicializa exportador
    exporter = DatabricksExporter()
    
    # Exporta todos os dados
    print("🚀 Iniciando exportação...")
    exports = exporter.export_all(db, compress=True, include_sensitive=False)
    
    print(f"\n✅ Exportação concluída! {len(exports)} arquivos gerados:")
    for data_type, filepath in exports.items():
        size = os.path.getsize(filepath) / 1024  # KB
        print(f"  • {data_type}: {filepath} ({size:.2f} KB)")
    
    # Cria notebook Databricks
    notebook = exporter.create_databricks_notebook(exports)
    print(f"\n📓 Notebook Databricks: {notebook}")

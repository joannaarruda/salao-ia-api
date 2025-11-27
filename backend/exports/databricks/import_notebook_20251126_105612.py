# Databricks notebook source
# MAGIC %md
# MAGIC # Importação de Dados - Salão IA
# MAGIC 
# MAGIC Notebook para importar dados do sistema Salão IA para Databricks
# MAGIC 
# MAGIC **Data de Geração:** 2025-11-26 10:56:12

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

print(f"✅ Usuários importados: {users_data_df.count()} registros")

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

print(f"✅ Agendamentos importados: {appointments_data_df.count()} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Importar Fichas de Atendimento

# COMMAND ----------

records_df = spark.read.json(base_path + "attendance_records_*.json.gz")
records_data_df = records_df.select(explode("data").alias("record")).select("record.*")

records_data_df.write.format("delta").mode("overwrite").saveAsTable("salao_ia.attendance_records")

print(f"✅ Fichas importadas: {records_data_df.count()} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Importar Histórico Médico

# COMMAND ----------

medical_df = spark.read.json(base_path + "medical_history_*.json.gz")
medical_data_df = medical_df.select(explode("data").alias("history")).select("history.*")

medical_data_df.write.format("delta").mode("overwrite").saveAsTable("salao_ia.medical_history")

print(f"✅ Históricos médicos importados: {medical_data_df.count()} registros")

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

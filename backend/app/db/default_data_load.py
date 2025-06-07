import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


column_mapping = {
    "REF_DATE": "ref_date",
    "TARGET": "target",
    "VAR2": "sexo",
    "IDADE": "idade",
    "VAR4": "flag_obito",
    "VAR5": "uf",
    "VAR8": "classe_social"
}

cols = ["ref_date", "target", "sexo", "idade", "flag_obito", "uf", "classe_social"]
df = pd.read_csv(
    "https://github.com/Neurolake/challenge-data-scientist/raw/refs/heads/main/datasets/credit_01/train.gz",
    usecols=list(column_mapping.keys()),
    parse_dates=["REF_DATE"],
    dtype={
        "target": "int8",
        "idade": "int8",
        "flag_obito": "str",
        "uf": "str",
        "classe_social": "str",
        "sexo": "str"
    },
    encoding='utf-8',
)

df = df.rename(columns=column_mapping)

df["uf"] = df["uf"].str.strip().str.upper()
df["classe_social"] = df["classe_social"].str.strip()
df["sexo"] = df["sexo"].str.strip().str.upper()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///clientes.db")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS clientes (
                ref_date DATE,
                target INTEGER,
                sexo CHAR(1),
                idade INTEGER,
                flag_obito CHAR(1),
                uf CHAR(2),
                classe_social CHAR(1)
            );
        """))
        conn.commit()
        
        df.to_sql(
            name="clientes",
            con=conn,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=200
        )

except Exception as e:
    print(f"An error occurred: {e}")

print(f"Successfully loaded {len(df)} records!")

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clientes"))
        count = result.scalar()
        print(f"Total records in the database: {count}")

        result = conn.execute(text("SELECT * FROM clientes LIMIT 5"))
        for row in result:
            print(row)
except Exception as e:
    print(f"An error occurred while counting records: {e}")

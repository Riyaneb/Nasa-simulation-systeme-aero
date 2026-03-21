import pandas as pd
import sqlite3

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")

df = pd.read_sql("SELECT * FROM Train",DataBase)

df["cycle max"] = df.groupby(["unit number","file origin"])["time, in cycles"].transform("max")
df["RUL"] = df["cycle max"] - df["time, in cycles"]
df = df.drop("cycle max",axis=1)

df.to_sql(name="Train",con=DataBase,if_exists="replace",index=False)

DataBase.close()
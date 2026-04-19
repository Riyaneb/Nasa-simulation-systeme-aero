import pandas as pd
import sqlite3
from sklearn.model_selection import GroupShuffleSplit

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")

df = pd.read_sql("""SELECT * FROM Train_Normalisé_FD001 ORDER BY "unit number" """,DataBase)

a = GroupShuffleSplit(test_size = 0.2,random_state=67) # On prend 80% des moteurs qui serviront à entrainer le modèle et 20% pour les données qu'il va test 
train_i, val_i = next(a.split(df, groups=df["unit number"])) #On recupere les index melangés

liste_moteur_train = list(df.iloc[train_i]["unit number"].unique())
liste_moteur_val = list(df.iloc[val_i]["unit number"].unique())

df2 = pd.DataFrame({"unit number" : liste_moteur_train + liste_moteur_val, "split" : ["train"] * len(liste_moteur_train) + ["validation"] * len(liste_moteur_val)})

df2.to_sql(name="split_FD001", con=DataBase, if_exists="replace", index=False)

DataBase.close()
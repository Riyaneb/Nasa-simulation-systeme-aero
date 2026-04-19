import pandas as pd
import sqlite3
from sklearn.preprocessing import StandardScaler
import joblib
import os

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")

df = pd.read_sql("SELECT * FROM Train_clean_FD001",DataBase)

colonne_base = ["unit number","time, in cycles","file origin","RUL"]

colonne_parametre = list(df.filter(like='operationnal').columns)

colonne_capteur = list(df.columns)

for element in colonne_base:
    colonne_capteur.remove(element)
for element in colonne_parametre:
    colonne_capteur.remove(element)

df = df.sort_values(["unit number","time, in cycles"],ascending=[True,True])

#Moyenne glissante :

moyenne_glissante = df.groupby('unit number')[colonne_capteur].rolling(window=15,min_periods=1).mean() #  pour chaque valeur d'un capteur associé à un moteur, je calcule ça moyenne à partir des 15 cycle d'avant et je le met dans la cellules i
moyenne_glissante.reset_index(level=0,drop=True,inplace=True) #enleve le multiindex
moyenne_glissante.rename(columns={element : element + " rm" for element in colonne_capteur},inplace=True)
print(moyenne_glissante)
print("\n\n")


#Ecart-type glissante :

ecart_glissante = df.groupby('unit number')[colonne_capteur].rolling(window=15,min_periods=1).std(ddof=0)
ecart_glissante.reset_index(level=0,drop=True,inplace=True)
ecart_glissante.rename(columns={element : element + " rs" for element in colonne_capteur},inplace=True)
print("\n\n")


df2 = pd.concat([df,moyenne_glissante,ecart_glissante],axis=1) #on colle les df

print(df2.shape)

# Là c'est facultatif pour un random forest mais obligatoire pour d'autre algorithme comme regression linéaire

scale = StandardScaler()
colonne_normaliser = list(df2.columns)
for element in colonne_base:
    colonne_normaliser.remove(element)

df2[colonne_normaliser] = scale.fit_transform(df2[colonne_normaliser])
print(df2)
os.makedirs("artifacts", exist_ok=True)
joblib.dump(scale, "artifacts/scaler_FD001.joblib")

df2.to_sql(name="Train_Normalisé_FD001",con=DataBase,if_exists="replace",index=False)

DataBase.close()
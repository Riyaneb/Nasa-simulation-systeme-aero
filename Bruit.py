import pandas as pd
import sqlite3

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")

df = pd.read_sql("SELECT * FROM Train_clean_FD001",DataBase)

colonne_base = ["unit number","time, in cycles","file origin","RUL"]

colonne_parametre = []
for i in range(1,4):
    colonne_parametre.append(f"operationnal setting {i}")

colonne_capteur = list(df.columns)

for element in colonne_base:
    colonne_capteur.remove(element)
for element in colonne_parametre:
    colonne_capteur.remove(element)

df = df.sort_values(["unit number","time, in cycles"],ascending=[True,True])

#Moyenne glissante :

moyenne_glissante = df.groupby('unit number')[colonne_capteur].rolling(window=15,min_periods=1).mean() #  pour chaque valeur d'un capteur associé à un moteur, je calcule ça moyenne à partir des 15 cycle d'avant et je le met dans la cellules i
moyenne_glissante.reset_index(level=0,drop=True,inplace=True) #enleve le multiindex
print(moyenne_glissante)
df_moyenne_glissante = df.copy()
df_moyenne_glissante[colonne_capteur] = moyenne_glissante
df_moyenne_glissante.rename(columns={element : element + " rm" for element in colonne_capteur},inplace=True)
print("\n\n")
print(df_moyenne_glissante)

#Ecart-type glissante :

ecart_glissante = df.groupby('unit number')[colonne_capteur].rolling(window=15,min_periods=1).std(ddof=0)
ecart_glissante.reset_index(level=0,drop=True,inplace=True)
df_ecart_glissante = df.copy()
df_ecart_glissante[colonne_capteur] = ecart_glissante
df_ecart_glissante.rename(columns={element : element + " rs" for element in colonne_capteur},inplace=True)
print("\n\n")
print(df_ecart_glissante) 

df2 = pd.merge(df,df_moyenne_glissante,on=["unit number","time, in cycles"],how="inner") #on colle les df en faisant attention a ce qu'elles s'imbriquent bien
df2 = pd.merge(df,df_ecart_glissante,on=["unit number","time, in cycles"],how="inner")

print("\n,\n")
print(df2.shape)

# La c'est facultatif pour un random forest mais obligatoire pour d'autre algorithme comme regression linéaire


DataBase.close()
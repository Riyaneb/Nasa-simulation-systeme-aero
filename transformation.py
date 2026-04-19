import pandas as pd
import sqlite3

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")

df = pd.read_sql("SELECT * FROM Train",DataBase)

#Capteurs Morts :

colonne_capteurs = [f"sensor measurement {i}" for i in range(1,22)] 
variance = df.groupby("file origin")[colonne_capteurs].var() #on crée des sous groupes FD001-4 et on calcule la variances de chaque capteur dans chaque fichier

print("\nVariance des capteurs : \n")
print(variance)

variance_FD001 = variance.loc["FD001"]
liste_capteur_mort = list(variance_FD001[variance_FD001 < 1e-4].index) #on fait une liste des capteurs morts

print("\nCapteurs morts du fichier FD001 : \n")
print(liste_capteur_mort)

variance_capteur_utile_FD001 = variance_FD001.drop(index=liste_capteur_mort) #on enleve les capteurs morts des variances de FD001

print("\nCapteurs utiles du fichier FD001 : \n")
print(variance_capteur_utile_FD001)

#Paramètre inutile :

colonne_parametre = []
for i in range(1,4):
    colonne_parametre.append(f"operationnal setting {i}")

variance2 = df.groupby("file origin")[colonne_parametre].var()
variance_2_FD001 = variance2.loc["FD001"]
liste_parametre_mort = list(variance_2_FD001[variance_2_FD001 == 0].index)

df_fd001 = df[df["file origin"] == "FD001"].copy() 
df_fd001 = df_fd001.drop(columns=liste_capteur_mort) #on garde que les capteurs utiles du fichier FD001 et on retire les capteurs morts
df_fd001 = df_fd001.drop(columns=liste_parametre_mort) #on garde que les paramètres utiles du fichier FD001 et on retire les paramètres constant
print(df_fd001)
df_fd001.to_sql(name="Train_clean_FD001",con=DataBase,if_exists="replace",index=False)

#Faudra faire ça avec les autres fichiers train et peut etre avec les Test aussi


DataBase.close()
import sqlite3
import pandas as pd

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")
curseur = DataBase.cursor()
curseur.execute("""SELECT COUNT(*), COUNT(DISTINCT "unit number" || "file origin") FROM Train """) 
#En gros le premier COUNT compte le nombre de ligne total alors que le deuxième compte le nombre de moteur different (distinct car le moteur 1 dans fichier 1 n'est pas égale a moteur 1 dans fichier 2)
print("Affiche (Nombre de ligne totale,Nombre de moteur different) :")
print(curseur.fetchall())
df = pd.read_sql("SELECT * FROM Train",DataBase)
print("Affiche les informations de la colonne RUL :")
print(df["RUL"].describe())
print("Affiche qu'une valeur RUL apparait : ")
print(df["RUL"].value_counts())
DataBase.close()

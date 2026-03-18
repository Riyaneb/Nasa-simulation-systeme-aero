import pandas as pd
import sqlite3

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")

nom_colonne = ["unit number","time, in cycles"]
for i in range(1,4):
    nom_colonne.append(f"operationnal setting {i}")
for i in range(1,22):
    nom_colonne.append(f"sensor measurement {i}")

dico = {}

for key in nom_colonne:
    dico[key] = []

TableauTest = pd.DataFrame(dico)


TableauShape = TableauTest.shape
for i in range(1,5):
    df = pd.read_table(f"CMAPSSData/test_FD00{i}.txt",sep=r'\s+',header=None)
    fileShape = df.shape
    if (fileShape[1] > 26):
        df = df.drop(df.columns[26:fileShape[1]],axis=1,inplace=True)
        fileShape = df.shape

    if(fileShape[1] != TableauShape[1]):
        print(f"Le fichier test_FD00{i} fait {fileShape[1]} colonne alors que TableauTest fait {TableauShape[1]} colonnes")
    else:
        df.columns = TableauTest.columns
        TableauTest = pd.concat([TableauTest,df],ignore_index=True)

TableauTest.to_sql(name="Test",con=DataBase,if_exists="replace")

DataBase.close()




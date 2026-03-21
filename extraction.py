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

dico["file origin"] = []

TableauTest = pd.DataFrame(dico)
TableauTrain = pd.DataFrame(dico)


TableauShape = TableauTest.shape
TableauTrainShape = TableauTrain.shape

for i in range(1,5):
    df = pd.read_table(f"CMAPSSData/test_FD00{i}.txt",sep=r'\s+',header=None,names=nom_colonne)
    fileShape = df.shape
    if (fileShape[1] > 26):
        df = df.drop(df.columns[26:fileShape[1]],axis=1)
        fileShape = df.shape
    df["file origin"] = [f"FD00{i}" for j in range(fileShape[0])] 

    fileShape = df.shape
    if(fileShape[1] != TableauShape[1]):
        print(f"Le fichier test_FD00{i} fait {fileShape[1]} colonne alors que TableauTest fait {TableauShape[1]} colonnes")
    else:
        print(f"test_FD00{i} remplit et ses colonnes sont : {df.columns}")
        TableauTest = pd.concat([TableauTest,df],ignore_index=True)

for i in range(1,5):
    df = pd.read_table(f"CMAPSSData/train_FD00{i}.txt",sep=r'\s+',header=None,names=nom_colonne)
    fileShape = df.shape
    if (fileShape[1] > 26):
        df = df.drop(df.columns[26:fileShape[1]],axis=1)
        fileShape = df.shape
    df["file origin"] = [f"FD00{i}" for j in range(fileShape[0])]

    fileShape = df.shape
    if(fileShape[1] != TableauTrainShape[1]):
        print(f"Le fichier train_FD00{i} fait {fileShape[1]} colonne alors que TableauTrain fait {TableauTrainShape[1]} colonnes")
    else:
        print(f"train_FD00{i} remplit et ses colonnes sont : {df.columns}")
        TableauTrain = pd.concat([TableauTrain,df],ignore_index=True)
        

TableauTest.to_sql(name="Test",con=DataBase,if_exists="replace",index=False)
TableauTrain.to_sql(name="Train",con=DataBase,if_exists="replace",index=False)

DataBase.close()




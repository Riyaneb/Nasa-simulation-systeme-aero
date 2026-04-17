import pandas as pd
import sqlite3

def chargerFichier(type,numero,nom_colonne):
    if type not in ('train','test'):
        print("Problème avec le type du fichier dans la fonction chargerFichier")
        exit()
    elif numero not in (1,2,3,4):
        print("probleme avec le numero dans la focntion chargerFichier")
        exit()
    df = pd.read_table(f"CMAPSSData/{type}_FD00{numero}.txt",sep=r'\s+',header=None,names=nom_colonne)
    fileShape = df.shape
    if (fileShape[1] > 26):
        df = df.drop(df.columns[26:fileShape[1]],axis=1)
        fileShape = df.shape
    df["file origin"] = [f"FD00{numero}" for j in range(fileShape[0])]
    return df
    


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


listeTest = []
listeTrain = []

for i in range(1,5):
    listeTrain.append(chargerFichier('train',i,nom_colonne))
    listeTest.append(chargerFichier('test',i,nom_colonne))

TableauTest = pd.concat(listeTest,ignore_index=True)
TableauTrain = pd.concat(listeTrain,ignore_index=True)
        

TableauTest.to_sql(name="Test",con=DataBase,if_exists="replace",index=False)
TableauTrain.to_sql(name="Train",con=DataBase,if_exists="replace",index=False)

DataBase.close()




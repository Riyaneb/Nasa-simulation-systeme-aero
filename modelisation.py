import pandas as pd
import sqlite3
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import matplotlib.pyplot as plt

DataBase = sqlite3.connect("Base_de_donnée_des_test.db")
df = pd.read_sql("SELECT * FROM Train_Normalisé_FD001",DataBase)
split = pd.read_sql("SELECT * FROM split_FD001",DataBase)

liste_moteur_train = list(split[split["split"] == "train"]["unit number"])
liste_moteur_val = list(split[split["split"] == "validation"]["unit number"])

df_train = df[df["unit number"].isin(liste_moteur_train)]
df_val = df[df["unit number"].isin(liste_moteur_val)]

suppr = ["unit number", "time, in cycles", "file origin", "RUL"]

x_train = df_train.drop(columns=suppr)
y_train = df_train["RUL"]

x_val = df_val.drop(columns=suppr)
y_val = df_val["RUL"]

#le but du modèle c'est de prédire y_train à partir des donnée de x_train
modele = LinearRegression()
modele.fit(x_train,y_train)
prediction_val_y = modele.predict(x_val)
prediction_val_y = np.clip(prediction_val_y, 0, 125)

rmse = np.sqrt(mean_squared_error(y_val, prediction_val_y))
mae = mean_absolute_error(y_val, prediction_val_y)
print(f"RMSE val : {rmse:.2f}")
print(f"MAE val  : {mae:.2f}")

plt.scatter(y_val, prediction_val_y, s=10)
plt.plot([0, 125], [0, 125], 'r--', label="Prédiction parfaite")
plt.xlabel("RUL réelle")
plt.ylabel("RUL prédite")
plt.title(f"Régression linéaire avec RMSE = {rmse:.2f} et MAE = {mae:.2f}")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("images/regression_lineaire.png", bbox_inches="tight")
plt.show()

DataBase.close()
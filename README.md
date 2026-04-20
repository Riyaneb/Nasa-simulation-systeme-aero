# Maintenance prédictive sur turboréacteurs — Dataset NASA CMAPSS (FD001)

Projet de prédiction de la durée de vie résiduelle (Remaining Useful Life, RUL) de turboréacteurs à partir du dataset CMAPSS FD001 publié par la NASA (Saxena et al., PHM'08). L'objectif est de construire un pipeline complet de machine learning, de l'extraction des données brutes jusqu'à un premier modèle prédictif.

## Contexte

Le dataset CMAPSS est un simulateur physique de turboréacteur qui produit des trajectoires de dégradation jusqu'à la panne. Chaque moteur est suivi par 21 capteurs (températures, pressions, vitesses de rotation) sur plusieurs centaines de cycles, avec une dégradation exponentielle injectée sur le module HPC (High Pressure Compressor). Le défi consiste à prédire, à partir d'une fenêtre de mesures, combien de cycles il reste au moteur avant la panne.

Le travail se concentre sur le jeu **FD001** : 100 moteurs d'entraînement, une seule condition opérationnelle (sea level), un seul mode de défaillance (dégradation HPC).

## Stack technique

- **Python 3.8+**
- **Pandas** : manipulation des données
- **SQLite** : stockage des fonnées
- **scikit-learn** : modèle baseline
- **matplotlib** : visualisations

## Architecture du pipeline

Le pipeline est organisé en scripts Python séquentiels. Chaque script produit une table SQLite consommée par le script suivant, ce qui permet de rejouer chaque étape indépendamment.

```
extraction.py      → Train, Test                       (tables brutes)
Traitement.py      → Train (+ colonne RUL)             (RUL limitée à 125)
transformation.py  → Train_clean_FD001                 (capteurs morts retirés)
Bruit.py           → Train_Normalisé_FD001             (features + normalisation)
melange.py         → split_FD001                       (séparation train/validation)
modelisation.py    → modèle régression linéaire      (RMSE + MAE)
```

## Détail des étapes

### 1. Extraction (`extraction.py`)

Lecture des 4 fichiers `train_FD00X.txt` et `test_FD00X.txt` de la NASA, concaténation en deux grandes tables `Train` et `Test` dans une base SQLite. Une colonne `file origin` est ajoutée à chaque ligne pour identifier le dataset d'origine (FD001 à FD004).

### 2. Calcul de la target RUL (`Traitement.py`)

La RUL est calculée sur la table Train par `cycle_max − cycle_actuel`, groupé par moteur (`unit number` + `file origin`). Le calcul est vectorisé via `groupby().transform("max")`.

La RUL est ensuite **plafonnée à 125** via `.clip(upper=125)`. Ca vient du fait que la RUL des moteurs bien avant la fin de vie n'est pas prédictible à partir des capteurs : le bruit de mesure y domine le signal de dégradation. Plafonner à 125 évite au modèle de gaspiller sa capacité à distinguer des états indistinguables.

### 3. Sélection des features (`transformation.py`)

**Capteurs morts** : calcul de la variance de chaque capteur par `file origin`, identification des capteurs à variance quasi-nulle (seuil `1e-4`). Sur FD001, 7 capteurs sont identifiés comme inutiles et retirés (sensors 1, 5, 6, 10, 16, 18, 19).

**Paramètres opérationnels constants** : même logique appliquée aux 3 paramètres opérationnels. Sur FD001, `operationnal setting 3` est constant (valeur 100.0 partout).

Résultat : table `Train_clean_FD001` avec 20 631 lignes × 20 colonnes (14 capteurs vivants + 2 paramètres utiles + méta-colonnes + RUL).

### 4. Feature engineering et normalisation (`Bruit.py`)

Deux éléments supplémentaires sont ajoutés :

- **Moyennes Glissante sur 15 cycles** (`_rm`) : Débruite le signal et révèle la tendance de dégradation.
- **Ecart-type Glissante sur 15 cycles** (`_rs`) : Capture la volatilité locale. En mécanique, la volatilité est un **précurseur de défaillance**.

Ces éléments sont calculées **par moteur** (`groupby('unit number')`). Le paramètre `min_periods=1` évite d'avoir des NaN en début de trajectoire (avec `min_periods=15`, on perdrait 14 lignes par moteur, soit 1 400 lignes sur 20 631). Le `ddof=0` dans le rolling std évite les NaN au cycle 1 (écart-type d'une seule observation).

**Normalisation** : `StandardScaler` de scikit-learn, fitté uniquement sur Train, appliqué à toutes les features sauf les méta-colonnes et la RUL. Le scaler est sérialisé dans `artifacts/scaler_FD001.joblib` pour pouvoir être réutilisé sur les données de test.

Résultat : table `Train_Normalisé_FD001` avec 20 631 lignes × 48 colonnes (14 capteurs normalisés + 14 rolling means + 14 rolling stds + 2 paramètres + 4 méta).

### 5. Split par moteur (`melange.py`)

Séparation du Train en train/validation **par moteur**.

Outil utilisé : `GroupShuffleSplit(test_size=0.2, random_state=67)` de scikit-learn, avec `groups=df["unit number"]`. Résultat : 80 moteurs en train, 20 moteurs en validation.

Le split est persisté dans une table SQLite `split_FD001` (100 lignes, 2 colonnes : `unit number`, `split`) pour que les étapes en aval l'utilisent sans avoir à le recalculer.

### 6. Baseline — régression linéaire (`modelisation.py`)

Régression linéaire sur l'ensemble des 44 features (14 capteurs bruts normalisés + 14 rolling means + 14 rolling stds + 2 paramètres). Entraînement sur les 80 moteurs de train, évaluation sur les 20 moteurs de validation.

Les prédictions sont limitées à `[0, 125]` après `predict()`. Le modèle peut prédire des RUL négatives ou supérieures à 125, la limitation borne les prédictions dans la plage réaliste.

**Résultats sur validation** :
- RMSE : **20.59** cycles
- MAE : **15.75** cycles

Ces chiffres servent de référence pour toute itération future. Un plot est sauvegardé dans `images/regression_lineaire.png`.

## Visualisations (`visualisation.ipynb`)

Notebook contenant les figures de présentation :

- **Évolution de capteurs bruts** pour un moteur.
- **Dégradation comparée** du capteur 11 sur 4 moteurs de durées de vie contrastées (moteurs 5, 6, 96, 98). Met en évidence la divergence des trajectoires en fin de vie.
- **Comparaison brut vs rolling mean** sur un moteur : illustre visuellement l'effet de lissage du feature engineering.
- **Corrélations capteurs / RUL** (Pearson) : identification a priori des capteurs les plus informatifs, cohérente avec la physique de la dégradation HPC.
- **Distribution de la RUL** avant et après la limitation : visualise l'impact du plafonnement à 125.

## Structure du projet

```
.
├── CMAPSSData/              # Données brutes NASA (train, test, RUL_FD00X.txt)
├── artifacts/               # Scaler sérialisés 
│   └── scaler_FD001.joblib
├── images/                  # Figures produites
├── Base_de_donnée_des_test.db  # Base SQLite centrale
├── extraction.py            # Étape 1 : ingestion
├── Traitement.py            # Étape 2 : calcul de la RUL
├── transformation.py        # Étape 3 : sélection de features
├── Bruit.py                 # Étape 4 : feature engineering + normalisation
├── melange.py               # Étape 5 : split train/validation par moteur
├── modelisation.py          # Étape 6 : Régression linéaire
├── verification.py          # Checks
├── visualisation.ipynb      # Figures
└── README.md
```
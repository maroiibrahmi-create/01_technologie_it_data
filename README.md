# Dashboard Support IT — Streamlit

Dashboard d'analyse des **800 tickets de support informatique** de l'exercice de formation
(janvier à août 2026).

Le projet répond aux 6 questions demandées dans la feuille **« Mode d'emploi »** du fichier Excel.

## 1. Contenu du projet

```text
support_dashboard/
├── app.py
├── requirements.txt
├── README.md
└── 01_Technologie_IT.xlsx   # à placer ici pour l'exécution locale
```

Les trois fichiers à rendre sont :

- `app.py`
- `requirements.txt`
- `README.md`

Le fichier Excel est la source de données et n'a pas besoin d'être intégré au code :
l'application peut soit le trouver localement sous `01_Technologie_IT.xlsx`, soit permettre
son import depuis la barre latérale.

## 2. Fonctionnalités

La première page répond directement aux questions :

1. **Types de demandes** les plus fréquents.
2. **Service** recevant le plus de tickets + délai médian de résolution.
3. **Part des tickets résolus dépassant le SLA**, avec comparaison par priorité.
4. **Temps de première réponse** selon le canal d'entrée.
5. **Évolution mensuelle** du volume et des dépassements SLA.
6. **Action opérationnelle proposée**, basée sur les chiffres.

Le dashboard contient également :

- 4 indicateurs clés ;
- plusieurs graphiques Matplotlib ;
- filtres par ville, service, canal, priorité, type, statut et période ;
- tableau des données filtrées ;
- téléchargement CSV des données filtrées.

## 3. Règle importante pour le SLA

Le fichier de consignes précise :

> SLA dépassé = Résolution (h) > Objectif SLA (h), uniquement sur les tickets résolus.

L'application respecte cette règle.

Les tickets **En cours** n'ont pas de durée de résolution et ne sont donc pas comptés
comme des dépassements SLA.

## 4. Résultats de référence avec les 800 tickets

Sans filtre :

- **800 tickets** au total ;
- **701 résolus** ;
- **99 en cours** ;
- **47,5 %** des tickets résolus dépassent l'objectif SLA.

Quelques résultats de référence :

| Question | Résultat |
|---|---|
| Type le plus fréquent | Logiciel — 199 tickets |
| Service avec le plus de tickets | Helpdesk — 358 tickets |
| Médiane de résolution du Helpdesk | 40,55 h |
| SLA dépassé — Critique | 54,1 % |
| SLA dépassé — Haute | 50,3 % |
| SLA dépassé — Normale | 45,4 % |
| Canal avec médiane de réponse la plus basse | Chat — 8,1 h |
| Canal avec médiane de réponse la plus haute | Téléphone — 9,55 h |
| Mois avec le plus de tickets | Avril — 118 tickets |

## 5. Installation locale

### Prérequis

Python 3.10 ou version plus récente recommandé.

### Installer les dépendances

Dans le dossier du projet :

```bash
pip install -r requirements.txt
```

### Lancer l'application

```bash
streamlit run app.py
```

Streamlit ouvre normalement l'application dans le navigateur.

## 6. Utilisation avec le fichier Excel

Placez :

```text
01_Technologie_IT.xlsx
```

dans le même dossier que `app.py`.

Vous pouvez aussi lancer l'application sans fichier local et importer le fichier Excel
directement depuis le bouton **Importer le fichier Excel** dans la barre latérale.

## 7. Publication sur Streamlit Community Cloud

1. Créez un dépôt GitHub.
2. Ajoutez :
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `01_Technologie_IT.xlsx` si vous souhaitez que les données soient intégrées au dépôt.
3. Ouvrez Streamlit Community Cloud.
4. Connectez votre compte GitHub.
5. Sélectionnez le dépôt.
6. Choisissez `app.py` comme fichier principal.
7. Lancez le déploiement.

Si le fichier Excel n'est pas ajouté au dépôt, utilisez simplement le bouton
**Importer le fichier Excel** après ouverture de l'application.

## 8. Technologies

- **Python**
- **Streamlit** — interface du dashboard
- **Pandas** — nettoyage, agrégation et calculs
- **Matplotlib** — visualisations
- **OpenPyXL** — lecture du fichier Excel `.xlsx`

## 9. Limites d'interprétation

Les graphiques présentent des relations descriptives. Par exemple, un canal avec un délai
médian de première réponse plus faible ne signifie pas que le canal est nécessairement la
cause de cette différence : priorité, type de demande, charge et autres facteurs peuvent
également intervenir.

Les données sont entièrement fictives et ont été créées pour un exercice de formation.

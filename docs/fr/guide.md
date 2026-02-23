# Guide d'utilisation -- AI Visual Inspection

## Presentation

Cette application permet l'inspection visuelle automatisee par intelligence
artificielle de PCB, microconnecteurs et assemblages de biocapteurs. Elle
detecte et classifie les defauts en temps reel, genere des statistiques et
assure la tracabilite reglementaire.

---

## Pages de l'application

### 1. Inspection en direct

La page principale permet d'analyser des images via trois sources :

- **Camera** : capture directe depuis la webcam via le navigateur.
- **Telechargement** : chargement d'un fichier image (PNG, JPG, BMP).
- **Image exemple** : selection parmi les images de demonstration placees
  dans le dossier `data/sample_images/`.

#### Fonctionnement

1. Selectionnez la source d'image.
2. Ajustez le seuil de confiance dans la barre laterale si necessaire.
3. L'analyse demarre automatiquement apres le chargement de l'image.
4. Les defauts detectes sont affiches avec des cadres de selection colores.
5. Cliquez sur **Enregistrer le resultat** pour sauvegarder dans le journal.

### 2. Tableau de bord

Le tableau de bord affiche les statistiques cumulees des inspections :

- Nombre total d'inspections et de defauts.
- Taux de defauts global.
- Repartition des defauts par categorie.
- Evolution dans le temps.
- Distribution des scores de confiance.

### 3. Tracabilite

Cette page est concue pour la conformite reglementaire :

- **FDA 21 CFR Part 11** : enregistrements electroniques avec horodatage.
- **ISO 13485** : tracabilite des inspections pour dispositifs medicaux.

Fonctionnalites :

- Filtrage par statut (CONFORME/NON CONFORME), date et operateur.
- Export CSV pour integration dans un systeme qualite.
- Generation de rapports PDF.

### 4. Guide

Cette page (celle que vous lisez).

---

## Configuration

### Seuil de confiance

Le curseur dans la barre laterale controle le seuil minimal de confiance.
Les detections en dessous de ce seuil sont ignorees.

- **Valeur recommandee** : 0.5 pour un modele personnalise.
- **En mode demo** : augmenter a 0.7 pour reduire les faux positifs.

### Mode demonstration

Si aucun modele personnalise n'est disponible dans `models/`, l'application
utilise un modele YOLO pretraine sur le dataset COCO. Les detections sont
alors mappees de maniere illustrative vers des categories de defauts PCB.

Un bandeau jaune indique que le mode demo est actif.

### Modele personnalise

Pour une detection reelle, consultez le fichier `models/README.md` qui
detaille la procedure d'entrainement et de deploiement d'un modele
specialise.

---

## Categories de defauts

| Categorie | Description |
|-----------|-------------|
| Vide de brasure | Cavite dans un joint de soudure |
| Composant manquant | Absence d'un composant attendu |
| Contamination | Particule ou residu sur la surface |
| Ecart dimensionnel | Dimension hors tolerance |
| Broche pliee | Broche de connecteur deformee |
| Corps etranger | Materiau non attendu sur l'assemblage |
| Rayure | Marque de surface |
| Desalignement | Composant mal positionne |

---

## Export et integration

### CSV

Le journal d'inspection est stocke dans `data/inspection_log.csv`. Il peut
etre exporte depuis la page Tracabilite et importe dans un systeme qualite
(SAP QM, Trackwise, MasterControl).

### PDF

Les rapports PDF sont generes avec reportlab (optionnel). Installez-le avec :

```
pip install reportlab
```

---

## Exigences techniques

- Python 3.10+
- Streamlit 1.40+
- Ultralytics (YOLOv8)
- OpenCV, Pillow, Plotly, pandas

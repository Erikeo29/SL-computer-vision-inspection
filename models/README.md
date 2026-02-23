# Modeles de detection / Detection models

## Modele pretraine (par defaut)

L'application utilise automatiquement `yolov8n.pt` (YOLO v8 nano pretraine
sur COCO) si aucun modele personnalise n'est disponible. Ce modele est
telecharge automatiquement par ultralytics au premier lancement.

En mode demonstration, les classes COCO sont mappees de maniere illustrative
vers des categories de defauts PCB.

## Modele personnalise

Pour une detection reelle de defauts, entrainer un modele YOLO sur un dataset
de defauts PCB/microconnecteurs et placer le fichier `.pt` ici.

### Etapes

1. Preparer un dataset annote au format YOLO (images + labels `.txt`).
2. Entrainer le modele :

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.train(
    data="path/to/data.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    name="pcb_defects",
)
```

3. Copier le fichier `best.pt` resultat dans ce repertoire et le renommer
   `pcb_defects.pt`.

4. Mettre a jour `config.yaml` si le nom du fichier est different :

```yaml
model:
  custom: "models/pcb_defects.pt"
```

### Categories attendues

Le fichier `data.yaml` du dataset doit definir les classes suivantes :

```yaml
names:
  0: solder_void
  1: missing_component
  2: contamination
  3: dimensional_deviation
  4: bent_pin
  5: foreign_material
  6: scratch
  7: misalignment
```

## Datasets publics recommandes

- [PCB Defect Detection (Kaggle)](https://www.kaggle.com/datasets)
- [DeepPCB](https://github.com/tangsanli5201/DeepPCB)
- [PCB-DATASET (Open Lab)](https://robotics.pkusz.edu.cn/resources/dataset/)

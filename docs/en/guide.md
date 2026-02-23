# User guide -- AI Visual Inspection

## Overview

This application enables automated AI-powered visual inspection of PCBs,
microconnectors and biosensor assemblies. It detects and classifies defects
in real time, generates statistics and ensures regulatory traceability.

---

## Application pages

### 1. Live inspection

The main page allows image analysis from three sources:

- **Camera**: direct capture from the browser webcam.
- **Upload**: image file upload (PNG, JPG, BMP).
- **Sample image**: selection from demo images placed in
  `data/sample_images/`.

#### How it works

1. Select the image source.
2. Adjust the confidence threshold in the sidebar if needed.
3. Analysis starts automatically after the image is loaded.
4. Detected defects are displayed with colored bounding boxes.
5. Click **Save result** to record in the inspection log.

### 2. Dashboard

The dashboard shows cumulative inspection statistics:

- Total number of inspections and defects.
- Overall defect rate.
- Defect distribution by category.
- Time-series evolution.
- Confidence score distribution.

### 3. Traceability

This page is designed for regulatory compliance:

- **FDA 21 CFR Part 11**: electronic records with timestamps.
- **ISO 13485**: inspection traceability for medical devices.

Features:

- Filtering by status (PASS/FAIL), date and operator.
- CSV export for integration into a quality system.
- PDF report generation.

### 4. Guide

This page (the one you are reading).

---

## Configuration

### Confidence threshold

The sidebar slider controls the minimum confidence threshold.
Detections below this threshold are discarded.

- **Recommended value**: 0.5 for a custom model.
- **In demo mode**: increase to 0.7 to reduce false positives.

### Demo mode

If no custom model is available in `models/`, the application uses a
YOLO model pretrained on the COCO dataset. Detections are then
illustratively mapped to PCB defect categories.

A yellow banner indicates that demo mode is active.

### Custom model

For real defect detection, see `models/README.md` for training and
deployment instructions.

---

## Defect categories

| Category | Description |
|----------|-------------|
| Solder void | Cavity in a solder joint |
| Missing component | Expected component absent |
| Contamination | Particle or residue on the surface |
| Dimensional deviation | Dimension out of tolerance |
| Bent pin | Deformed connector pin |
| Foreign material | Unexpected material on the assembly |
| Scratch | Surface mark |
| Misalignment | Mispositioned component |

---

## Export and integration

### CSV

The inspection log is stored in `data/inspection_log.csv`. It can be
exported from the Traceability page and imported into a quality system
(SAP QM, Trackwise, MasterControl).

### PDF

PDF reports are generated with reportlab (optional). Install with:

```
pip install reportlab
```

---

## Technical requirements

- Python 3.10+
- Streamlit 1.40+
- Ultralytics (YOLOv8)
- OpenCV, Pillow, Plotly, pandas

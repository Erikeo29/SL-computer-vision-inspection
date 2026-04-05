# SL-computer-vision-inspection

AI-powered visual inspection application for PCB and microconnector defect detection using YOLOv8.

## Features

- Real-time defect detection on uploaded images using a YOLOv8 model trained on PCB defects.
- Camera feed integration for live inspection workflows.
- Defect classification with confidence scores and bounding box overlay.
- Inspection traceability log with CSV export.
- Interactive dashboard with defect distribution and trend charts.
- Automated inspection report generation.
- Bilingual interface (FR/EN).

## Installation

```bash
git clone https://github.com/Erikeo29/SL-computer-vision-inspection.git
cd SL-computer-vision-inspection
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## License

MIT

# 📘 Genome‑wide CNV + BAF Plotter  
DRAGEN‑compatible multi‑sample visualization tool

This repository provides a lightweight, reproducible Python workflow for generating genome‑wide CNV + BAF plots directly from DRAGEN CNV VCF and DRAGEN BAF bedgraph files.

It supports batch processing of multiple samples using a simple list of sample directories, and produces clean, publication‑quality PNG figures.

Tested on Python 3.10.12.

## 🧬 Features
- ✔ Simple directory‑based input  
- ✔ Genome‑wide CNV visualization from DRAGEN *.cnv.vcf.gz  
- ✔ Genome‑wide BAF visualization from DRAGEN *.baf.bedgraph.gz  
- ✔ Batch processing for large cohorts  

## ⚡ Quick Start

    pip install -r requirements.txt
    python scripts/batch_plot.py examples/sample_dirs.txt output/

## 📁 Repository Structure

    cnv-baf-plotter/
    │
    ├── scripts/
    │   ├── plot_cnv_baf.py      # Core CNV + BAF plotting logic
    │   └── batch_plot.py        # Multi-sample runner
    │
    ├── examples/
    │   ├── sample_dirs.txt      # Example input list
    │   └── example_plots/       # Example output images
    │
    ├── requirements.txt
    └── README.md

## 📥 Input Requirements

Each sample directory must contain:

- <sample>.cnv.vcf.gz  
- <sample>.baf.bedgraph.gz  

The tool automatically supports:

- <sample>.baf.bedgraph.gz (germline workflows)  
- <sample>.tumor.baf.bedgraph.gz (tumor/normal workflows)  

## 📄 Example sample_dirs.txt

One sample directory per line:

- /path/to/project/Run1/Sample1/  
- /path/to/project/Run1/Sample2/  
- /path/to/project/Run2/Sample3/  

Absolute paths are recommended, but relative paths work if run consistently.

## ▶️ How to Run

1. Install dependencies

        pip install -r requirements.txt

2. Run batch plotting

        python scripts/batch_plot.py examples/sample_dirs.txt output_plots/

This generates:

- output_plots/Sample1_CNV_BAF.png  
- output_plots/Sample2_CNV_BAF.png  
- output_plots/Sample3_CNV_BAF.png  

## 🖼 Example Output

- examples/example_plots/Sample1_CNV_BAF.png
- examples/example_plots/Sample2_CNV_BAF.png

## 🧠 How It Works

CNV Track  
- Reads absolute copy number from DRAGEN CNV VCF  
- Converts to log₂(CN/2) for array‑style visualization  
- Plots genome‑wide CNV segments  
- Uses alternating chromosome shading  
- Highlights gains (red), losses (blue), neutral (grey)  

BAF Track  
- Reads BAF from DRAGEN bedgraph  
- Downsamples for speed and clarity  
- Plots grey BAF dots across the genome  
- Shares the same genome‑wide coordinate system as CNV  

## 📜 License

This project is licensed under the MIT License.  
See the LICENSE file for details.

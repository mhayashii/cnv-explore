# 📘 Genome‑wide CNV + BAF Plotter  
DRAGEN‑compatible multi‑sample visualization tool

This repository provides a lightweight, reproducible Python workflow for generating genome‑wide CNV + BAF plots directly from DRAGEN CNV VCF and DRAGEN BAF files.

It supports batch processing of multiple samples using a simple list of sample directories, and produces clean, publication‑quality PNG figures.

Tested on Python 3.10.12.

## 🧬 Features
- ✔ Simple directory‑based input  
- ✔ Genome‑wide CNV visualization from DRAGEN *.cnv.vcf.gz  
- ✔ BAF visualization from:
  - *.tumor.baf.bedgraph.gz
  - *.baf.bedgraph.gz
  - *.hard-filtered.baf.bw (automatic fallback)
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

The tool automatically detects the best available BAF file in this priority order:

1. <sample>.tumor.baf.bedgraph.gz (tumor/normal workflows)
2. <sample>.baf.bedgraph.gz (germline workflows)  
3. <sample>.hard-filtered.baf.bw (fallback)

## 📄 Example sample_dirs.txt

One sample directory per line:

- /path/to/project/Run1/Sample1/  
- /path/to/project/Run1/Sample2/  
- /path/to/project/Run2/Sample3/  

Absolute paths recommended.

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

See:

- examples/example_plots/

## 🧠 How It Works

CNV Track  
- Reads absolute copy number from DRAGEN CNV VCF  
- Converts to log₂(CN/2)  
- Plots genome‑wide CNV segments  
- Alternating chromosome shading  
- Highlights gains (red), losses (blue), neutral (grey)  

BAF Track  
- Loads BAF from either:
  - bedgraph (*.baf.bedgraph.gz)
  - hard‑filtered BigWig (*.hard-filtered.baf.bw)
- Downsamples for speed
- Plots BAF dots across the genome  
- Shares the same genome‑wide coordinate system as CNV  

## 📜 License

This project is licensed under the MIT License.  
See the LICENSE file for details.

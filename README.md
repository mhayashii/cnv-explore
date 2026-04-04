# 📘 Genome‑wide CNV + MAF Plotter  
### **DRAGEN‑compatible multi‑sample visualization tool**

This repository provides a clean, reproducible Python workflow for generating **genome‑wide CNV + MAF plots** from **DRAGEN CNV VCF** and **DRAGEN BAF SEG** files.  
It supports **batch processing** of multiple samples using a simple list of sample directories.

The goal is to offer a lightweight, easy‑to‑use plotting tool that produces **CNV/MAF visualizations** directly from DRAGEN outputs.

Tested on Python 3.9–3.11

---

## 🧬 Features

- ✔ **Genome‑wide CNV plotting** using DRAGEN CNV VCF  
- ✔ **Genome‑wide MAF plotting** using DRAGEN `.baf.seg`  
- ✔ **Batch processing** for dozens of samples  
- ✔ **Simple input format** (list of sample directories)  
- ✔ **DRAGEN‑specific, no manifests required**  
- ✔ **Clean, modular Python scripts**  
- ✔ **Publication‑quality PNG output**

---

## ⚡ Quick Start

pip install -r requirements.txt
python scripts/batch_plot.py examples/sample_dirs.txt output/

---

## 📁 Repository Structure

```
cnv-baf-plotter/
│
├── scripts/
│   ├── plot_cnv_baf.py      # Core plotting logic
│   └── batch_plot.py        # Multi-sample runner
│
├── examples/
│   ├── sample_dirs.txt      # Example input list
│   └── example_plots/       # Example output images
│
├── requirements.txt
└── README.md
```

---

## 📥 Input Requirements

Each **sample directory** must contain the following DRAGEN output files:

```
<sample>.cnv.vcf.gz
<sample>.baf.seg
```

These are standard outputs from DRAGEN CNV calling.

The **run folder name does not matter**.  
Only the **sample directory** structure is important.

**Note:** DRAGEN `.baf.seg` files contain **mirrored BAF**, i.e., the  
**minor allele fraction (MAF)**.  
Therefore, values range from **0 to 0.5**, and the plot is labeled accordingly.

---

## 📄 Example `sample_dirs.txt`

Provide one sample directory per line:

```
/path/to/project/Run1/Sample1/
/path/to/project/Run1/Sample2/
/path/to/project/Run2/Sample3/
```

**Absolute paths are recommended** to avoid path resolution issues.  
Relative paths are also supported if run from a consistent working directory.

This file is passed to `batch_plot.py`.

---

## ▶️ How to Run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run batch plotting

```
python scripts/batch_plot.py examples/sample_dirs.txt output_plots/
```

This will generate:

```
output_plots/Sample1_CNV_MAF.png
output_plots/Sample2_CNV_MAF.png
output_plots/Sample3_CNV_MAF.png
```

---

## 🖼 Example Output

(Place your example PNGs in `examples/example_plots/` and embed them here.)

```
examples/example_plots/Sample1_CNV_MAF.png
examples/example_plots/Sample2_CNV_MAF.png
```

---

## 🧠 How It Works

### CNV Track  
- Extracts CN from DRAGEN CNV VCF  
- Converts to log2(CN/2)  
- Plots genome‑wide segments with alternating chromosome shading  

### MAF Track  
- Uses **segmented MAF** (`.baf.seg`)  
- Displays tumor‑shifted allele imbalance patterns  
- Clean, denoised, publication‑quality visualization  

---

## 📜 License

This project is licensed under the MIT License.
See the LICENSE file for details.
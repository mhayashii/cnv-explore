"""
plot_cnv_baf.py

Core plotting function for genome-wide CNV + BAF visualization
using DRAGEN CNV VCF and DRAGEN BAF SEG files.

This module is imported by batch_plot.py.
"""

import os
import gzip
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

# Silence harmless log2(0) warnings
warnings.filterwarnings("ignore", message="divide by zero encountered in log2")

# ---------------------------------------------------------
# Chromosome utilities
# ---------------------------------------------------------
def chr_to_num(chrom):
    """Convert chr string to numeric ordering (1–24)."""
    c = str(chrom).replace("chr", "")
    if c == "X":
        return 23
    if c == "Y":
        return 24
    return int(c)


# ---------------------------------------------------------
# Load CNV VCF
# ---------------------------------------------------------
def load_cnv_vcf(vcf_path):
    """
    Parse DRAGEN CNV VCF and extract:
        chrom, start, end, CN, log2(CN/2)
    """
    records = []

    with gzip.open(vcf_path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue

            fields = line.strip().split("\t")
            chrom, pos, _, _, _, _, _, info, fmt, sample = fields[:10]

            # Extract END from INFO
            end = None
            for item in info.split(";"):
                if item.startswith("END="):
                    end = int(item.split("=")[1])
                    break

            pos = int(pos)

            # Extract CN from FORMAT
            fmt_keys = fmt.split(":")
            sample_vals = sample.split(":")
            fmt_dict = dict(zip(fmt_keys, sample_vals))
            cn = float(fmt_dict.get("CN", "nan"))

            records.append([chrom, pos, end, cn])

    df = pd.DataFrame(records, columns=["chrom", "start", "end", "cn"])
    df["log2"] = np.log2(df["cn"] / 2).clip(-2, 2)
    df["chr_num"] = df["chrom"].apply(chr_to_num)

    return df


# ---------------------------------------------------------
# Load BAF SEG
# ---------------------------------------------------------
def load_baf_seg(baf_path):
    """
    Load DRAGEN BAF SEG file.
    Expected columns:
        Sample, Chromosome, Start, End, Num_Probes, Segment_Mean, BAF_SLM_STATE
    """
    df = pd.read_csv(baf_path, sep="\t")

    # Normalize column names
    df.columns = [c.lower() for c in df.columns]

    # Required columns
    required = {"chromosome", "start", "end", "segment_mean"}
    if not required.issubset(df.columns):
        raise ValueError(f"BAF SEG file {baf_path} missing required columns")

    df["baf_val"] = df["segment_mean"]
    df["chr_num"] = df["chromosome"].apply(chr_to_num)

    return df


# ---------------------------------------------------------
# Build genome-wide coordinates
# ---------------------------------------------------------
def add_genome_coords(df, start_col="start", end_col="end"):
    """
    Add genome-wide coordinates (gstart, gend) based on chromosome offsets.
    """
    chrom_sizes = df.groupby("chr_num")[end_col].max().sort_index()

    offset = {}
    running = 0
    for c, size in chrom_sizes.items():
        offset[c] = running
        running += size

    df["gstart"] = df.apply(lambda r: offset[r["chr_num"]] + r[start_col], axis=1)
    df["gend"]   = df.apply(lambda r: offset[r["chr_num"]] + r[end_col], axis=1)

    return df, offset, chrom_sizes


# ---------------------------------------------------------
# Main plotting function
# ---------------------------------------------------------
def plot_cnv_baf(sample, cnv_vcf_path, baf_seg_path, out_png):
    """
    Create a genome-wide CNV + BAF plot for a single sample.
    """

    # Load data
    cnv = load_cnv_vcf(cnv_vcf_path)
    baf = load_baf_seg(baf_seg_path)

    # Build genome-wide coordinates
    cnv, offset, chrom_sizes = add_genome_coords(cnv)
    baf, _, _ = add_genome_coords(baf)

    # Prepare figure
    fig, axes = plt.subplots(2, 1, figsize=(20, 8), sharex=True)

    # Alternating chromosome shading
    for i, c in enumerate(chrom_sizes.index):
        x0 = offset[c]
        x1 = offset[c] + chrom_sizes[c]
        if i % 2 == 0:
            axes[0].axvspan(x0, x1, color="#f0f0f0", alpha=0.4)
            axes[1].axvspan(x0, x1, color="#f0f0f0", alpha=0.4)

    # CNV track
    for _, row in cnv.iterrows():
        color = "red" if row["log2"] > 0.2 else ("blue" if row["log2"] < -0.2 else "gray")
        axes[0].plot([row["gstart"], row["gend"]],
                     [row["log2"], row["log2"]],
                     color=color, linewidth=2)
        
    axes[0].axhline(0, color="black", linestyle="--", linewidth=0.6, alpha=0.7)

    axes[0].set_ylabel("log2(CN/2)")
    axes[0].set_title(f"{sample} — Genome-wide CNV Profile")
    
    # Chromosome labels
    chrom_labels = list(chrom_sizes.index)
    chrom_positions = [offset[c] + chrom_sizes[c] / 2 for c in chrom_labels]
    axes[0].set_xticks(chrom_positions)
    axes[0].set_xticklabels([str(c) for c in chrom_labels], fontsize=8)

    # BAF track (segmented)
    for _, row in baf.iterrows():
        axes[1].plot([row["gstart"], row["gend"]],
                     [row["baf_val"], row["baf_val"]],
                     color="black", alpha=0.7, linewidth=1)

    axes[1].set_ylabel("MAF (minor allele fraction)")
    axes[1].set_ylim(-0.05, 1.05)
    axes[1].set_title(f"{sample} — Genome-wide MAF Profile (segmented)")

    # Chromosome boundaries
    for c in offset.values():
        axes[0].axvline(c, color="lightgray", linewidth=0.5)
        axes[1].axvline(c, color="lightgray", linewidth=0.5)

    # Chromosome labels
    axes[1].set_xticks(chrom_positions)
    axes[1].set_xticklabels([str(c) for c in chrom_labels])

    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

    print(f"[OK] Saved plot: {out_png}")
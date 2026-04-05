#!/usr/bin/env python3
import os
import gzip
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore", message="divide by zero encountered in log2")

# ---------------------------------------------------------
# Chromosome utilities
# ---------------------------------------------------------
def chr_to_num(chrom):
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
    records = []

    with gzip.open(vcf_path, "rt") as f:
        for line in f:
            if line.startswith("#"):
                continue

            fields = line.strip().split("\t")
            chrom, pos, _, _, _, _, _, info, fmt, sample = fields[:10]

            # Extract END
            end = None
            for item in info.split(";"):
                if item.startswith("END="):
                    end = int(item.split("=")[1])
                    break

            pos = int(pos)

            # Extract CN
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
# Load BAF bedgraph
# ---------------------------------------------------------
def load_baf_bedgraph(path, downsample=10):
    rows = []
    with gzip.open(path, "rt") as f:
        for i, line in enumerate(f):
            if line.startswith("#"):
                continue
            if i % downsample != 0:
                continue
            chrom, start, end, baf = line.strip().split("\t")
            rows.append((chrom, int(start), float(baf)))

    df = pd.DataFrame(rows, columns=["chrom", "pos", "baf"])
    df["chr_num"] = df["chrom"].apply(chr_to_num)
    return df

# ---------------------------------------------------------
# Build genome-wide coordinates
# ---------------------------------------------------------
def add_genome_coords(df, start_col="start", end_col="end"):
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
def plot_cnv_baf(sample, cnv_vcf_path, baf_bedgraph_path, out_png, downsample=10):

    # Load data
    cnv = load_cnv_vcf(cnv_vcf_path)
    baf = load_baf_bedgraph(baf_bedgraph_path, downsample=downsample)

    # Build genome-wide coordinates
    cnv, offset, chrom_sizes = add_genome_coords(cnv)
    baf, _, _ = add_genome_coords(baf, start_col="pos", end_col="pos")

    # Prepare figure
    fig, axes = plt.subplots(2, 1, figsize=(20, 8), sharex=True)

    # -----------------------------------------------------
    # Alternating chromosome shading
    # -----------------------------------------------------
    for i, c in enumerate(chrom_sizes.index):
        x0 = offset[c]
        x1 = offset[c] + chrom_sizes[c]
        if i % 2 == 0:
            axes[0].axvspan(x0, x1, color="#f0f0f0", alpha=0.4)
            axes[1].axvspan(x0, x1, color="#f0f0f0", alpha=0.4)

    # -----------------------------------------------------
    # TOP PANEL — CNV
    # -----------------------------------------------------
    for _, row in cnv.iterrows():
        color = "red" if row["log2"] > 0.2 else ("blue" if row["log2"] < -0.2 else "gray")
        axes[0].plot(
            [row["gstart"], row["gend"]],
            [row["log2"], row["log2"]],
            color=color,
            linewidth=2
        )

    axes[0].axhline(0, color="black", linestyle="--", linewidth=0.6, alpha=0.7)
    axes[0].set_ylabel("log2(CN/2)")
    axes[0].set_title(f"{sample} — Genome-wide CNV Profile")

    # -----------------------------------------------------
    # BOTTOM PANEL — BAF
    # -----------------------------------------------------
    axes[1].scatter(
        baf["gstart"], baf["baf"],
        s=2, color="gray", alpha=0.5
    )
    axes[1].set_ylabel("BAF")
    axes[1].set_ylim(-0.05, 1.05)
    axes[1].set_title(f"{sample} — Genome-wide BAF Profile")

    # -----------------------------------------------------
    # Chromosome boundaries + labels (bottom only)
    # -----------------------------------------------------
    chrom_labels = list(chrom_sizes.index)
    chrom_positions = [offset[c] + chrom_sizes[c] / 2 for c in chrom_labels]

    # Remove "chr"
    clean_labels = [str(c).replace("chr", "") for c in chrom_labels]

    # No numeric ticks
    axes[0].tick_params(axis="x", length=0)
    axes[1].tick_params(axis="x", length=0)

    # Bottom labels only
    axes[0].set_xticks(chrom_positions)
    axes[0].set_xticklabels(clean_labels, fontsize=8)

    axes[1].set_xticks(chrom_positions)
    axes[1].set_xticklabels(clean_labels, fontsize=8)

    # Boundaries
    for c in offset.values():
        axes[0].axvline(c, color="lightgray", linewidth=0.5)
        axes[1].axvline(c, color="lightgray", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

    print(f"[OK] Saved plot: {out_png}")
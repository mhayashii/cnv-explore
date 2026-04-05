"""
batch_plot.py

Batch CNV+BAF plotting for multiple DRAGEN samples.

Input:
    A text file containing one sample directory per line.
    Each directory must contain:
        <sample>.cnv.vcf.gz
        <sample>.baf.bedgraph.gz

Usage:
    python batch_plot.py sample_dirs.txt output_dir/
"""

import os
import sys
from plot_cnv_baf import plot_cnv_baf


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def find_dragen_files(sample_dir):
    """
    Given a sample directory, return:
        sample_name, cnv_vcf_path, baf_bedgraph_path

    Accepted BAF files (priority order):
        <sample>.tumor.baf.bedgraph.gz
        <sample>.baf.bedgraph.gz
    """

    sample = os.path.basename(os.path.normpath(sample_dir))

    cnv_vcf = os.path.join(sample_dir, f"{sample}.cnv.vcf.gz")

    # Priority 1: tumor-normal workflow
    baf_tumor = os.path.join(sample_dir, f"{sample}.tumor.baf.bedgraph.gz")

    # Priority 2: germline workflow
    baf_plain = os.path.join(sample_dir, f"{sample}.baf.bedgraph.gz")

    if not os.path.exists(cnv_vcf):
        raise FileNotFoundError(f"Missing CNV VCF: {cnv_vcf}")

    # Choose the best available BAF file
    if os.path.exists(baf_tumor):
        baf_bedgraph = baf_tumor
    elif os.path.exists(baf_plain):
        baf_bedgraph = baf_plain
    else:
        raise FileNotFoundError(
            f"Missing BAF bedgraph: neither {baf_tumor} nor {baf_plain}"
        )

    return sample, cnv_vcf, baf_bedgraph


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: python batch_plot.py sample_dirs.txt output_dir/")
        sys.exit(1)

    list_file = sys.argv[1]
    outdir = sys.argv[2]

    os.makedirs(outdir, exist_ok=True)

    # Read sample directories
    with open(list_file) as f:
        sample_dirs = [line.strip() for line in f if line.strip()]

    print(f"[INFO] Loaded {len(sample_dirs)} sample directories")

    # Process each sample
    for sample_dir in sample_dirs:
        try:
            sample, cnv_vcf, baf_bedgraph = find_dragen_files(sample_dir)
        except Exception as e:
            print(f"[WARN] Skipping {sample_dir}: {e}")
            continue

        out_png = os.path.join(outdir, f"{sample}_CNV_BAF.png")

        # Skip if already exists
        if os.path.exists(out_png):
            print(f"[SKIP] {sample} (already plotted)")
            continue

        print(f"[RUN] Plotting {sample}...")
        try:
            plot_cnv_baf(sample, cnv_vcf, baf_bedgraph, out_png)
        except Exception as e:
            print(f"[ERROR] Failed for {sample}: {e}")


if __name__ == "__main__":
    main()
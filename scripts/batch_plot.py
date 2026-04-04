"""
batch_plot.py

Batch CNV+BAF plotting for multiple DRAGEN samples.

Input:
    A text file containing one sample directory per line.
    Each directory must contain:
        <sample>.cnv.vcf.gz
        <sample>.baf.seg

Usage:
    python batch_plot.py sample_dirs.txt output_dir/

Example sample_dirs.txt:
    /path/to/project/Run1/Sample1/
    /path/to/project/Run1/Sample2/
    /path/to/project/Run2/Sample3/
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
        sample_name, cnv_vcf_path, baf_seg_path

    Expected files:
        <sample>.cnv.vcf.gz
        <sample>.baf.seg
    """
    sample = os.path.basename(os.path.normpath(sample_dir))

    cnv_vcf = os.path.join(sample_dir, f"{sample}.cnv.vcf.gz")
    baf_seg = os.path.join(sample_dir, f"{sample}.baf.seg")

    if not os.path.exists(cnv_vcf):
        raise FileNotFoundError(f"Missing CNV VCF: {cnv_vcf}")

    if not os.path.exists(baf_seg):
        raise FileNotFoundError(f"Missing BAF SEG: {baf_seg}")

    return sample, cnv_vcf, baf_seg


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: python batch_plot.py sample_dirs.txt output_dir/")
        sys.exit(1)

    list_file = sys.argv[1]
    outdir = sys.argv[2]

    # Create output directory
    os.makedirs(outdir, exist_ok=True)

    # Read sample directories
    with open(list_file) as f:
        sample_dirs = [line.strip() for line in f if line.strip()]

    print(f"[INFO] Loaded {len(sample_dirs)} sample directories")

    # Process each sample
    for sample_dir in sample_dirs:
        try:
            sample, cnv_vcf, baf_seg = find_dragen_files(sample_dir)
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
            plot_cnv_baf(sample, cnv_vcf, baf_seg, out_png)
        except Exception as e:
            print(f"[ERROR] Failed for {sample}: {e}")


if __name__ == "__main__":
    main()
########################################
# script for looking at chromatin features at a list of annotated sites, for example, histone modification signal at gene promoters.

########################################

import os
import subprocess
import logging

def generate_bigwig(Configuration):
    """
    Generate BigWig files from BAM files using samtools and bamCoverage.
    """
    # Define paths for BAM files and BigWig output
    sample_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    input_bam = os.path.join(sample_dir, f"{Configuration.file_to_process}_bowtie2.bam")
    bigwig_dir = os.path.join(Configuration.bigwig_dir)
    os.makedirs(bigwig_dir, exist_ok=True)

    # Define file paths
    sorted_bam = os.path.join(sample_dir, f"{Configuration.file_to_process}.sorted.bam")
    input_bam = os.path.join(sample_dir, f"{Configuration.file_to_process}_bowtie2.bam")
    output_bw = os.path.join(bigwig_dir, f"{Configuration.file_to_process}_raw.bw")

    # Sort BAM file using samtools
    if not os.path.exists(sorted_bam):
        logging.info(f"Sorting BAM file: {input_bam}")
        subprocess.run(["samtools", "sort", "-o", sorted_bam, input_bam], check=True)
    
    # Index the sorted BAM file
    logging.info(f"Indexing sorted and non sorted BAM file: {sorted_bam}")
    subprocess.run(["samtools", "index", sorted_bam], check=True)
    subprocess.run(["samtools", "index", input_bam], check=True)
    
    # Generate BigWig file using bamCoverage
    logging.info(f"Generating BigWig file: {output_bw}")
    subprocess.run(["bamCoverage", "-b", sorted_bam, "-o", output_bw], check=True)


def compute_matrix_and_plot(Configuration):
    """
    Generate heatmap matrices and plot heatmap using computeMatrix and plotHeatmap.
    """
    # Define directories
    bigwig_dir = os.path.join(Configuration.bigwig_dir)
    heatmap_dir = os.path.join(Configuration.heatmap_dir)
    matrix_file = os.path.join(heatmap_dir, 'matrix_gene.mat')
    plot_file = os.path.join(heatmap_dir, 'Histone_gene.png')
    
    os.makedirs(heatmap_dir, exist_ok=TRUE)

    # Define BigWig input files for different histone marks (adjust as necessary)
    bw_file = os.path.join(bigwig_dir, f"{Configuration.file_to_process}_raw.bw")
    
    # Define regions of interest
    regions_file = os.path.join(Configuration.hg38genes)

    # Run computeMatrix to generate the matrix for heatmap
    logging.info(f"Running computeMatrix scale-regions command.")
    subprocess.run([
        "computeMatrix", "scale-regions",
        "-S", bw_file, "-R", regions_file,
        "--beforeRegionStartLength", "3000", "--regionBodyLength", "5000", "--afterRegionStartLength", "3000",
        "--skipZeros", "-o", matrix_file, "-p", "8"
    ], check=True)

    # Run plotHeatmap to generate the heatmap from the matrix
    logging.info(f"Generating heatmap: {plot_file}")
    subprocess.run([
        "plotHeatmap", "-m", matrix_file,
        "-out", plot_file, "--sortUsing", "sum"
    ], check=True)


def generate_summit_regions_and_compute_matrix(Configuration):
    """
    Generate summit regions for peak calling (MACS2) from the summits file and create matrix for heatmap.
    The function uses the pre-generated summits file from MACS2.
    """

    # Path to the summits file (already in BED format)
    summit_file = os.path.join(Configuration.macs2_narrow_dir, Configuration.file_to_process, 
                                f"macs2_narrowpeak_q0.01_summits.bed")
    bigwig_dir = os.path.join(Configuration.bigwig_dir)

    # Define output matrix and BigWig file paths
    bigwig_file = os.path.join(bigwig_dir, f"{Configuration.file_to_process}_raw.bw")
    matrix_file = os.path.join(Configuration.matrix, f"{Configuration.file_to_process}_macs2.mat")
    
    # Use the summit file directly for computeMatrix
    # Here we assume that the summits file is in BED format with the format: chrom start end name score
    logging.info(f"Using summit file: {summit_file} for generating matrix.")
    
    # Run computeMatrix for summit regions
    logging.info(f"Running computeMatrix reference-point for summit regions.")
    subprocess.run([
        "computeMatrix", "reference-point", 
        "-S", bigwig_file, "-R", summit_file, 
        "--skipZeros", "-o", matrix_file, "-p", "8", "-a", "3000", "-b", "3000", "--referencePoint", "center"
    ], check=True)

    # Run plotHeatmap for the generated matrix
    plot_file = os.path.join(Configuration.matrix, f"{Configuration.file_to_process}_macs2_narrowpeak_heatmap.png")
    logging.info(f"Generating heatmap for summit regions: {plot_file}")
    subprocess.run([
        "plotHeatmap", "-m", matrix_file,
        "-out", plot_file, "--sortUsing", "sum",
        "--startLabel", "Peak Start", "--endLabel", "Peak End",
        "--xAxisLabel", "", "--regionsLabel", "Peaks", "--samplesLabel", f"{Configuration.file_to_process}"
    ], check=True)

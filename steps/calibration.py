########################################
# script for performing spike-in calibration to normalize coverage based on the ratio of fragments
# mapped to the primary genome and the E. coli genome.

########################################

# The underlying assumption is that the ratio of fragments mapped to the primary genome to the E. coli genome 
# is the same for a series of samples, each using the same number of cells. Because of this assumption, we do 
# not normalize between experiments or between batches of purified pATn5, which can have very different amounts 
# of carry-over E. coli DNA. Using a constant C to avoid small fractions in normalized data, we define a 
# scaling factor S as

# S = C / (fragments mapped to E. coli genome)

# Normalized coverage is then calculated as:

# Normalized coverage = (primary_genome_coverage) * S

# The Constant is an arbitrary multiplier, typically 10,000. The resulting file will be comparatively small as a genomic coverage bedgraph file.

import os
import subprocess
import logging

def spike_in_calibration(Configuration):
    """
    Perform spike-in calibration to normalize coverage based on the ratio of fragments
    mapped to the primary genome and the E. coli genome.
    """

    # Set directories and files
    sample_dir = os.path.join(Configuration.cleaned_alignments_dir, Configuration.file_to_process)
    bedgraph_dir = os.path.join(Configuration.bedgraph_dir)
    os.makedirs(bedgraph_dir, exist_ok=True)

    # Define file paths
    filtered_bed = os.path.join(sample_dir, f"{Configuration.file_to_process}_bowtie2.filtered.fragments.bed")
    chrom_size_file = Configuration.chrom_size_file

    # Check if the filtered bed file exists
    if not os.path.exists(filtered_bed):
        raise FileNotFoundError(f"Filtered fragments BED file not found: {filtered_bed}")

    # Calculate the sequencing depth (seqDepth)
    seq_depth_file = os.path.join(sample_dir, f"{Configuration.file_to_process}_spike_in.seqDepth")
    if not os.path.exists(seq_depth_file):
        raise FileNotFoundError(f"Sequence depth file not found: {seq_depth_file}")

    with open(seq_depth_file, "r") as f:
        seq_depth = int(f.read().strip())

    logging.info(f"Sequencing depth (seqDepth) for {Configuration.file_to_process}: {seq_depth}")

    # If seqDepth > 1, perform spike-in calibration
    if seq_depth > 1:
        # Create the scale factor based on seqDepth
        scale_factor = 10000 / seq_depth
        logging.info(f"Calculated scale factor: {scale_factor}")

        # Build the bedtools command for genome coverage
        bedgraph_output = os.path.join(bedgraph_dir, f"{Configuration.file_to_process}_bowtie2.fragments.normalized.bedgraph")
        bedgraph_command = [
            "bedtools", "genomecov", "-bg", "-scale", str(scale_factor), "-i", filtered_bed,
            "-g", chrom_size_file, ">", bedgraph_output
        ]

        # Join the command into a single string
        bedgraph_command = " ".join(bedgraph_command)

        logging.info(f"Running bedtools genomecov command: {bedgraph_command}")

        # Run the command to generate the normalized bedgraph file
        try:
            subprocess.run(bedgraph_command, shell=True, check=True)
            logging.info(f"Spike-in calibration completed. Normalized coverage saved to: {bedgraph_output}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running bedtools genomecov command: {e}")
            raise

    else:
        logging.warning(f"Sequencing depth is too low ({seq_depth}). Skipping spike-in calibration.")


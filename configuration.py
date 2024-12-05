########################################

# utility that contains a class that gets the configuration

########################################

import logging
import datetime

class Config:
    """
    Class containing the parameters 
    """
    
    def __init__(self):
        
        self.RAW_input_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/raw/nov2024"
        self.QC_dir_raw = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/qc_output/raw"
        self.QC_dir_trimmed = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/qc_output/trimmed"
        self.cleaned_alignments_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/cleaned_alignments"
        self.trimmed_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/trimmed"
        self.bowtie2_index = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/external/bowtie2index/genome_index"
        self.bowtie2_index_spike_in = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/common_files/data/external/spike_in/ecoli_K_12_MG1655_bowtie_index"
        self.picard = "/mnt/jw01-aruk-home01/projects/functional_genomics/bin/picard/picard.jar"
        self.fraglength_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/fragment_length"
        self.bedgraph_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/bedgraph"
        self.chrom_size_file = "/mnt/jw01-aruk-home01/projects/functional_genomics/common_files/data/external/reference/Homo_sapiens/hg38/Sequence/WholeGenomeFasta/GRCh38.chrom.sizes"
        self.macs2_narrow_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/peak_calling/narrow"
        self.macs2_broad_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/peak_calling/broad"
        self.bigwig_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/bigwig"
        self.hg38genes = "/mnt/jw01-aruk-home01/projects/functional_genomics/common_files/data/external/genes.bed"
        self.heatmap_dir = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/heatmap"
        self.matrix = "/mnt/jw01-aruk-home01/projects/oa_functional_genomics/projects/CUT_Tag/analyses/processing_pipeline/data/output/matrix"
        
        
        self._init_logging()

        self.file_to_process = None


    def _init_logging(self):
        cur_date = datetime.datetime.now()
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s - %(message)s",
            handlers=[
                # logging.FileHandler("{0}/{1}.log".format(self.logs_dir, f"{cur_date.year}-{cur_date.month}-{cur_date.day}_{cur_date.hour}.{cur_date.minute}.{cur_date.second}"), mode="a"),
                logging.StreamHandler()])
from Modules import Module

class Bowtie2(Module):
    def __init__(self, module_id):
        super(Bowtie2, self).__init__(module_id)

        self.input_keys = ["R1", "R2", "samtools", "bowtie2", "ref", "nr_cpus", "mem"]

        self.output_keys = ["bam", "R1", "R2"]

    def define_input(self):
        self.add_argument("R1",             is_required=True)
        self.add_argument("R2")
        self.add_argument("samtools",       is_required=True, is_resource=True)
        self.add_argument("bowtie2",        is_required=True, is_resource=True)
        self.add_argument("ref",            is_required=True, is_resource=True)
        self.add_argument("nr_cpus",        is_required=True, default_value=8)
        self.add_argument("mem",            is_required=True, default_value="nr_cpus * 4")

    def define_output(self, platform, split_name=None):

        bam_out = self.generate_unique_file_name(split_name=split_name,
                                                 extension="bam")
        R1_unmapped_fastq_out   = self.generate_unique_file_name(split_name=split_name,
                                                                 extension="unmapped.1.fastq.gz")

        self.add_output(platform, "bam", bam_out)
        self.add_output(platform, "R1", R1_unmapped_fastq_out)

        if self.get_arguments("R2").get_value() is not None:
            R2_unmapped_fastq_out = self.generate_unique_file_name(split_name=split_name,
                                                                   extension="unmapped.2.fastq.gz")
            self.add_output(platform, "R2", R2_unmapped_fastq_out)

    def define_command(self, platform):

        # Get arguments to run Bowtie2 aligner
        R1                  = self.get_arguments("R1").get_value()
        R2                  = self.get_arguments("R2").get_value()
        samtools            = self.get_arguments("samtools").get_value()
        bowtie2             = self.get_arguments("bowtie2").get_value()
        ref                 = self.get_arguments("ref").get_value()
        nr_cpus             = self.get_arguments("nr_cpus").get_value()
        bam_out             = self.get_output("bam")
        r1_unmapped_fastq   = self.get_output("R1")
        unmapped_fastq_base = r1_unmapped_fastq.replace(".1.", ".%.")

        # Design command line based on read type (i.e. paired-end or single-end)
        if self.get_arguments("R2").get_value() is not None:
            bowtie2_cmd = "{0} --local -q -p {1} -x {2} -1 {3} -2 {4} --reorder --no-mixed --no-discordant --un-conc-gz {5} -t !LOG2!"\
                            .format(bowtie2, nr_cpus, ref, R1, R2, unmapped_fastq_base)

        else:
            bowtie2_cmd = "{0} --local -q -p {1} -x {2} -U {3} --reorder --no-mixed --no-discordant --al-gz {4} -t !LOG2!"\
                            .format(bowtie2, nr_cpus, ref, R1, r1_unmapped_fastq)

        # Generating command for converting SAM to BAM
        sam_to_bam_cmd = "{0} view -uS -@ {1} - !LOG2!".format(samtools, nr_cpus)

        # Generating command for sorting BAM
        bam_sort_cmd = "{0} sort -@ {1} - -o {2} !LOG3!".format(samtools, nr_cpus, bam_out)

        cmd = "{0} | {1} | {2}".format(bowtie2_cmd, sam_to_bam_cmd, bam_sort_cmd)

        return cmd
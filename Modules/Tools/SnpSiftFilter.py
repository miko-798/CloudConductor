from Modules import Module

class SnpSiftFilter(Module):

    def __init__(self, module_id):
        super(SnpSiftFilter, self).__init__(module_id)

        self.input_keys     = ["vcf", "snpsift", "java", "nr_cpus", "mem"]
        self.output_keys    = ["vcf"]
        self.quick_command  = False

    def define_input(self):
        self.add_argument("vcf",                is_required=True)
        self.add_argument("snpsift",            is_required=True, is_resource=True)
        self.add_argument("java",               is_required=True, is_resource=True)
        self.add_argument("filter_exp",         is_required=True)
        # self.add_argument("region_type",        is_required=True, default_value="exonic")
        # self.add_argument("variant_type",       is_required=True, default_value="synonymous SNV,unknown,frameshift_deletion,nonframeshift substitution")
        # self.add_argument("genomic_superdups",  is_required=True, default_value=True)
        # self.add_argument("pop_freq_max",       is_required=True, default_value=0.001)
        # self.add_argument("nastring",           is_required=True, default_value=".")
        self.add_argument("nr_cpus",            is_required=True, default_value=2)
        self.add_argument("mem",                is_required=True, default_value=6)

    def define_output(self, platform, split_name=None):
        # Declare VCF output filename
        vcf = self.generate_unique_file_name(split_name=split_name, extension=".vcf")
        self.add_output(platform, "vcf", vcf)

    def define_command(self, platform):
        # Get input arguments
        vcf_in              = self.get_arguments("vcf").get_value()
        snpsift             = self.get_arguments("snpsift").get_value()
        java                = self.get_arguments("java").get_value()
        filter_exp          = self.get_arguments("filter_exp").get_value()
        # region_type         = self.get_arguments("region_type").get_value()
        # variant_type        = self.get_arguments("variant_type").get_value()
        # genomic_superdups   = self.get_arguments("genomic_superdups").get_value()
        # pop_freq_max        = self.get_arguments("pop_freq_max").get_value()
        # nastring            = self.get_arguments("nastring").get_value()
        mem                 = self.get_arguments("mem").get_value()

        # Get output file
        vcf_out = self.get_output("vcf")

        # intialize filter types
        # region_filter = None
        # variant_type_filter= None
        # filter_expression = None

        # Check for multiple region filters and build region filter
        # if region_type is "exonic":
        #     region_filter = "Func.refGene = exonic & Func.refGene != '.'"
        # elif len(region_type.split(",")) > 0:
        #     regions = region_type.split(",")
        #     regions = list(map(lambda x: re.sub('^', 'Func.refGene = ', x), regions))
        #     regions.append('Func.refGene != %s') % nastring
        #     region_filter = " & ".join(regions)

        # built variant type filter
        # variant_types = variant_type.split(",")
        # variant_types = list(map(lambda x: re.sub('^', 'ExonicFunc.refGene = ', x), variant_types))

        # Set JVM options
        jvm_options = "-Xmx%dG -Djava.io.tmpdir=%s" % (mem * 4 / 5, platform.get_workspace_dir("tmp"))

        # Generating SnpSift command
        cmd = "%s %s -jar %s filter \"%s\" -f %s > %s !LOG2!" % (java, jvm_options, snpsift, filter_exp, vcf_in, vcf_out)
        return cmd
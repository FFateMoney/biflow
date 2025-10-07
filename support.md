| 工具名        | tool        |
|:----------:|:-----------:|
| FastQC     | fastqc      |
| TrimGalore | trim_galore |
| bowtie2    | bowtie2     |
| bwa        | bwa         |
| gatk4      | gatk        |
| plink      | plink       |
| vcftools   | vcftools    |
| picard     | piard       |
| multiqc    | multicq     |
| samtools   | samtools    |
| hapmap     | hapmap      |

| 工具名        | 可选subcommand                                                     |
|:----------:| -------------------------------------------------------------------------------------------- |
| FastQC     | fastqc                                                                                       |
| TrimGalore | trim_galore                                                                                  |
| bowtie2    | indexing,mapping                                                                             |
| bwa        | index,mem                                                                                    |
| gatk4      | haplotype_caller,combine_gvcfs,genotyping,variant_filtering,select_variants,varint_selection |
| plink      | plink                                                                                        |
| vcftools   | filter                                                                                       |
| picard     | mark_duplicates,add_read_groups,create_sequence_dictionary                                   |
| multiqc    | multiqc                                                                                      |
| samtools   | sort,faidx,local_realignment                                                                 |
| hapmap     | vcf2hapmap                                                                                   |

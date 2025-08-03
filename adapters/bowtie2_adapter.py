from adapters.base_adapter import BaseAdapter
from pathlib import Path

class Bowtie2Adapter(BaseAdapter):
    def __init__(self, config, sample_data=None):
        self.config = config
        self.sample_data = sample_data
    
    def indexing(self, ref_path, index_dir):
        """构建Bowtie2索引"""
        cmd = (
            f"{self.config['tools']['bowtie2']}-build "
            f"--threads {self.config['threads']} "
            f"{ref_path} {index_dir/'ref'}"
        )
        return self.run_command(cmd)
    
    def mapping(self, sample, read1, read2, index_dir, output_dir):
        """执行Bowtie2比对"""
        cmd = (
            f"{self.config['tools']['bowtie2']} -p {self.config['threads']} "
            f"-x {index_dir/'ref'} "
            f"-1 {read1} -2 {read2} "
            f"-S {output_dir/f'{sample}.sam'}"
        )
        return self.run_command(cmd)
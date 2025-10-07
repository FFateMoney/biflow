## 什么是Biflow

Biflow是一个为生物信息分析而生的工作流管理程序，它连接了一些生物信息分析工具，使这些工具可以被一个简单的配置文件编制成一个工作流，这个工作流可以一键运行，期间无需人的干预。Biflow有清晰的日志记录，支持断点重跑、并行加速。目前支持的分析工具可在[映射表](./support.md)的工具列查询，用户也可以通过简单的代码编写拓展其所需要的工具。

## Biflow的架构

对于Biflow而言，一个配置文件就是一个工作流，一个工作流由多个节点组成。一般而言，一个节点执行一个分析工具的一个操作。例如，工作流demo包含节点A，B，C。节点A执行gatk的haplotype_caller，节点B执行gatk的combine_gvcfs，节点c执行gatk的genotyping，这三个节点就构成了一个简单的工作流。

## 安装Biflow

Biflow是一个python程序，运行依赖于Python3,因此请确保你的机器已经正确安装了python3。然后，你可以运行下面的命令行获取Biflow的源代码

```
git clone https://github.com/FFateMoney/biflow.git
```

或者你也可以直接在Biflow的github仓库下载源代码压缩包，然后解压。
到这一步，你已经可以正常运行Biflow了，但是Biflow只是一个工作流控制程序，并不包含任何生物信息分析工具，因此为了真正使用它，你要先安装你需要使用的生物信息工具，如GATK4等。为此，我们构建了一个docker image,这个image已经安装了Biflow支持的所有工具，你可以通过下面的命令行来获取它:

```
docker pull fatemoney/biflow:0.3
```

在这个image中，所有以可执行文件存在的工具包，都可以直接按照名字调用，如直接在命令行输入gatk或trim_galore。所有以jar包形式存在的工具包，都存在于/opt目录下，可通过类似于下面的命令行来调用

```
java -jar /opt/picard.jar
```

## 运行Biflow

### 使用我们提供的配置文件快速开始

首先通过下面的命令行启动下载好的docker image，注意挂载你的数据文件夹和Biflow源代码文件夹。

```
docker run -it -v your_Biflow_path:/biflow - your_work_path/work:/work /fatemoney/biflow:0.3bin/bash
```

然后运行下面的命令行开始工作流：

```
python /biflow/main.py -c /biflow/config/full.yaml
```

我们的提供的配置文件包括了较为完整的生物信息分析流程，你可以通过我们的配置生成器直观的查看其具体步骤。首先打开我们的配置生成器网页[配置生成器](https://github.com/FFateMoney/biflow_config_generator)，然后按照教程导入我们提供的配置文件即可。

### 自定义配置文件

biflow使用的配置文件是yaml格式的文件，一个标准的biflow配置文件可参考源代码中的[full.yaml](./config/full.yaml)。该文件分为两个部分，一个是global部分，一个是nodes部分。

#### global部分

该部分包含三个参数，如下表所示：

| 参数        | 作用                                                                   |
| --------- |:-------------------------------------------------------------------- |
| flow_name | 工作流名字，用于命名全局日志文件。全局日志文件会记录各个节点的运行情况，例如各个节点运行的起始时间等。                  |
| log_dir   | 全局日志文件存放的位置                                                          |
| parallel  | 可设置为true或flase。用于控制该工作流内的节点之间是否可以并行运行。详情请参考nodes部分对dependencies参数的解释 |

#### nodes部分

该部分定义了各个不同的节点，每个节点内包含九个参数，如下表所示：

| 参数           | 作用                                                                                                                                                                                                                                                |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id           | 节点的唯一标识符，类型为数字，不可重复                                                                                                                                                                                                                               |
| tool         | 决定节点的调用的工具包，例如bwa、vcftools等。支持的工具包的列表和其与参数值的映射请参考[映射表](./support.md)                                                                                                                                                  |
| subcommand   | 决定使用的工具包的具体操作，例如tool设置为bwa，subcommand设置为index，则调用的是bwa index操作。每个工具包支持的具体操作请参考[映射表](./support.md)                                                                                                                                                 |
| input_dir    | 该参数可以是一个键值对的数组，也可以是单个键值对。用来设置输入文件的目录，例如，若设置为input_dir: reference: /work/input/ref，则该节点会到/work/input/ref目录下寻找reference。若需要同时设置多个文件的输入目录，则需要设置为数组的形式，具体请参考[full.yaml](./config/full.yaml)                                                           |
| output_dir   | 该参数决定节点输出文件的位置                                                                                                                                                                                                                                    |
| log_dir      | 该参数决定节点的日志记录位置，每个节点都会有一个独立的文件夹来记录该节点运行的具体情况，例如，若设置为output_dir: /work/output/02_VariantCalling，则该节点的日志会记录在/work/output/02_VariantCalling目录下。                                                                                                       |
| dependencies | 该参数可为空或为一个数组，其决定了节点的次序，当global中parallel的值设置为true时，同一层次的节点可并行运行。若节点B必须在节点A后运行，则称节点B依赖节点A，此时节点B的dependencies数组必须包含节点A的id。注意依赖是有传递性的，即若有节点运行顺序A->B->C，则节点B的dependencies必须包含节点A的id，节点C的dependencies必须包含节点B的id，但不必包含节点A的id。没有依赖关系的两个节点就为同一层次节点，即可同步运行。 |
| parallelize  | 类似于global的parallel，区别在于global的parallel控制的是节点与节点间的并行关系，而parallelize控制的是单个节点内部的并行关系。例如在gatk的haplotype_caller中，可同时从多个bam文件生成vcf文件。                                                                                                                   |
| params       | 该参数可为一个数组或为空。该参数是用来设置不同的节点运行的不同的命令所需要的特定的参数的。如，运行bwa命令，parmas需要包含bwa_path，运行samtools需要包含samtools_path，简单来说，该参数包含的内容因所调用的tool与subcommand而异。                                                                                                        |

为了方便设定参数，我们提供可视化设置节点参数与节点间依赖关系的配置生成器，请转到[配置生成器](https://github.com/FFateMoney/biflow_config_generator)的github仓库查看详细教程。 





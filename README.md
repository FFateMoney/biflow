## 什么是Biflow

Biflow是一个为生物信息分析而生的工作流管理程序，允许你使用简单的yaml文件作为配置文件，开启生物信息分析流程，同时我们提供了参数生成器，帮助用户使用可视化界面，便捷地设定允许配置。
Biflow拥有易拓展的特性，目前支持的生信分析工具有：GATK4,BWA,Samtools,Picard,Plink,Bowtie2,fastqc,Vcftools,Multiqc,Hapmap,LDdecay,Trimgalore
用户可以通过简单的代码编写拓展其所需要的工具。
在运行中，Biflow有着完整的日志记录，支持断点重跑，并支持自由设定是否允许并行化运行。

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
在这个image中，所有以可执行文件存在的工具包，都可以直接按照名字调用，如直接在命令行输入gatk或trim_galore。所有以jar包形式存在的工具包，都存在于/opt目录下，可通过类似于
```
java -jar /opt/picard.jar
```
的命令行来调用

## 运行Biflow

### 使用我们提供的配置文件快速开始
首先通过下面的命令行启动下载好的docker image，注意挂载你的数据文件夹和Biflow源代码文件夹。
```
docker run -it -v your_Biflow_path:/biflow your_data_path:/data /bin/bash
```
然后运行下面的命令行开始工作流：
```
python /biflow/main.py -c /biflow/config/demo.yaml
```
我们的提供的配置文件包括了较为完整的生物信息分析流程，你可以通过我们的配置生成器直观的查看其具体步骤。打开我们的配置生成器网页
[配置生成器](https://github.com/FFateMoney/biflow_config_generator)
然后按照教程导入我们提供的配置文件即可。

### 自定义配置文件
请转到[配置生成器](https://github.com/FFateMoney/biflow_config_generator)的github仓库查看详细教程。






#  Multiagents Structural Analysis 

## Overview / 项目简介



## Included Tasks / 包含任务

- **Task 1**: 单自由度弹簧体系
- **Task 2**：简支梁弹性静力分析
- **Task 3**：两层剪切型结构动力分析
- **Task 4**：单层单跨钢框架非线性加载分析 

## Project Structure / 项目结构

```text
task 1/
  T_SDOF_static.py
  sdof_visualization.py


task 2/
  beam_analysis.py
  visualize.py

task 3/
  two_story_shear.py

task 4/
  steel_frame_pushover.py

```

## Requirements / 运行环境

- Python 3.x
- `openseespy`
- `numpy`
- `matplotlib`

Install dependencies with:

安装依赖：

```bash
pip install openseespy numpy matplotlib
```

## How to Run / 运行方式

Run each script inside its own folder so output files are saved locally:

建议进入各自任务文件夹后再运行脚本，这样输出结果会保存在对应目录中：

```bash
cd "task 1"
python T_SDOF_static.py
python sdof_visualization.py

cd "../task 2"
python beam_analysis.py
python visualize.py

cd "../task 3"
python two_story_shear.py

cd "../task 4"
python steel_frame_pushover.py
```



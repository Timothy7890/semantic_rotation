# Semantic_Rotation



### 使用**Semantic_rotation**展示语义点云------------------------------------------



对原始点云进行缩放重构，确保能够将点云放进open3d的视窗下

```
input_txt_dir = r"C:\Users\Administrator\Desktop\mp4\other_input\input"
output_dir = r"C:\Users\Administrator\Desktop\mp4\other_input\combine_txt"
output_mp4_dir = rf"C:\Users\Administrator\Desktop\mp4\other_output"
```

`input_txt_dir`为输入点云的目录；

`output_dir`为重构点云的输出目录；

`output_mp4_dir`为mp4视频的输出目录。



## Installation：

### ffmpeg：

​	需要在命令行中能识别到ffmpeg即可。



### conda 安装

##### 新建conda环境

```
conda create -n semantic_rotation python==3.8 -y
conda activate semantic_rotation
pip install open3d==0.17.0
pip install opencv-python==4.10.0.82
git clone https://github.com/Timothy7890/semantic_rotation.git
cd semantic_rotation
pip install -e .
```

##### 从已有环境安装(需要注意open3d版本的关系，报错可以新建conda环境)

```
conda activate your_env
git clone https://github.com/Timothy7890/semantic_rotation.git
cd semantic_rotation
pip install -e .
```



## 运行

### 命令行运行

```
python Run_Sematic_R_cmd.py --input_dir "C:\Users\Administrator\Desktop\mp4\other_input\input" --output_dir "C:\Users\Administrator\Desktop\mp4\other_input\combine_txt" --output_mp4_dir "C:\Users\Administrator\Desktop\mp4\other_output" --overwrite
```





## 输入点云要求：

1. txt格式；
2. 间隔符为空格；
3. 前七列是x y z r g b 和语义信息。



## 备注：

 #输出的视频时长为14s，不支持自定义调节

 #在第七秒进行过渡，过渡时长为0.5s 

 #设置y轴为点云旋转轴




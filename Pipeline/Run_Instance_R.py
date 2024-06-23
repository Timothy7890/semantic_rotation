import os
from Tran_and_scaling.Reput_txt_instance import translate_and_scale_point_cloud_instance
from Vedio.Semantic_vedio_instance import generate_rotating_point_cloud_video_from_txt_instance

workspace = r"D:\004_Shidi\007_ZhaoYaqin\corn_project\data\mp4"
# 使用示例
input_txt_dir = os.path.join(workspace, "raw_txt")
output_dir = os.path.join(workspace, "combine_txt")
output_mp4_dir = os.path.join(workspace, "output")

OVERWRITE = False
reput_size = 1.0
windows_setting = (640, 640)
# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)
os.makedirs(output_mp4_dir, exist_ok=True)

for filename in os.listdir(input_txt_dir):
    if filename.endswith(".txt"):
        # 构建输入文件路径
        input_file = os.path.join(input_txt_dir, filename)
        # 调用函数处理点云文件!!!!!!!!
        translate_and_scale_point_cloud_instance(input_file, output_dir, reput_size, OVERWRITE)
        # 构建处理后的txt文件路径
        processed_txt = os.path.join(output_dir, filename)
        # 调用函数生成旋转点云视频!!!!!!!!
        generate_rotating_point_cloud_video_from_txt_instance(processed_txt, output_mp4_dir, windows_setting,OVERWRITE)



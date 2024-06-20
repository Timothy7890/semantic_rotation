import os
import argparse
from Tran_and_scaling.Reput_txt import translate_and_scale_point_cloud
from Vedio.Semantic_vedio import generate_rotating_point_cloud_video_from_txt

def main(args):
    input_txt_dir = args.input_dir
    output_dir = args.output_dir
    output_mp4_dir = args.output_mp4_dir
    overwrite = args.overwrite

    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_mp4_dir, exist_ok=True)

    for filename in os.listdir(input_txt_dir):
        if filename.endswith(".txt"):
            # 构建输入文件路径
            input_file = os.path.join(input_txt_dir, filename)
            # 调用函数处理点云文件
            translate_and_scale_point_cloud(input_file, output_dir, overwrite)
            # 构建处理后的txt文件路径
            processed_txt = os.path.join(output_dir, filename)
            # 调用函数生成旋转点云视频
            generate_rotating_point_cloud_video_from_txt(processed_txt, output_mp4_dir, overwrite)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process point cloud txt files and generate rotating point cloud videos.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing input txt files.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to save processed txt files.")
    parser.add_argument("--output_mp4_dir", type=str, required=True, help="Directory to save generated mp4 videos.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")

    args = parser.parse_args()
    main(args)
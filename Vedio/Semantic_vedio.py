import open3d as o3d
import numpy as np
import cv2
import os
import subprocess
import shutil

def generate_rotating_point_cloud_video_from_txt(input_txt_path, output_mp4_path, overwrite = False):
    # 获取txt文件名(不包含扩展名)
    txt_name = os.path.splitext(os.path.basename(input_txt_path))[0]

    # 构建输出视频文件路径
    output_mp4_name = f"{txt_name}.mp4"
    output_mp4_file = os.path.join(output_mp4_path, output_mp4_name)
    if overwrite == False:
        # 检查输出视频文件是否存在
        if os.path.exists(output_mp4_file):
            print(f"输出视频文件 {output_mp4_file}已完成，无需重复执行。")
            return

    def read_point_cloud_from_txt(file_path, use_original_rgb, has_header=True):
        if has_header:
            point_cloud_data = np.genfromtxt(file_path, skip_header=1)
        else:
            point_cloud_data = np.loadtxt(file_path)

        xyz = point_cloud_data[:, :3]

        if use_original_rgb:
            rgb = point_cloud_data[:, 3:6]
        else:
            scalar = point_cloud_data[:, 6]
            rgb = np.zeros((len(scalar), 3))
            rgb[scalar == 0] = [23, 184, 220]
            rgb[scalar == 1] = [253, 90, 68]
            rgb[scalar == 2] = [255, 255, 255]

        rgb = rgb / 255.0

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)
        pcd.colors = o3d.utility.Vector3dVector(rgb)

        return pcd

    def generate_rotating_point_cloud_video(file_path, use_original_rgb, output_video_path, has_header=True):
        pcd = read_point_cloud_from_txt(file_path, use_original_rgb, has_header)

        centroid = np.asarray(pcd.points).mean(axis=0)
        pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points) - centroid)

        rotation_angle = np.pi / 100
        rotation_matrix = o3d.geometry.get_rotation_matrix_from_xyz((0, rotation_angle, 0))

        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window("Open3D", width=1280, height=720)
        vis.add_geometry(pcd)

        render_option = vis.get_render_option()
        render_option.point_size = 0.5
        # render_option.point_size = 5


        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc , 30.0, (1280, 720))

        total_rotation_angle = np.pi * 2
        rotated_angle = 0

        for _ in range(30):
            vis.poll_events()
            vis.update_renderer()

        first_frame = vis.capture_screen_float_buffer()
        first_frame = np.asarray(first_frame) * 255
        first_frame = first_frame.astype(np.uint8)
        first_frame_bgr = cv2.cvtColor(first_frame, cv2.COLOR_RGB2BGR)
        for _ in range(int(0.5 * 30)):
            out.write(first_frame_bgr)

        while vis.poll_events():
            pcd.rotate(rotation_matrix, centroid)
            vis.update_geometry(pcd)
            vis.update_renderer()

            image = vis.capture_screen_float_buffer()
            image = np.asarray(image) * 255
            image = image.astype(np.uint8)
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            out.write(image_bgr)

            rotated_angle += rotation_angle
            if rotated_angle >= total_rotation_angle:
                break

        last_frame = vis.capture_screen_float_buffer()
        last_frame = np.asarray(last_frame) * 255
        last_frame = last_frame.astype(np.uint8)
        last_frame_bgr = cv2.cvtColor(last_frame, cv2.COLOR_RGB2BGR)
        for _ in range(int(0.5 * 30)):
            out.write(last_frame_bgr)

        out.release()
        vis.destroy_window()

    # 获取txt文件所在的文件夹路径
    txt_folder = os.path.dirname(input_txt_path)

    # 在txt文件夹下生成1.mp4和2.mp4
    video1_path = os.path.join(txt_folder, "1.mp4")
    video2_path = os.path.join(txt_folder, "2.mp4")
    generate_rotating_point_cloud_video(input_txt_path, True, video1_path)
    generate_rotating_point_cloud_video(input_txt_path, False, video2_path)

    # 在txt文件夹下生成3.mp4
    video3_path = os.path.join(txt_folder, "3.mp4")
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", video1_path,
        "-i", video2_path,
        "-filter_complex", "[0][1]xfade=transition=fade:duration=0.5:offset=7,format=yuv420p",
        "-c:v", "libx264",
        "-c:a", "copy",
        video3_path
    ]
    subprocess.call(ffmpeg_command)

    # 获取txt文件名(不包含扩展名)
    txt_name = os.path.splitext(os.path.basename(input_txt_path))[0]

    # 复制3.mp4到输出路径,并重命名为txt文件名
    output_mp4_name = f"{txt_name}.mp4"
    output_mp4_path = os.path.join(output_mp4_path, output_mp4_name)
    shutil.copy2(video3_path, output_mp4_path)


if __name__ == "__main__":
    # 指定输入txt文件的路径
    input_txt_path = r"C:\Users\Administrator\Desktop\mp4\input\D06_OR-0.1.txt"

    # 指定输出mp4文件的路径
    output_mp4_path = r"C:\Users\Administrator\Desktop\mp4\output"

    # 调用函数生成旋转点云视频并复制到输出路径
    generate_rotating_point_cloud_video_from_txt(input_txt_path, output_mp4_path)
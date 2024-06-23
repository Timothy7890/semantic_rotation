import open3d as o3d
import numpy as np
import cv2
import os
import subprocess
import shutil
import matplotlib.colors

def generate_rotating_point_cloud_video_from_txt_instance(input_txt_path, output_mp4_path, windows_setting,overwrite = False):

    window_width, window_height = windows_setting

    def generate_aesthetic_colors(num_colors):
        hue_range = np.linspace(0, 1, num_colors + 1)[:-1]
        saturation = np.random.uniform(0.6, 0.9, size=num_colors)
        value = np.random.uniform(0.6, 0.9, size=num_colors)

        hsv_colors = np.stack((hue_range, saturation, value), axis=-1)
        rgb_colors = (matplotlib.colors.hsv_to_rgb(hsv_colors) * 255).astype(int)

        return rgb_colors
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
    print("正在执行点云绕轴旋转录制。")
    def read_point_cloud_from_txt_instance(file_path, use_original_rgb, has_header=True):
        if has_header:
            point_cloud_data = np.genfromtxt(file_path, skip_header=1)
        else:
            point_cloud_data = np.loadtxt(file_path)

        xyz = point_cloud_data[:, :3]

        if use_original_rgb:
            rgb = point_cloud_data[:, 3:6]
        else:
            scalar = point_cloud_data[:, 7]
            unique_scalars = np.unique(scalar[scalar > 0])

            num_unique_scalars = len(unique_scalars)
            # colors = generate_aesthetic_colors(num_unique_scalars)
            colors = np.random.randint(0, 256, size=(num_unique_scalars, 3))

            rgb = np.zeros((len(scalar), 3))
            # 谷底的玉米语义为白色
            rgb[scalar == -1] = [255, 255, 255]  # 白色
            # 辅助边框为白色
            rgb[scalar == -2] = [255, 255, 255]  # 白色
            for i, unique_scalar in enumerate(unique_scalars):
                rgb[scalar == unique_scalar] = colors[i]

        rgb = rgb / 255.0

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)
        pcd.colors = o3d.utility.Vector3dVector(rgb)

        return pcd

    def generate_rotating_point_cloud_video(file_path, use_original_rgb, output_video_path, window_width, window_height, has_header=True):
        pcd = read_point_cloud_from_txt_instance(file_path, use_original_rgb, has_header)

        centroid = np.asarray(pcd.points).mean(axis=0)
        pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points) - centroid)

        rotation_angle = np.pi / 100
        rotation_matrix = o3d.geometry.get_rotation_matrix_from_xyz((0, rotation_angle, 0))

        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window("Open3D", width=window_width, height=window_height)
        vis.add_geometry(pcd)

        render_option = vis.get_render_option()
        render_option.point_size = 0.5
        # render_option.point_size = 5


        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc , 30.0, (window_width, window_height))

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
    generate_rotating_point_cloud_video(input_txt_path, True, video1_path, window_width, window_height)
    generate_rotating_point_cloud_video(input_txt_path, False, video2_path,window_width, window_height)

    # 在txt文件夹下生成3.mp4
    video3_path = os.path.join(txt_folder, "3.mp4")
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", video1_path,
        "-i", video2_path,
        "-filter_complex", "[0][1]xfade=transition=fade:duration=0.8:offset=7,format=yuv420p",
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
    generate_rotating_point_cloud_video_from_txt_instance(input_txt_path, output_mp4_path)
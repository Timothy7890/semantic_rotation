import os
import numpy as np

def translate_and_scale_point_cloud(input_file, output_dir, reput_size, overwrite=False):
    # 获取输入文件名（不包括扩展名）
    input_filename = os.path.splitext(os.path.basename(input_file))[0]

    # 构建输出文件路径
    output_file = os.path.join(output_dir, f"{input_filename}.txt")
    if overwrite == False:
        # 检查输出文件是否存在
        if os.path.exists(output_file):
            print(f"输出文件 {output_file} 已完成平移和旋转,无需重复执行")
            return

    # 读取点云文件的前7列数据
    point_cloud = np.genfromtxt(input_file, skip_header=1, usecols=range(7))

    # 如果点云数据超过7列,只保留前7列
    if point_cloud.shape[1] > 7:
        point_cloud = point_cloud[:, :7]

    # 获取xyz坐标
    xyz = point_cloud[:, :3]

    # 计算xz的平均值
    mean_x, _, mean_z = np.mean(xyz, axis=0)

    # 平移点云
    xyz[:, 0] -= mean_x
    xyz[:, 2] -= mean_z

    # 计算y的范围
    min_y, max_y = np.min(xyz[:, 1]), np.max(xyz[:, 1])
    y_range = max_y - min_y

    # 如果y的范围大于0.75,则缩放点云
    if y_range > reput_size:
        scale_factor = reput_size / y_range
        xyz *= scale_factor

    # 计算y的平均值
    mean_y = np.mean(xyz[:, 1])

    # 平移y坐标,使其均值落在-0.1
    xyz[:, 1] -= mean_y - (-0.1)

    # 更新点云数据的前3列
    point_cloud[:, :3] = xyz

    # 保存处理后的7列点云数据到输出文件
    np.savetxt(output_file, point_cloud, fmt='%.6f')

    # 正方体边长
    length = 1

    # 正方体中心点坐标
    center = np.array([0, 0, 0])

    # 生成正方体顶点坐标
    vertices = np.array([
        [-length / 2, -length / 2, -length / 2],
        [length / 2, -length / 2, -length / 2],
        [length / 2, length / 2, -length / 2],
        [-length / 2, length / 2, -length / 2],
        [-length / 2, -length / 2, length / 2],
        [length / 2, -length / 2, length / 2],
        [length / 2, length / 2, length / 2],
        [-length / 2, length / 2, length / 2]
    ]) + center

    # 定义正方体边的顶点索引
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # 底面边
        (4, 5), (5, 6), (6, 7), (7, 4),  # 顶面边
        (0, 4), (1, 5), (2, 6), (3, 7)  # 侧面边
    ]

    # 创建正方体点云数据
    cube_point_cloud = []

    for edge in edges:
        start, end = vertices[edge[0]], vertices[edge[1]]

        # 计算边上的点的数量（这里设置为边长的10倍）
        num_points = int(length * 10)

        # 生成边上的点坐标
        for i in range(num_points + 1):
            t = i / num_points
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])
            z = start[2] + t * (end[2] - start[2])

            # 设置为白色
            r = g = b = 255
            cube_point_cloud.append([x, y, z, r, g, b, 2])

    # 将正方体点云数据转换为NumPy数组
    cube_point_cloud = np.array(cube_point_cloud)

    # 组合原始点云和正方体点云
    combined_point_cloud = np.vstack((point_cloud, cube_point_cloud))

    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)

    # 获取输入文件名（不包括扩展名）
    input_filename = os.path.splitext(os.path.basename(input_file))[0]

    # 构建输出文件路径
    output_file = os.path.join(output_dir, f"{input_filename}.txt")

    # 保存结果到新的txt文件
    header = 'x y z r g b object_id'
    fmt = ['%.6f'] * 3 + ['%d'] * 4  # 设置保存格式
    np.savetxt(output_file, combined_point_cloud, fmt=fmt, delimiter=' ', header=header, comments='')


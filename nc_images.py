#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绘制NC文件生成的JSON数据的脚本
根据指定的颜色规则生成PNG图像
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
import os

def get_color_for_value(value):
    """
    根据数值获取对应的颜色
    规则：
    - 10-15: 使用10对应的颜色
    - 15-20: 使用15对应的颜色
    - 20-25: 使用20对应的颜色
    - 25-30: 使用25对应的颜色
    - 30-35: 使用30对应的颜色
    - 35-40: 使用35对应的颜色
    - 40-45: 使用40对应的颜色
    - 45-50: 使用45对应的颜色
    - 50-55: 使用50对应的颜色
    - 55-60: 使用55对应的颜色
    - 60-65: 使用60对应的颜色
    - 65-70: 使用65对应的颜色
    - >70: 使用70对应的颜色
    - 其他值: 透明
    """
    color_map = {
        10: "rgb(62, 160, 239)",
        15: "rgb(108, 225, 238)",
        20: "rgb(96, 214, 63)",
        25: "rgb(70, 137, 37)",
        30: "rgb(252, 251, 74)",
        35: "rgb(223, 195, 73)",
        40: "rgb(239, 147, 47)",
        45: "rgb(231, 53, 31)",
        50: "rgb(184, 43, 41)",
        55: "rgb(183, 36, 28)",
        60: "rgb(236, 62, 237)",
        65: "rgb(132, 39, 179)",
        70: "rgb(174, 148, 237)"
    }
    
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return (0, 0, 0, 0)  # 透明
    
    # 确定颜色区间
    if value < 10:
        return (0, 0, 0, 0)  # 透明
    elif value < 15:
        return convert_rgb_to_rgba(color_map[10])
    elif value < 20:
        return convert_rgb_to_rgba(color_map[15])
    elif value < 25:
        return convert_rgb_to_rgba(color_map[20])
    elif value < 30:
        return convert_rgb_to_rgba(color_map[25])
    elif value < 35:
        return convert_rgb_to_rgba(color_map[30])
    elif value < 40:
        return convert_rgb_to_rgba(color_map[35])
    elif value < 45:
        return convert_rgb_to_rgba(color_map[40])
    elif value < 50:
        return convert_rgb_to_rgba(color_map[45])
    elif value < 55:
        return convert_rgb_to_rgba(color_map[50])
    elif value < 60:
        return convert_rgb_to_rgba(color_map[55])
    elif value < 65:
        return convert_rgb_to_rgba(color_map[60])
    elif value < 70:
        return convert_rgb_to_rgba(color_map[65])
    else:
        return convert_rgb_to_rgba(color_map[70])

def convert_rgb_to_rgba(rgb_string):
    """将RGB字符串转换为RGBA元组"""
    # 提取RGB值
    rgb_values = rgb_string.replace("rgb(", "").replace(")", "").split(", ")
    r = int(rgb_values[0]) / 255.0
    g = int(rgb_values[1]) / 255.0
    b = int(rgb_values[2]) / 255.0
    return (r, g, b, 1.0)  # 不透明

def create_image_from_json(json_file_path, output_path=None):
    """
    从JSON文件创建图像
    
    Args:
        json_file_path: JSON文件路径
        output_path: 输出PNG文件路径，如果为None则自动生成
    """
    try:
        print(f"正在读取JSON文件: {json_file_path}")
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list) or len(data) == 0:
            print("JSON文件格式不正确或为空")
            return
        
        # 处理第一个文件的数据
        file_data = data[0]
        data_points = file_data['data_points']
        
        print(f"数据点总数: {len(data_points)}")
        
        # 提取坐标和值
        latitudes = []
        longitudes = []
        values = []
        
        for point in data_points:
            if point['value'] is not None and not (isinstance(point['value'], float) and np.isnan(point['value'])):
                latitudes.append(point['latitude'])
                longitudes.append(point['longitude'])
                values.append(point['value'])
        
        print(f"有效数据点数量: {len(values)}")
        
        if not values:
            print("没有找到有效的数据点")
            return
        
        # 统计数值分布
        value_counts = {}
        for value in values:
            if value < 10:
                key = "<10"
            elif value < 15:
                key = "10-15"
            elif value < 20:
                key = "15-20"
            elif value < 25:
                key = "20-25"
            elif value < 30:
                key = "25-30"
            elif value < 35:
                key = "30-35"
            elif value < 40:
                key = "35-40"
            elif value < 45:
                key = "40-45"
            elif value < 50:
                key = "45-50"
            elif value < 55:
                key = "50-55"
            elif value < 60:
                key = "55-60"
            elif value < 65:
                key = "60-65"
            elif value < 70:
                key = "65-70"
            else:
                key = ">70"
            
            value_counts[key] = value_counts.get(key, 0) + 1
        
        print("数值分布:")
        for key in sorted(value_counts.keys()):
            print(f"  {key}: {value_counts[key]} 个点")
        
        # 创建图像
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 设置坐标范围
        lat_min, lat_max = min(latitudes), max(latitudes)
        lon_min, lon_max = min(longitudes), max(longitudes)
        
        # 添加一些边距
        lat_margin = (lat_max - lat_min) * 0.05
        lon_margin = (lon_max - lon_min) * 0.05
        
        ax.set_xlim(lon_min - lon_margin, lon_max + lon_margin)
        ax.set_ylim(lat_min - lat_margin, lat_max + lat_margin)
        
        # 绘制每个数据点
        print("正在绘制数据点...")
        for i, (lat, lon, value) in enumerate(zip(latitudes, longitudes, values)):
            color = get_color_for_value(value)
            if color[3] > 0:  # 如果不是透明
                # 绘制一个小的矩形表示数据点
                rect = Rectangle((lon - 0.01, lat - 0.01), 0.02, 0.02, 
                               facecolor=color, edgecolor='none', alpha=color[3])
                ax.add_patch(rect)
        
        # 设置标题和标签
        filename = file_data['file_info']['filename']
        variable_name = file_data['data_variable']['name']
        variable_units = file_data['data_variable']['units']
        
        ax.set_title(f'数据可视化: {filename}\n变量: {variable_name} ({variable_units})', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('经度', fontsize=12)
        ax.set_ylabel('纬度', fontsize=12)
        
        # 添加网格
        ax.grid(True, alpha=0.3)
        
        # 创建颜色条
        create_colorbar(ax, fig)
        
        # 保存图像
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(json_file_path))[0]
            output_path = f"{base_name}_visualization.png"
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"图像已保存到: {output_path}")
        
        plt.show()
        
    except Exception as e:
        print(f"创建图像时出错: {str(e)}")
        import traceback
        traceback.print_exc()

def create_colorbar(ax, fig):
    """创建颜色条"""
    # 创建颜色映射
    color_map = {
        10: "rgb(62, 160, 239)",
        15: "rgb(108, 225, 238)",
        20: "rgb(96, 214, 63)",
        25: "rgb(70, 137, 37)",
        30: "rgb(252, 251, 74)",
        35: "rgb(223, 195, 73)",
        40: "rgb(239, 147, 47)",
        45: "rgb(231, 53, 31)",
        50: "rgb(184, 43, 41)",
        55: "rgb(183, 36, 28)",
        60: "rgb(236, 62, 237)",
        65: "rgb(132, 39, 179)",
        70: "rgb(174, 148, 237)"
    }
    
    # 创建颜色列表
    colors = []
    bounds = []
    
    for threshold in sorted(color_map.keys()):
        rgb_string = color_map[threshold]
        rgb_values = rgb_string.replace("rgb(", "").replace(")", "").split(", ")
        r = int(rgb_values[0]) / 255.0
        g = int(rgb_values[1]) / 255.0
        b = int(rgb_values[2]) / 255.0
        colors.append((r, g, b))
        bounds.append(threshold)
    
    # 添加最后一个边界
    bounds.append(75)  # 大于70的值
    
    # 创建颜色映射
    cmap = mcolors.ListedColormap(colors)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    # 创建颜色条
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.8)
    cbar.set_label('数值范围', fontsize=12)
    
    # 设置颜色条刻度
    tick_labels = []
    for i, bound in enumerate(bounds[:-1]):
        if i == 0:
            tick_labels.append(f'<{bound}')
        else:
            tick_labels.append(f'{bounds[i-1]}-{bound}')
    
    tick_labels.append(f'>{bounds[-2]}')
    cbar.set_ticks([(bounds[i] + bounds[i+1])/2 for i in range(len(bounds)-1)])
    cbar.set_ticklabels(tick_labels)

def main():
    """主函数"""
    print("开始处理NC文件数据可视化...")
    
    # 查找JSON文件
    json_files = [
        'SA000000001M_20250902225000_CR_filtered.json',
        'SA000000001M_20250902225000_CR_all.json'
    ]
    
    print("当前目录文件列表:")
    for file in os.listdir('.'):
        if file.endswith('.json'):
            print(f"  - {file}")
    
    for json_file in json_files:
        if os.path.exists(json_file):
            print(f"找到文件: {json_file}")
            print(f"文件大小: {os.path.getsize(json_file)} 字节")
            create_image_from_json(json_file)
            break
    else:
        print("未找到可用的JSON文件")
        print("请确保以下文件之一存在:")
        for file in json_files:
            print(f"  - {file}")
        
        # 尝试查找其他JSON文件
        all_json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        if all_json_files:
            print(f"发现其他JSON文件: {all_json_files}")
            print("尝试处理第一个文件...")
            create_image_from_json(all_json_files[0])

if __name__ == "__main__":
    main()

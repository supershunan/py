#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看过滤后的NC数据JSON文件
"""

import json
import os
import glob

def view_filtered_data():
    """查看过滤后的数据文件"""
    
    # 查找所有过滤后的JSON文件
    filtered_files = glob.glob("*_filtered.json")
    
    if not filtered_files:
        print("没有找到过滤后的JSON文件")
        return
    
    print("=== 过滤后的NC数据统计 ===")
    
    total_points = 0
    for filtered_file in filtered_files:
        # 读取过滤后的数据
        with open(filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        
        print(f"\n文件: {filtered_file}")
        print(f"文件大小: {os.path.getsize(filtered_file) / (1024*1024):.2f} MB")
        print(f"包含 {len(filtered_data)} 个文件的数据")
        
        for i, file_data in enumerate(filtered_data):
            filename = file_data['file_info']['filename']
            points_count = len(file_data['data_points'])
            total_points += points_count
            
            print(f"  文件 {i+1}: {filename}")
            print(f"    数据点数量: {points_count:,}")
            
            # 显示坐标范围
            coord_sys = file_data['coordinate_system']
            print(f"    纬度范围: {coord_sys['latitude_range'][0]:.4f} 到 {coord_sys['latitude_range'][1]:.4f}")
            print(f"    经度范围: {coord_sys['longitude_range'][0]:.4f} 到 {coord_sys['longitude_range'][1]:.4f}")
            
            # 显示数据变量信息
            data_var = file_data['data_variable']
            print(f"    数据变量: {data_var['name']}")
            print(f"    单位: {data_var['units']}")
            print(f"    描述: {data_var['long_name']}")
            
            # 显示前几个数据点
            print(f"    前5个数据点:")
            for j, point in enumerate(file_data['data_points'][:5]):
                print(f"      点 {j+1}: 纬度={point['latitude']:.4f}, 经度={point['longitude']:.4f}, 值={point['value']}")
    
    print(f"\n总计: {total_points:,} 个有效数据点")
    
    # 查找所有完整数据文件进行比较
    all_files = glob.glob("*_all.json")
    if all_files:
        total_all_points = 0
        for all_file in all_files:
            with open(all_file, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
            total_all_points += sum(len(file_data['data_points']) for file_data in all_data)
        
        filtered_ratio = total_points / total_all_points * 100
        
        print(f"\n=== 数据过滤效果 ===")
        print(f"原始数据点: {total_all_points:,}")
        print(f"过滤后数据点: {total_points:,}")
        print(f"过滤率: {filtered_ratio:.2f}%")
        print(f"过滤掉的数据点: {total_all_points - total_points:,}")

if __name__ == "__main__":
    view_filtered_data()

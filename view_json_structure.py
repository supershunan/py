#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看JSON文件结构的脚本
"""

import json

def view_json_structure():
    """查看JSON文件的结构"""
    try:
        with open('nc_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("JSON文件结构分析:")
        print("=" * 50)
        
        if isinstance(data, list):
            print(f"根元素是列表，包含 {len(data)} 个文件的数据")
            
            for i, file_data in enumerate(data):
                print(f"\n文件 {i+1}: {file_data['file_info']['filename']}")
                print(f"  变量数量: {len(file_data['file_info']['variables'])}")
                print(f"  维度: {file_data['file_info']['dimensions']}")
                print(f"  数据点数量: {len(file_data['data_points'])}")
                print(f"  坐标系统:")
                print(f"    纬度变量: {file_data['coordinate_system']['latitude_variable']}")
                print(f"    经度变量: {file_data['coordinate_system']['longitude_variable']}")
                print(f"    纬度范围: {file_data['coordinate_system']['latitude_range']}")
                print(f"    经度范围: {file_data['coordinate_system']['longitude_range']}")
                print(f"  数据变量:")
                print(f"    名称: {file_data['data_variable']['name']}")
                print(f"    单位: {file_data['data_variable']['units']}")
                print(f"    长名称: {file_data['data_variable']['long_name']}")
                
                # 显示前5个数据点
                print(f"  前5个数据点:")
                for j, point in enumerate(file_data['data_points'][:5]):
                    print(f"    点 {j+1}: 纬度={point['latitude']:.4f}, 经度={point['longitude']:.4f}, 值={point['value']}")
                
                # 统计有效值
                valid_values = [p['value'] for p in file_data['data_points'] if p['value'] is not None and not (isinstance(p['value'], float) and str(p['value']).lower() == 'nan')]
                print(f"  有效数据点数量: {len(valid_values)}")
                if valid_values:
                    print(f"  数值范围: {min(valid_values):.4f} 到 {max(valid_values):.4f}")
                
                break  # 只显示第一个文件的信息
        
        else:
            print("根元素不是列表")
            
    except Exception as e:
        print(f"读取JSON文件时出错: {str(e)}")

if __name__ == "__main__":
    view_json_structure()

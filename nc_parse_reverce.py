#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NC文件解析器
解析当前目录下的所有NC文件，提取经纬度和对应的数据值，生成JSON格式
"""

import os
import json
import numpy as np
from netCDF4 import Dataset
from pathlib import Path
import glob

class NumpyEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理numpy类型"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def parse_nc_file(file_path, filter_nan=True):
    """
    解析单个NC文件，提取经纬度和数据值
    
    Args:
        file_path (str): NC文件路径
        filter_nan (bool): 是否过滤NaN值，默认为True
        
    Returns:
        dict: 包含文件信息和数据的字典
    """
    try:
        with Dataset(file_path, 'r') as nc:
            # 获取文件信息
            file_info = {
                'filename': os.path.basename(file_path),
                'variables': list(nc.variables.keys()),
                'dimensions': {},
                'global_attributes': {}
            }
            
            # 安全地获取维度信息
            for dim_name, dim_obj in nc.dimensions.items():
                file_info['dimensions'][str(dim_name)] = len(dim_obj)
            
            # 安全地获取全局属性
            for attr_name in nc.ncattrs():
                try:
                    file_info['global_attributes'][attr_name] = nc.getncattr(attr_name)
                except:
                    file_info['global_attributes'][attr_name] = str(nc.getncattr(attr_name))
            
            # 查找经纬度变量
            lat_var = None
            lon_var = None
            
            # 常见的经纬度变量名
            lat_names = ['lat', 'latitude', 'y', 'Y', 'LAT', 'LATITUDE']
            lon_names = ['lon', 'longitude', 'x', 'X', 'LON', 'LONGITUDE']
            
            for var_name in nc.variables:
                var = nc.variables[var_name]
                if hasattr(var, 'long_name'):
                    long_name = var.long_name.lower()
                    if any(name in long_name for name in ['lat', 'latitude']):
                        lat_var = var_name
                    elif any(name in long_name for name in ['lon', 'longitude']):
                        lon_var = var_name
                elif var_name.lower() in [name.lower() for name in lat_names]:
                    lat_var = var_name
                elif var_name.lower() in [name.lower() for name in lon_names]:
                    lon_var = var_name
            
            # 如果没找到，尝试从维度名推断
            if not lat_var or not lon_var:
                for dim_name in nc.dimensions:
                    if dim_name.lower() in [name.lower() for name in lat_names]:
                        lat_var = dim_name
                    elif dim_name.lower() in [name.lower() for name in lon_names]:
                        lon_var = dim_name
            
            if not lat_var or not lon_var:
                print(f"警告: 在文件 {file_path} 中未找到经纬度变量")
                return None
            
            # 读取经纬度数据
            lats = nc.variables[lat_var][:]
            lons = nc.variables[lon_var][:]
            
            # 查找数据变量（排除经纬度变量）
            data_vars = []
            for var_name in nc.variables:
                if var_name not in [lat_var, lon_var]:
                    var = nc.variables[var_name]
                    if len(var.dimensions) >= 2:  # 至少是2D数据
                        data_vars.append(var_name)
            
            if not data_vars:
                print(f"警告: 在文件 {file_path} 中未找到数据变量")
                return None
            
            # 选择第一个数据变量进行处理
            data_var_name = data_vars[0]
            data_var = nc.variables[data_var_name]
            data = data_var[:]
            
            # 处理缺失值
            if hasattr(data_var, '_FillValue'):
                data = np.ma.masked_equal(data, data_var._FillValue)
            elif hasattr(data_var, 'missing_value'):
                data = np.ma.masked_equal(data, data_var.missing_value)
            
            # 转换为普通数组，缺失值设为None
            data = np.where(np.ma.getmask(data), None, data)
            
            # 生成经纬度网格
            if len(lats.shape) == 1 and len(lons.shape) == 1:
                # 1D经纬度，需要生成网格
                lon_grid, lat_grid = np.meshgrid(lons, lats)
            else:
                # 已经是网格形式
                lat_grid = lats
                lon_grid = lons
            
            # 创建数据点列表
            data_points = []
            for i in range(lat_grid.shape[0]):
                for j in range(lat_grid.shape[1]):
                    if data.shape[0] > i and data.shape[1] > j:
                        # 确保所有值都是Python原生类型
                        lat_val = float(lat_grid[i, j])
                        lon_val = float(lon_grid[i, j])
                        # 翻转索引：原来data[i,j]对应lat[i],lon[j]，现在对应lat[j],lon[i]
                        # 即：原来经度对应j索引，纬度对应i索引，现在翻转
                        val = data[j, i] if j < data.shape[0] and i < data.shape[1] else data[i, j]
                        if val is not None:
                            val = float(val)
                        
                        # 如果启用NaN过滤，跳过NaN值
                        if filter_nan and (val is None or np.isnan(val)):
                            continue
                        
                        point = {
                            'latitude': lat_val,
                            'longitude': lon_val,
                            'value': val
                        }
                        data_points.append(point)
            
            result = {
                'file_info': file_info,
                'coordinate_system': {
                    'latitude_variable': lat_var,
                    'longitude_variable': lon_var,
                    'latitude_range': [float(np.min(lats)), float(np.max(lats))],
                    'longitude_range': [float(np.min(lons)), float(np.max(lons))]
                },
                'data_variable': {
                    'name': data_var_name,
                    'units': getattr(data_var, 'units', 'unknown'),
                    'long_name': getattr(data_var, 'long_name', data_var_name)
                },
                'data_points': data_points
            }
            
            return result
            
    except Exception as e:
        print(f"错误: 解析文件 {file_path} 时出错: {str(e)}")
        return None

def main():
    """
    主函数：解析当前目录下的所有NC文件
    """
    # 查找当前目录下的所有NC文件
    nc_files = glob.glob("*.nc")
    
    if not nc_files:
        print("当前目录下没有找到NC文件")
        return
    
    print(f"找到 {len(nc_files)} 个NC文件:")
    for file in nc_files:
        print(f"  - {file}")
    
    # 解析所有文件（包含所有数据）
    all_results = []
    # 解析所有文件（只包含非NaN数据）
    filtered_results = []
    
    for nc_file in nc_files:
        print(f"\n正在解析文件: {nc_file}")
        
        # 解析包含所有数据的结果
        result = parse_nc_file(nc_file, filter_nan=False)
        if result:
            all_results.append(result)
            print(f"  成功解析（包含所有数据），包含 {len(result['data_points'])} 个数据点")
        
        # 解析只包含非NaN数据的结果
        filtered_result = parse_nc_file(nc_file, filter_nan=True)
        if filtered_result:
            filtered_results.append(filtered_result)
            print(f"  成功解析（过滤NaN），包含 {len(filtered_result['data_points'])} 个数据点")
        
        if not result and not filtered_result:
            print(f"  解析失败")
    
    if all_results or filtered_results:
        # 为每个NC文件生成对应的JSON文件
        for i, nc_file in enumerate(nc_files):
            nc_filename = os.path.splitext(os.path.basename(nc_file))[0]  # 去掉.nc扩展名
            
            # 保存包含所有数据的文件
            if i < len(all_results) and all_results[i]:
                output_file = f"{nc_filename}_all.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump([all_results[i]], f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
                
                print(f"\n包含所有数据的文件已保存到 {output_file}")
                print(f"包含 {len(all_results[i]['data_points'])} 个数据点")
            
            # 保存只包含非NaN数据的文件
            if i < len(filtered_results) and filtered_results[i]:
                filtered_output_file = f"{nc_filename}_filtered.json"
                with open(filtered_output_file, 'w', encoding='utf-8') as f:
                    json.dump([filtered_results[i]], f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
                
                print(f"过滤NaN后的文件已保存到 {filtered_output_file}")
                print(f"包含 {len(filtered_results[i]['data_points'])} 个有效数据点")
                
                # 显示过滤效果
                if i < len(all_results) and all_results[i]:
                    filtered_ratio = len(filtered_results[i]['data_points']) / len(all_results[i]['data_points']) * 100
                    print(f"数据过滤率: {filtered_ratio:.2f}% ({len(filtered_results[i]['data_points'])}/{len(all_results[i]['data_points'])})")
        
        # 显示总体统计
        total_all_points = sum(len(result['data_points']) for result in all_results)
        total_filtered_points = sum(len(result['data_points']) for result in filtered_results)
        
        if all_results and filtered_results:
            overall_filtered_ratio = total_filtered_points / total_all_points * 100
            print(f"\n=== 总体统计 ===")
            print(f"总数据点: {total_all_points:,}")
            print(f"有效数据点: {total_filtered_points:,}")
            print(f"总体过滤率: {overall_filtered_ratio:.2f}%")
        
        # 显示第一个文件的前几个数据点作为示例
        if filtered_results:
            first_result = filtered_results[0]
            print(f"\n示例数据点 (来自 {first_result['file_info']['filename']}, 已过滤NaN):")
            for i, point in enumerate(first_result['data_points'][:5]):
                print(f"  点 {i+1}: 纬度={point['latitude']:.4f}, 经度={point['longitude']:.4f}, 值={point['value']}")
    else:
        print("没有成功解析任何文件")

if __name__ == "__main__":
    main()

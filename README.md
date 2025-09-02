# NC 文件解析器

这个 Python 脚本用于解析当前目录下的所有 NC（NetCDF）文件，提取经纬度和对应的数据值，并生成 JSON 格式的输出。

## 功能特点

- 自动识别 NC 文件中的经纬度变量
- 支持多种常见的经纬度变量命名方式
- 处理缺失值和异常数据
- 生成包含完整元数据的 JSON 输出
- 支持批量处理多个 NC 文件

## 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install netCDF4 numpy
```

## 使用方法

1. 将 NC 文件放在脚本所在的目录中
2. 运行脚本：

```bash
python nc_parser.py
```

## 输出格式

脚本会为每个 NC 文件生成两个对应的 JSON 文件：

1. **`{nc文件名}_all.json`** - 包含所有数据点（包括 NaN 值）
2. **`{nc文件名}_filtered.json`** - 只包含非 NaN 的有效数据点

例如，对于文件 `SA000000001M_20250902152000_CR.nc`，会生成：
- `SA000000001M_20250902152000_CR_all.json`
- `SA000000001M_20250902152000_CR_filtered.json`

每个 JSON 文件都包含以下结构：

```json
[
  {
    "file_info": {
      "filename": "文件名.nc",
      "variables": ["变量列表"],
      "dimensions": {"维度信息"},
      "global_attributes": {"全局属性"}
    },
    "coordinate_system": {
      "latitude_variable": "纬度变量名",
      "longitude_variable": "经度变量名",
      "latitude_range": [最小纬度, 最大纬度],
      "longitude_range": [最小经度, 最大经度]
    },
    "data_variable": {
      "name": "数据变量名",
      "units": "单位",
      "long_name": "长名称"
    },
    "data_points": [
      {
        "latitude": 纬度值,
        "longitude": 经度值,
        "value": 数据值
      }
    ]
  }
]
```

## 支持的经纬度变量名

脚本会自动识别以下常见的经纬度变量名：

**纬度变量：**

- lat, latitude, y, Y, LAT, LATITUDE

**经度变量：**

- lon, longitude, x, X, LON, LONGITUDE

## 注意事项

- 脚本会处理当前目录下的所有 `.nc` 文件
- 如果某个文件解析失败，会显示错误信息但继续处理其他文件
- 缺失值会被转换为 `null`
- 输出文件使用 UTF-8 编码
- 过滤后的文件只包含有效的数值数据，不包含 NaN 值
- 脚本会显示数据过滤的统计信息

## 查看数据统计

运行 `python view_filtered_data.py` 可以查看过滤后数据的详细统计信息。

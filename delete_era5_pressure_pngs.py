import os
from pathlib import Path

ERA5_PRESSURE_LIST = [
    'geopotential-200', 'geopotential-500', 'geopotential-700', 'geopotential-850',
    'specific_humidity-200', 'specific_humidity-500', 'specific_humidity-700', 'specific_humidity-850',
    'temperature-200', 'temperature-500', 'temperature-700', 'temperature-850',
    'u_component_of_wind-200', 'u_component_of_wind-500', 'u_component_of_wind-700', 'u_component_of_wind-850',
    'v_component_of_wind-200', 'v_component_of_wind-500', 'v_component_of_wind-700', 'v_component_of_wind-850',
]

target_dir = Path('~/zzn_data/jsonbig/datajson/process_data/synoptic/datajson/WSInstruct/processpng_synoptic_small').expanduser()

deleted = 0
for png in target_dir.glob('*.png'):
    if any(keyword in png.name for keyword in ERA5_PRESSURE_LIST):
        png.unlink()
        deleted += 1
        if deleted % 1000 == 0:
            print(f"已删除 {deleted} 个文件...")

print(f"完成！共删除 {deleted} 个 PNG 文件。")

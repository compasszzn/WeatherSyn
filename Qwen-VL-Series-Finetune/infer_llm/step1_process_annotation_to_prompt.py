import os
import json
from datetime import datetime
import config
import os
import json

def parse_month(timestamp_str):
    """从 '2022-01-01T08' 提取 '2022-01'"""
    return timestamp_str[:7]

def generate_data(area, level):
    # 文件路径（都是 JSON，不是 JSONL）
    if level=='single':
        train_json = f"/WSInstruct/json/sft/annotation_train_{area}.json"
        test_json = f"/WSInstruct/json/sft/annotation_test_{area}.json"
        output_path = f"/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/datajson/combined/combined_{area}.json"

    # 读取 train 数据
    with open(train_json, 'r') as f:
        train_data = json.load(f)

    # 建立按月份分组的映射
    month_to_examples = {}
    for example in train_data:
        month = example['image'][0][-13:-11]
        month_to_examples.setdefault(month, []).append(example)

    # 读取 test 数据
    with open(test_json, 'r') as f:
        test_data = json.load(f)


    output_data={}
    output_data["sys_prompt"] = f"As an AI assistant with expertise in weather analysis and forecasting, you are equipped to interpret a comprehensive figures that illustrating various weather variables crucial for understanding the latest weather conditions across the {config.stations[area]}. Your responsibility as a weather forecaster is to produce a general weather forecast for the future using the current weather condition images provided."
    # output_data["prompt_template"] = f"\n  <Thought process>\n   A reference classification hierarchy is defined below {group_text}, you are required to generate the weather report   \n  </Thought process>\n    <Question>Please analyze the following figures and generate a forecast report from today into ne</Question>\n <Examples> Below are a few examples of weather analysis to help understand how the region and type of concern relate to different weather conditions:\n  "
    output_data["prompt_template"]=f"<Question>You must generate a concise multi-day weather forecast based on a template. For each day, replace the placeholder content with a natural language summary consistent with the weather phenomena represented in the figures. Keep the description concise and focused on the keyword groups listed for each date. </Question>\n <Examples> Below are a few examples of weather analysis to help understand how the region and type of concern relate to different weather conditions:\n  "
    output_data["prompt_template_zero"] ="<Question>You must generate a concise multi-day weather forecast based on a template. For each day, replace the placeholder content with a natural language summary consistent with the weather phenomena represented in the figures. Keep the description concise and focused on the keyword groups listed for each date. </Question>\n "
    output_data["para_description"] = config.DESCRIPTION
    samples = []
    for sample in test_data:
        one_sample = {}
        
        one_sample["md_id"]=str(sample['id'])
        one_sample["template"]=f"<Template>{sample['Expected_format']} </Template>\n"
        one_sample["area_ans"]=sample['conversations'][1]['value']
        weekday = datetime.strptime(sample['image'][0][-17:-6], '%Y%m%d_%H').strftime('%A')
        one_sample["time"]=sample['image'][0][-17:-4]+' '+weekday
        one_sample["para_paths"]=sample['image']
        one_sample['daily_forecast'] = sample['daily_forecast']
        test_month = sample['image'][0][-13:-11]
        example_set = month_to_examples.get(test_month, [])
        examples=[]
        for example in example_set[-2:]:
            one_example = {}
            one_example["md_id"]=str(example['id'])
            one_example["template"]=f"<Template>{sample['Expected_format']} </Template>\n"
            one_example["area_ans"]=example['conversations'][1]['value']
            weekday = datetime.strptime(example['image'][0][-17:-6], '%Y%m%d_%H').strftime('%A')
            one_example["time"]=example['image'][0][-17:-4]+' '+weekday
            one_example["para_paths"]=example['image']
            examples.append(one_example)
        one_sample["examples"] = examples
        samples.append(one_sample)
    output_data["samples"]=samples

    # 保存为 JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved: {output_path}")


# for level in ['single']:
for level in ['single']:
    # for area in ['hk','box']:
    for area in config.final_stations:
        generate_data(
            area=area,
            level=level,
        )

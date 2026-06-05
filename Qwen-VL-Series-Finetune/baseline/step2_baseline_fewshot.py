from openai import OpenAI
import os
import base64
import json
import time
import argparse
from collections import defaultdict
import config
import copy
import re
import pdb
# MODEL = 'gpt-4-turbo-2024-04-09'
# MODEL = 'gpt-4o-2024-05-13'
import openai
llm_to_api = {
    "gpt-5-nano": "gpt-5-nano-2025-08-07",
    "gpt-4.1-mini": "gpt-4.1-mini-2025-04-14",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gpt-oss-120b": "gpt-oss-120b",
    "claude-3-7-sonnet-20250219": "claude-3-7-sonnet-20250219",
    "deepseek-chat":"deepseek-chat",
    "omniearth":"omniearth",
    "gemini-3":"gemini-3-pro-preview",
    "gpt-5.2":"gpt-5.2"
}
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def encode_text(text):
  return {"type": "text", "text": f"{text}"}

def image_description(image_list: list, time: str, description_map):
    # Define the base structure of the output
    output = []

    begnining = f"<Parameters> \n The following {len(image_list)} figures represent weather condition at {time} and each figure contains multiple weather parameters, the most important variable in each figure is provided as follow: "
    end = "</Parameters>"
    output.append({
      "type": "text",
            "text": begnining
    })

    # Iterate through the image list
    for i, image_info in enumerate(image_list):
        # Append the text description for the image
        output.append(encode_text(description_map[image_info['abbrev']]))

        # Append the image data
        output.append({
              "type": "image_url",
              "image_url": {
                "url": f"data:image/png;base64,{image_info['data']}",
                },
        })
    output.append(encode_text(end))

    return output

import os
import json
from datetime import datetime, timedelta

def check_pattern_matches(path, pattern_matches):
    """
    pattern_matches 是四个 tuple:
       (date_str, weekday_str, forecast_str)
    """

    # ====== 从文件名提取 date ======
    filename = os.path.basename(path)
    base_date = filename[:8]   # 例如 "20220505"

    try:
        base_dt = datetime.strptime(base_date, "%Y%m%d")
    except:
        return False, f"{path} — cannot parse base date {base_date}"

    # ====== pattern 长度验证 ======
    if len(pattern_matches) != 4:
        return False, f"{path} — pattern_matches should contain 4 entries, got {len(pattern_matches)}"

    # ====== 遍历每一天 ======
    for i in range(4):
        expected_date = (base_dt + timedelta(days=i)).strftime("%Y%m%d")
        expected_weekday = (base_dt + timedelta(days=i)).strftime("%A")

        actual_date, actual_weekday, _ = pattern_matches[i]

        # ---- 日期检查 ----
        if actual_date != expected_date:
            return False, (
                f"{path} — index {i}: expected date {expected_date}, got {actual_date}"
            )

        # ---- weekday 检查 ----
        if actual_weekday != expected_weekday:
            return False, (
                f"{path} — index {i}: weekday mismatch for date {actual_date}: "
                f"expected {expected_weekday}, got {actual_weekday}"
            )

    # 全部通过
    return True, None


def encode_example(weather_parameters: list[str], area_ans: int, example_id: int, hint=None) ->  list[str]:

    example_answers = f"""
      <Weather report>{area_ans}</Weather report>
    """
    example_block = []
    example_block.append(encode_text(f'<Example {example_id}>\n'))
    example_block += weather_parameters
    if hint is not None:
      example_block.append(encode_text(hint))
    example_block.append(encode_text(example_answers))
    example_block.append(encode_text(f'</Example {example_id}>\n'))

    return example_block

def encode_question(weather_parameters: list[str], hint=None) -> list[str]:
    problem_block = []
    problem_block.append(encode_text('<Problem>\n'))
    problem_block+=weather_parameters
    if hint is not None:
        problem_block.append(encode_text(hint))
    problem_block.append(encode_text('</Problem>'))
    return problem_block

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="settings")
    parser.add_argument("-s", "--save_folder", type=str, default="Qwen-VL-Series-Finetune/output", help="output results file path")
    parser.add_argument("--image_path", type=str, default="/WSInstruct/processpng_synoptic_small", help="input prompt file path")
    parser.add_argument("-m", "--model", type=str, default="gemini-3", help="model id")
    parser.add_argument("--area", default="AKQ",type=str, help="The path to save annotation final combined json file.")
    parser.add_argument("--type", default="single",type=str, help="The path to save annotation final combined json file.")
    parser.add_argument("--shot", default=2,type=int, help="The path to save annotation final combined json file.")
    opt = parser.parse_args()
    area_names = config.final_stations
    print(opt.model)
    for area_name in area_names[-2:]:
        output_dir = os.path.join(opt.save_folder,f'output_{opt.model}_shot_{opt.shot}',f"output_test_{area_name}")
        save_path = os.path.join(opt.save_folder,f'output_{opt.model}_shot_{opt.shot}',f"output_test_{area_name}.jsonl")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if "gpt" in opt.model:
            # azure_endpoint = "https://api2.aigcbest.top/v1"
            # api_key = "sk-DMus0ZE9nPsOiAewkkGg3kLa9iceBoLXZX1zBlzyULinD6tJ"
            azure_endpoint = "https://35.aigcbest.top/v1"
            api_key = "sk-H83OuMQHNmIjnRNDuswNvEv6bNDA2yrKK3KuRvySw1A7Ge1O"
            client = OpenAI(base_url = azure_endpoint,api_key=api_key)
        elif "gemini" in opt.model or "claude" in opt.model:
            azure_endpoint = "https://api2.aigcbest.top/v1"
            api_key = "sk-DMus0ZE9nPsOiAewkkGg3kLa9iceBoLXZX1zBlzyULinD6tJ"
            client = OpenAI(base_url = azure_endpoint,api_key=api_key)
        elif "deepseek" in opt.model:
            azure_endpoint = "https://api.deepseek.com"
            api_key = "sk-81d6d99cd0bb4053be049a06071b5b9e"
            client = OpenAI(base_url = azure_endpoint,api_key=api_key)

        elif 'omniearth' in opt.model:
            client = OpenAI(
                base_url = "http://localhost:8000/v1",
                api_key = "EMPTY"
            )
        
        input_path = f"Qwen-VL-Series-Finetune/output/combined/combined_{area_name}.json"
        with open(input_path, 'r') as file:
            data = json.load(file)
        
        time_sleep = 5
        sys_prompt = data["sys_prompt"]
        prompt_template = data["prompt_template"]
        para_description = data["para_description"]
        media_type = "image/png"
        
        ### list
        new_pred_contents = []
        for sample in data["samples"]:
            image_id = sample['para_paths'][0][-17:-4]
            # Create a new sample with the modified key
            new_sample = copy.deepcopy(sample)
            new_sample['image_id'] = f"{image_id}"
            new_pred_contents.append(new_sample)

        id_list = [x['image_id'] for x in new_pred_contents]
        caption_files = [f"{id}.json" for id in id_list]

        prediction_set = {}
        for sample in new_pred_contents:
            id = sample['image_id']
            prediction_set[id] = sample

        max_retry = 10
        
        retry_count = 0
        while True:
            completed_files = os.listdir(output_dir)
            print(f"completed_files: {len(completed_files)}")

            incomplete_files = [f for f in caption_files if f not in completed_files]
            print(f"incomplete_files: {len(incomplete_files)}")

            if len(incomplete_files) == 0:
                break

            
            for index, date_json  in enumerate(incomplete_files):
                result = defaultdict(dict)
                sample = prediction_set[date_json[:-5]]
                img_list = list()
                final_prompt = [prompt_template]
                print("processing",index)
                for img_path in sample["para_paths"]:

                    para_name = img_path[len(area_name) + 1:-18] 
                    img_path = os.path.join(opt.image_path,img_path)
                    with open(img_path, 'rb') as image_file:
                        img = image_file.read()
                        image_data = base64.b64encode(img).decode('utf-8')
                        img_list.append({
                        'abbrev':para_name,
                        'media_type':media_type,
                        'data':image_data
                        })
                result["A"] = sample["area_ans"]

                parameter_question = image_description(img_list, sample["time"], para_description)
                prompt_question = encode_question(parameter_question,sample['template'])
                final_prompt
                for example_index, example_md in enumerate(sample["examples"][-opt.shot:]):
                    example_img_list = list()
                    for img_path in example_md["para_paths"]:
                        para_name = img_path[len(area_name) + 1:-18]
                        img_path = os.path.join(opt.image_path,img_path)
                        with open(img_path, 'rb') as image_file:
                            img = image_file.read()
                            image_data = base64.b64encode(img).decode('utf-8')
                            example_img_list.append({
                            'abbrev':para_name,
                            'media_type':media_type,
                            'data':image_data
                            })
                    parameter_example = image_description(example_img_list, example_md["time"], para_description)
                    prompt_example = encode_example(parameter_example,example_md["area_ans"], example_index + 1,example_md['template'])
                    final_prompt += prompt_example

                final_prompt.append(encode_text('</Examples>'))
                final_prompt += prompt_question
                # sys_prompt="hello"
                # final_prompt="hello"
                try:
                    response_mcq = client.chat.completions.create(
                        model=llm_to_api[opt.model],
                        temperature=0.3,
                        messages=[
                            {
                                "role": "system",
                                "content": sys_prompt
                                },
                            {
                                "role": "user",
                                "content": final_prompt,
                            },
                        ]
                    )

                    response_content = response_mcq.choices[0].message.content
                    time.sleep(time_sleep)

                    result["P"] = response_content
                    result["image_name"] = sample['para_paths']
                    result["daily_forecast"] = sample['daily_forecast']
                    pattern = re.compile(
                        r"<<(\d{8}),\s*([A-Za-z]+)>>\s*Report:\s*(.*?)(?=<<\d{8},|\Z)",
                        re.DOTALL
                    )
                    pattern_matches = pattern.findall(response_content)
                    check,check_reason = check_pattern_matches(date_json,pattern_matches)
                    if check:
                        out_path = os.path.join(output_dir, date_json)

                        with open(out_path, "w", encoding="utf-8") as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                    else:
                        print(check_reason)
                        # retry_count += 1
                        time.sleep(time_sleep)
                        continue
                except Exception as e:
                    print(f"Error at sample {index}: {e}")
                    # retry_count += 1
                    time.sleep(time_sleep)  # 避免频繁重试


        combined_contents = []

        for file_name in sorted(os.listdir(output_dir)):
            if file_name.endswith(".json"):
                file_path = os.path.join(output_dir, file_name)
                with open(file_path, "r", encoding="utf-8") as json_file:
                    content = json.load(json_file)
                    combined_contents.append(content)

        jsonl_path = os.path.join(save_path)
        with open(jsonl_path, "w", encoding="utf-8") as jsonl_file:
            for item in combined_contents:
                jsonl_file.write(json.dumps(item, ensure_ascii=False) + "\n")

        print("All evaluation completed! JSONL saved at:", jsonl_path)


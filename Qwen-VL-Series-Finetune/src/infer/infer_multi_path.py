import argparse
from threading import Thread
# import gradio as gr
# from PIL import Image
from src.utils import load_pretrained_model, get_model_name_from_path, disable_torch_init
# from transformers import TextIteratorStreamer
# from functools import partial
import warnings
from qwen_vl_utils import process_vision_info
from torch.utils.data import Dataset, DataLoader
import pdb
import os
import json
from datetime import datetime, timedelta
import re

warnings.filterwarnings("ignore")

def check_pattern_matches(path, pattern_matches):
    """
    pattern_matches 是四个 tuple:
       (date_str, weekday_str, forecast_str)
    """

    # ====== 从文件名提取 date ======
    filename = os.path.basename(path)
    base_date = filename[-17:-9]   # 例如 "20220505"

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

def is_video_file(filename):
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg']
    return any(filename.lower().endswith(ext) for ext in video_extensions)

import hashlib
import requests
import config
from IPython.display import Markdown, display
import numpy as np
from PIL import Image
import decord
from decord import VideoReader, cpu
from tqdm import tqdm

class VCGPTDataset(Dataset):

    video_formats = ['.mp4', '.webm', '.avi', '.mov', '.mkv']

    def __init__(self, data_list,args):
        self.data_list = data_list
        self.args=args

    def __len__(self):
        return len(self.data_list)
    
    def __getitem__(self, idx):
        line = self.data_list[idx]
        question = line['conversations'][0]['value']
        answer = line['conversations'][1]['value']

        daily_forecast = line['daily_forecast']

        images_name_list = line['image']

        # for fmt in self.video_formats:  # Added this line
        base_path = self.args.image_path

        content_list = []
        for image_name in images_name_list:
            temp_path = os.path.join(base_path, image_name)
            if os.path.exists(temp_path):
                content_list.append({
                    "type": "image",
                    "image": temp_path
                })
            else:
                raise KeyError
        content_list.append({
            "type": "text",
            "text": question
        })

        messages = [
            {
                "role": "user",
                "content": content_list
            }
        ]

        return {
                'conversation':messages,
                'question':question, 
                'answer':answer,
                'video_name':images_name_list,
                'daily_forecast':daily_forecast}

def collate_fn(batch):
    conversation = [x['conversation'] for x in batch]
    question = [x['question'] for x in batch]
    answer = [x['answer'] for x in batch]
    video_name = [x['video_name'] for x in batch]
    daily_forecast = [x['daily_forecast'] for x in batch]
    return conversation, question, answer, video_name, daily_forecast

def main(args):
    global processor, model, device
    for area in config.final_stations[29:]:
    # for area in [args.area]:
        question_file = os.path.join(f"{args.question_file}/annotation_{args.task}_{area}.json")

        with open(question_file, "r") as f:
            questions = json.load(f)

        dataset = VCGPTDataset(questions,args)

        dataloader = DataLoader(dataset, shuffle=False, batch_size=args.batch_size, num_workers=args.num_workers,collate_fn=collate_fn)

        answer_file = os.path.join(f"{args.answer_file}/output_{args.task}_{area}.jsonl")
        os.makedirs(os.path.dirname(answer_file), exist_ok=True)
        

        device = args.device
        
        disable_torch_init()

        use_flash_attn = True
        
        model_name = get_model_name_from_path(args.model_path)
        
        if args.disable_flash_attention:
            use_flash_attn = False

        processor, model = load_pretrained_model(model_base = args.model_base, model_path = args.model_path, 
                                                    device_map=args.device, model_name=model_name, 
                                                    load_4bit=args.load_4bit, load_8bit=args.load_8bit,
                                                    device=args.device, use_flash_attn=use_flash_attn
        )
        processor.tokenizer.padding_side = "left"
        with open(answer_file, "w") as ans_file:
            for i, (conversation,question, answer,video_name, daily_forecast) in enumerate(tqdm(dataloader)):
                # 准备输入（只需要准备一次）
                text = processor.apply_chat_template(conversation, tokenize=False, add_generation_prompt=True)
                image_inputs, video_inputs = process_vision_info(conversation)
                inputs = processor(
                    text=text,
                    images=image_inputs,
                    videos=video_inputs,
                    padding=True,
                    return_tensors="pt",
                )
                
                inputs = inputs.to("cuda")

                batch_size = len(inputs.input_ids)

                batch_output_results = [[] for _ in range(batch_size)]
                
                # 正则表达式用于提取pattern
                pattern = re.compile(
                    r"<<(\d{8}),\s*([A-Za-z]+)>>\s*Report:\s*(.*?)(?=<<\d{8},|\Z)",
                    re.DOTALL
                )

                # 外层循环：对每个样本生成sample_time次
                for time in range(args.sample_time):
                    # 重试机制：如果batch中任何一个样本验证失败，重新生成整个batch
                    max_retries = args.max_retries
                    retry_count = 0
                    all_passed = False
                    
                    while not all_passed:
                        # 批量生成
                        generated_ids = model.generate(
                            **inputs, 
                            max_new_tokens=args.max_new_tokens,
                            temperature=args.temperature,
                            top_k=50,
                            top_p=0.9,
                            do_sample=True)
                        generated_ids_trimmed = [
                            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                        ]
                        output_text = processor.batch_decode(
                            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                        )
                        
                        # 验证所有样本
                        all_passed = True
                        for j in range(batch_size):
                            pred_text = output_text[j]
                            pattern_matches = pattern.findall(pred_text)
                            
                            # 从video_name中提取日期路径
                            video_name_item = video_name[j]
                            if isinstance(video_name_item, list):
                                date_path = video_name_item[0] if len(video_name_item) > 0 else ""
                            else:
                                date_path = video_name_item
                            
                            # 验证输出格式
                            if date_path:
                                check, check_reason = check_pattern_matches(date_path, pattern_matches)
                            else:
                                check = False
                                check_reason = "Cannot extract date from video_name (empty or invalid format)"
                            
                            if not check:
                                all_passed = False
                                if retry_count == 0:  # 只在第一次失败时打印
                                    print(f"Warning: Pattern check failed for sample {j} (time {time}): {check_reason}")
                                break
                        
                        # 只有整个batch通过了才添加到结果中
                        if all_passed:
                            for j in range(batch_size):
                                batch_output_results[j].append(output_text[j])
                            break
                        else:
                            retry_count += 1
                            if retry_count <= max_retries:
                                print(f"Batch {i}, sample_time {time}: Validation failed, retrying ({retry_count}/{max_retries})...")
                            else:
                                # 达到最大重试次数，跳过这个sample_time
                                print(f"Batch {i}, sample_time {time}: Max retries reached, skipping this sample_time...")
                                break  

                for j in range(batch_size):
                    qa = {
                        'image_name': video_name[j],
                        'Q': question[j],
                        'A': answer[j],
                        'P': batch_output_results[j],
                        'daily_forecast': daily_forecast[j] # 一个长度为20的list
                    }
                    ans_file.write(json.dumps(qa) + "\n")
                    ans_file.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/outputmodel/merged_single")
    parser.add_argument("--model-base", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/model/Qwen2.5-VL-7B-Instruct")
    parser.add_argument("--image-path", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/data_era5/processpng_synoptic")
    parser.add_argument("--question_file", type=str, default="/WSInstruct/json/sft_rft_dpo")
    parser.add_argument("--answer_file", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/datajson/infer50")
    parser.add_argument("--task", type=str, default="train")
    parser.add_argument("--fps", type=float, default=5.0) 
    parser.add_argument("--sample_time", type=int, default=3) 
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--load-8bit", action="store_true")
    parser.add_argument("--load-4bit", action="store_true")
    parser.add_argument("--disable_flash_attention", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.9)
    # parser.add_argument("--repetition-penalty", type=float, default=1.2)
    parser.add_argument("--max-new-tokens", type=int, default=200)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--batch-size", type=int, required=False, default=8)
    parser.add_argument("--num-workers", type=int, required=False, default=16)
    parser.add_argument("--area", type=str, required=False, default="box")
    parser.add_argument("--local_rank", type=int, required=False, default=16)
    parser.add_argument("--max-retries", type=int, default=10, help="Maximum number of retries for a batch if validation fails")
    args = parser.parse_args()
    main(args)
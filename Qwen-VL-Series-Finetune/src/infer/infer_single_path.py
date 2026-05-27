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
import config
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
    if 'Day' in path:
        base_date = filename[-22:-14]
    else:
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

import os
import hashlib
import requests

from IPython.display import Markdown, display
import numpy as np
from PIL import Image
import decord
from decord import VideoReader, cpu
import pdb
import json
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
    if "grpo" in args.model_path:
        processor.image_processor.do_resize = True
    if "ood" in args.model_path:
        ood_name = args.model_path.split("ood_")[-1]
        information_file = os.path.join(f"/WSInstruct/json/sft_generalization/split_{ood_name}/generalization_stations.json")
        with open(information_file, "r") as f:
            information = json.load(f)
            need_station = information['test']
            config.final_stations = need_station
    if "generalization" in args.model_path:
        seed_name = args.model_path.split('_')[-1]
        information_file = os.path.join(f"/WSInstruct/json/sft_generalization/generalization_stations_{seed_name}.json")
        with open(information_file, "r") as f:
            information = json.load(f)
            need_station = information['test']
            config.final_stations = need_station

    for area in config.final_stations[15:]:
        question_file = os.path.join(f"{args.question_file}/annotation_{args.task}_{area}.json")

        with open(question_file, "r") as f:
            questions = json.load(f)

        dataset = VCGPTDataset(questions,args)

        dataloader = DataLoader(dataset, shuffle=False, batch_size=args.batch_size, num_workers=args.num_workers,collate_fn=collate_fn)

        answer_file = os.path.join(f"{args.answer_file}/output_{args.task}_{area}.jsonl")
        os.makedirs(os.path.dirname(answer_file), exist_ok=True)
        
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
                
                # 重试机制：如果验证失败，重新生成整个batch
                max_retries = args.max_retries
                retry_count = 0
                all_passed = False
                
                while not all_passed:
                    # Inference
                    generated_ids = model.generate(
                        **inputs, 
                        max_new_tokens=args.max_new_tokens,
                        temperature=args.temperature,
                        # repetition_penalty=args.repetition_penalty,
                        # top_k=10,
                        do_sample=True)
                    generated_ids_trimmed = [
                        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
                    ]
                    output_text = processor.batch_decode(
                        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
                    )
                    
                    # 验证所有样本
                    all_passed = True
                    pattern = re.compile(
                        r"<<(\d{8}),\s*([A-Za-z]+)>>\s*Report:\s*(.*?)(?=<<\d{8},|\Z)",
                        re.DOTALL
                    )

                    # 先验证整个batch是否都通过check
                    for j in range(batch_size):
                        pred_text = output_text[j]
                        pattern_matches = pattern.findall(pred_text)

                        # 从video_name中提取日期（video_name可能是list，取第一个）
                        video_name_item = video_name[j]
                        if isinstance(video_name_item, list):
                            date_path = video_name_item[0] if len(video_name_item) > 0 else ""
                        else:
                            date_path = video_name_item
                        
                        # 验证输出格式（如果date_path为空，跳过验证）
                        if date_path:
                            check, check_reason = check_pattern_matches(date_path, pattern_matches)
                        else:
                            check = False
                            check_reason = "Cannot extract date from video_name (empty or invalid format)"
                        
                        if not check:
                            all_passed = False
                            # pdb.set_trace()
                            if retry_count == 0:  # 只在第一次失败时打印
                                print(f"Warning: Pattern check failed for {date_path}: {check_reason}")
                    
                    # 只有整个batch通过了才append batch result
                    if all_passed:
                        batch_results = []
                        for j in range(batch_size):
                            qa = {
                                'image_name': video_name[j],
                                'Q': question[j],
                                'A': answer[j],
                                'P': output_text[j],
                                'daily_forecast': daily_forecast[j]
                            }
                            batch_results.append(qa)
                        
                        # 保存整个batch的结果
                        for qa in batch_results:
                            ans_file.write(json.dumps(qa, ensure_ascii=False) + "\n")
                        ans_file.flush()
                        break
                    else:
                        retry_count += 1
                        if retry_count <= max_retries:
                            print(f"Batch {i}: Validation failed, retrying ({retry_count}/{max_retries})...")
                        else:
                            # 达到最大重试次数，不保存结果（因为check未通过）
                            print(f"Batch {i}: Max retries reached, skipping batch due to validation failures...")

        # ans_file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/outputmodel/merged_single_rft_generalization_ood_NE_NW")
    parser.add_argument("--model-base", type=str, default="Qwen/Qwen3-VL-8B-Instruct")
    parser.add_argument("--image-path", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/processpng")
    parser.add_argument("--question_file", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/datajson/annotation")
    parser.add_argument("--answer_file", type=str, default="/hpc2hdd/home/mpeng885/zzn_data/json/datajson/output_qwen_ood_NE_NW")
    parser.add_argument("--task", type=str, default="test")
    parser.add_argument("--data_type", type=str, default="single")
    parser.add_argument("--fps", type=float, default=5.0) 
    parser.add_argument("--device", type=str, default="cuda")
    # parser.add_argument("--area", type=str, default="ABQ")
    parser.add_argument("--load-8bit", action="store_true")
    parser.add_argument("--load-4bit", action="store_true")
    parser.add_argument("--disable_flash_attention", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.3)
    # parser.add_argument("--repetition-penalty", type=float, default=1.2)
    parser.add_argument("--max-new-tokens", type=int, default=600)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--batch-size", type=int, required=False, default=8)
    parser.add_argument("--num-workers", type=int, required=False, default=16)
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retries for a batch if validation fails")
    args = parser.parse_args()
    main(args)
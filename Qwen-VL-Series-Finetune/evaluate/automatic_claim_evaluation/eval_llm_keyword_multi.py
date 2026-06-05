import os
import argparse
import json
import ast
import traceback
from tqdm import tqdm
from multiprocessing.pool import Pool
import random
import copy
import pdb
import config
import re
import openai
from openai import OpenAI
import config
from concurrent.futures import ThreadPoolExecutor, as_completed
def classify_hits(hits, mapping):

    classified_list = []
    for w in hits:
        matched = False
        for sub_class, sub_words in mapping.items():
            if w in sub_words:
                classified_list.append(sub_class)
                matched = True
                break
        if not matched:
            classified_list.append("unknown")
    return classified_list
client = OpenAI(
    base_url = "http://localhost:8000/v1",
    api_key = "EMPTY"
)
def extract_all_keywords_with_llm(daily_forecast, group_dict):
    """
    Pass the entire daily_forecast list to the LLM in one call,
    and return structured JSON that includes extracted keywords
    and keyword groups for each day.
    """

    # Convert dictionaries to readable JSON strings
    group_text = json.dumps(group_dict, ensure_ascii=False, indent=2)
    forecast_text = json.dumps(daily_forecast, ensure_ascii=False, indent=2)
    subcategories = [sub for group_dict in group_dict.values() for sub in group_dict.keys()]
    system_prompt = f"""
        You are an advanced weather forecast text analysis model.
        Your task is to analyze the meaning of the forecast texts semantically and
        classify each day's forecast into the most relevant meteorological categories
        and subcategories.
        """
    user_prompt = f"""
        The valid classification hierarchy is defined below:
        ## group_dict (Keyword Groups)
        {group_text}

        
        Each subcategory contains example words or phrases. These examples serve as
        semantic references, not strict matching tokens. You should classify the
        forecast based on meaning.

        ## daily_forecast (Input Data for All Days)
        {forecast_text}

        ---

        Please output **strict JSON**, formatted as a list:
        [
        {{
            "date": "YYYYMMDD",
            "weekday": "xxx",
            "keywords": ["high_pressure","Storm","hot_temperature","dry_air"],
            "keyword_groups": ["Pressure_System,""Event","Temperature","Humidity"]
        }},
        ...
        ]

        Requirements:
        
        - **keywords**:  
        The detected **subcategories** (from `group_dict`).  
        Each selected subcategory must be chosen from the valid list:
        {subcategories}

        - **keyword_groups**:  
        The parent **categories** corresponding to each subcategory.  
        Each category must be selected from:
        {list(group_dict.keys())}

        ### RULES

        1. Do **not** rely solely on exact word matching; use **semantic interpretation**.  
        2. If no keywords are detected for a day, return empty lists.  
        3. Do **not** output explanations, comments, markdown, or any text outside valid JSON.
        4. Output must be valid JSON at the top level—no trailing commas.
        """
    
    
    pred_message = [
        {
            "role": "system",
            "content": system_prompt
            },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
    # 🔥 Call the LLM (replace this with your actual API call)
    completion = client.chat.completions.create(
        model="model/Qwen2.5-72B-Instruct",
        messages=pred_message,
    )
    answer_response_message = json.loads(completion.choices[0].message.content)

    return answer_response_message

def process_single_file(file, prediction_set, output_dir, valid_keywords, keyword_to_group, map_keyword_dict, args):
    """
    Process a single caption file and return the result.
    """
    try:
        key = file[:-5] # Strip file extension
        qa_set = prediction_set[key]
        answer = qa_set['a']
        if "dpo_accept_reject" in output_dir:
            pred = qa_set['accept']
        else:
            pred = qa_set['p']
        
        pattern = re.compile(
            r"<<(\d{8}),\s*([A-Za-z]+)>>\s*Report:\s*(.*?)(?=<<\d{8},|\Z)",
            re.DOTALL
        )

        # ----------- answer ----------
        answer_matches = pattern.findall(answer)
        
        answer_results = []
        for date, weekday, report in answer_matches:
            answer_results.append({
                "date": date,
                "weekday": weekday,
                "report": report.strip()
            })

        answer_keyword_results = qa_set['daily_forecast']
        valid_idx = [idx for idx, item in enumerate(answer_keyword_results) if len(item['keywords']) != 0]
        # ----------- pred ----------
        pred_matches = pattern.findall(pred)

        pred_results = []
        for date, weekday, report in pred_matches:
            clean_report = re.sub(r'##\s*Focus on[\s\S]*?##', '', report, flags=re.IGNORECASE)
            pred_results.append( {
                "date": date,
                "weekday": weekday,
                "report": clean_report.strip()
            })
        if len(answer_results)!=len(pred_results):
            record = {
                "area": args.area,
                "date": re.search(r"(\d{8})", answer).group(1),
                "model": args.model
            }
            record_path = os.path.join(output_dir, f"Bad_{args.area}_{args.model}.json")
            if os.path.exists(record_path):
                with open(record_path, "r", encoding="utf-8") as rf:
                    existing = json.load(rf)
                    if not isinstance(existing, list):
                        existing = [existing]
            else:
                existing = []

            existing.append(record)

            with open(record_path, "w", encoding="utf-8") as wf:
                json.dump(existing, wf, ensure_ascii=False, indent=2)
            print("error:",existing)
            return key, True, None
        pred_keyword_results = extract_all_keywords_with_llm(pred_results, map_keyword_dict)
        for i in range(len(pred_keyword_results)):
            pred_keyword_results[i]['keywords'] = list(set(pred_keyword_results[i]['keywords']) & valid_keywords)
            pred_keyword_results[i]['keyword_groups'] = list({keyword_to_group[kw] for kw in pred_keyword_results[i]['keywords']})
        for i in range(len(pred_keyword_results)):
            if pred_keyword_results[i]['date']!=answer_keyword_results[i]['date']:
                record = {
                    "area": args.area,
                    "date": re.search(r"(\d{8})", answer).group(1),
                    "model": args.model
                }
                record_path = os.path.join(output_dir, f"Bad_{args.area}_{args.model}.json")
                if os.path.exists(record_path):
                    with open(record_path, "r", encoding="utf-8") as rf:
                        existing = json.load(rf)
                        if not isinstance(existing, list):
                            existing = [existing]
                else:
                    existing = []

                existing.append(record)

                with open(record_path, "w", encoding="utf-8") as wf:
                    json.dump(existing, wf, ensure_ascii=False, indent=2)
                print("error:",existing)
                return key, True, None

        result_qa_pair = [{"pred_keyword":pred_keyword_results}, {"answer_keyword":answer_keyword_results}, qa_set]

        # Save the question-answer pairs to a json file.
        with open(f"{output_dir}/{key}.json", "w") as f:
            json.dump(result_qa_pair, f, indent=4)
        
        return key, True, None
    except Exception as e:
        return file, False, str(e)

def annotate(prediction_set, caption_files, output_dir,map_keyword_dict,args, max_workers=8):
    """
    Evaluates question and answer pairs using GPT-3
    Returns a score for correctness.
    Uses concurrent processing for multiple caption files.
    """

    # 所有子类别 + keyword → group 映射
    valid_keywords = set()
    keyword_to_group = {}

    for group_name, sub_dict in map_keyword_dict.items():
        for subkeyword in sub_dict.keys():
            valid_keywords.add(subkeyword)
            keyword_to_group[subkeyword] = group_name

    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(
                process_single_file, 
                file, 
                prediction_set, 
                output_dir, 
                valid_keywords, 
                keyword_to_group, 
                map_keyword_dict, 
                args
            ): file for file in caption_files
        }
        
        # Process completed tasks with progress bar
        for future in tqdm(as_completed(future_to_file), total=len(caption_files), desc="Processing files"):
            file = future_to_file[future]
            try:
                key, success, error = future.result()
                if not success:
                    print(f"Error processing file '{key}': {error}")
            except Exception as e:
                print(f"Error processing file '{file}': {e}")
                traceback.print_exc()


def main(args):
    all_stations = config.final_stations
    for single_station in all_stations:
        args.area = single_station
        if args.model=="qwen":
            if args.dpo_type=="no":
                pred_path = os.path.join(args.folder,f"output_{args.model}",f"output_test_{args.area}.jsonl")
            else:
                pred_path = os.path.join(args.folder,f"output_{args.model}_{args.dpo_type}",f"output_test_{args.area}.jsonl")
        else:
            pred_path = os.path.join(args.folder,f"output_{args.model}_shot_{args.shot}",f"output_test_{args.area}.jsonl")
        # pdb.set_trace()
        print(single_station)
        print(pred_path)
        pred_contents = [eval(line) for line in open(pred_path, 'r').readlines()]

        # Dictionary to store the count of occurrences for each image_id
        image_id_counts = {}
        new_pred_contents = []

        map_json_path = "Qwen-VL-Series-Finetune/config/unique_keywords_map.json"

        with open(map_json_path, "r", encoding="utf-8") as f:
            map_keyword_dict = json.load(f)

        # Iterate through each sample in pred_contents
        for sample in pred_contents:
            image_id = sample['image_name'][0][-17:]
            if image_id in image_id_counts:
                image_id_counts[image_id] += 1
            else:
                image_id_counts[image_id] = 0

            # Create a new sample with the modified key
            new_sample = copy.deepcopy(sample)
            new_sample['image_list'] = sample['image_name']
            new_sample['image_name'] = f"{image_id}_{image_id_counts[image_id]}"
            new_pred_contents.append(new_sample)

        # Generating list of id's and corresponding files
        id_list = [x['image_name'] for x in new_pred_contents]
        caption_files = [f"{id}.json" for id in id_list]

        if args.model=="qwen":
            if args.dpo_type=="no":
                output_dir = os.path.join(args.folder,f'result_correctness_{args.model}',f'{args.model}_{args.area}')
            else:
                output_dir = os.path.join(args.folder,f"result_correctness_{args.model}_{args.dpo_type}",f"{args.model}_{args.area}")
        else:
            output_dir = os.path.join(args.folder,f'result_correctness_{args.model}',f'{args.model}_shot_{args.shot}_{args.area}')
        # Generate output directory if not exists.
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Preparing dictionary of question-answer sets
        prediction_set = {}
        for sample in new_pred_contents:
            id = sample['image_name']
            # question = sample['Q']
            # answer = sample[list(sample.keys())[0]]['A']
            answer = sample['A']
            pred = sample['P']

            if args.dpo_type == "dpo_accept_reject":
                accept = sample['accept']
                reject = sample['reject']
                original_score = sample['original_score']
                qa_set = {"q": sample['Q'],"image_name":sample["image_list"], "a": answer, "p": pred,"accept":accept,"reject":reject,"original_score":original_score}
            elif args.model=="qwen":
                qa_set = {"q":  sample['Q'], "a": answer, "p": pred, "daily_forecast":sample["daily_forecast"]}
            else:
                qa_set = {"a": answer, "p": pred, "daily_forecast":sample["daily_forecast"]}
            prediction_set[id] = qa_set

        while True:
            try:
                # Files that have not been processed yet.
                completed_files = os.listdir(output_dir)
                print(f"completed_files: {len(completed_files)}")

                # Files that have not been processed yet.
                incomplete_files = [f for f in caption_files if f not in completed_files]
                print(f"incomplete_files: {len(incomplete_files)}")
                if len(incomplete_files) == 0:
                    break
                annotate(prediction_set,incomplete_files,output_dir,map_keyword_dict, args, max_workers=args.max_workers)

            except Exception as e:
                traceback.print_exc()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-3")
    parser.add_argument("--area", default="qwen", help="The path to file containing prediction.")
    parser.add_argument("--type", default="single", help="The path to file containing prediction.")
    parser.add_argument("--long_type", default="short", help="The path to file containing prediction.")
    parser.add_argument("--model", default="gemini-2.5-flash", help="The path to file containing prediction.")
    parser.add_argument("--shot", default=2,type=int, help="The path to file containing prediction.")
    parser.add_argument("--folder", default="Qwen-VL-Series-Finetune/output", help="The path to file containing prediction.")
    parser.add_argument("--dpo_type", default="sft", help="The path to file containing prediction.")
    parser.add_argument("--max_workers", default=40, type=int, help="Maximum number of concurrent workers for processing caption files.")

    args = parser.parse_args()
    main(args)

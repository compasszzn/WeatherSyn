import os
import argparse
import json
import ast
import traceback
from tqdm import tqdm
from multiprocessing.pool import Pool
import random
import copy
import openai
import pdb
from openai import OpenAI
import config
import re
import time
llm_to_api = {
    "gpt-5": "gpt-5-2025-08-07",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "claude-3-5-sonnet-20240620": "claude-3-5-sonnet-20240620",
    "deepseek-chat":"deepseek-chat",
}

def init(model):
    if "gpt" in model:
        azure_endpoint = ""
        api_key = ""
        client = OpenAI(base_url = azure_endpoint,api_key=api_key)
    elif "gemini" in model or "claude" in model:
        azure_endpoint = ""
        api_key = ""
        client = OpenAI(base_url = azure_endpoint,api_key=api_key)
    elif "deepseek" in model:
        azure_endpoint = ""
        api_key = ""
        client = OpenAI(base_url = azure_endpoint,api_key=api_key)
    return client


def interaction(client, message_text,eval_model):
    completion = client.chat.completions.create(
        messages=message_text,
        model=llm_to_api[eval_model],
        seed=random.randint(0, 100000),
        temperature=0.3
    )
    return completion



def annotate(prediction_set, caption_files, output_dir, args, client):
    """
    Evaluates question and answer pairs using GPT-3
    Returns a score for correctness.
    """

    for file in tqdm(caption_files):
        key = file[:-5] # Strip file extension
        qa_set = prediction_set[key]
        # question = qa_set['q']
        answer = qa_set['a']

        pred_list = qa_set['p']
        try:
            message = [
                {
                    "role": "system",
                    "content":
                        "You are an expert meteorological evaluator specializing in assessing the quality of generated weather forecasts. "
                        "Here is a weather forecasting scenario, including the ground truth forecast and eight candidate predicted forecasts. "
                        "From the perspective of a professional weather analyst, you are required to rank the quality of these responses based on the following criteria:\n"
                        "(1) Consistency with the meteorological facts in the ground truth forecast (short for Fact.Cons);\n"
                        "(2) Quality of summarization of key weather signals without introducing misleading emphasis or irrelevant detail (short for Summ.Qual).\n\n"
                        "To help you rank these responses, we additionally provide background information including forecast period, key weather variables, and the reference forecast.\n\n"
                        "You should generate the response in the following format:\n"
                        "Fact.Cons: R11 > R2 ... > R1;\n"
                        "Summ.Qual: R11 > R2 ... > R1.\n"
                        "After the rankings, provide several sentences explaining your evaluation.\n\n"
                        "Important guidelines:\n"
                        "- Focus only on factual and meteorological correctness.\n"
                        "- Penalize hallucinated weather events or incorrect trends heavily.\n"
                        "- Overly verbose answers that obscure the core forecast should be ranked lower in Summ.Qual.\n"
                        "- Minor wording differences are acceptable if the facts are preserved."
                },
                {
                    "role": "user",
                    "content":
                        f"Ground Truth Forecast:\n{answer}\n\n"
                        "Candidate Forecasts:\n"
                        f"R1: {pred_list[0]}\n"
                        f"R2: {pred_list[1]}\n"
                        f"R3: {pred_list[2]}\n"
                        f"R4: {pred_list[3]}\n"
                        f"R5: {pred_list[4]}\n"
                        f"R6: {pred_list[5]}\n"
                        f"R7: {pred_list[6]}\n"
                        f"R8: {pred_list[7]}\n"
                        f"R9: {pred_list[8]}\n"
                        f"R10: {pred_list[9]}\n"
                        f"R11: {pred_list[10]}\n\n"
                        "Please rank them following the required format."
                }
            ]
        
            
            completion = interaction(client, message, args.eval_model)
            response_message = completion.choices[0].message.content
                

            result_qa_pair = [response_message, qa_set]

            # Save the question-answer pairs to a json file.
            with open(f"{output_dir}/{key}.json", "w") as f:
                json.dump(result_qa_pair, f)

        except Exception as e:
            print(f"Error processing file '{key}': {e}")
            traceback.print_exc()


def main(args, client):
    all_stations = config.final_stations
    for station in all_stations:
        models = ['output_gpt-4.1-mini_shot_2','output_gpt-5-nano_shot_2','output_gemini-2.5-flash_shot_2','output_claude-3-7-sonnet-20250219_shot_2','output_qwen_weatherqa','output_qwen_omniearth','output_gpt-5.2_shot_2','output_gemini-3_shot_2', 'output_qwen_sft','output_qwen_rft','output_qwen_dpo']
        new_pred_contents = {}
        for model in models:
            pred_path = os.path.join(args.folder,model,f"output_test_{station}.jsonl")
            pred_contents = [eval(line) for line in open(pred_path, 'r').readlines()]
            
            pred_contents = pred_contents[::10]  # 每5步取一个

            for sample in pred_contents:
                image_id = sample['image_name'][0][-17:]
                if image_id not in new_pred_contents:
                    new_pred_contents[image_id] = []
                # Create a new sample with the modified key
                new_sample = copy.deepcopy(sample)
                new_sample['image_list'] = sample['image_name']
                new_sample['image_name'] = f"{image_id}"
                new_pred_contents[image_id].append(new_sample)
        
        # Generating list of id's and corresponding files
        id_list = sorted(list(new_pred_contents.keys()))
        caption_files = [f"{id}.json" for id in id_list]
        output_dir = os.path.join(args.folder,'rebutal_result_correctness_llm',f'{station}_{args.eval_model}')
        # Generate output directory if not exists.
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Preparing dictionary of question-answer sets
        prediction_set = {}
        for key,samples in new_pred_contents.items():
            
            id = key
            # question = sample['Q']
            answer = samples[0]['A']
            pred_list = []
            for sample in samples:
                pred = sample['P']
                pred_list.append(pred)

            qa_set = {"a": answer, "p": pred_list}
            prediction_set[id] = qa_set
        
        while True:
            try:
                # Files that have not been processed yet.
                completed_files = os.listdir(output_dir)
                print(f"completed_files: {len(completed_files)}")

                # Files that have not been processed yet.
                incomplete_files = [f for f in caption_files if f not in completed_files]
                print(f"incomplete_files: {len(incomplete_files)}")

                # Break the loop when there are no incomplete files
                if len(incomplete_files) == 0:
                    break

                # Use a pool of workers to process the files in parallel.
                annotate(prediction_set,incomplete_files,output_dir, args, client)

            except Exception as e:
                traceback.print_exc()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-3")
    parser.add_argument("--folder", default="Qwen-VL-Series-Finetune/output", help="The path to file containing prediction.")
    parser.add_argument("--eval_model", default="gpt-5", help="The path to file containing prediction.")

    args = parser.parse_args()
    client = init(args.eval_model)
    main(args, client)
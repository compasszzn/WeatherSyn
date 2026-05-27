import os
import argparse
import json
import ast
import traceback
from tqdm import tqdm
from multiprocessing.pool import Pool
import random
import base64
from openai import OpenAI
import config

llm_to_api = {
    "gpt4": "gpt-4o-2024-08-06",
    # "gpt4mini": "gpt-4o-mini-2024-07-18",
    # "gpt": "gpt-3.5-turbo-0125",
    # "gpto3": "gpt-3.5-turbo-0125",
    "claude": "Claude-3.5-Sonnet",
    # "glm": "glm-4-plus",
    # "qwen72b": "Qwen2.5-72B-Instruct",
    # "llama8b": "meta-llama/Llama-3-8b-chat-hf",
    # "llama": "meta-llama/Llama-3-70b-chat-hf",
    # "gemma": "gemma-7b-it",
    # "mixtral": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    # "deepseek": "deepseek-chat",
    # "doubao": "ep-20250215195227-lg4pc",
    # "dsR1": "ep-20250215203640-lxb6j"
}

def init():
    client = OpenAI(
        base_url = "https://35.aigcbest.top/v1",
        api_key = 'sk-4PhY006ulJWLVjUf19B39a8f9bB34aBdA7B0C21e96B38873'
    )

    return client

def interaction(client, message_text):
    completion = client.chat.completions.create(
        messages=message_text,
        model=llm_to_api['gpt4'],
        seed=random.randint(0, 100000),
        temperature=0.3,
    )

    return completion

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
def annotate(prediction_set, caption_files, output_dir, args):
    """
    Evaluates question and answer pairs using GPT-3
    Returns a score for correctness.
    """
    if args.shot == 0:
        system_prompt=(
            f"As an AI assistant with expertise in weather forecasting, you are equipped to interpret a comprehensive figures that illustrating various weather variables crucial for understanding the latest weather conditions across the {config.AREA_NAME_MAP[area]}.\n"
            f"Your responsibility as a weather forecaster is to provide accurate and timely insights into weather conditions.\n")
    for file in tqdm(caption_files):
        key = file[:-5] # Strip file extension
        qa_set = prediction_set[int(key)]
        question = qa_set['Q']
        image_list = qa_set['image_name'][0:1]
        formatted = []
        for img in image_list:
            base64_image = encode_image(f"/hpc2hdd/home/mpeng885/zzn_data/data/processpng/{img}")
            formatted.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            })
        formatted.append({
            "type": "text",
            "text": question  # 假设问题字段是 question
        })
        try:
            message = [
                    {
                        "role": "system",
                        "content":system_prompt
                    },
                    {
                        "role": "user",
                        "content":formatted

                    }
                ]

            completion = interaction(client, message)
            # Convert response to a Python dictionary.
            response_message = completion.choices[0].message.content
            response_dict = {"P":[response_message]}
            result_qa_pair = [qa_set|response_dict]

            # Save the question-answer pairs to a json file.
            with open(f"{output_dir}/{key}.json", "w") as f:
                json.dump(result_qa_pair, f)

        except Exception as e:
            print(f"Error processing file '{key}': {e}")


def main(args):
    pred_path = os.path.join(args.pred_folder,f"annotation_test_{args.area}_{args.type}.json")
    with open(pred_path, 'r') as f:
        pred_contents = json.load(f)
    # pred_contents = pred_contents[:3]
    id_list = [x['id'] for x in pred_contents]
    caption_files = [f"{id}.json" for id in id_list]

    output_dir = os.path.join(args.output_dir,f"split_{args.area}_{args.type}")
    # Generate output directory if not exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Preparing dictionary of question-answer sets
    prediction_set = {}
    for sample in pred_contents:
        id = sample['id']
        question = sample['conversations'][0]['value']
        image = sample['image']
        answer = sample['conversations'][1]['value']
        qa_set = {"image_name": image,"Q": question,"A":answer}
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
            annotate(prediction_set,incomplete_files,args.output_dir, args)

        except Exception as e:
            traceback.print_exc()

    # Combine all the processed files into one
    combined_contents = []
    json_path = os.path.join(args.output_dir,f"output_{args.area}_{args.type}.jsonl")

    # Iterate through json files
    for file_name in tqdm(os.listdir(output_dir)):
        if file_name.endswith(".json"):
            file_path = os.path.join(output_dir, file_name)
            with open(file_path, "r") as json_file:
                content = json.load(json_file)
                combined_contents.extend(content)

    # Write combined content to a json file
    with open(json_path, "w") as fout:
        for item in combined_contents:
            fout.write(json.dumps(item) + "\n")
    print("All evaluation completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-3")
    parser.add_argument("--pred-folder", default="/hpc2hdd/home/mpeng885/zzn_data/json/datajson/annotation", help="The path to file containing prediction.")
    parser.add_argument("--output-dir", default="/hpc2hdd/home/mpeng885/zzn_data/json/datajson/output_gpt4o", help="The path to save annotation json files.")
    parser.add_argument("--shot", default=2,type=int, help="The path to save annotation final combined json file.")
    parser.add_argument("--area", default="box",type=str, help="The path to save annotation final combined json file.")
    parser.add_argument("--type", default="single",type=str, help="The path to save annotation final combined json file.")
    args = parser.parse_args()
    client = init()
    main(args)

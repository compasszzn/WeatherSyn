from sacrebleu import corpus_bleu
from rouge_score import rouge_scorer
import pdb
import re
import json
from openai import OpenAI
client = OpenAI(
    base_url = "http://localhost:8000/v1",
    api_key = "EMPTY"
)
map_json_path = "Qwen-VL-Series-Finetune/config/unique_keywords_map.json"

with open(map_json_path, "r", encoding="utf-8") as f:
    map_keyword_dict = json.load(f)
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

def f1_reward(completions, assistant, **kwargs):
    rewards = []
    valid_keywords = set()
    keyword_to_group = {}

    for group_name, sub_dict in map_keyword_dict.items():
        for subkeyword in sub_dict.keys():
            valid_keywords.add(subkeyword)
            keyword_to_group[subkeyword] = group_name
    print(completions)
    print(assistant)
    for pred, answer in zip(completions, assistant):
        pattern = re.compile(
            r"<<(\d{8}),\s*([A-Za-z]+)>>\s*Report:\s*(.*?)(?=<<\d{8},|\Z)",
            re.DOTALL
        )
        answer_matches = pattern.findall(answer)
        pred_matches = pattern.findall(pred)
        if len(answer_matches)==4 and len(pred_matches)==4:
            answer_results = []
            for date, weekday, report in answer_matches:
                answer_results.append({
                    "date": date,
                    "weekday": weekday,
                    "report": report.strip()
                })
            pred_results = []
            for date, weekday, report in pred_matches:
                pred_results.append( {
                    "date": date,
                    "weekday": weekday,
                    "report": report.strip()
                })
            while True:
                try:
                    pred_keyword_results = extract_all_keywords_with_llm(pred_results, map_keyword_dict)
                    answer_keyword_results = extract_all_keywords_with_llm(answer_results, map_keyword_dict)
                    if len(pred_keyword_results)!=4 or len(answer_keyword_results)!=4:
                        raise Exception("The number of keywords is not 4")
                    else:
                        for i in range(len(pred_keyword_results)):
                            pred_keyword_results[i]['keywords'] = list(set(pred_keyword_results[i]['keywords']) & valid_keywords)
                            pred_keyword_results[i]['keyword_groups'] = list({keyword_to_group[kw] for kw in pred_keyword_results[i]['keywords']})
                        for i in range(len(answer_keyword_results)):
                            answer_keyword_results[i]['keywords'] = list(set(answer_keyword_results[i]['keywords']) & valid_keywords)
                            answer_keyword_results[i]['keyword_groups'] = list({keyword_to_group[kw] for kw in answer_keyword_results[i]['keywords']})
                        date_f1_scores = []
                        for i in range(len(answer_keyword_results)):
                            if answer_keyword_results[i]['keywords'] == 0:
                                date_f1_scores.append(1)
                                continue
                            else:
                                TP = len(set(pred_keyword_results[i]['keywords']) & set(answer_keyword_results[i]['keywords']))
                                FP = len(set(pred_keyword_results[i]['keywords']) - set(answer_keyword_results[i]['keywords']))
                                FN = len(set(answer_keyword_results[i]['keywords']) - set(pred_keyword_results[i]['keywords']))
                                precision = TP / (TP + FP) if (TP + FP) > 0 else 0
                                recall = TP / (TP + FN) if (TP + FN) > 0 else 0
                                f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                                date_f1_scores.append(f1_score)
                        rewards.append(sum(date_f1_scores)/len(date_f1_scores))
                        break
                except Exception as e:
                    continue
        else:
            reward = 0.0
            rewards.append(reward)
    return rewards

def format_reward(completions, **kwargs):
    """Reward function that checks if the completion has a specific format."""
    pattern = re.compile(
        r"<<(\d{8}),\s*([A-Za-z]+)>>\s*Report:\s*(.*?)(?=<<\d{8},|\Z)",
        re.DOTALL
    )
    rewards = []
    for content in completions:
        matches = pattern.findall(content)
        # 如果匹配到4个pattern，格式正确
        reward = 1.0 if len(matches) == 4 else 0.0
        rewards.append(reward)
    return rewards#[1,0]

# def rougel_reward(completions, assistant, **kwargs):
#     rewards = []
#     for completion, sol in zip(completions, assistant):
#         cands  = completion
#         refs   = sol
#         reward = _rouge.score(cands, refs)["rougeL"].fmeasure
#         rewards.append(reward)
#     return rewards



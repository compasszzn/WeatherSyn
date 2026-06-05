import os
import json
import argparse
from pathlib import Path
from typing import Dict, Tuple, Set, Iterator
from collections import defaultdict
import re
from sacrebleu import corpus_bleu
from rouge_score import rouge_scorer
from nltk.translate.meteor_score import meteor_score
import nltk


def iter_all_area_json_files(base_folder: str) -> Iterator[Tuple[str, Path]]:

    base_folder = Path(base_folder)

    if not base_folder.exists():
        raise FileNotFoundError(f"Base folder not found: {base_folder}")

    for shot_dir in sorted(base_folder.iterdir()):
        if not shot_dir.is_dir():
            continue

        dir_name = shot_dir.name
        area_name = dir_name.split("_")[-1]

        for json_file in sorted(shot_dir.glob("*png_0.json")):
            yield area_name, json_file


def merge_all_json_files(base_folder: str) -> list:
    """
    将 base_folder 下所有 json 文件合并为一个 list
    """
    merged_data = []

    for area, json_path in iter_all_area_json_files(base_folder):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        merged_data.append({
            "area": area,
            "file_name": json_path.name,
            "data": data
        })

    return merged_data


def evaluate_result_folder(result_folder: str, base_path: str, rouge_scorer_instance):
    """评估单个result_folder的BLEU-1、ROUGE-L、Distinct-1和METEOR分数"""
    base_folder = os.path.join(base_path, result_folder)
    
    # 检查文件夹是否存在
    if not os.path.exists(base_folder):
        print(f"\nWarning: Folder not found: {base_folder}, skipping...")
        return None
    
    # 1. 合并所有 JSON
    merged_results = merge_all_json_files(base_folder)
    pattern = re.compile(
        r"<<(\d{8}),\s*([A-Za-z]+)>>\s*Report:\s*(.*?)(?=<<\d{8},|\Z)",
        re.DOTALL
    )
    
    # 存储每个样本的平均分数
    sample_averages = []
    
    # 4. 遍历 merged_results 计算 BLEU-1 和 ROUGE-L
    for result in merged_results:
        predict_sentence = result["data"][2]["p"]
        answer_sentence = result["data"][2]["a"]

        # ----------- answer and predict ----------
        answer_results = []
        predict_results = []
        answer_matches = pattern.findall(answer_sentence)
        predict_matches = pattern.findall(predict_sentence)
        for date, weekday, report in answer_matches:
            answer_results.append({
                "date": date,
                "weekday": weekday,
                "report": report.strip()
            })
        for date, weekday, report in predict_matches:
            predict_results.append({
                "date": date,
                "weekday": weekday,
                "report": report.strip()
            })
        
        # 计算每个report的BLEU-1、ROUGE-L、Distinct-1和METEOR，然后计算该样本的平均值
        bleu1_scores = []
        rouge_l_scores = []
        distinct1_scores = []
        meteor_scores = []
        min_len = min(len(answer_results), len(predict_results))
        for i in range(min_len):
            answer_report = answer_results[i]["report"]
            predict_report = predict_results[i]["report"]
            if answer_report == "No forecast available":
                continue
            # 计算BLEU-1 (使用precisions[0]，即1-gram precision)
            bleu_result = corpus_bleu([predict_report], [[answer_report]])
            bleu1 = bleu_result.precisions[0] / 100.0  # BLEU-1 precision (0-1范围)
            
            # 计算ROUGE-L (参数顺序: prediction, reference)
            rouge_result = rouge_scorer_instance.score(predict_report, answer_report)
            rouge_l = rouge_result["rougeL"].fmeasure  # ROUGE-L F1 score (0-1范围)
            
            # 计算Distinct-1: 唯一1-gram数量 / 总1-gram数量
            tokens = predict_report.split()
            if len(tokens) > 0:
                unique_tokens = len(set(tokens))
                distinct1 = unique_tokens / len(tokens)
            else:
                distinct1 = 0.0
            
            # 计算METEOR (参数顺序: reference, hypothesis)
            try:
                reference_tokens = answer_report.split()
                hypothesis_tokens = predict_report.split()
                if len(reference_tokens) > 0 and len(hypothesis_tokens) > 0:
                    meteor = meteor_score([reference_tokens], hypothesis_tokens)
                else:
                    meteor = 0.0
            except Exception:
                meteor = 0.0
            
            bleu1_scores.append(bleu1)
            rouge_l_scores.append(rouge_l)
            distinct1_scores.append(distinct1)
            meteor_scores.append(meteor)
        
        # 计算该样本的平均值
        if len(bleu1_scores) > 0:
            sample_avg_bleu1 = sum(bleu1_scores) / len(bleu1_scores)
            sample_avg_rouge_l = sum(rouge_l_scores) / len(rouge_l_scores)
            sample_avg_distinct1 = sum(distinct1_scores) / len(distinct1_scores)
            sample_avg_meteor = sum(meteor_scores) / len(meteor_scores)
            
            sample_averages.append({
                "area": result["area"],
                "file_name": result["file_name"],
                "avg_bleu1": round(sample_avg_bleu1, 4),
                "avg_rouge_l": round(sample_avg_rouge_l, 4),
                "avg_distinct1": round(sample_avg_distinct1, 4),
                "avg_meteor": round(sample_avg_meteor, 4),
                "count": len(bleu1_scores)
            })
    
    # 计算所有样本的平均值
    if len(sample_averages) > 0:
        total_bleu1 = sum(s["avg_bleu1"] for s in sample_averages)
        total_rouge_l = sum(s["avg_rouge_l"] for s in sample_averages)
        total_distinct1 = sum(s["avg_distinct1"] for s in sample_averages)
        total_meteor = sum(s["avg_meteor"] for s in sample_averages)
        avg_bleu1 = round(total_bleu1 / len(sample_averages), 4)
        avg_rouge_l = round(total_rouge_l / len(sample_averages), 4)
        avg_distinct1 = round(total_distinct1 / len(sample_averages), 4)
        avg_meteor = round(total_meteor / len(sample_averages), 4)
    else:
        avg_bleu1 = 0.0
        avg_rouge_l = 0.0
        avg_distinct1 = 0.0
        avg_meteor = 0.0
    
    return {
        "result_folder": result_folder,
        "avg_bleu1": avg_bleu1,
        "avg_rouge_l": avg_rouge_l,
        "avg_distinct1": avg_distinct1,
        "avg_meteor": avg_meteor,
        "total_samples": len(sample_averages)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate correctness results")

    parser.add_argument(
        "--result_folder",
        type=str,
        default=None,
        help="Result folder name (if not provided, will loop through all folders)"
    )

    parser.add_argument(
        "--base_path",
        type=str,
        default="Qwen-VL-Series-Finetune/output",
        help="Base path"
    )
    args = parser.parse_args()

    # 确保nltk的wordnet数据已下载（METEOR需要）
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    
    # 初始化ROUGE scorer
    rouge_scorer_instance = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    
    # 定义要循环处理的result_folder列表
    result_folders = [
        "result_correctness_qwen_rft",
        "result_correctness_qwen_sft",
        "result_correctness_qwen_dpo",
    ]
    
    # 如果指定了result_folder，只处理那一个
    if args.result_folder:
        result_folders = [args.result_folder]
    
    # 循环处理每个result_folder
    all_results = []
    for result_folder in result_folders:
        result = evaluate_result_folder(result_folder, args.base_path, rouge_scorer_instance)
        if result:
            all_results.append(result)
            # 打印单个结果
            print("\n" + "="*60)
            print(f"Result Folder: {result['result_folder']}")
            print("Overall Average (across all samples):")
            print("="*60)
            print(f"Average BLEU-1: {result['avg_bleu1']}")
            print(f"Average ROUGE-L: {result['avg_rouge_l']}")
            print(f"Average Distinct-1: {result['avg_distinct1']}")
            print(f"Average METEOR: {result['avg_meteor']}")
            print(f"Total samples evaluated: {result['total_samples']}")
            print("="*60)
    
    # 打印汇总结果
    if len(all_results) > 1:
        print("\n" + "="*60)
        print("Summary of All Results:")
        print("="*60)
        print(f"{'Result Folder':<50} {'BLEU-1':<10} {'ROUGE-L':<10} {'Distinct-1':<12} {'METEOR':<10} {'Samples':<10}")
        print("-"*60)
        for result in all_results:
            print(f"{result['result_folder']:<50} {result['avg_bleu1']:<10} {result['avg_rouge_l']:<10} {result['avg_distinct1']:<12} {result['avg_meteor']:<10} {result['total_samples']:<10}")
        print("="*60)

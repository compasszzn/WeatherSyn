import os
import json
import argparse
from pathlib import Path
from typing import Dict, Tuple, Set, Iterator
from collections import defaultdict


def load_keyword_map(map_json_path: str) -> Tuple[Set[str], Dict[str, str], Dict[str, list]]:
    """
    加载关键词映射文件
    """
    with open(map_json_path, "r", encoding="utf-8") as f:
        map_keyword_dict = json.load(f)

    valid_keywords = set()
    keyword_to_group = {}
    group_to_keyword = {}

    for group_name, sub_dict in map_keyword_dict.items():
        group_to_keyword[group_name] = list(sub_dict.keys())

    for group_name, sub_dict in map_keyword_dict.items():
        for keyword in sub_dict.keys():
            valid_keywords.add(keyword)
            keyword_to_group[keyword] = group_name

    return valid_keywords, keyword_to_group, group_to_keyword


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


def init_results(group_to_keyword: Dict[str, list]) -> Dict[str, Dict[str, dict]]:
    """
    初始化统计字典
    """
    results = defaultdict(dict)
    for group, keywords in group_to_keyword.items():
        for kw in keywords:
            results[group][kw] = {
                "TP": 0,
                "FP": 0,
                "FN": 0,
                "count": 0,
                "precision": 0.0,
                "recall": 0.0
            }
    return results


def compute_keyword_metrics(all_results: Dict[str, Dict[str, dict]]):
    """
    根据 TP/FP/FN 计算 keyword-level precision / recall
    """
    for group, kw_dict in all_results.items():
        for kw, stats in kw_dict.items():
            tp = stats["TP"]
            fp = stats["FP"]
            fn = stats["FN"]

            stats["precision"] = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            stats["recall"] = tp / (tp + fn) if (tp + fn) > 0 else 0.0

def save_group_metrics_ordered(group_metrics: dict, output_path: str):
    """
    按指定顺序保存 group-level metrics 到 JSON/CSV/LaTeX
    """
    ordered_groups = [
        "Temperature",
        "wind",
        "Humidity",
        "Frontal_System",
        "Pressure_System",
        "Synoptic_Feature",
        "Wind_Flow_System",
        "Event"
    ]

    ordered_metrics = {group: group_metrics[group] for group in ordered_groups if group in group_metrics}

    # 保存 JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ordered_metrics, f, indent=2, ensure_ascii=False)

    print(f"Ordered group metrics saved to: {output_path}")



def compute_group_weighted_metrics(all_results: Dict[str, Dict[str, dict]]) -> Dict[str, dict]:
    """
    根据 keyword-level precision/recall 和 count 计算 group-level weighted precision/recall
    使用简单倒数加权：出现次数越多，权重越低，并计算 weighted F1
    """
    group_metrics = {}

    for group, kw_dict in all_results.items():
        # 权重 = 1 / count
        weights = {kw: 1 / v["count"] if v["count"] > 0 else 0 for kw, v in kw_dict.items()}
        total_weight = sum(weights.values())

        total_count = sum(v["count"] for v in kw_dict.values())

        if total_weight == 0:
            group_metrics[group] = {
                "weighted_precision": 0.0,
                "weighted_recall": 0.0,
                "weighted_f1": 0.0,
                "total_count": total_count
            }
            continue

        wp = sum(v["precision"] * weights[kw] for kw, v in kw_dict.items()) / total_weight
        wr = sum(v["recall"] * weights[kw] for kw, v in kw_dict.items()) / total_weight

        # 计算 F1
        if wp + wr > 0:
            wf1 = 2 * wp * wr / (wp + wr)
        else:
            wf1 = 0.0

        group_metrics[group] = {
            "weighted_precision": wp,
            "weighted_recall": wr,
            "weighted_f1": wf1,
            "total_count": total_count
        }

    return group_metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate correctness results")

    parser.add_argument(
        "--result_folder",
        type=str,
        default="result_correctness_qwen_sft_small",
        help="Result folder name"
    )

    parser.add_argument(
        "--base_path",
        type=str,
        default="/hpc2hdd/home/mpeng885/zzn_data/jsonbig/datajson/process_data/synoptic/datajson",
        help="Base path"
    )

    parser.add_argument(
        "--map_json_path",
        type=str,
        default="Qwen-VL-Series-Finetune/config/unique_keywords_map.json",
        help="Keyword map json path"
    )

    args = parser.parse_args()

    base_folder = os.path.join(args.base_path, args.result_folder)

    # 1. 合并所有 JSON
    merged_results = merge_all_json_files(base_folder)

    # 2. 加载关键词映射
    valid_keywords, keyword_to_group, group_to_keyword = load_keyword_map(args.map_json_path)

    # 3. 初始化统计结构
    all_results = init_results(group_to_keyword)

    # 4. 遍历 merged_results 统计 TP / FP / FN / count
    for result in merged_results:
        predict_keywords_list = result["data"][0]["pred_keyword"]
        answer_keywords_list = result["data"][1]["answer_keyword"]

        for date_idx in range(len(predict_keywords_list)):
            pred = set(predict_keywords_list[date_idx]["keywords"])
            gt = set(answer_keywords_list[date_idx]["keywords"])
            if len(gt) == 0:
                continue
            gt_groups = answer_keywords_list[date_idx]["keyword_groups"]

            for group in gt_groups:
                for keyword in group_to_keyword[group]:
                    is_gt = keyword in gt
                    is_pred = keyword in pred

                    if is_gt and is_pred:
                        all_results[group][keyword]["TP"] += 1
                        all_results[group][keyword]["count"] += 1
                    elif is_gt and not is_pred:
                        all_results[group][keyword]["FN"] += 1
                        all_results[group][keyword]["count"] += 1
                    elif not is_gt and is_pred:
                        all_results[group][keyword]["FP"] += 1
                        
                    else:
                        pass

    # 5. 计算 keyword-level precision/recall
    compute_keyword_metrics(all_results)

    # 6. 计算 group-level weighted precision/recall
    group_metrics = compute_group_weighted_metrics(all_results)

    # 7. 保存结果
    keyword_results_path = os.path.join(base_folder, "all_keyword_results.json")
    group_results_path = os.path.join(base_folder, "group_weighted_metrics.json")

    save_group_metrics_ordered(group_metrics, group_results_path)
    save_group_metrics_ordered(all_results, keyword_results_path)

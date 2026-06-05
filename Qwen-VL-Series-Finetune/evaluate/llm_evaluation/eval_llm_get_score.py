import os
import json
import re
from collections import defaultdict
from pathlib import Path
from tqdm import tqdm
import argparse
import traceback

def extract_ranking_from_text(response_message):
    """
    从response_message中提取Fact.Cons和Summ.Qual的排序列表
    提取所有R标识符，前9个作为Fact.Cons，第10-18个作为Summ.Qual
    处理等号（并列）的情况
    """
    # 提取所有R标识符（按出现顺序）
    all_ranks = re.findall(r'R\d+', response_message)
    
    fact_cons_ranking = None
    summ_qual_ranking = None
    
    # 前9个R作为Fact.Cons
    if len(all_ranks) >= 9:
        fact_cons_ranking = all_ranks[:11]
    
    # 第10-18个R作为Summ.Qual
    if len(all_ranks) >= 18:
        summ_qual_ranking = all_ranks[11:22]
    
    return fact_cons_ranking, summ_qual_ranking


def get_top1_ranks(ranking_list):
    """
    获取排名列表中的top-1（考虑等号并列的情况）
    如果有等号，并列第一的都算top-1
    
    这里ranking_list是从文本中提取的，按顺序排列
    但在原始文本中可能有等号，我们需要从原始文本中检查等号
    
    由于我们在extract_ranking_from_text中已经提取了所有R标识符，
    这里我们需要检查原始文本中的等号模式来确定并列情况
    但为了简化，我们可以假设：
    - 如果ranking_list的第一个元素出现多次，那么可能有并列
    - 实际上，我们需要在提取时就考虑等号
    
    重新设计：在提取排名时，如果遇到等号，应该将等号连接的都视为同一排名
    """
    if not ranking_list:
        return []
    
    # 对于提取的列表，第一个就是top-1
    # 但实际上，如果原文本中有等号，我们需要在提取时就处理
    # 目前先返回第一个元素，因为等号的情况需要在提取时处理
    return [ranking_list[0]]


def extract_ranking_with_equality(response_message):
    """
    提取top-1排名（最高排名），考虑等号（并列）的情况
    从"Fact"开始，找到第一个R，如果是等号就继续加入，如果是>就停止
    同样从"Summ"开始处理
    """
    
    def find_top1_ranks_from_keyword(text, keyword):
        """
        从指定的关键词开始，找到第一个R，然后根据后面的符号决定是否加入更多R
        如果后面是=号，继续加入下一个R；如果是>号，停止
        返回top-1的R列表（可能有并列）
        """
        # 找到关键词的位置（不区分大小写）
        keyword_pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        keyword_match = keyword_pattern.search(text)
        if not keyword_match:
            return None
        
        # 从关键词位置开始搜索
        start_pos = keyword_match.end()
        text_from_keyword = text[start_pos:]
        
        # 找到第一个R
        first_rank_match = re.search(r'R\d+', text_from_keyword)
        if not first_rank_match:
            return None
        
        top1_ranks = []
        current_pos = first_rank_match.end()
        
        # 获取第一个R
        first_rank = first_rank_match.group()
        top1_ranks.append(first_rank)
        
        # 检查这个R后面的符号
        while current_pos < len(text_from_keyword):
            # 跳过空格
            while current_pos < len(text_from_keyword) and text_from_keyword[current_pos] == ' ':
                current_pos += 1
            
            if current_pos >= len(text_from_keyword):
                break
            
            next_char = text_from_keyword[current_pos]
            
            if next_char == '=':
                # 如果是等号，跳过等号和空格，找到下一个R
                current_pos += 1
                while current_pos < len(text_from_keyword) and text_from_keyword[current_pos] == ' ':
                    current_pos += 1
                
                # 查找下一个R
                next_rank_match = re.search(r'R\d+', text_from_keyword[current_pos:])
                if next_rank_match:
                    next_rank = next_rank_match.group()
                    top1_ranks.append(next_rank)
                    current_pos = current_pos + next_rank_match.end()
                else:
                    break
            elif next_char == '>':
                # 如果是>号，停止
                break
            else:
                # 其他字符，停止
                break
        
        return top1_ranks if top1_ranks else None
    
    # 从"Fact"开始查找top-1
    fact_cons_top1 = find_top1_ranks_from_keyword(response_message, 'Fact')
    
    # 从"Summ"开始查找top-1
    summ_qual_top1 = find_top1_ranks_from_keyword(response_message, 'Summ')
    
    return fact_cons_top1, summ_qual_top1


def process_all_results(base_dir):
    """
    处理所有模型的结果，统计top-1百分比
    对于每个JSON文件，收集所有模型的排名，统计每个R作为top-1的次数
    """
    base_path = Path(base_dir)
    
    # 收集所有station
    stations = set()
    model_folders = {}
    
    # 遍历所有文件夹，提取station和model信息
    for folder in base_path.iterdir():
        if not folder.is_dir():
            continue
        
        folder_name = folder.name
        # 格式: STATION_MODEL
        parts = folder_name.split('_', 1)
        if len(parts) == 2:
            station = parts[0]
            model = parts[1]
            stations.add(station)
            if station not in model_folders:
                model_folders[station] = {}
            model_folders[station][model] = folder
    
    # 存储每个station每个文件的top-1统计
    # file_top1[station][file_name][metric] = set of top1 ranks from all models
    file_top1 = defaultdict(lambda: defaultdict(lambda: {
        'Fact.Cons': [],
        'Summ.Qual': []
    }))
    
    # 第一步：收集所有模型对每个文件的评价
    for station in tqdm(sorted(stations), desc="Collecting rankings"):
        if station not in model_folders:
            continue
        
        for model, model_folder in model_folders[station].items():
            # 读取该模型文件夹下的所有json文件
            json_files = list(model_folder.glob("*.json"))
            
            for json_file in tqdm(json_files, desc=f"{station}_{model}", leave=False):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if len(data) >= 1:
                        response_message = data[0]
                        file_name = json_file.name
                        
                        # 提取top-1排名（考虑等号）
                        fact_cons_top1, summ_qual_top1 = extract_ranking_with_equality(response_message)
                        
                        if fact_cons_top1:
                            # fact_cons_top1已经是一个列表，包含top-1的R（可能有并列）
                            file_top1[station][file_name]['Fact.Cons'].extend(fact_cons_top1)
                        
                        if summ_qual_top1:
                            # summ_qual_top1已经是一个列表，包含top-1的R（可能有并列）
                            file_top1[station][file_name]['Summ.Qual'].extend(summ_qual_top1)
                
                except Exception as e:
                    print(f"Error processing {json_file}: {e}")
                    traceback.print_exc()
                    continue
    
    # 第二步：统计每个R作为top-1的百分比
    top1_counts = {
        'Fact.Cons': defaultdict(int),
        'Summ.Qual': defaultdict(int)
    }
    total_files_count = 0
    total_votes_count = {
        'Fact.Cons': 0,
        'Summ.Qual': 0
    }
    
    # 对每个文件，统计所有模型中每个R作为top-1的次数
    for station in file_top1:
        for file_name in file_top1[station]:
            total_files_count += 1
            
            for metric in ['Fact.Cons', 'Summ.Qual']:
                if file_name in file_top1[station] and metric in file_top1[station][file_name]:
                    # 该文件所有模型的top-1列表
                    top1_list = file_top1[station][file_name][metric]
                    
                    # 统计该文件的投票总数（包括并列的情况）
                    total_votes_count[metric] += len(top1_list)
                    
                    # 统计每个R出现的次数
                    for rank in top1_list:
                        top1_counts[metric][rank] += 1
    
    # 计算top-1百分比（基于总投票次数）
    top1_percentages = {
        'Fact.Cons': {},
        'Summ.Qual': {}
    }
    
    for metric in ['Fact.Cons', 'Summ.Qual']:
        total_votes = total_votes_count[metric]
        for rank in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9','R10','R11']:
            count = top1_counts[metric][rank]
            # 百分比基于总投票次数
            percentage = (count / total_votes * 100) if total_votes > 0 else 0.0
            top1_percentages[metric][rank] = {
                'count': count,
                'percentage': round(percentage, 2)
            }
    
    return {
        'top1_percentages': top1_percentages,
        'total_files': total_files_count,
        'total_votes': total_votes_count
    }


def print_results(results):
    """
    打印Top-1排名百分比
    """
    top1_percentages = results.get('top1_percentages', {})
    total_votes = results.get('total_votes', {})
    
    print("Top-1 Ranking Percentages")
    print("(Percentage of top-1 votes where each response is ranked as the best one)")
    print("=" * 80)
    
    # Fact.Cons Top-1百分比
    print("\nFact.Cons Top-1 Percentages:")
    fact_cons_top1 = top1_percentages.get('Fact.Cons', {})
    sorted_fact_cons_top1 = sorted(fact_cons_top1.items(), 
                                   key=lambda x: x[1]['percentage'], 
                                   reverse=True)
    fc_total = total_votes.get('Fact.Cons', 0)
    for rank, data in sorted_fact_cons_top1:
        print(f"  {rank}: {data['percentage']:.2f}% ({data['count']}/{fc_total})")
    
    # Summ.Qual Top-1百分比
    print("\nSumm.Qual Top-1 Percentages:")
    summ_qual_top1 = top1_percentages.get('Summ.Qual', {})
    sorted_summ_qual_top1 = sorted(summ_qual_top1.items(), 
                                   key=lambda x: x[1]['percentage'], 
                                   reverse=True)
    sq_total = total_votes.get('Summ.Qual', 0)
    for rank, data in sorted_summ_qual_top1:
        print(f"  {rank}: {data['percentage']:.2f}% ({data['count']}/{sq_total})")


def main():
    parser = argparse.ArgumentParser(description="Calculate top-1 ranking percentages from LLM evaluation results")
    parser.add_argument(
        "--base_dir",
        type=str,
        default="Qwen-VL-Series-Finetune/output/rebutal_result_correctness_llm",
        help="Base directory containing all model results"
    )
    
    args = parser.parse_args()
    
    # 处理所有结果
    results = process_all_results(args.base_dir)
    
    # 打印结果
    print_results(results)


if __name__ == "__main__":
    main()


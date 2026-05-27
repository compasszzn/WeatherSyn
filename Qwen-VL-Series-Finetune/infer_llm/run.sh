# areas=('box' 'hk' 'lox' 'lwx' 'mtr' 'okx' 'pbz' 'pqr' 'sew' 'vef')
areas=('mtr' 'okx' 'pbz' 'pqr' 'sew' 'vef')

# # 遍历循环
for area in "${areas[@]}"
do
    echo "Running area: $area"
    python /home/zinanzheng/project/video2text/Qwen2-VL-Finetune/evaluate/infer_llm/step2_weatherqa_zeroshot_gpt5.py \
        --area "$area" \
        --type 'single' \
        --shot 0 \
        --model 'gpt5'
done

# 遍历循环
# for area in "${areas[@]}"
# do
#     echo "Running area: $area"
#     python /home/zinanzheng/project/video2text/Qwen2-VL-Finetune/evaluate/infer_llm/step2_weatherqa_zeroshot_claude.py \
#         --area "$area" \
#         --type 'single' \
#         --shot 0 \
#         --model 'geminif'
# done
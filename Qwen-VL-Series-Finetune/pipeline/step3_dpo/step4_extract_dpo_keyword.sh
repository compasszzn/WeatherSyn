#!/bin/bash

# areas=('box' 'hk' 'lox' 'lwx' 'mtr' 'okx' 'pbz' 'pqr' 'sew' 'vef')


python Qwen-VL-Series-Finetune/evaluate/automatic_claim_evaluation/eval_llm_keyword_multi.py \
    --area "$area" \
    --model "qwen" \
    --type "single" \
    --folder "Qwen-VL-Series-Finetune/output" \
    --dpo_type "dpo"
    

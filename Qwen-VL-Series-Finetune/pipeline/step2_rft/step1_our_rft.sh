#!/bin/bash

#SBATCH -p i64m1tga800u
#SBATCH --cpus-per-task=4 
#SBATCH --gres=gpu:2
#SBATCH --output=/hpc2hdd/home/zzheng078/jhaidata/video2text/Qwen2-VL-Finetune/output_%j.log

# module load cuda/12.4
# module load ffmpeg
# source ~/.bashrc
conda activate qwenvl
cd Qwen-VL-Series-Finetune
# export CUDA_HOME=/usr/local/cuda-12.4
export DS_SKIP_CUDA_CHECK=1
# You can use 2B instead of 7B
# MODEL_NAME="Qwen/Qwen2-VL-7B-Instruct"
# MODEL_NAME="Qwen/Qwen2-VL-2B-Instruct"
MODEL_NAME="Qwen/Qwen3-VL-8B-Instruct"
# MODEL_NAME="Qwen/Qwen2.5-VL-7B-Instruct"

export PYTHONPATH=src:$PYTHONPATH

# GLOBAL_BATCH_SIZE=128
# BATCH_PER_DEVICE=16
# NUM_DEVICES=4

GLOBAL_BATCH_SIZE=32
BATCH_PER_DEVICE=2
NUM_DEVICES=8
GRAD_ACCUM_STEPS=$((GLOBAL_BATCH_SIZE / (BATCH_PER_DEVICE * NUM_DEVICES)))

# --include localhost:2,3
deepspeed --master_port 5600 src/train/train_sft.py \
    --use_liger False \
    --deepspeed scripts/zero3_offload.json \
    --model_id $MODEL_NAME \
    --data_path /WSInstruct/json/rft/annotation_train_merged.json \
    --image_folder /WSInstruct/processpng_synoptic_small \
    --remove_unused_columns False \
    --freeze_vision_tower False \
    --freeze_llm False \
    --freeze_merger False \
    --bf16 True \
    --fp16 False \
    --disable_flash_attn2 False \
    --output_dir /model/WeathersynRFT \
    --num_train_epochs 1 \
    --per_device_train_batch_size $BATCH_PER_DEVICE \
    --gradient_accumulation_steps $GRAD_ACCUM_STEPS \
    --image_min_pixels $((256 * 28 * 28)) \
    --image_max_pixels $((512 * 28 * 28)) \
    --learning_rate 5e-6 \
    --merger_lr 1e-5 \
    --vision_lr 2e-6 \
    --weight_decay 0.1 \
    --warmup_ratio 0.03 \
    --lr_scheduler_type "cosine" \
    --logging_steps 1 \
    --tf32 True \
    --gradient_checkpointing True \
    --report_to tensorboard \
    --lazy_preprocess True \
    --save_strategy "steps" \
    --save_steps 400 \
    --save_total_limit 10 \
    --dataloader_num_workers 4
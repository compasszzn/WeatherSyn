conda activate qwenvl
cd Qwen-VL-Series-Finetune
export CUDA_HOME=/usr/local/cuda
export DS_SKIP_CUDA_CHECK=1
export PYTHONPATH=src:$PYTHONPATH
export CUDA_VISIBLE_DEVICES=2
python Qwen-VL-Series-Finetune/src/infer/infer_single_path.py \
    --model-base Qwen/Qwen3-VL-8B-Instruct \
    --model-path /model/WeathersynRFT \
    --question_file /WSInstruct/json/test \
    --answer_file Qwen-VL-Series-Finetune/output/output_qwen_rft \
    --image-path /WSInstruct/processpng_synoptic_small \
    --temperature 0.3 \
    --task test
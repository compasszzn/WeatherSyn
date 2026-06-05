CUDA_VISIBLE_DEVICES=0,1,2,3 python -m vllm.entrypoints.openai.api_server \
    --model model/Qwen2.5-72B-Instruct \
    --tensor-parallel-size 4 \
    --max-model-len 4096 \
    --max-num-seqs 64 \
    --gpu-memory-utilization 0.95 \
    --port 8000
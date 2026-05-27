#!/bin/bash
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export DS_SKIP_CUDA_CHECK=1
cd LLaMA-Factory

llamafactory-cli train examples/our/qwen3_vl_full_sft.yaml
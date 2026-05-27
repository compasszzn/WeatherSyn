# 🌍 WeatherSyn: An Instruction Tuning MLLM For Weather Forecasting Report Generation

This is the **official PyTorch Lightning implementation** of the paper:  
**WeatherSyn: An Instruction Tuning MLLM For Weather Forecasting Report Generation**, accepted at **ICML 2026**.  
[[📄 arXiv]](https://arxiv.org/abs/2605.07522)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hanjq17/GMN/blob/main/LICENSE)

---


## Installation

### Environments

- Ubuntu 22.04
- Nvidia-Driver 550.120
- Cuda version 12.8

Install the required packages using `environment.yaml`.

### Using `requirements.txt`

```bash
conda create -n qwenvl python=3.11
conda activate qwenvl
pip install -r requirements.txt -f https://download.pytorch.org/whl/cu128
pip install qwen-vl-utils
pip install flash-attn --no-build-isolation
```
### Training and Evaluation Pipeline

#### SFT 

Qwen-VL-Series-Finetune/pipeline/step1_sft

#### RFt

Qwen-VL-Series-Finetune/pipeline/step2_rft

#### DPO

Qwen-VL-Series-Finetune/pipeline/step3_dpo

## TODO

- [x] Training Code
- [x] Automatic Claim Evaluation Code
- [ ] Reference Evaluation Code
- [ ] LLM Evaluation Code
- [ ] Dataset Construction Pipeline
- [ ] Upload Dataset
- [ ] Upload Model


## Acknowledgement

This project is based on

- [Qwen-VL-Series-Finetune](https://github.com/2U1/Qwen-VL-Series-Finetune): Open-source projcet of finetuning Qwen-VL-Series.
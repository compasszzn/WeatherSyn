# 🌍 WeatherSyn: An Instruction Tuning MLLM For Weather Forecasting Report Generation

This is the **official PyTorch Lightning implementation** of the paper:  
**WeatherSyn: An Instruction Tuning MLLM For Weather Forecasting Report Generation**, accepted at **ICML 2026**.  
[![arXiv](https://img.shields.io/badge/arXiv-2510.04017-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.07522)
[![ICML 2026](https://img.shields.io/badge/ICML-2026-blue)](https://icml.cc/virtual/2026/poster/63486)
[![Dataset](https://img.shields.io/badge/Dataset-Hugging%20Face-ffd21e?logo=huggingface&logoColor=yellow)](https://huggingface.co/datasets/compasszzn/WSInstruct)
[![Model](https://img.shields.io/badge/Model-Hugging%20Face-ffd21e?logo=huggingface&logoColor=yellow)](https://huggingface.co/compasszzn/WeatherSynSFT)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hanjq17/GMN/blob/main/LICENSE)

---

## Overview

**WeatherSyn** is a multimodal large language model (MLLM) that takes meteorological
chart images (e.g. ERA5 / HRES synoptic charts) together with a natural-language
instruction, and produces human-readable **weather forecasting reports**. The model
is built on the **Qwen-VL series** and trained with a three-stage instruction-tuning
recipe — **SFT → RFT → DPO** — on the **WSInstruct** dataset.

## TODO
- [x] Upload Dataset
- [x] Upload Model
- [x] Training Code
- [x] Automatic Claim Evaluation Code
- [x] Reference Evaluation Code
- [x] LLM Evaluation Code



## Repository Structure

```
WeatherSyn/
├── Qwen-VL-Series-Finetune/      # Core training / inference / evaluation code (Qwen-VL based)
│   ├── pipeline/                 # End-to-end run scripts for each training stage
│   │   ├── step1_sft/            # Supervised Fine-Tuning
│   │   ├── step2_rft/            # Rejection / Reinforced Fine-Tuning
│   │   └── step3_dpo/            # Direct Preference Optimization
│   ├── src/                      # Model, dataset, training and inference source
│   ├── evaluate/                 # Evaluation code (claim / keyword / LLM scoring)
│   ├── config/                   # Keyword maps and other configs
│   └── scripts/                  # DeepSpeed (ZeRO) configs, helpers
├── LLaMA-Factory/                # Used for the DPO stage (llamafactory-cli)
└── requirements.txt
```

## Installation

### Environments

- Ubuntu 22.04
- Nvidia-Driver 550.120
- Cuda version 12.8

### Using `requirements.txt`

```bash
conda create -n qwenvl python=3.11
conda activate qwenvl
pip install -r requirements.txt -f https://download.pytorch.org/whl/cu128
pip install qwen-vl-utils
pip install flash-attn --no-build-isolation
```

## Dataset & Model

- **Dataset (WSInstruct):** [compasszzn/WSInstruct](https://huggingface.co/datasets/compasszzn/WSInstruct)
- **Model (WeatherSyn-SFT):** [compasszzn/WeatherSynSFT](https://huggingface.co/compasszzn/WeatherSynSFT)
- **Model (WeatherSyn-RFT):** [compasszzn/WeatherSynSFT](https://huggingface.co/compasszzn/WeatherSynRFT)
- **Model (WeatherSyn-DPO):** [compasszzn/WeatherSynSFT](https://huggingface.co/compasszzn/WeatherSynDPO)

After downloading, the training/inference scripts expect the data laid out as:

```
WSInstruct/
├── json/
│   ├── sft/
│   │    ├──annotation_train_merged.json # Total annotations
│   │    ├──annotation_train_[...].json # Regional split annotations
│   ├── rft/
│   │    ├──annotation_train_merged.json # Total annotations
│   │    ├──annotation_train_[...].json # Regional split annotations
│   ├── dpo/
│   │    ├──annotation_train_merged.json # Total annotations
│   │    ├──annotation_train_[...].json # Regional split annotations
│   └── test/
│   │    ├──annotation_test_merged.json # Total annotations
│   │    ├──annotation_trest_[...].json # Regional split annotations
└── processpng_synoptic_small/    # images
```

Update the `--data_path`, `--image_folder` and related paths in the pipeline scripts
to point at your local download location.

## Training and Evaluation Pipeline

The full recipe is split into three stages, each under
`Qwen-VL-Series-Finetune/pipeline/`. Every stage shares the same five-step workflow:
**train → infer on test set → deploy a judge LLM → extract keywords/claims → compute F1.**

| Step | Script | Purpose |
| ---- | ------ | ------- |
| 1 | `step1_*.sh`           | Train the model for this stage |
| 2 | `step2_infer_*_test.sh`| Run inference on the test set |
| 3 | `step3_deployment_qwen.sh` | **Automatic Claim Evaluation** Serve a judge LLM (vLLM, e.g. Qwen2.5-72B) for |
| 4 | `step4_extract_*_keyword.sh` | **Automatic Claim Evaluation** Extract weather claims/keywords from generations |
| 5 | `step5_compute_f1.sh`  | **Automatic Claim Evaluation** Score extracted claims against references (F1) |
| 6 | `step6_reference_evaluation.sh`  | **Reference Evaluation** Compute BLEU-1, ROUGE-L, METEOR score |
| 7 | `step7_llm_evaluation.sh`  | **LLM Evaluation** LLM rank the results |
### Stage 1 — SFT (Supervised Fine-Tuning)

```bash
bash Qwen-VL-Series-Finetune/pipeline/step1_sft/step1_our_sft.sh
```

Fine-tunes `Qwen/Qwen3-VL-8B-Instruct` (vision tower, LLM and merger all trainable)
with DeepSpeed ZeRO-3 offload on the SFT split of WSInstruct.

### Stage 2 — RFT (Rejection / Reinforced Fine-Tuning)

```bash
bash Qwen-VL-Series-Finetune/pipeline/step2_rft/step1_our_rft.sh
```

Continues training on the RFT split, using the same training entry point with
higher-quality / filtered responses.

### Stage 3 — DPO (Direct Preference Optimization)

```bash
bash Qwen-VL-Series-Finetune/pipeline/step3_dpo/step1_our_dpo.sh
```

Runs preference optimization via **LLaMA-Factory**
(`llamafactory-cli train examples/our/qwen3_vl_full_sft.yaml`).


## Baseline Inference

```
step1 generate few shot prompt
python Qwen-VL-Series-Finetune/baseline/step1_process_annotation_to_prompt.py
step2 fewshot result
python Qwen-VL-Series-Finetune/baseline/step2_baseline_fewshot.py
step3 zeroshot result
python Qwen-VL-Series-Finetune/baseline/step2_baseline_zeroshot.py
```

## Citation
If you find this work useful, please consider citing: 
```bibtex 
@article{zheng2026weathersyn,
  title={WeatherSyn: An Instruction Tuning MLLM For Weather Forecasting Report Generation},
  author={Zheng, Zinan and Liu, Yang and Chen, Nuo and Zheng, Juepeng and Cheng, Hong and Li, Jia},
  journal={arXiv preprint arXiv:2605.07522},
  year={2026}
}
```
## Acknowledgement

This project is based on

- [Qwen-VL-Series-Finetune](https://github.com/2U1/Qwen-VL-Series-Finetune): Open-source project of finetuning Qwen-VL-Series.
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory): Unified efficient fine-tuning framework, used for the DPO stage.

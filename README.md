# 🌍 WeatherSyn: An Instruction Tuning MLLM For Weather Forecasting Report Generation

This is the **official PyTorch Lightning implementation** of the paper:  
**WeatherSyn: An Instruction Tuning MLLM For Weather Forecasting Report Generation**, accepted at **ICML 2026**.  
[![arXiv](https://img.shields.io/badge/arXiv-2510.04017-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2605.07522)
[![ICML 2026](https://img.shields.io/badge/ICML-2026-blue)](https://icml.cc/virtual/2026/poster/63486)
[![Dataset](https://img.shields.io/badge/Dataset-Hugging%20Face-ffd21e?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/compasszzn/WSInstruct)
[![Model](https://img.shields.io/badge/Model-Hugging%20Face-ffd21e?logo=huggingface&logoColor=black)](https://huggingface.co/compasszzn/WeatherSynSFT)
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
- [ ] Reference Evaluation Code
- [ ] LLM Evaluation Code
- [ ] Dataset Construction Pipeline


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

<!-- ### Evaluation

The **Automatic Claim Evaluation** lives in
`Qwen-VL-Series-Finetune/evaluate/automatic_claim_evaluation/`:

- `eval_llm_keyword_multi.py` — extract weather keywords/claims from model outputs
  (uses the deployed judge LLM).
- `score.py` — aggregate keyword-level **F1** against references, using the keyword
  map in `Qwen-VL-Series-Finetune/config/unique_keywords_map.json`. -->

<!-- ## Dataset Construction

Scripts for building WSInstruct and the benchmark from raw meteorological data are
under `Dataset_and_Benchmark/` and `data_download/`, covering data download
(ERA5 / HRES), region filtering, location resolution, chart rendering (`process_png`)
and weather-glossary extraction.

 -->

## Acknowledgement

This project is based on

- [Qwen-VL-Series-Finetune](https://github.com/2U1/Qwen-VL-Series-Finetune): Open-source project of finetuning Qwen-VL-Series.
- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory): Unified efficient fine-tuning framework, used for the DPO stage.

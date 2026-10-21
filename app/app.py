from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import yaml

API_URL = st.sidebar.text_input("TuneForge API", "http://localhost:8000")

st.set_page_config(page_title="TuneForge Studio", page_icon="⚒️", layout="wide")
st.title("⚒️ TuneForge Studio")
st.caption(
    "Build, launch, track, and evaluate parameter-efficient LLM adaptation experiments."
)

tabs = st.tabs(["New experiment", "Runs", "Evaluation", "About"])

with tabs[0]:
    st.subheader("Create a LoRA experiment")

    try:
        hardware = requests.get(f"{API_URL}/capabilities", timeout=3).json()
    except Exception:
        hardware = {"can_train": False, "gpu_name": None, "recommended_precision": "unknown"}

    gpu_label = hardware.get("gpu_name") or "No CUDA GPU detected"
    st.info(
        f"Host: {gpu_label} · recommended precision: "
        f"{hardware.get('recommended_precision', 'unknown')}"
    )

    col1, col2 = st.columns(2)

    with col1:
        model_name = st.text_input(
            "Base model",
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        )
        dataset_source = st.selectbox(
            "Dataset source",
            ["Hugging Face", "Upload CSV/JSONL"],
        )
        num_samples = st.number_input("Training samples", 1, 100000, 1000)
        max_seq_length = st.select_slider(
            "Max sequence length",
            options=[128, 256, 512, 1024, 2048],
            value=512,
        )

    uploaded_path = None
    dataset_name = "databricks/databricks-dolly-15k"

    with col2:
        if dataset_source == "Hugging Face":
            dataset_name = st.text_input(
                "Hugging Face dataset",
                "databricks/databricks-dolly-15k",
            )
        else:
            uploaded = st.file_uploader(
                "Upload instruction data",
                type=["csv", "json", "jsonl"],
            )
            if uploaded:
                upload_dir = Path("studio_uploads")
                upload_dir.mkdir(exist_ok=True)
                uploaded_path = upload_dir / uploaded.name
                uploaded_path.write_bytes(uploaded.getbuffer())

                try:
                    if uploaded.name.endswith(".csv"):
                        preview = pd.read_csv(uploaded_path).head(5)
                    else:
                        preview = pd.read_json(uploaded_path, lines=uploaded.name.endswith(".jsonl")).head(5)
                    st.dataframe(preview, use_container_width=True)
                except Exception as exc:
                    st.warning(f"Preview unavailable: {exc}")

        instruction_field = st.text_input("Instruction field", "instruction")
        context_field = st.text_input("Context field", "context")
        response_field = st.text_input("Response field", "response")

    st.markdown("### LoRA")
    l1, l2, l3, l4 = st.columns(4)
    with l1:
        rank = st.selectbox("Rank (r)", [4, 8, 16, 32], index=1)
    with l2:
        alpha = st.selectbox("Alpha", [8, 16, 32, 64], index=1)
    with l3:
        dropout = st.number_input("Dropout", 0.0, 0.5, 0.05, step=0.01)
    with l4:
        targets = st.multiselect(
            "Target modules",
            ["q_proj", "k_proj", "v_proj", "o_proj"],
            default=["q_proj", "v_proj"],
        )

    st.markdown("### Training")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        epochs = st.number_input("Epochs", 1, 10, 1)
    with t2:
        batch = st.selectbox("Batch size", [1, 2, 4, 8], index=2)
    with t3:
        grad_accum = st.selectbox("Grad accumulation", [1, 2, 4, 8, 16], index=2)
    with t4:
        learning_rate = st.number_input(
            "Learning rate",
            min_value=0.000001,
            max_value=0.01,
            value=0.0002,
            format="%.6f",
        )

    seed = st.number_input("Seed", 0, 999999, 42)
    effective_batch = batch * grad_accum
    st.metric("Effective batch size", effective_batch)

    payload = {
        "model_name": model_name,
        "dataset_name": dataset_name if dataset_source == "Hugging Face" else "",
        "dataset": {
            "source": "huggingface" if dataset_source == "Hugging Face" else "local",
            "path": str(uploaded_path) if uploaded_path else None,
            "instruction_field": instruction_field,
            "context_field": context_field,
            "response_field": response_field,
        },
        "seed": int(seed),
        "num_train_samples": int(num_samples),
        "max_seq_length": int(max_seq_length),
        "lora": {
            "r": int(rank),
            "alpha": int(alpha),
            "dropout": float(dropout),
            "target_modules": targets,
        },
        "training": {
            "learning_rate": float(learning_rate),
            "epochs": int(epochs),
            "per_device_batch_size": int(batch),
            "gradient_accumulation_steps": int(grad_accum),
            "weight_decay": 0.01,
            "lr_scheduler_type": "cosine",
            "warmup_fraction": 0.03,
            "gradient_checkpointing": True,
            "logging_steps": 10,
        },
        "generation": {"max_new_tokens": 256, "do_sample": False},
        "output_dir": "studio-managed",
        "evaluation_prompts": [
            "Explain what a neural network is in 2-3 sentences.",
            "What are three tips for better sleep?",
        ],
    }

    with st.expander("Generated experiment configuration"):
        st.code(yaml.safe_dump(payload, sort_keys=False), language="yaml")

    launch = st.checkbox(
        "Launch immediately on this host",
        value=False,
        help="Requires the API host to have a CUDA GPU.",
    )

    if st.button("Create experiment", type="primary"):
        try:
            response = requests.post(
                f"{API_URL}/experiments",
                json={"config": payload, "launch": launch},
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            st.success(f"Created {result['run_id']} · status: {result['status']}")
            st.json(result)
        except Exception as exc:
            st.error(f"Could not create experiment: {exc}")

with tabs[1]:
    st.subheader("Experiment runs")
    try:
        runs = requests.get(f"{API_URL}/experiments", timeout=5).json()
        if runs:
            st.dataframe(pd.DataFrame(runs), use_container_width=True)
        else:
            st.info("No Studio runs yet.")
    except Exception as exc:
        st.warning(f"API unavailable: {exc}")

with tabs[2]:
    st.subheader("Base vs adapted evidence")
    comparison_path = Path("artifacts/tinyllama-dolly/evaluation/comparison.json")

    if not comparison_path.exists():
        st.info("Run an evaluation to populate the comparison artifact.")
    else:
        payload = json.loads(comparison_path.read_text(encoding="utf-8"))
        for index, item in enumerate(payload.get("comparisons", []), start=1):
            st.markdown(f"### Prompt {index}")
            st.code(item["prompt"])
            left, right = st.columns(2)
            with left:
                st.markdown("**Base model**")
                st.write(item["baseline_response"])
            with right:
                st.markdown("**LoRA adapted**")
                st.write(item["adapted_response"])

with tabs[3]:
    st.subheader("What TuneForge Studio demonstrates")
    st.write(
        "TuneForge Studio is a self-service experiment layer over the reusable TuneForge "
        "training engine. It lets users define model, dataset, LoRA, and training settings; "
        "checks host capability; persists experiment configuration; and can launch a real "
        "GPU-backed training process when CUDA is available."
    )

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import yaml

st.set_page_config(page_title="TuneForge Studio", page_icon="⚒️", layout="wide")

API_URL = st.sidebar.text_input(
    "TuneForge API",
    os.getenv("TUNEFORGE_API_URL", "http://localhost:8000"),
)

st.title("⚒️ TuneForge Studio")
st.caption(
    "Build, launch, track, and evaluate parameter-efficient LLM adaptation experiments."
)

tabs = st.tabs(["New experiment", "Runs", "Adapters", "Evaluation", "About"])

with tabs[0]:
    st.subheader("Create an adaptation experiment")

    try:
        hardware = requests.get(f"{API_URL}/capabilities", timeout=3).json()
    except requests.RequestException:
        hardware = {
            "can_train": False,
            "gpu_name": None,
            "recommended_precision": "unknown",
        }

    gpu_label = hardware.get("gpu_name") or "No CUDA GPU detected"
    st.info(
        f"Host: {gpu_label} · recommended precision: "
        f"{hardware.get('recommended_precision', 'unknown')}"
    )

    col1, col2 = st.columns(2)

    with col1:
        method = st.radio(
            "Adaptation method",
            ["LoRA", "QLoRA (4-bit)"],
            horizontal=True,
        )
        model_name = st.text_input(
            "Base model",
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        )
        dataset_source = st.selectbox(
            "Dataset source",
            ["Hugging Face", "Upload CSV/JSON/JSONL"],
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
                        preview = pd.read_json(
                            uploaded_path,
                            lines=uploaded.name.endswith(".jsonl"),
                        ).head(5)

                    st.dataframe(preview, use_container_width=True)
                except (ValueError, OSError, pd.errors.ParserError) as exc:
                    st.warning(f"Preview unavailable: {exc}")

        instruction_field = st.text_input("Instruction field", "instruction")
        context_field = st.text_input("Context field", "context")
        response_field = st.text_input("Response field", "response")

    st.markdown("### Adapter configuration")
    l1, l2, l3, l4 = st.columns(4)

    with l1:
        rank = st.selectbox("Rank (r)", [4, 8, 16, 32], index=1)

    with l2:
        alpha = st.selectbox("Alpha", [8, 16, 32, 64], index=1)

    with l3:
        dropout = st.number_input(
            "Dropout",
            0.0,
            0.5,
            0.05,
            step=0.01,
        )

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
        grad_accum = st.selectbox(
            "Grad accumulation",
            [1, 2, 4, 8, 16],
            index=2,
        )

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

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Effective batch", effective_batch)
    metric2.metric("Quantization", "4-bit NF4" if method.startswith("QLoRA") else "None")
    metric3.metric(
        "Host training",
        "Ready" if hardware.get("can_train") else "Config only",
    )

    payload = {
        "model_name": model_name,
        "dataset_name": (
            dataset_name
            if dataset_source == "Hugging Face"
            else ""
        ),
        "dataset": {
            "source": (
                "huggingface"
                if dataset_source == "Hugging Face"
                else "local"
            ),
            "path": str(uploaded_path) if uploaded_path else None,
            "instruction_field": instruction_field,
            "context_field": context_field,
            "response_field": response_field,
        },
        "quantization": {
            "mode": "4bit" if method.startswith("QLoRA") else "none",
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
        "generation": {
            "max_new_tokens": 256,
            "do_sample": False,
        },
        "output_dir": "studio-managed",
        "evaluation_prompts": [
            "Explain what a neural network is in 2-3 sentences.",
            "What are three tips for better sleep?",
        ],
    }

    try:
        validation = requests.post(
            f"{API_URL}/experiments/validate",
            json={"config": payload, "launch": False},
            timeout=3,
        ).json()
    except requests.RequestException:
        validation = {"valid": False, "errors": ["API unavailable"]}

    if validation.get("valid"):
        st.success("Configuration validation passed.")
    else:
        st.warning(" · ".join(validation.get("errors", [])))

    with st.expander("Generated experiment YAML"):
        st.code(
            yaml.safe_dump(payload, sort_keys=False),
            language="yaml",
        )

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

            st.success(
                f"Created {result['run_id']} · "
                f"status: {result['status']}"
            )
            st.json(result)
        except requests.RequestException as exc:
            st.error(f"Could not create experiment: {exc}")

with tabs[1]:
    st.subheader("Experiment runs")

    try:
        queue_state = requests.get(
            f"{API_URL}/queue",
            timeout=5,
        ).json()
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Queued", queue_state.get("pending", 0))
        q2.metric("Running", queue_state.get("claimed", 0))
        q3.metric("Succeeded", queue_state.get("done", 0))
        q4.metric("Failed", queue_state.get("failed", 0))
    except requests.RequestException as exc:
        st.caption(f"Queue status unavailable: {exc}")

    try:
        runs = requests.get(
            f"{API_URL}/experiments",
            timeout=5,
        ).json()
    except requests.RequestException as exc:
        runs = []
        st.warning(f"API unavailable: {exc}")

    if not runs:
        st.info("No Studio runs yet.")
    else:
        runs_df = pd.DataFrame(runs)
        st.dataframe(runs_df, use_container_width=True)

        run_ids = [run["run_id"] for run in runs]
        selected_run = st.selectbox("Inspect run", run_ids)

        detail = requests.get(
            f"{API_URL}/experiments/{selected_run}",
            timeout=5,
        ).json()

        d1, d2, d3 = st.columns(3)
        d1.metric("Status", detail.get("status", "unknown"))
        d2.metric("Worker", detail.get("worker_id") or "—")
        d3.metric("Updated", detail.get("updated_at", "—"))

        action1, action2 = st.columns(2)

        if (
            detail.get("status") in {"ready", "queued"}
            and action1.button("Cancel run", key=f"cancel-{selected_run}")
        ):
            response = requests.post(
                f"{API_URL}/experiments/{selected_run}/cancel",
                timeout=5,
            )
            if response.ok:
                st.success("Run cancelled.")
                st.rerun()
            else:
                st.error(response.text)

        if (
            detail.get("status") in {"failed", "cancelled"}
            and action2.button("Retry run", key=f"retry-{selected_run}")
        ):
                response = requests.post(
                f"{API_URL}/experiments/{selected_run}/retry",
                timeout=5,
            )
            if response.ok:
                st.success("Run re-queued.")
                st.rerun()
            else:
                st.error(response.text)

        telemetry = requests.get(
            f"{API_URL}/experiments/{selected_run}/telemetry",
            timeout=5,
        ).json().get("points", [])

        if telemetry:
            telemetry_df = pd.DataFrame(telemetry)

            if "step" in telemetry_df and "loss" in telemetry_df:
                loss_df = telemetry_df[["step", "loss"]].dropna().set_index("step")
                if not loss_df.empty:
                    st.markdown("#### Training loss")
                    st.line_chart(loss_df)

            if "step" in telemetry_df and "gpu_allocated_gb" in telemetry_df:
                memory_df = (
                    telemetry_df[["step", "gpu_allocated_gb"]]
                    .dropna()
                    .set_index("step")
                )
                if not memory_df.empty:
                    st.markdown("#### GPU memory allocated")
                    st.line_chart(memory_df)

            st.dataframe(telemetry_df, use_container_width=True)
        else:
            st.info("No telemetry points have been emitted for this run yet.")

        if st.checkbox("Show recent training log"):
            log_payload = requests.get(
                f"{API_URL}/experiments/{selected_run}/logs",
                params={"max_lines": 150},
                timeout=5,
            ).json()
            st.code("\n".join(log_payload.get("lines", [])))

with tabs[2]:
    st.subheader("Adapter registry")

    try:
        adapters = requests.get(
            f"{API_URL}/adapters",
            timeout=5,
        ).json()
    except requests.RequestException as exc:
        adapters = []
        st.warning(f"API unavailable: {exc}")

    if adapters:
        adapter_rows = []

        for item in adapters:
            params = item.get("parameters", {})
            adapter_rows.append(
                {
                    "adapter_id": item.get("adapter_id"),
                    "base_model": item.get("model_name"),
                    "method": (
                        "QLoRA"
                        if item.get("quantization_mode") == "4bit"
                        else "LoRA"
                    ),
                    "size_mb": round(
                        item.get("size_bytes", 0) / (1024 ** 2),
                        2,
                    ),
                    "trainable_percent": round(
                        params.get("trainable_percentage", 0),
                        4,
                    ),
                    "lifecycle": item.get("lifecycle", "candidate"),
                    "created_at": item.get("created_at"),
                }
            )

        st.dataframe(
            pd.DataFrame(adapter_rows),
            use_container_width=True,
        )

        adapter_ids = [item["adapter_id"] for item in adapters]
        selected_adapter = st.selectbox(
            "Manage adapter lifecycle",
            adapter_ids,
        )
        selected_record = next(
            item for item in adapters
            if item["adapter_id"] == selected_adapter
        )
        current_state = selected_record.get("lifecycle", "candidate")
        st.write(f"Current lifecycle: **{current_state}**")

        transitions = {
            "candidate": ["validated", "archived"],
            "validated": ["production", "archived"],
            "production": ["archived"],
            "archived": [],
        }
        allowed = transitions.get(current_state, [])

        if allowed:
            target_state = st.selectbox(
                "Transition to",
                allowed,
                key=f"state-{selected_adapter}",
            )
            reason = st.text_input(
                "Reason",
                key=f"reason-{selected_adapter}",
            )

            if st.button(
                "Apply lifecycle transition",
                key=f"transition-{selected_adapter}",
            ):
                response = requests.post(
                    f"{API_URL}/adapters/{selected_adapter}/transition",
                    json={
                        "target_state": target_state,
                        "reason": reason or "Studio lifecycle transition.",
                    },
                    timeout=5,
                )
                if response.ok:
                    st.success(
                        f"{selected_adapter} moved to {target_state}."
                    )
                    st.rerun()
                else:
                    st.error(response.text)
        else:
            st.info("Archived adapters have no further lifecycle transitions.")
    else:
        st.info("No trained adapters registered yet.")

with tabs[3]:
    st.subheader("Base vs adapted evidence")
    comparison_path = Path(
        "artifacts/tinyllama-dolly/evaluation/comparison.json"
    )

    if not comparison_path.exists():
        st.info(
            "Run an evaluation to populate the comparison artifact."
        )
    else:
        comparison_payload = json.loads(
            comparison_path.read_text(encoding="utf-8")
        )

        scorecard = comparison_payload.get("scorecard", {})
        baseline_average = scorecard.get("baseline_average", {})
        adapted_average = scorecard.get("adapted_average", {})

        if scorecard:
            st.markdown("### Evaluation scorecard")
            score_rows = []

            for metric in [
                "latency_seconds",
                "generated_tokens",
                "tokens_per_second",
                "word_count",
                "repetition_ratio",
            ]:
                score_rows.append(
                    {
                        "metric": metric,
                        "baseline": baseline_average.get(metric),
                        "adapted": adapted_average.get(metric),
                    }
                )

            st.dataframe(
                pd.DataFrame(score_rows),
                use_container_width=True,
            )
            st.caption(
                "These are descriptive runtime/output metrics, not a claim of semantic quality."
            )

        for index, item in enumerate(
            comparison_payload.get("comparisons", []),
            start=1,
        ):
            st.markdown(f"### Prompt {index}")
            st.code(item["prompt"])

            left, right = st.columns(2)

            with left:
                st.markdown("**Base model**")
                st.write(item["baseline_response"])
                if item.get("baseline_metrics"):
                    st.json(item["baseline_metrics"])

            with right:
                st.markdown("**Adapted model**")
                st.write(item["adapted_response"])
                if item.get("adapted_metrics"):
                    st.json(item["adapted_metrics"])

with tabs[4]:
    st.subheader("What TuneForge Studio demonstrates")
    st.write(
        "TuneForge Studio is a self-service LLM adaptation workbench over "
        "a reusable training engine. It separates experiment definition, "
        "GPU execution, telemetry, adapter persistence, and evaluation."
    )

    st.markdown(
        """
        **Implemented today**
        - LoRA and 4-bit QLoRA experiment configuration
        - Hugging Face and uploaded instruction datasets
        - GPU-aware precision selection
        - FastAPI experiment control plane
        - persisted experiment IDs and configuration
        - telemetry JSONL for loss and GPU memory
        - versioned adapter registry
        - controlled base-vs-adapted evaluation

        **Next production milestones**
        - remote GPU workers and queueing
        - authentication and multi-user isolation
        - richer automatic evaluation
        - Dockerized deployment
        - adapter promotion/version lifecycle
        """
    )

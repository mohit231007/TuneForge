from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="TuneForge", page_icon="⚒️", layout="wide")
st.title("⚒️ TuneForge")
st.caption("LoRA adaptation evidence: configuration, adapter footprint, and base-vs-adapted outputs.")

comparison_path = Path("artifacts/tinyllama-dolly/evaluation/comparison.json")
metadata_path = Path("artifacts/tinyllama-dolly/run_metadata.json")

left, right = st.columns(2)

with left:
    st.subheader("Experiment")
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        parameters = metadata.get("parameters", {})
        training = metadata.get("training", {})
        adapter = metadata.get("adapter", {})
        st.metric("Trainable %", f"{parameters.get('trainable_percentage', 0):.4f}%")
        st.metric("Training steps", training.get("global_step", "—"))
        size_mb = adapter.get("size_bytes", 0) / (1024 ** 2)
        st.metric("Adapter size", f"{size_mb:.2f} MB")
    else:
        st.info("Run training to generate run_metadata.json.")

with right:
    st.subheader("Why LoRA?")
    st.write(
        "TuneForge updates a small adapter parameter set while keeping the base model frozen. "
        "The reference configuration targets q_proj and v_proj attention projections."
    )

st.divider()
st.subheader("Base vs adapted responses")

if not comparison_path.exists():
    st.warning(
        "No evaluation artifact found yet. Run the evaluation command and refresh this page."
    )
else:
    payload = json.loads(comparison_path.read_text(encoding="utf-8"))
    for index, item in enumerate(payload.get("comparisons", []), start=1):
        st.markdown(f"### Prompt {index}")
        st.code(item["prompt"])
        base_col, adapted_col = st.columns(2)
        with base_col:
            st.markdown("**Base model**")
            st.write(item["baseline_response"])
        with adapted_col:
            st.markdown("**LoRA adapted**")
            st.write(item["adapted_response"])
        st.divider()

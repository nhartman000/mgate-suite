#!/usr/bin/env python3
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.quaternion import Point3D, KADMON_3D_POINTS
from engine.macro_triangulation import MacroTriangulation
from engine.mobius import TriadicMobiusTransport, CANONICAL_MOS, MobiusOperatorString
from engine.model_adapter import call_model

st.set_page_config(page_title="Kadmon Lexical Interferometer", layout="wide", initial_sidebar_state="expanded")

# UI Styling
st.markdown("""
<style>
    .big-font { font-size:20px !important; color: #00FF00; font-family: monospace; }
    .emoji-string { font-size: 24px; background-color: #1E1E1E; padding: 10px; border-radius: 5px; letter-spacing: 2px;}
    .stApp { background-color: #0a0a0a; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

st.title("🌌 Kadmon Topologic Tomography & Alignment Engine")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Engine Parameters")
    execution_mode = st.radio("2nd Order Mode", ["COUPLE (Projective)", "PAIR (Unified)"])
    model_selection = st.selectbox("LLM Backend", ["gemini-pro", "mock-deterministic"])
    seed = st.number_input("Deterministic Seed", value=42)
    st.markdown("---")
    st.header("👤 Human Position")
    z_depth = st.slider("Abstraction Depth (Z)", min_value=0.0, max_value=1.0, value=0.0, step=0.1, help="0.0 = Literal/Factual, 1.0 = Highly Abstract")
    y_stance = st.slider("Dialectical Stance (Y)", min_value=-0.5, max_value=0.5, value=0.0, step=0.1)

# Main Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 1. Input Prompt")
    user_prompt = st.text_area("Enter Query / Problem Space:", height=150)
    trigger = st.button("🚀 EXECUTE KADMON PIPELINE", use_container_width=True)

with col2:
    st.subheader("📐 2. Cognitive Geometry (Macro-Triangle)")
    plot_placeholder = st.empty()

# Execution Logic
if trigger and user_prompt:
    st.markdown("---")
    st.subheader("🔬 3. Triadic Möbius Transport (TMT v1.0)")
    
    # Run 3D Alignment
    tri = MacroTriangulation()
    tri.set_query_position(-0.75, y_stance, z_depth)
    tri.execute_second_order(mode=execution_mode.split()[0], agent1_z=z_depth, agent2_z=z_depth)
    alignment = tri.calculate_alignment()
    
    user_pos = KADMON_3D_POINTS["user_anchor"]
    query_pos = Point3D(-0.75, y_stance, z_depth)
    ai_pos = tri.ai_resolved_point
    
    # Draw 3D Plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter3d(
        x=[user_pos.x], y=[user_pos.y], z=[user_pos.z],
        mode='markers+text', name='👤 User (-1.31)',
        marker=dict(size=8, color='blue'), text=["USER"]
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[query_pos.x], y=[query_pos.y], z=[query_pos.z],
        mode='markers+text', name='❓ Query (-0.75)',
        marker=dict(size=8, color='orange'), text=["QUERY"]
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[ai_pos.x], y=[ai_pos.y], z=[ai_pos.z],
        mode='markers+text', name='🤖 AI Resolved',
        marker=dict(size=10, color='green'), text=["AI MODEL"]
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[user_pos.x, query_pos.x, ai_pos.x, user_pos.x],
        y=[user_pos.y, query_pos.y, ai_pos.y, user_pos.y],
        z=[user_pos.z, query_pos.z, ai_pos.z, user_pos.z],
        mode='lines', name='Macro-Triangle',
        line=dict(color='cyan', width=2)
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-2, 0], title='X (Determinism)'),
            yaxis=dict(range=[-1, 1], title='Y (Stance)'),
            zaxis=dict(range=[-0.5, 1.5], title='Z (Abstraction)')
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=400,
        paper_bgcolor="#0a0a0a",
        font=dict(color="#ffffff")
    )
    
    plot_placeholder.plotly_chart(fig, use_container_width=True)
    
    area = alignment['alignment_gap_area']
    if area < 0.1:
        st.success(f"✅ Perfect Alignment | Alignment Gap Area: {area:.4f}")
    else:
        st.warning(f"⚠️ Misalignment Detected | Alignment Gap Area: {area:.4f}")

    # Run Lexical Interferometry
    class Adapter:
        def call(self, prompt):
            return call_model(prompt, seed)
    
    tmt = TriadicMobiusTransport(Adapter())
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.write("🟢 **Start (S0)** -> Sent to A")
        st.markdown(f"<div class='emoji-string'>{CANONICAL_MOS}</div>", unsafe_allow_html=True)
        time.sleep(0.5)
    
    with st.spinner("Running TMT loop..."):
        result = tmt.execute_loop(CANONICAL_MOS)
    
    with col_b:
        st.write("🟠 **Twist Injected (S2t)** -> Sent to C")
        st.markdown(f"<div class='emoji-string'>{result['S2t']}</div>", unsafe_allow_html=True)
        time.sleep(0.5)
    
    with col_c:
        st.write("🔴 **Returned (S3)** -> Canonicalized")
        st.markdown(f"<div class='emoji-string'>{result['S3']}</div>", unsafe_allow_html=True)
    
    if result['distortion_detected']:
        st.error(f"**Holonomy Vector Detected:** Latent space is non-orientable. Twist delta = {result['holonomy']['twist_delta']}")
    else:
        st.success("**No Distortion:** Flat orientable manifold detected.")

    # Final Output
    st.markdown("---")
    st.subheader("📄 Final AI Semantic Response")
    
    response = call_model(user_prompt, seed)
    st.success(response)
    
    with st.expander("View .QSON Audit Trace"):
        st.json({
            "trace_id": st.session_state.get('run_trace_id', 'TRJ_xxxx'),
            "kadmon_alignment": alignment,
            "holonomy_result": result['holonomy'],
            "distortion_detected": result['distortion_detected']
        })

st.caption("Kadmon MRI Monitor v1.0 | Dark Mode recommended")

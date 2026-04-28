import streamlit as st
import os
import time
import subprocess
import glob
import re
import json
import pandas as pd
import sympy as sp
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="GRAV - Galaxy Rotation Analyze Viewer", layout="wide", initial_sidebar_state="expanded")

# ASCII 아트 로딩 화면
GRAV_SPLASH = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        ░██████╗░██████╗░░█████╗░██╗░░░██╗            ║
    ║        ██╔════╝░██╔══██╗██╔══██╗██║░░░██║            ║
    ║        ██║░░██╗░██████╔╝███████║╚██╗░██╔╝            ║
    ║        ██║░░╚██╗██╔══██╗██╔══██║░╚████╔╝░            ║
    ║        ╚██████╔╝██║░░██║██║░░██║░░╚██╔╝░░            ║
    ║        ░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░            ║
    ║                                                       ║
    ║           Galaxy Rotation Analyze Viewer       ║
    ║                                                       ║
    ║                  ∴ · ∘ ◦ ● ◦ ∘ · ∴                   ║
    ║              ∘ ◦ ● ◉ ▣ GRAV ▣ ◉ ● ◦ ∘                ║
    ║                  ∴ · ∘ ◦ ● ◦ ∘ · ∴                   ║
    ║                                                       ║
    ║              Loading astronomical data...            ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
"""

class GravityDiscoveryApp:
    def __init__(self):
        if 'initialized' not in st.session_state:
            st.session_state.initialized = False
            st.session_state.current_page = 1
            st.session_state.is_running = False
            st.session_state.last_results = None

    def show_splash(self):
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(f"```\n{GRAV_SPLASH}\n```")
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.005)
                progress_bar.progress(i + 1)
        placeholder.empty()
        st.session_state.initialized = True

    def sidebar(self):
        st.sidebar.markdown(f"## ▣ GRAV Control Panel")
        data_path = st.sidebar.text_input("Data Directory", value="sparc_data/")
        
        st.sidebar.markdown("### ⚙️ Hyperparameters")
        epochs = st.sidebar.slider("Neural Training Epochs", 10, 2000, 1000)
        pysr_iter = st.sidebar.slider("Symbolic Iterations", 1, 200, 100)
        
        st.sidebar.markdown("### 🧹 Data Cleaning")
        chi2_cutoff = st.sidebar.number_input("Chi2 Cutoff (Important)", value=30.0, min_value=0.1, max_value=1000.0, step=5.0)
        
        st.sidebar.markdown("---")
        run_btn = st.sidebar.button("🚀 EXECUTE DISCOVERY", use_container_width=True, type="primary", disabled=st.session_state.is_running)
        
        results_dir = st.sidebar.text_input("Results Directory", value="results")
        
        return {
            "data": data_path,
            "epochs": epochs,
            "pysr_iter": pysr_iter,
            "chi2_cutoff": chi2_cutoff,
            "out": results_dir,
            "run_btn": run_btn
        }

    def run_backend(self, config):
        st.session_state.is_running = True
        cmd = [
            "python", "main.py",
            "--data", config["data"],
            "--epochs", str(config["epochs"]),
            "--pysr_iter", str(config["pysr_iter"]),
            "--chi2_cutoff", str(config["chi2_cutoff"]),
            "--out", config["out"]
        ]
        
        with st.status("🌌 GRAV: Executing Discovery Pipeline...", expanded=True) as status:
            st.write(f"Executing: `{' '.join(cmd)}`")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
            
            log_placeholder = st.empty()
            logs = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    logs.append(line.strip())
                    log_placeholder.code("\n".join(logs[-15:])) # Show last 15 lines
            
            if process.returncode == 0:
                status.update(label="▣ Discovery Complete!", state="complete")
            else:
                status.update(label="❌ Error during execution", state="error")
                st.error(f"Backend failed with exit code {process.returncode}")
        
        st.session_state.is_running = False
        st.rerun()

    def display_gallery(self, results_dir):
        st.write("---")
        st.header("🖼️ Discovery Results Gallery (Multi-Galaxy View)")
        
        # Detect ALL comparison pages
        png_files = glob.glob(os.path.join(results_dir, "comparison_page_*.png"))
        if not png_files:
            st.info("No result images found. Please run the discovery pipeline.")
            return

        # Sort by page number
        def extract_page_num(f):
            match = re.search(r'comparison_page_(\d+).png', f)
            return int(match.group(1)) if match else 0
        
        png_files.sort(key=extract_page_num)
        total_pages = len(png_files)

        # Pagination Logic
        col_prev, col_info, col_next = st.columns([1, 2, 1])
        
        with col_info:
            st.write(f"#### Viewing Page {st.session_state.current_page} of {total_pages}")
            page_slider = st.slider("Navigate to Page", 1, total_pages, st.session_state.current_page)
            if page_slider != st.session_state.current_page:
                st.session_state.current_page = page_slider
                st.rerun()

        with col_prev:
            if st.button("⬅️ Previous", use_container_width=True, disabled=(st.session_state.current_page <= 1)):
                st.session_state.current_page -= 1
                st.rerun()

        with col_next:
            if st.button("Next ➡️", use_container_width=True, disabled=(st.session_state.current_page >= total_pages)):
                st.session_state.current_page += 1
                st.rerun()

        # Display current image
        current_img = png_files[st.session_state.current_page - 1]
        st.image(current_img, use_container_width=True, caption=f"Analysis Batch: {os.path.basename(current_img)}")
        
        st.success(f"Successfully loaded {total_pages} result pages. Each page contains up to 12 galaxies.")

    def display_summary(self, results_dir):
        json_path = os.path.join(results_dir, "results.json")
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            st.write("---")
            st.header("🎯 Universal Discovery Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall RMSE", f"{data.get('overall_rmse', 0):.2f} km/s")
            c2.metric("Reduced χ²", f"{data.get('overall_red_chi2', 0):.2f}")
            c3.metric("Theory Alignment", data.get('model_alignment', 'Unknown'))
            
            st.info(f"### Discovered Equation: ${sp.latex(sp.sympify(data.get('equation', '0')))}$")

def main():
    app = GravityDiscoveryApp()
    
    if not st.session_state.initialized:
        app.show_splash()

    config = app.sidebar()
    
    st.title("🌌 GRAV: Galaxy Rotation Analyze Viewer")
    st.caption("Advanced AI Platform for Autonomous Gravity Theory Discovery")
    
    if config["run_btn"]:
        app.run_backend(config)
    
    # Always try to display results if they exist
    app.display_summary(config["out"])
    app.display_gallery(config["out"])

if __name__ == "__main__":
    main()

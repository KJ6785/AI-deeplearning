import matplotlib.pyplot as plt
import numpy as np
import os
import sympy as sp

def save_comparison_plots(galaxies_data, eq_str, output_dir="results"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 수식을 함수로 변환 (r, v_b, g_bar 3개 인자)
    r_sym, vb_sym, gb_sym = sp.symbols('r v_b g_bar')
    expr = sp.sympify(eq_str)
    discovered_func = sp.lambdify((r_sym, vb_sym, gb_sym), expr, 'numpy')

    n_galaxies = len(galaxies_data)
    n_pages = (n_galaxies + 8) // 9

    print(f"--- Generating {n_pages} pages of comparison plots ---")

    for page in range(n_pages):
        fig, axes = plt.subplots(3, 3, figsize=(22, 18))
        fig.suptitle(f"Galaxy Rotation Curve Comparison (Page {page+1})\nBlack:Obs, Red:AI Discovered Law, Blue:MOND, Purple:DarkMatter", fontsize=22)
        
        for i in range(9):
            idx = page * 9 + i
            row, col = i // 3, i % 3
            ax = axes[row, col]
            
            if idx >= n_galaxies:
                ax.axis('off')
                continue
            
            data = galaxies_data[idx]
            r = data['r']
            v_b = data['v_b']
            g_bar = (v_b**2) / (r + 1e-6) # g_bar 피처 생성
            
            # 1. Observed Data
            ax.errorbar(r, data['v_obs'], yerr=data['v_err'], fmt='ko', label='Observed', markersize=5, alpha=0.4)
            
            # 2. AI Discovered Equation
            try:
                v_ai = discovered_func(r, v_b, g_bar)
                # 만약 스칼라가 반환되면 배열로 변환
                if np.isscalar(v_ai): v_ai = np.ones_like(r) * v_ai
                ax.plot(r, v_ai, 'r-', label='AI Discovered', linewidth=3.0)
            except Exception as e:
                print(f"Plot error for {data['name']}: {e}")
            
            # 3. MOND Theory (Standard)
            a0 = 1.2e-10 
            v_mond = np.sqrt(v_b**2 + np.sqrt(a0 * (v_b**2 / (r+1e-6)) * (r*3.086e19)) * 1e-3)
            ax.plot(r, v_mond, 'b--', label='MOND', alpha=0.8)

            # 4. Dark Matter (NFW)
            v_halo = 120 * (r / (r + 10))
            v_dm = np.sqrt(v_b**2 + v_halo**2)
            ax.plot(r, v_dm, 'm:', label='Dark Matter (NFW)', alpha=0.8)

            ax.set_title(f"{data['name']}", fontsize=15)
            ax.grid(True, linestyle=':', alpha=0.6)
            if i == 0: ax.legend(fontsize=12)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        save_path = f"{output_dir}/comparison_page_{page+1}.png"
        plt.savefig(save_path)
        plt.close()
        print(f"Saved: {save_path}")

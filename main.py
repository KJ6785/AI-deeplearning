# Julia/PySR 관련 충돌 방지를 위해 다른 모듈보다 먼저 임포트
try:
    from src.discovery.symbolic import EquationDiscovery
except ImportError:
    pass

import argparse
import os
import numpy as np
import torch
import sympy as sp

from src.data.loader import SPARCDataset, get_sparc_dataloader, get_combined_dataloader, HDF5Manager
from src.models.operator import GalaxyDeepONet
from src.models.fno import GravityFNO
from src.training.trainer import GravityTrainer
from src.discovery.symbolic import EquationDiscovery
from src.discovery.pde import PDEDiscovery
from src.interpretation.interpreter import PhysicsInterpreter
from src.interpretation.visualizer import save_comparison_plots
from src.interpretation.validator import PhysicsValidator

if 'EquationDiscovery' not in globals():
    from src.discovery.symbolic import EquationDiscovery

def main():
    parser = argparse.ArgumentParser(description="SPARC Galaxy Gravity Discovery Platform")
    parser.add_argument("--data", type=str, required=True, help="Path to SPARC ASCII data file or directory")
    parser.add_argument("--model_type", type=str, default="DeepONet", choices=["DeepONet", "FNO"], help="Model type to use")
    parser.add_argument("--epochs", type=int, default=1000, help="Number of training epochs")
    parser.add_argument("--pysr_iter", type=int, default=100, help="PySR iterations")
    parser.add_argument("--use_sindy", action="store_true", help="Whether to use SINDy for PDE discovery")
    parser.add_argument("--out", type=str, default="results", help="Output directory")
    parser.add_argument("--chi2_cutoff", type=float, default=30.0, help="Red Chi2 threshold to filter out outlier galaxies")
    args = parser.parse_args()

    # 1. Data Management
    print(f"--- 1. Data Service: Loading {args.data} ---")
    h5_manager = HDF5Manager()
    
    galaxies_for_plotting = []
    if os.path.isdir(args.data):
        files = [os.path.join(args.data, f) for f in os.listdir(args.data) if f.endswith('.dat')]
        dataloader = get_combined_dataloader(files, batch_size=64)
    else:
        files = [args.data]
        dataloader = get_sparc_dataloader(args.data, batch_size=32)

    for f in files:
        dataset = SPARCDataset(f, normalize=False)
        if not dataset.data.empty:
            df = dataset.data
            name = os.path.basename(f).replace('_rotmod.dat', '')
            galaxy_data = {
                'name': name,
                'r': df['Rad'].values,
                'v_obs': df['Vobs'].values,
                'v_err': df['errV'].values,
                'v_b': np.sqrt(df['Vgas']**2 + df['Vdisk']**2 + df['Vbul']**2).values,
                'rho_b': (np.sqrt(df['Vgas']**2 + df['Vdisk']**2 + df['Vbul']**2).values**2) / (df['Rad'].values + 1e-6)
            }
            galaxies_for_plotting.append(galaxy_data)
            h5_manager.save_galaxy(name, galaxy_data)

    # 2. Neural Operator Training
    print(f"--- 2. Neural Operator Service: Training {args.model_type} ---")
    if args.model_type == "DeepONet":
        model = GalaxyDeepONet(branch_dim=20, hidden_dim=64)
    else:
        model = GravityFNO(modes=16, width=64)
    
    trainer = GravityTrainer(model, model_type=args.model_type, lr=1e-3, lambda_physics=0.1)
    trainer.train(dataloader, epochs=args.epochs)
    
    # 2.1 Smart Data Cleaning: Filter Outliers using Trained Model
    print(f"--- 2.1 Data Cleaning: Filtering galaxies with Red Chi2 > {args.chi2_cutoff} ---")
    model.eval()
    clean_galaxies = []
    outliers = []
    
    validator = PhysicsValidator()
    stats = dataloader.dataset.stats
    
    for g in galaxies_for_plotting:
        # Get model prediction for this specific galaxy
        r_norm = (g['r'] - stats['r_mean']) / stats['r_std']
        vb_norm = (g['v_b'] - stats['v_mean']) / stats['v_std']
        
        r_tensor = torch.tensor(r_norm, dtype=torch.float32).unsqueeze(-1)
        vb_tensor = torch.tensor(vb_norm, dtype=torch.float32).unsqueeze(-1)
        
        with torch.no_grad():
            if args.model_type == "DeepONet":
                v_profile = torch.ones(len(g['r']), 20) * vb_tensor
                v_pred_norm = model(v_profile, r_tensor).numpy().flatten()
            else:
                x_in = torch.cat([vb_tensor, r_tensor], dim=-1).unsqueeze(0)
                out = model(x_in)
                v_pred_norm = out[0, :, 1].numpy().flatten()
        
        v_pred = v_pred_norm * stats['v_std'] + stats['v_mean']
        
        # Calculate individual Red Chi2
        g_v_err_safe = np.maximum(g['v_err'], 3.0)
        chi2 = np.sum(((g['v_obs'] - v_pred) / g_v_err_safe)**2)
        dof = len(g['r']) - 3
        red_chi2 = chi2 / dof if dof > 0 else 0
        
        if red_chi2 <= args.chi2_cutoff:
            clean_galaxies.append(g)
        else:
            outliers.append((g['name'], red_chi2))

    print(f"  Cleaned dataset: {len(clean_galaxies)} galaxies kept, {len(outliers)} outliers removed.")
    if outliers:
        print(f"  Removed Outliers: {', '.join([f'{name}({val:.1f})' for name, val in outliers[:5]])}...")

    # 3. PDE / Symbolic Discovery (On CLEAN data only)
    print("--- 3. Discovery Service: Extracting Theory from Clean Data ---")
    
    # Concatenate clean data for PySR
    all_r_clean = np.concatenate([g['r'] for g in clean_galaxies])
    all_vb_clean = np.concatenate([g['v_b'] for g in clean_galaxies])
    
    # Wrap in Series for consistency with previous code
    import pandas as pd
    r_phys_clean = pd.Series(all_r_clean)
    vb_phys_clean = pd.Series(all_vb_clean)

    # Symbolic Regression (PySR)
    discovery = EquationDiscovery(niterations=args.pysr_iter)
    best_row = discovery.discover(model, args.model_type, stats, r_phys_clean, vb_phys_clean)
    best_eq_str = best_row['equation']
    
    # ... (Rest of Step 3.1)
    
    # Optional SINDy (PDE Discovery)
    if args.use_sindy:
        print("--- 3.1 PDE Discovery (SINDy) ---")
        pde_discovery = PDEDiscovery()
        # 첫 번째 은하에 대해 모델이 예측한 Phi와 v를 사용하여 PDE 추출
        g = galaxies_for_plotting[0]
        
        # 모델로부터 Phi_pred 추출 시도
        r_norm_single = (g['r'] - stats['r_mean']) / stats['r_std']
        vb_norm_single = (g['v_b'] - stats['v_mean']) / stats['v_std']
        
        # 차원을 [1, N, 2]로 정확히 맞춤
        r_tensor = torch.tensor(r_norm_single, dtype=torch.float32).unsqueeze(-1)
        vb_tensor = torch.tensor(vb_norm_single, dtype=torch.float32).unsqueeze(-1)
        
        model.eval()
        with torch.no_grad():
            if args.model_type == "FNO":
                x_in = torch.cat([vb_tensor, r_tensor], dim=-1).unsqueeze(0) # [1, N, 2]
                out = model(x_in)
                Phi_pred = out[0, :, 0].numpy() * stats['v_std'] # 스케일 복원
            else:
                # DeepONet은 Phi가 없으므로 v를 기반으로 가상 포텐셜 생성
                Phi_pred = -np.cumsum(g['v_obs']**2 / (g['r'] + 1e-6)) * (g['r'][1] - g['r'][0])

        try:
            pde_eqs = pde_discovery.discover(g['r'], Phi_pred, g['v_obs'], g['rho_b'])
            print(f"SINDy Discovered PDEs for {g['name']}:")
            for i, eq in enumerate(pde_eqs):
                print(f"  Eq {i}: {eq}")
        except Exception as e:
            print(f"SINDy Discovery skipped due to: {e}")

    # 4. Validation & Interpretation
    print("--- 4. Validation Service: Checking Physics ---")
    interpreter = PhysicsInterpreter()
    validator = PhysicsValidator()
    
    # Prepare data for metrics
    all_r, all_v, all_err, all_vb = [], [], [], []
    for batch in dataloader:
        all_r.append(batch['radius'].numpy())
        all_v.append(batch['v_obs'].numpy())
        all_err.append(batch['v_err'].numpy())
        all_vb.append(batch['v_baryon'].numpy())
    
    r_norm = np.concatenate(all_r).flatten()
    v_norm = np.concatenate(all_v).flatten()
    err_norm = np.concatenate(all_err).flatten()
    vb_norm = np.concatenate(all_vb).flatten()

    r_np = r_norm * stats['r_std'] + stats['r_mean']
    v_np = v_norm * stats['v_std'] + stats['v_mean']
    # v_err is already in physical units (km/s) from the SPARC data, 
    # it was NOT normalized in the loader (check loader.py)
    err_np = err_norm.flatten() 
    vb_np = vb_norm * stats['v_std'] + stats['v_mean']

    # Evaluate the BEST discovered equation on the actual data
    v_ai = validator.evaluate_equation(best_eq_str, r_np, vb_np)
    
    print("\n--- Diagnostic: Per-Galaxy Metrics ---")
    galaxy_metrics = []
    for g in galaxies_for_plotting:
        g_v_ai = validator.evaluate_equation(best_eq_str, g['r'], g['v_b'])
        g_rmse = np.sqrt(np.mean((g['v_obs'] - g_v_ai)**2))
        g_v_err_safe = np.maximum(g['v_err'], 3.0)
        g_chi2 = np.sum(((g['v_obs'] - g_v_ai) / g_v_err_safe)**2)
        g_dof = (len(g['r']) - 3)
        g_red_chi2 = g_chi2 / g_dof if g_dof > 0 else 0
        g_mean_err = np.mean(g['v_err'])
        g_ratio = g_rmse / g_mean_err if g_mean_err > 0 else 0
        
        galaxy_metrics.append({
            'name': g['name'],
            'rmse': g_rmse,
            'red_chi2': g_red_chi2,
            'mean_err': g_mean_err,
            'ratio': g_ratio
        })
        print(f"  {g['name']:<15} | RMSE: {g_rmse:>6.2f} | Red Chi2: {g_red_chi2:>6.2f} | Ratio(RMSE/Err): {g_ratio:>5.1f}")

    # Sort and show top 5 outliers
    print("\n--- [OUTLIER CANDIDATES] Top 5 Worst Fit Galaxies ---")
    worst_fit = sorted(galaxy_metrics, key=lambda x: x['red_chi2'], reverse=True)[:5]
    for i, g in enumerate(worst_fit, 1):
        print(f"  {i}. {g['name']:<12} : Red Chi2 = {g['red_chi2']:.1f} (RMSE: {g['rmse']:.1f}, Mean Err: {g['mean_err']:.2f})")

    print(f"\nError Statistics: Min={np.min(err_np):.2f}, Max={np.max(err_np):.2f}, Mean={np.mean(err_np):.2f}")

    rmse, chi_sq, red_chi_sq = interpreter.calculate_metrics(best_eq_str, r_np, v_np, err_np, vb_np)
    analysis = interpreter.analyze_equation(best_eq_str)
    
    # Physical Validation (Energy conservation check for discovered v)
    is_valid, energy_violation = validator.check_energy_conservation(v_ai, r_np)
    
    print("\n" + "="*50)
    print("FINAL ANALYSIS REPORT (Enhanced)")
    print("="*50)
    print(f"1. Statistical Metrics (Observed vs AI Theory):")
    print(f"   - RMSE: {rmse:.4f} km/s")
    print(f"   - Reduced χ²: {red_chi_sq:.4f}")
    print(f"   - Energy Conservation Violation: {energy_violation:.6e}")
    
    print(f"\n2. Theory Discovery:")
    print(f"   - Model Alignment: {analysis['model']}")
    print(f"   - Equation (SymPy): {analysis['simplified_eq']}")
    print(f"   - LaTeX: {sp.latex(analysis['simplified_eq'])}")
    print("="*50)

    # 5. Visualization Service: Generating Reports
    print(f"\n--- 5. Visualization Service: Generating Reports ---")
    save_comparison_plots(clean_galaxies, best_eq_str, output_dir=args.out)

    # JSON 결과 저장 (GUI 반영을 위해)
    import json
    results_data = {
        "equation": best_eq_str,
        "simplified": str(analysis['simplified_eq']),
        "galaxies": [g['name'] for g in clean_galaxies]
    }
    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(results_data, f)
    print(f"All reports and plots saved to {args.out}/ directory.")

if __name__ == "__main__":
    main()

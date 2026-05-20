from pysr import PySRRegressor
import numpy as np
import torch
import multiprocessing

class EquationDiscovery:
    def __init__(self, niterations=40):
        # Physics-focused configuration with maximum stability
        self.model = PySRRegressor(
            niterations=niterations,
            binary_operators=["+", "*", "/", "^"],
            unary_operators=["log", "sqrt"], 
            constraints={"^": (-1, 3)},
            nested_constraints={
                "log": {"log": 0, "sqrt": 1},
                "sqrt": {"log": 1, "sqrt": 0},
            },
            complexity_of_operators={"+": 1, "*": 2, "/": 3, "^": 4, "log": 5, "sqrt": 3},
            parsimony=0.005,
            populations=8,        # Stability over speed
            population_size=30,
            maxsize=20,
            timeout_in_seconds=600,
            model_selection="best",
            parallelism="serial", # No background threads
            procs=0,              # CRITICAL: Disable Julia worker processes completely
            elementwise_loss="loss(prediction, target) = (prediction - target)^2",
        )

    def discover(self, model, model_type, stats, r_phys, vb_phys, n_samples=1000):
        model.eval()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.to(device)
        
        # 1. Samples maintaining physical correlation between r and v_b
        # Instead of independent linspace, we sample from the joint distribution or interpolate
        indices = np.linspace(0, len(r_phys)-1, n_samples).astype(int)
        r = r_phys.iloc[indices].values.reshape(-1, 1)
        v_b = vb_phys.iloc[indices].values.reshape(-1, 1)
        
        # 2. Normalize for model input
        r_norm = (r - stats['r_mean']) / stats['r_std']
        vb_norm = (v_b - stats['v_mean']) / stats['v_std']
        
        r_tensor = torch.tensor(r_norm, dtype=torch.float32).to(device)
        vb_tensor = torch.tensor(vb_norm, dtype=torch.float32).to(device)
        
        # 3. Model Inference
        with torch.no_grad():
            if model_type == 'DeepONet':
                # DeepONet expected branch input [N, 20] and query input [N, 1]
                # Assuming v_b is the branch signal (expanded to 20)
                v_profile = torch.ones(n_samples, 20).to(device) * vb_tensor
                v_pred_norm = model(v_profile, r_tensor).cpu().numpy()
            elif model_type == 'FNO':
                x = torch.cat([vb_tensor, r_tensor], dim=-1).unsqueeze(1) # [N, 1, 2]
                out = model(x)
                v_pred_norm = out[:, :, 1].cpu().numpy().flatten()
        
        # 4. Denormalize to physical units
        v_pred_phys = v_pred_norm.flatten() * stats['v_std'] + stats['v_mean']
        
        # 5. Features for PySR: r, v_b, and Newtonian acceleration g_bar
        g_bar = (v_b.flatten()**2) / (r.flatten() + 1e-6)
        X = np.stack([r.flatten(), v_b.flatten(), g_bar], axis=1)
        
        self.model.fit(X, v_pred_phys, variable_names=["r", "v_b", "g_bar"])
        
        return self.model.get_best()

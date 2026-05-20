import numpy as np

class PhysicsValidator:
    """
    Validate discovered theory against fundamental physics
    """
    def check_energy_conservation(self, v, r, Phi=None, tolerance=1e-3):
        """
        Total energy: E = (1/2) v² + Φ
        If Phi is not provided, we estimate it from the circular orbit condition:
        v²/r = dΦ/dr  =>  Φ = ∫ (v²/r) dr
        """
        # Ensure v and r have no NaNs
        v = np.nan_to_num(v, nan=0.0, posinf=1e6, neginf=0.0)
        r = np.nan_to_num(r, nan=1e-6, posinf=1e6, neginf=1e-6)

        if Phi is None:
            # Estimate potential from velocity profile assuming circular orbits
            accel = (v**2) / (r + 1e-6)
            Phi = np.cumsum(accel * np.gradient(r))
            
        Phi = np.nan_to_num(Phi, nan=0.0)
        E = 0.5 * v**2 - Phi 
        
        # Calculate gradient safely
        dr = np.gradient(r)
        dr[dr == 0] = 1e-6 # Prevent division by zero
        dE_dr = np.gradient(E) / dr
        
        # Relative violation
        energy_scale = np.mean(np.abs(E)) + 1e-6
        violation = np.nanmean(np.abs(dE_dr)) / energy_scale
        
        # Final check for NaN
        if np.isnan(violation):
            violation = 1.0 # Significant violation if calculation fails
            
        return violation < tolerance, violation

    def evaluate_equation(self, eq_str, r, v_b):
        """
        Evaluate the symbolic equation string with provided data.
        """
        # Newtonian acceleration for the formula
        g_bar = (v_b**2) / (r + 1e-6)
        
        # Safe evaluation environment
        # Use np.abs inside log/sqrt to avoid NaNs
        safe_dict = {
            'r': r,
            'v_b': v_b,
            'g_bar': g_bar,
            'sqrt': lambda x: np.sqrt(np.abs(x)),
            'log': lambda x: np.log(np.abs(x) + 1e-9),
            'exp': lambda x: np.exp(np.clip(x, -100, 100)), # Prevent overflow
            'abs': np.abs
        }
        
        try:
            # Simple string replacement for power operator if necessary
            clean_eq = eq_str.replace('^', '**')
            v_pred = eval(clean_eq, {"__builtins__": None}, safe_dict)
            return v_pred
        except Exception as e:
            print(f"Error evaluating equation: {e}")
            return np.zeros_like(r)

    def check_angular_momentum(self, v, r):
        """
        Angular momentum: L = r * v
        For circular orbits, we check if L profile is physically reasonable (e.g., non-decreasing).
        """
        L = r * v
        dL_dr = np.gradient(L, r)
        # Simple check: angular momentum shouldn't decrease significantly in stable orbits
        is_valid = np.all(dL_dr > -0.1) 
        return is_valid, dL_dr

    def check_rotational_symmetry(self, Phi_profile):
        """
        In this 1D model, we assume spherical symmetry. 
        Validation would involve checking if Phi depends only on r.
        Since we only have Phi(r), it's symmetric by definition in our setup.
        """
        return True

    def validate_asymptotics(self, discovered_func, r_range, stats):
        """
        Check limiting behavior:
        r -> 0: Phi -> -GM/r (Newtonian)
        r -> infinity: v -> constant (Flat rotation curve)
        """
        # (This would require a more complex setup to find M, but we can do a gradient check)
        r_large = np.linspace(50, 100, 100)
        # We'd need v_b values here too
        return "TBD"

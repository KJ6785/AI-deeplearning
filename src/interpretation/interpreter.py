import sympy as sp

class PhysicsInterpreter:
    def __init__(self):
        # r: 반지름, v_b: 바리온 속도, g_bar: 바리온 가속도 (v_b^2 / r)
        self.r, self.v_b, self.g_bar = sp.symbols('r v_b g_bar')
        
    def calculate_metrics(self, eq_str, r_data, v_obs, v_err, v_b_data):
        import numpy as np
        # PySR에서 명시적으로 지정한 변수 이름 사용 (r, v_b, g_bar)
        
        # g_bar 계산
        g_bar_data = (v_b_data**2) / (r_data + 1e-6)
        
        # 수식을 함수로 변환
        eq = sp.sympify(eq_str)
        func = sp.lambdify((self.r, self.v_b, self.g_bar), eq, 'numpy')
        
        v_pred = func(r_data, v_b_data, g_bar_data)
        
        # 1. RMSE
        residuals = v_obs - v_pred
        rmse = np.sqrt(np.mean(residuals**2))
        
        # 2. Chi-Squared with Error Floor (at least 3 km/s as per SPARC intrinsic dispersion)
        # Some SPARC points have tiny errors (< 1 km/s) which blow up chi-sq
        error_floor = 3.0 
        v_err_safe = np.maximum(v_err, error_floor)
        
        chi_sq = np.sum((residuals / v_err_safe)**2)
        dof = len(v_obs) - 3 # r, v_b, g_bar components
        red_chi_sq = chi_sq / dof if dof > 0 else chi_sq
        
        # Diagnostic: Compare RMSE to Mean Error
        mean_err = np.mean(v_err_safe)
        if rmse > 2 * mean_err:
            print(f"  [Diagnostic] Warning: RMSE ({rmse:.2f}) is much larger than mean error ({mean_err:.2f}).")
            print(f"               Check for systematic bias or complex DM halos.")
        
        return rmse, chi_sq, red_chi_sq

    def analyze_equation(self, eq_str):
        eq = sp.sympify(eq_str)
        mond_score = 0
        dm_score = 0
        evidence = []
        
        # MOND 특징: 바리온 가속도 g_bar의 제곱근에 비례하는 성분
        if eq.has(sp.sqrt(self.g_bar)) or 'g_bar' in str(eq):
            mond_score += 0.5
            evidence.append("Dependence on baryonic acceleration (g_bar) detected - Strong MOND signature")
        
        # 암흡물질 특징: 반지름 r에 대한 추가적인 항
        if eq.has(self.r) and not eq.has(self.g_bar):
            dm_score += 0.3
            evidence.append("Direct radial dependence detected - Potential Dark Matter halo signature")

        if mond_score > dm_score:
            model = "MOND (Modified Newtonian Dynamics)"
            confidence = mond_score
        elif dm_score > mond_score:
            model = "Dark Matter (Newtonian + Halo)"
            confidence = dm_score
        else:
            model = "Hybrid / Uncertain"
            confidence = 0.5

        return {
            'model': model,
            'confidence': confidence,
            'evidence': evidence,
            'simplified_eq': sp.simplify(eq)
        }

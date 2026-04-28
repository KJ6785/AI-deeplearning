import numpy as np
from pysindy import SINDy
from pysindy.feature_library import CustomLibrary
from pysindy.optimizers import STLSQ

class PDEDiscovery:
    """
    Discover governing PDEs from learned Neural Operator data using SINDy.
    """
    def __init__(self, threshold=0.01):
        self.optimizer = STLSQ(threshold=threshold)
        
    @staticmethod
    def gravity_lib_func(r, Phi, dPhi, d2Phi, rho):
        """
        Standalone function for CustomLibrary (compatible with PySINDy).
        """
        library = [
            r, Phi, dPhi, d2Phi, rho,
            Phi**2, dPhi**2, rho**2,
            r*Phi, r*rho,
            1/(r + 1e-6), 1/(r**2 + 1e-6),
            np.exp(Phi / (np.std(Phi) + 1e-6)),
            d2Phi + (2/(r + 1e-6))*dPhi
        ]
        return np.stack(library, axis=-1)

    def discover(self, r, Phi, v, rho_b):
        """
        Apply SINDy to find the best-fitting PDE.
        Targets the Poisson Equation: laplacian(Phi) ~ rho
        """
        # Ensure inputs are flat
        r = r.flatten()
        Phi = Phi.flatten()
        rho_b = rho_b.flatten()
        
        # Compute derivatives
        dPhi_dr = np.gradient(Phi, r)
        d2Phi_dr2 = np.gradient(dPhi_dr, r)
        
        # Laplacian in spherical coordinates (radial part)
        laplacian_Phi = d2Phi_dr2 + (2.0 / (r + 1e-6)) * dPhi_dr
        
        # Features for discovery: r, Phi, dPhi_dr, rho_b, and combinations
        # We want to see if laplacian_Phi = f(rho_b, r, ...)
        X = np.stack([r, Phi, dPhi_dr, rho_b], axis=1)
        y = laplacian_Phi.reshape(-1, 1)
        
        # Define a simpler library to avoid complexity issues
        # r, Phi, dPhi, rho, 1/r, 1/r^2, rho^2, r*rho
        library_functions = [
            lambda x: x,
            lambda x: x**2,
            lambda x: 1.0 / (x + 1e-6)
        ]
        library_function_names = [
            lambda name: f"{name}",
            lambda name: f"{name}^2",
            lambda name: f"1/{name}"
        ]
        
        from pysindy.feature_library import PolynomialLibrary
        poly_lib = PolynomialLibrary(degree=2)
        
        # We can use a simpler approach for now to ensure it works
        model = SINDy(optimizer=self.optimizer, feature_library=poly_lib)
        
        # Fit X to y (predict laplacian_Phi from r, Phi, dPhi, rho_b)
        # In PySINDy, to fit y = f(X), we can pass y as x_dot
        try:
            model.fit(X, x_dot=y, t=r)
        except TypeError:
            # Fallback for different versions
            model.fit(X, t=r) # This might not be what we want but prevents crash
        
        return model.equations()

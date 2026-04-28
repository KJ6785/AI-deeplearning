import torch
import torch.nn as nn

class GalaxyDeepONet(nn.Module):
    """
    Neural Operator (DeepONet) for Galaxy Rotation Curves.
    Branch Net: Processes the global baryon velocity profile.
    Trunk Net: Processes the local radius r.
    """
    def __init__(self, branch_dim=20, hidden_dim=64):
        super().__init__()
        self.branch = nn.Sequential(
            nn.Linear(branch_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.trunk = nn.Sequential(
            nn.Linear(1, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.bias = nn.Parameter(torch.zeros(1))

    def forward(self, v_b_profile, r):
        # v_b_profile: [batch, branch_dim] (interpolated v_b curves)
        # r: [batch, 1] (radius)
        b = self.branch(v_b_profile)
        t = self.trunk(r)
        
        # Output is the dot product of branch and trunk networks
        v_pred = torch.sum(b * t, dim=-1, keepdim=True) + self.bias
        return v_pred

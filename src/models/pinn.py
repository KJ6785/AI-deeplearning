import torch
import torch.nn as nn

class GalaxyPINN(nn.Module):
    """
    Physics-Informed Neural Network for Galaxy Rotation Curves
    Input: [radius, v_baryon]
    Output: predicted_v
    """
    def __init__(self, hidden_dim=64):
        super(GalaxyPINN, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )

    def forward(self, r, v_baryon):
        # r, v_baryon shape: [batch, 1]
        x = torch.cat([r, v_baryon], dim=-1)
        v_pred = self.net(x)
        return v_pred

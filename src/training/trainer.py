import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class GravityTrainer:
    def __init__(self, model, model_type='DeepONet', lr=1e-3, lambda_physics=0.1):
        self.model = model
        self.model_type = model_type
        self.optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
        self.criterion = nn.MSELoss()
        self.lambda_physics = lambda_physics
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def compute_physics_loss(self, r, v_pred, Phi_pred=None):
        if Phi_pred is None:
            return torch.mean(torch.relu(-v_pred)**2)
            
        r.requires_grad = True
        dPhi_dr = torch.autograd.grad(
            Phi_pred, r,
            grad_outputs=torch.ones_like(Phi_pred),
            create_graph=True
        )[0]
        
        residual = dPhi_dr + (v_pred**2 / (r + 1e-6))
        return torch.mean(residual**2)

    def train_step(self, batch):
        self.model.train()
        r = batch['radius'].to(self.device)
        v_obs = batch['v_obs'].to(self.device)
        v_b = batch['v_baryon'].to(self.device)

        # 미분 추적을 위해 최상단에서 설정
        r.requires_grad = True

        self.optimizer.zero_grad()
        
        if self.model_type == 'DeepONet':
            v_profile = torch.ones(r.size(0), 20).to(self.device) * v_b
            v_pred = self.model(v_profile, r)
            Phi_pred = None
            loss_data = self.criterion(v_pred, v_obs)
            loss_physics = self.compute_physics_loss(r, v_pred, Phi_pred)
        elif self.model_type == 'FNO':
            # FNO: 배치를 하나의 시퀀스로 간주 [1, Batch, Channel]
            # (Spatial 정보를 위해 배치를 정렬된 상태로 처리하는 것이 좋으나, 
            #  일단은 현재 배치를 하나의 시퀀스로 묶음)
            x = torch.cat([v_b, r], dim=-1).unsqueeze(0) # [1, Batch, 2]
            out = self.model(x)
            Phi_pred, v_pred = out[:, :, 0], out[:, :, 1]
            loss_data = self.criterion(v_pred.squeeze(0), v_obs.flatten())
            loss_physics = self.compute_physics_loss(r, v_pred.squeeze(0), Phi_pred.squeeze(0))
        
        total_loss = loss_data + self.lambda_physics * loss_physics
        total_loss.backward()
        self.optimizer.step()
        
        return total_loss.item(), loss_data.item(), loss_physics.item()

    def train(self, dataloader, epochs=500):
        print(f"Starting {self.model_type} training on {self.device}...")
        for epoch in range(epochs):
            total_l, data_l, phys_l = 0, 0, 0
            for batch in dataloader:
                l, dl, pl = self.train_step(batch)
                total_l += l
                data_l += dl
                phys_l += pl
            
            if (epoch + 1) % 50 == 0 or epoch == 0:
                avg_loss = total_l/len(dataloader)
                print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.6f} (Data: {data_l/len(dataloader):.4f})")

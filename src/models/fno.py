import torch
import torch.nn as nn
import torch.nn.functional as F

class SpectralConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, modes):
        super(SpectralConv1d, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.modes = modes
        self.scale = (1 / (in_channels * out_channels))
        self.weights = nn.Parameter(self.scale * torch.rand(in_channels, out_channels, modes, dtype=torch.cfloat))

    def forward(self, x):
        batchsize = x.shape[0]
        # Fourier transform
        x_ft = torch.fft.rfft(x)
        
        # 입력 데이터 길이에 맞춰 실제 사용할 모드 수 결정 (에러 방지 핵심)
        actual_modes = min(self.modes, x_ft.size(-1))
        
        # Multiply relevant Fourier modes
        out_ft = torch.zeros(batchsize, self.out_channels, x.size(-1) // 2 + 1, device=x.device, dtype=torch.cfloat)
        
        # 가중치와 입력의 모드 수를 일치시켜 곱셈 수행
        out_ft[:, :, :actual_modes] = torch.einsum("bix,iox->box", 
                                                   x_ft[:, :, :actual_modes], 
                                                   self.weights[:, :, :actual_modes])
        
        # Inverse Fourier transform
        x = torch.fft.irfft(out_ft, n=x.size(-1))
        return x

class GravityFNO(nn.Module):
    def __init__(self, modes=16, width=64):
        super(GravityFNO, self).__init__()
        self.modes = modes
        self.width = width
        self.fc0 = nn.Linear(2, self.width)

        self.conv0 = SpectralConv1d(self.width, self.width, self.modes)
        self.conv1 = SpectralConv1d(self.width, self.width, self.modes)
        self.conv2 = SpectralConv1d(self.width, self.width, self.modes)
        self.conv3 = SpectralConv1d(self.width, self.width, self.modes)
        
        self.w0 = nn.Conv1d(self.width, self.width, 1)
        self.w1 = nn.Conv1d(self.width, self.width, 1)
        self.w2 = nn.Conv1d(self.width, self.width, 1)
        self.w3 = nn.Conv1d(self.width, self.width, 1)

        self.fc1 = nn.Linear(self.width, 128)
        self.fc2 = nn.Linear(128, 2)

    def forward(self, x):
        # x shape: [batch, N_points, 2]
        x = self.fc0(x)
        x = x.permute(0, 2, 1) # [batch, width, N_points]

        x1 = self.conv0(x)
        x2 = self.w0(x)
        x = F.gelu(x1 + x2)

        x1 = self.conv1(x)
        x2 = self.w1(x)
        x = F.gelu(x1 + x2)

        x1 = self.conv2(x)
        x2 = self.w2(x)
        x = F.gelu(x1 + x2)

        x1 = self.conv3(x)
        x2 = self.w3(x)
        x = F.gelu(x1 + x2)

        x = x.permute(0, 2, 1) # [batch, N_points, width]
        x = F.gelu(self.fc1(x))
        x = self.fc2(x)
        return x

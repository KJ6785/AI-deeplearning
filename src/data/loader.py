import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import os
import h5py

class HDF5Manager:
    """
    Manage HDF5 storage for galaxy data as specified in TRD.
    """
    def __init__(self, h5_path="data/sparc_data.h5"):
        self.h5_path = h5_path
        if not os.path.exists(os.path.dirname(h5_path)):
            os.makedirs(os.path.dirname(h5_path))

    def save_galaxy(self, galaxy_name, data_dict):
        with h5py.File(self.h5_path, 'a') as f:
            if galaxy_name in f:
                del f[galaxy_name]
            g = f.create_group(galaxy_name)
            for k, v in data_dict.items():
                g.create_dataset(k, data=v)

    def load_galaxy(self, galaxy_name):
        with h5py.File(self.h5_path, 'r') as f:
            if galaxy_name not in f:
                return None
            g = f[galaxy_name]
            return {k: np.array(v) for k, v in g.items()}

class SPARCDataset(Dataset):
    """
    Enhanced SPARC Galaxy Rotation Curve Loader with reversible normalization.
    """
    def __init__(self, file_path, normalize=True):
        self.file_path = file_path
        self.normalize = normalize
        self.data = self._load_data(file_path)
        
        if normalize:
            self.stats = {
                'r_mean': self.data['Rad'].mean(),
                'r_std': self.data['Rad'].std(),
                'v_mean': self.data['Vobs'].mean(),
                'v_std': self.data['Vobs'].std(),
            }
        
    def _load_data(self, file_path):
        try:
            df = pd.read_csv(file_path, sep=r'\s+', comment='#', names=[
                'Rad', 'Vobs', 'errV', 'Vgas', 'Vdisk', 'Vbul', 'SBdisk', 'SBbul'
            ])
            df = df.interpolate(method='linear', limit_direction='both')
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return pd.DataFrame()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        r = row['Rad']
        v = row['Vobs']
        v_err = row['errV']
        v_b = np.sqrt(row['Vgas']**2 + row['Vdisk']**2 + row['Vbul']**2)
        
        # Baryonic mass distribution proxy (proportional to v_b^2 / r)
        rho_b = (v_b**2) / (r + 1e-6)

        if self.normalize:
            r_val = (r - self.stats['r_mean']) / self.stats['r_std']
            v_val = (v - self.stats['v_mean']) / self.stats['v_std']
            v_b_val = (v_b - self.stats['v_mean']) / self.stats['v_std']
        else:
            r_val, v_val, v_b_val = r, v, v_b

        return {
            'radius': torch.tensor([r_val], dtype=torch.float32),
            'v_obs': torch.tensor([v_val], dtype=torch.float32),
            'v_err': torch.tensor([v_err], dtype=torch.float32),
            'v_baryon': torch.tensor([v_b_val], dtype=torch.float32),
            'rho_b': torch.tensor([rho_b], dtype=torch.float32)
        }

class CombinedSPARCDataset(Dataset):
    def __init__(self, file_list, normalize=True):
        self.datasets = [SPARCDataset(f, normalize=False) for f in file_list]
        self.all_data = pd.concat([ds.data for ds in self.datasets], ignore_index=True)
        self.normalize = normalize
        
        if normalize:
            self.stats = {
                'r_mean': self.all_data['Rad'].mean(),
                'r_std': self.all_data['Rad'].std(),
                'v_mean': self.all_data['Vobs'].mean(),
                'v_std': self.all_data['Vobs'].std(),
            }

    def __len__(self):
        return len(self.all_data)

    def __getitem__(self, idx):
        row = self.all_data.iloc[idx]
        r = row['Rad']
        v = row['Vobs']
        v_err = row['errV']
        v_b = np.sqrt(row['Vgas']**2 + row['Vdisk']**2 + row['Vbul']**2)
        rho_b = (v_b**2) / (r + 1e-6)
        
        if self.normalize:
            r_val = (r - self.stats['r_mean']) / self.stats['r_std']
            v_val = (v - self.stats['v_mean']) / self.stats['v_std']
            v_b_val = (v_b - self.stats['v_mean']) / self.stats['v_std']
        else:
            r_val, v_val, v_b_val = r, v, v_b

        return {
            'radius': torch.tensor([r_val], dtype=torch.float32),
            'v_obs': torch.tensor([v_val], dtype=torch.float32),
            'v_err': torch.tensor([v_err], dtype=torch.float32),
            'v_baryon': torch.tensor([v_b_val], dtype=torch.float32),
            'rho_b': torch.tensor([rho_b], dtype=torch.float32)
        }

def get_combined_dataloader(file_list, batch_size=64, shuffle=True):
    dataset = CombinedSPARCDataset(file_list)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

def get_sparc_dataloader(file_path, batch_size=32, shuffle=True):
    dataset = SPARCDataset(file_path)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

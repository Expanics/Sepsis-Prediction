import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import joblib
import os

# =============================================================================
# EXACT 121 features expected by the model (ALPHABETICALLY SORTED)
# This order matches the non_output_cols minus starttime, endtime, subject_id, row_id
# =============================================================================
MODEL_INPUT_FEATURES = [
    'age', 'albumin_max', 'albumin_min', 'alp_max', 'alp_min', 'alt_max', 'alt_min',
    'aniongap_max', 'aniongap_min', 'antibiotic_count', 'ast_max', 'ast_min',
    'bands_max', 'bands_min', 'baseexcess_max', 'baseexcess_min', 'bicarbonate_max',
    'bicarbonate_min', 'bilirubin_direct_max', 'bilirubin_direct_min',
    'bilirubin_indirect_max', 'bilirubin_indirect_min', 'bilirubin_total_max',
    'bilirubin_total_min', 'bun_max', 'bun_min', 'calcium_max', 'calcium_min',
    'chloride_max', 'chloride_min', 'ck_mb_max', 'ck_mb_min', 'creatinine_max',
    'creatinine_min', 'crp_max', 'crp_min', 'dbp_max', 'dbp_min', 'fibrinogen_max',
    'fibrinogen_min', 'fio2_max', 'fio2_min', 'gcs_eyes_max', 'gcs_eyes_min',
    'gcs_max', 'gcs_min', 'gcs_motor_max', 'gcs_motor_min', 'gcs_verbal_max',
    'gcs_verbal_min', 'gender', 'ggt_max', 'ggt_min', 'globulin_max', 'globulin_min',
    'glucose_max', 'glucose_min', 'heart_rate_max', 'heart_rate_min', 'height',
    'hemoglobin_max', 'hemoglobin_min', 'hr', 'immature_granulocytes_max',
    'immature_granulocytes_min', 'inr_max', 'inr_min', 'lactate_max', 'lactate_min',
    'lymphocytes_abs_max', 'lymphocytes_abs_min', 'mbp_max', 'mbp_min',
    'neutrophils_abs_max', 'neutrophils_abs_min', 'ntprobnp_max', 'ntprobnp_min',
    'pco2_max', 'pco2_min', 'pfratio_max', 'pfratio_min', 'ph_max', 'ph_min',
    'platelet_max', 'platelet_min', 'po2_max', 'po2_min', 'potassium_max',
    'potassium_min', 'pt_max', 'pt_min', 'resp_rate_max', 'resp_rate_min',
    'sbp_max', 'sbp_min', 'so2_max', 'so2_min', 'sodium_max', 'sodium_min',
    'spo2_max', 'spo2_min', 'stay_id', 'temperature_max', 'temperature_min',
    'total_protein_max', 'total_protein_min', 'totalco2_max', 'totalco2_min',
    'troponin_t_max', 'troponin_t_min', 'urineoutput_max', 'urineoutput_min',
    'vaso_dopamine_max', 'vaso_epinephrine_max', 'vaso_norepinephrine_max',
    'vaso_phenylephrine_max', 'vaso_vasopressin_max', 'ventilation_flag',
    'wbc_max', 'wbc_min', 'weight'
]

# --- Model Definitions (Copied from Notebook) ---

class TemporalAttnPool(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.score = nn.Linear(d_model, 1)

    def forward(self, z, padding_mask):
        scores = self.score(z).squeeze(-1)  # [B, T]
        scores = scores.masked_fill(~padding_mask, -1e9)
        alpha = torch.softmax(scores, dim=1)
        pooled = (z * alpha.unsqueeze(-1)).sum(dim=1)
        return pooled


class GRUDTransformer(nn.Module):
    """
    GRU-D Transformer model with multi-head outputs for different window sizes.
    Matches the notebook training architecture exactly.
    """
    def __init__(
        self,
        n_features,
        hidden_size=64,
        d_model=128,
        nhead=4,
        num_layers=2,
        reg_dim=8,
        bin_dim=1
    ):
        super().__init__()

        self.input_size = n_features * 3  # x + mask + delta
        self.gru = nn.GRU(self.input_size, hidden_size, batch_first=True)
        self.to_dmodel = nn.Linear(hidden_size, d_model)

        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.attn_pool = TemporalAttnPool(d_model)

        # 6-head setup: 3 regression heads + 3 binary heads (per window size 6, 12, 24)
        self.reg_heads = nn.ModuleList([nn.Linear(d_model, reg_dim) for _ in range(3)])
        self.bin_heads = nn.ModuleList([nn.Linear(d_model, bin_dim) for _ in range(3)])
        self.heads = nn.ModuleList(list(self.reg_heads) + list(self.bin_heads))

    def forward(self, x, mask, delta, window_id=None):
        inp = torch.cat([x, mask, delta], dim=-1)
        h, _ = self.gru(inp)
        z = self.to_dmodel(h)

        time_mask = mask.sum(dim=-1) > 0
        z = self.transformer(z, src_key_padding_mask=~time_mask)
        pooled = self.attn_pool(z, padding_mask=time_mask)

        # For inference, use window_id=0 (6-hour window) by default
        if window_id is None:
            window_id = torch.zeros(x.size(0), dtype=torch.long, device=x.device)

        y_reg_out = torch.zeros(x.size(0), self.reg_heads[0].out_features, device=x.device)
        y_bin_out = torch.zeros(x.size(0), self.bin_heads[0].out_features, device=x.device)

        for i, w_id in enumerate(window_id):
            y_reg_out[i] = self.reg_heads[w_id](pooled[i])
            y_bin_out[i] = self.bin_heads[w_id](pooled[i])

        return y_reg_out, y_bin_out


# --- Wrapper Class ---

class ModelWrapper:
    def __init__(self, model_dir):
        self.device = torch.device("cpu")
        print(f"Loading model artifacts from {model_dir}...")
        
        # Load scalers and global mean from new model files
        self.scaler_X = joblib.load(os.path.join(model_dir, "scaler_X.pkl"))
        self.scaler_y_reg = joblib.load(os.path.join(model_dir, "scaler_y_reg.pkl"))
        self.global_feat_mean = np.load(os.path.join(model_dir, "global_feat_mean30.npy"))
        
        # Model parameters
        self.n_features = self.scaler_X.mean_.shape[0] if hasattr(self.scaler_X, "mean_") else 121
        self.reg_dim = 8  # respiration, coagulation, liver, cardiovascular, cns, renal, hours_beforesepsis, hours_beforedeath
        self.bin_dim = 1  # sepsis (binary)
        
        print(f"Initializing model with n_features={self.n_features}, reg_dim={self.reg_dim}, bin_dim={self.bin_dim}")
        
        # Initialize model architecture
        self.model = GRUDTransformer(
            n_features=self.n_features,
            hidden_size=64,
            d_model=128,
            nhead=4,
            num_layers=2,
            reg_dim=self.reg_dim,
            bin_dim=self.bin_dim
        )
        
        # Load model weights - try different formats
        model_path = os.path.join(model_dir, "model_joblib.pkl")
        weights_loaded = False
        
        # Custom unpickler to handle CUDA tensors on CPU-only machines
        import pickle
        import io
        
        class CPU_Unpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if module == 'torch.storage' and name == '_load_from_bytes':
                    return lambda b: torch.load(io.BytesIO(b), map_location='cpu')
                else:
                    return super().find_class(module, name)
        
        # Try CPU_Unpickler first (handles CUDA->CPU mapping)
        try:
            with open(model_path, 'rb') as f:
                state_dict = CPU_Unpickler(f).load()
            if isinstance(state_dict, dict) and 'model' in state_dict:
                self.model.load_state_dict(state_dict['model'])
            elif isinstance(state_dict, dict) and 'model_state_dict' in state_dict:
                self.model.load_state_dict(state_dict['model_state_dict'])
            else:
                self.model.load_state_dict(state_dict)
            print("Model weights loaded successfully ✅")
            weights_loaded = True
        except Exception as e:
            print(f"CPU_Unpickler failed: {e}")
            
        # Try torch.load as fallback
        if not weights_loaded:
            try:
                state_dict = torch.load(model_path, map_location='cpu')
                if isinstance(state_dict, dict) and 'model' in state_dict:
                    self.model.load_state_dict(state_dict['model'])
                elif isinstance(state_dict, dict) and 'model_state_dict' in state_dict:
                    self.model.load_state_dict(state_dict['model_state_dict'])
                else:
                    self.model.load_state_dict(state_dict)
                print("Model weights loaded via torch.load ✅")
                weights_loaded = True
            except Exception as e:
                print(f"torch.load failed: {e}")
             
        self.model.to(self.device)
        self.model.eval()

        # Output columns - regression outputs (scaled)
        self.regression_cols = [
            "respiration", "coagulation", "liver", "cardiovascular",
            "cns", "renal", "hours_beforesepsis", "hours_beforedeath"
        ]
        # Binary output (logit -> sigmoid)
        self.binary_cols = ["sepsis"]

    def preprocess_sequence(self, records: list):
        """
        Preprocess patient records for model input with GRU-D style imputation.
        """
        if not records:
            return None, None, None
            
        df = pd.DataFrame(records)
        
        # Map gender (f0_) to numeric
        if 'f0_' in df.columns:
            df['gender'] = df['f0_'].map({'M': 0, 'F': 1, 'Male': 0, 'Female': 1})
            df['gender'] = df['gender'].fillna(0)
        elif 'gender' not in df.columns:
            df['gender'] = np.nan
            
        # Add missing columns
        if 'weight' not in df.columns:
            df['weight'] = np.nan
            
        # Nullify target columns (prevent data leakage)
        target_cols = [
            "respiration", "coagulation", "liver", "cardiovascular",
            "cns", "renal", "hours_beforesepsis", "sepsis",
            "fod", "hours_beforedeath"
        ]
        for col in target_cols:
            if col in df.columns:
                df[col] = np.nan
        
        # Ensure all required features exist
        for col in MODEL_INPUT_FEATURES:
            if col not in df.columns:
                df[col] = np.nan
                
        X_df = df[MODEL_INPUT_FEATURES]
        X_seq = X_df.apply(pd.to_numeric, errors='coerce').to_numpy(dtype=np.float32)
        
        T, F = X_seq.shape
        
        if F != self.n_features:
            print(f"WARNING: Feature count mismatch. Expected {self.n_features}, got {F}.")
            
        # GRU-D style imputation
        mask = ~np.isnan(X_seq)
        X_filled = np.zeros_like(X_seq)
        delta = np.zeros_like(X_seq)
        
        # Get time column (hr) for delta calculation
        if 'hr' in df.columns:
            times = df['hr'].values.astype(float)
        else:
            times = np.arange(T, dtype=float)
            
        for f in range(F):
            mean_val = self.global_feat_mean[f] if f < len(self.global_feat_mean) else 0.0
            last_val = mean_val
            last_time = times[0] if len(times) > 0 else 0
            
            for t in range(T):
                if mask[t, f]:
                    delta[t, f] = 0.0
                    last_val = X_seq[t, f]
                    last_time = times[t]
                    X_filled[t, f] = last_val
                else:
                    if t > 0:
                        delta[t, f] = times[t] - last_time
                    else:
                        delta[t, f] = 0.0
                        
                    gamma = np.exp(-delta[t, f])
                    X_filled[t, f] = gamma * last_val + (1 - gamma) * mean_val
                    last_val = X_filled[t, f]
                    
        # Scale features
        X_scaled = self.scaler_X.transform(X_filled)
        
        # Handle NaN/Inf from scaling (zero-variance features produce NaN)
        X_scaled = np.nan_to_num(X_scaled, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Convert to tensors [1, T, F]
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(0)
        mask_tensor = torch.tensor(mask.astype(float), dtype=torch.float32).unsqueeze(0)
        delta_tensor = torch.tensor(delta, dtype=torch.float32).unsqueeze(0)
        
        return X_tensor, mask_tensor, delta_tensor

    def predict(self, records: list, window_id: int = 0):
        """
        Run prediction and return all 10 outputs.
        
        Args:
            records: List of patient records
            window_id: Prediction window (0=6h, 1=12h, 2=24h)
        """
        if not records:
            return None
        
        # Validate window_id
        window_id = max(0, min(2, window_id))  # Clamp to [0, 1, 2]
            
        with torch.no_grad():
            X, mask, delta = self.preprocess_sequence(records)
            if X is None:
                return None
                
            X = X.to(self.device)
            mask = mask.to(self.device)
            delta = delta.to(self.device)
            
            # Use specified window_id (0=6h, 1=12h, 2=24h)
            window_tensor = torch.tensor([window_id], dtype=torch.long, device=self.device)
            
            y_reg_out, y_bin_out = self.model(X, mask, delta, window_tensor)
            
            # Inverse transform regression outputs
            y_reg_np = y_reg_out.cpu().numpy()
            y_reg_original = self.scaler_y_reg.inverse_transform(y_reg_np)
            
            # Apply sigmoid to binary output (trained with BCEWithLogitsLoss)
            y_bin_np = torch.sigmoid(y_bin_out).cpu().numpy()
            
            result = {}
            
            # Regression outputs
            for i, col in enumerate(self.regression_cols):
                val = float(y_reg_original[0, i])
                # Clip SOFA scores to valid range [0, 4]
                if col in ["respiration", "coagulation", "liver", "cardiovascular", "cns", "renal"]:
                    val = max(0.0, min(4.0, val))
                # Clip hours to non-negative
                elif col in ["hours_beforesepsis", "hours_beforedeath"]:
                    val = max(0.0, val)
                result[col] = val
            
            # Binary output (sepsis probability)
            result["sepsis"] = float(y_bin_np[0, 0])
            
            # FOD (failure of organ dysfunction) - calculate from SOFA
            # High SOFA total indicates higher mortality risk
            sofa_sum = sum([
                result.get("respiration", 0),
                result.get("coagulation", 0),
                result.get("liver", 0),
                result.get("cardiovascular", 0),
                result.get("cns", 0),
                result.get("renal", 0)
            ])
            # Map SOFA to mortality probability using sigmoid
            # SOFA >= 11 has ~50% mortality in studies
            result["fod"] = 1.0 / (1.0 + np.exp(-0.3 * (sofa_sum - 8)))
            
            return result

# ai_service/lstm_model.py
import os
import pickle
import torch
from django.conf import settings  # Import settings để lấy thư mục gốc của dự án (nếu cần)

# Định nghĩa cấu trúc mạng LSTM (Giữ nguyên)
class HighPerformanceLSTM(torch.nn.Module):
    def __init__(self, num_products, embedding_dim=128, hidden_dim=256, num_layers=2):
        super().__init__()
        self.embedding = torch.nn.Embedding(num_products, embedding_dim)
        self.lstm = torch.nn.LSTM(embedding_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.layer_norm = torch.nn.LayerNorm(hidden_dim)
        self.fc = torch.nn.Linear(hidden_dim, num_products)
        
    def forward(self, x):
        out = self.embedding(x)
        out, _ = self.lstm(out)
        out = out[:, -1, :]
        out = self.layer_norm(out)
        return self.fc(out)


class LSTMRecommenderService:
    def __init__(self, model_relative_path="model_store/best_lstm_recommendation_model.pth", 
                 mappings_relative_path="model_store/product_mappings.pkl"):
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Mẹo nhỏ: Sử dụng BASE_DIR của Django để tạo đường dẫn tuyệt đối, 
        # tránh lỗi "FileNotFoundError" khi bạn deploy hoặc chạy test từ các thư mục khác nhau.
        if hasattr(settings, 'BASE_DIR'):
            model_path = os.path.join(settings.BASE_DIR, model_relative_path)
            mappings_path = os.path.join(settings.BASE_DIR, mappings_relative_path)
        else:
            # Fallback nếu test script độc lập không qua Django settings
            model_path = model_relative_path
            mappings_path = mappings_relative_path
        
        if not os.path.exists(mappings_path) or not os.path.exists(model_path):
            raise FileNotFoundError(
                f"\n[AI Error] Không tìm thấy file weights hoặc mapping!\n"
                f"Đường dẫn đã thử:\n- Model: {os.path.abspath(model_path)}\n- Mapping: {os.path.abspath(mappings_path)}"
            )
            
        # Tải bộ ánh xạ ID sản phẩm
        with open(mappings_path, "rb") as f:
            mappings = pickle.load(f)
            
        self.product_to_idx = mappings['product_to_idx']
        self.idx_to_product = mappings['idx_to_product']
        self.SEQUENCE_LENGTH = mappings.get('SEQUENCE_LENGTH', 10)
        self.num_products = len(self.product_to_idx)
        
        # Khởi tạo mạng và nạp trọng số
        self.model = HighPerformanceLSTM(num_products=self.num_products, embedding_dim=128, hidden_dim=256, num_layers=2)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def predict_sequence(self, user_history_list, num_predictions=20):
        if not user_history_list:
            return []

        current_seq_indices = []
        for prod in user_history_list:
            if prod in self.product_to_idx:
                current_seq_indices.append(self.product_to_idx[prod])
                
        if not current_seq_indices:
            return []
            
        if len(current_seq_indices) < self.SEQUENCE_LENGTH:
            current_seq_indices = [0] * (self.SEQUENCE_LENGTH - len(current_seq_indices)) + current_seq_indices
        else:
            current_seq_indices = current_seq_indices[-self.SEQUENCE_LENGTH:]
            
        predicted_indices = []
        
        with torch.no_grad():
            for _ in range(num_predictions):
                input_tensor = torch.tensor([current_seq_indices], dtype=torch.long).to(self.device)
                logits = self.model(input_tensor)
                
                next_item_idx = torch.argmax(logits, dim=1).item()
                predicted_indices.append(next_item_idx)
                
                current_seq_indices = current_seq_indices[1:] + [next_item_idx]
                
        return [self.idx_to_product[idx] for idx in predicted_indices if idx in self.idx_to_product]


# KHỞI TẠO SINGLETON INSTANCE (Tự động map theo đường dẫn mới của bạn)
lstm_predictor = LSTMRecommenderService()
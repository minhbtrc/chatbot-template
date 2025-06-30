#!/usr/bin/env python3
"""
Script review dataset cho evaluation RAG system
Sử dụng: python review_dataset.py
"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

def load_dataset(dataset_file: str) -> List[Dict[str, Any]]:
    """Load dataset từ file JSON"""
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        print(f"✅ Đã load {len(dataset)} câu hỏi từ {dataset_file}")
        return dataset
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {dataset_file}")
        return []
    except json.JSONDecodeError:
        print(f"❌ File JSON không hợp lệ: {dataset_file}")
        return []

class DatasetReviewer:
    def __init__(self, dataset_file: str):
        self.dataset_file = dataset_file
        self.dataset = load_dataset(dataset_file)
        self.reviewed_dataset: List[Dict[str, Any]] = []
        self.removed_items: List[Dict[str, Any]] = []
        self.current_index = 0
    
    def display_question(self, item: Dict[str, Any], index: int) -> None:
        """Hiển thị câu hỏi để review"""
        print("\n" + "="*80)
        print(f"📋 Câu hỏi {index+1}/{len(self.dataset)}")
        print("="*80)
        print(f"🆔 ID: {item.get('id', 'N/A')}")
        print(f"📝 Loại: {item.get('question_type', 'N/A')} | Độ khó: {item.get('difficulty', 'N/A')}")
        print(f"📄 Document: {item.get('document_id', 'N/A')}")
        
        print(f"\n❓ CÂU HỎI:")
        print(f"   {item.get('question', 'N/A')}")
        
        print(f"\n💡 TRẢ LỜI MONG ĐỢI:")
        expected_answer = item.get('expected_answer', 'N/A')
        if len(expected_answer) > 200:
            print(f"   {expected_answer[:200]}...")
        else:
            print(f"   {expected_answer}")
        
        print(f"\n📖 CONTEXT:")
        expected_context = item.get('expected_context', 'N/A')
        if len(expected_context) > 150:
            print(f"   {expected_context[:150]}...")
        else:
            print(f"   {expected_context}")
        
        print("\n" + "="*80)
    
    def get_user_decision(self) -> str:
        """Lấy quyết định từ user"""
        print("\n🎯 HƯỚNG DẪN:")
        print("  k = Keep (Giữ lại)")
        print("  r = Remove (Loại bỏ)")
        print("  s = Skip (Bỏ qua)")
        print("  b = Back (Quay lại câu trước)")
        print("  q = Quit (Thoát và lưu)")
        print("  h = Help (Hướng dẫn chi tiết)")
        
        while True:
            action = input("\n👉 Quyết định của bạn (k/r/s/b/q/h): ").lower().strip()
            
            if action in ['k', 'r', 's', 'b', 'q', 'h']:
                return action
            else:
                print("❗ Vui lòng chọn một trong: k, r, s, b, q, h")
    
    def show_help(self) -> None:
        """Hiển thị hướng dẫn chi tiết"""
        help_text = """
📚 HƯỚNG DẪN CHI TIẾT

✅ KEEP (Giữ lại) - Chọn 'k' khi:
  - Câu hỏi rõ ràng, dễ hiểu
  - Có thể trả lời dựa trên context được cung cấp
  - Câu trả lời expected hợp lý và chính xác
  - Phù hợp với domain knowledge
  - Có giá trị cho việc evaluation

❌ REMOVE (Loại bỏ) - Chọn 'r' khi:
  - Câu hỏi mơ hồ, khó hiểu
  - Không thể trả lời từ context
  - Câu trả lời sai hoặc không chính xác
  - Quá đơn giản hoặc quá phức tạp
  - Duplicate với câu hỏi khác
  - Không phù hợp với mục đích evaluation

⏭️ SKIP (Bỏ qua) - Chọn 's' khi:
  - Không chắc chắn về quyết định
  - Cần xem xét thêm
  - Sẽ quay lại sau

🔙 BACK (Quay lại) - Chọn 'b' để:
  - Xem lại câu hỏi trước đó
  - Thay đổi quyết định trước

💾 QUIT (Thoát) - Chọn 'q' để:
  - Lưu tiến trình hiện tại
  - Thoát khỏi session review
"""
        print(help_text)
        input("\nNhấn Enter để tiếp tục...")
    
    def review_interactive(self) -> str:
        """Review dataset tương tác"""
        print("🔍 BẮT ĐẦU REVIEW DATASET")
        print("=" * 50)
        
        if not self.dataset:
            print("❌ Dataset trống hoặc không load được")
            return ""
        
        while self.current_index < len(self.dataset):
            item = self.dataset[self.current_index]
            
            # Hiển thị câu hỏi
            self.display_question(item, self.current_index)
            
            # Lấy quyết định
            action = self.get_user_decision()
            
            if action == 'k':  # Keep
                self.reviewed_dataset.append(item)
                print("✅ Đã giữ lại câu hỏi")
                self.current_index += 1
                
            elif action == 'r':  # Remove
                reason = input("📝 Lý do loại bỏ: ").strip()
                if not reason:
                    reason = "Không đạt tiêu chí chất lượng"
                
                item_with_reason = item.copy()
                item_with_reason['removal_reason'] = reason
                item_with_reason['removed_at'] = datetime.now().isoformat()
                self.removed_items.append(item_with_reason)
                
                print(f"❌ Đã loại bỏ: {reason}")
                self.current_index += 1
                
            elif action == 's':  # Skip
                print("⏭️ Đã bỏ qua câu hỏi này")
                self.current_index += 1
                
            elif action == 'b':  # Back
                if self.current_index > 0:
                    self.current_index -= 1
                    # Remove from reviewed/removed lists if exists
                    prev_item = self.dataset[self.current_index]
                    self.reviewed_dataset = [x for x in self.reviewed_dataset if x.get('id') != prev_item.get('id')]
                    self.removed_items = [x for x in self.removed_items if x.get('id') != prev_item.get('id')]
                    print("🔙 Quay lại câu hỏi trước")
                else:
                    print("❗ Đã ở câu hỏi đầu tiên")
                    
            elif action == 'q':  # Quit
                print("💾 Đang lưu tiến trình...")
                return self.save_progress()
                
            elif action == 'h':  # Help
                self.show_help()
        
        print("\n🎉 Đã review hết tất cả câu hỏi!")
        return self.save_progress()
    
    def save_progress(self) -> str:
        """Lưu tiến trình review"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Lưu dataset đã filter
        filtered_file = f"filtered_dataset_{timestamp}.json"
        with open(filtered_file, 'w', encoding='utf-8') as f:
            json.dump(self.reviewed_dataset, f, ensure_ascii=False, indent=2)
        
        # Lưu items bị loại bỏ
        removed_file = f"removed_items_{timestamp}.json"
        with open(removed_file, 'w', encoding='utf-8') as f:
            json.dump(self.removed_items, f, ensure_ascii=False, indent=2)
        
        # Tạo báo cáo review
        report_file = f"review_report_{timestamp}.txt"
        self.create_review_report(report_file)
        
        print(f"\n📊 KẾT QUỢ REVIEW:")
        print(f"✅ Giữ lại: {len(self.reviewed_dataset)} câu hỏi")
        print(f"❌ Loại bỏ: {len(self.removed_items)} câu hỏi")
        print(f"⏭️ Bỏ qua: {len(self.dataset) - len(self.reviewed_dataset) - len(self.removed_items)} câu hỏi")
        print(f"📁 File filtered: {filtered_file}")
        print(f"📁 File removed: {removed_file}")
        print(f"📄 Báo cáo: {report_file}")
        
        return filtered_file
    
    def create_review_report(self, report_file: str) -> None:
        """Tạo báo cáo chi tiết về quá trình review"""
        
        # Thống kê
        total_reviewed = len(self.reviewed_dataset) + len(self.removed_items)
        keep_rate = len(self.reviewed_dataset) / total_reviewed * 100 if total_reviewed > 0 else 0
        
        # Phân tích lý do loại bỏ
        removal_reasons = {}
        for item in self.removed_items:
            reason = item.get('removal_reason', 'Không rõ')
            removal_reasons[reason] = removal_reasons.get(reason, 0) + 1
        
        # Phân tích theo loại câu hỏi
        kept_by_type = {}
        removed_by_type = {}
        
        for item in self.reviewed_dataset:
            q_type = item.get('question_type', 'unknown')
            kept_by_type[q_type] = kept_by_type.get(q_type, 0) + 1
            
        for item in self.removed_items:
            q_type = item.get('question_type', 'unknown')
            removed_by_type[q_type] = removed_by_type.get(q_type, 0) + 1
        
        report = f"""
📊 BÁO CÁO REVIEW DATASET
=========================

🕒 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📁 File gốc: {self.dataset_file}

📈 TỔNG QUAN:
- Tổng số câu hỏi: {len(self.dataset)}
- Đã review: {total_reviewed}
- Giữ lại: {len(self.reviewed_dataset)} ({keep_rate:.1f}%)
- Loại bỏ: {len(self.removed_items)} ({100-keep_rate:.1f}%)
- Chưa review: {len(self.dataset) - total_reviewed}

🔍 PHÂN TÍCH LÝ DO LOẠI BỎ:
{chr(10).join([f"- {reason}: {count} câu" for reason, count in removal_reasons.items()])}

📋 PHÂN TÍCH THEO LOẠI CÂU HỎI:

Giữ lại:
{chr(10).join([f"- {q_type}: {count} câu" for q_type, count in kept_by_type.items()])}

Loại bỏ:
{chr(10).join([f"- {q_type}: {count} câu" for q_type, count in removed_by_type.items()])}

💡 KHUYẾN NGHỊ:
- Tỷ lệ giữ lại: {"Tốt" if keep_rate >= 70 else "Cần cải thiện" if keep_rate >= 50 else "Cần xem xét lại quy trình sinh dataset"}
- Chất lượng dataset: {"Đạt yêu cầu" if len(self.reviewed_dataset) >= 50 else "Cần sinh thêm dataset"}

🔄 BƯỚC TIẾP THEO:
1. Kiểm tra file filtered_dataset_*.json
2. Chạy evaluation pipeline với dataset đã filter
3. Phân tích kết quả evaluation
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

def auto_filter_dataset(dataset_file: str) -> str:
    """Auto filter dataset dựa trên tiêu chí cơ bản"""
    
    dataset = load_dataset(dataset_file)
    if not dataset:
        return ""
    
    print("🤖 Bắt đầu auto-filter dataset...")
    
    criteria = {
        "min_question_length": 10,
        "max_question_length": 500,
        "min_answer_length": 20,
        "max_answer_length": 2000,
        "required_fields": ["id", "question", "expected_answer", "expected_context"],
        "forbidden_patterns": ["test", "example", "dummy", "lorem ipsum"]
    }
    
    filtered_dataset = []
    removed_items = []
    
    for item in dataset:
        should_keep = True
        removal_reason = ""
        
        # Kiểm tra các field bắt buộc
        for field in criteria["required_fields"]:
            if field not in item or not item[field]:
                should_keep = False
                removal_reason = f"Thiếu field: {field}"
                break
        
        if should_keep:
            question = item.get("question", "")
            answer = item.get("expected_answer", "")
            
            # Kiểm tra độ dài
            if len(question) < criteria["min_question_length"]:
                should_keep = False
                removal_reason = "Câu hỏi quá ngắn"
            elif len(question) > criteria["max_question_length"]:
                should_keep = False
                removal_reason = "Câu hỏi quá dài"
            elif len(answer) < criteria["min_answer_length"]:
                should_keep = False
                removal_reason = "Câu trả lời quá ngắn"
            elif len(answer) > criteria["max_answer_length"]:
                should_keep = False
                removal_reason = "Câu trả lời quá dài"
            
            # Kiểm tra pattern cấm
            if should_keep:
                text_to_check = f"{question} {answer}".lower()
                for pattern in criteria["forbidden_patterns"]:
                    if pattern in text_to_check:
                        should_keep = False
                        removal_reason = f"Chứa pattern cấm: {pattern}"
                        break
        
        if should_keep:
            filtered_dataset.append(item)
        else:
            item_with_reason = item.copy()
            item_with_reason['removal_reason'] = removal_reason
            item_with_reason['removed_at'] = datetime.now().isoformat()
            removed_items.append(item_with_reason)
    
    # Lưu kết quả
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filtered_file = f"auto_filtered_dataset_{timestamp}.json"
    with open(filtered_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_dataset, f, ensure_ascii=False, indent=2)
    
    removed_file = f"auto_removed_items_{timestamp}.json"
    with open(removed_file, 'w', encoding='utf-8') as f:
        json.dump(removed_items, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Auto-filter hoàn thành:")
    print(f"  - Giữ lại: {len(filtered_dataset)} câu hỏi")
    print(f"  - Loại bỏ: {len(removed_items)} câu hỏi")
    print(f"  - File output: {filtered_file}")
    
    return filtered_file

def main():
    """Main function"""
    
    print("🔍 RAG Dataset Reviewer")
    print("=" * 50)
    
    # Lấy file dataset
    dataset_file = input("Nhập tên file dataset (hoặc Enter để dùng file mới nhất): ").strip()
    
    if not dataset_file:
        # Tìm file dataset mới nhất
        import glob
        dataset_files = glob.glob("evaluation_dataset_*.json")
        if dataset_files:
            dataset_file = max(dataset_files, key=os.path.getctime)
            print(f"📁 Sử dụng file: {dataset_file}")
        else:
            print("❌ Không tìm thấy file dataset nào")
            return
    
    if not os.path.exists(dataset_file):
        print(f"❌ File không tồn tại: {dataset_file}")
        return
    
    # Chọn mode review
    print("\n🎯 Chọn mode review:")
    print("1. Interactive Review (Tương tác từng câu)")
    print("2. Auto Filter (Tự động filter theo tiêu chí)")
    
    mode = input("Chọn mode (1/2): ").strip()
    
    if mode == "1":
        # Interactive review
        reviewer = DatasetReviewer(dataset_file)
        filtered_file = reviewer.review_interactive()
        
        if filtered_file:
            print(f"\n🎉 Review hoàn thành!")
            print(f"📁 Dataset đã filter: {filtered_file}")
            print("\n🔄 Bước tiếp theo:")
            print("python run_evaluation.py")
        
    elif mode == "2":
        # Auto filter
        filtered_file = auto_filter_dataset(dataset_file)
        
        if filtered_file:
            print(f"\n🎉 Auto-filter hoàn thành!")
            print(f"📁 Dataset đã filter: {filtered_file}")
            print("\n💡 Lưu ý: Nên review manual để đảm bảo chất lượng")
            print("\n🔄 Bước tiếp theo:")
            print("python run_evaluation.py")
    
    else:
        print("❌ Mode không hợp lệ")

if __name__ == "__main__":
    main() 
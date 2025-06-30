#!/usr/bin/env python3
"""
Script chạy evaluation cho RAG system
Sử dụng: python run_evaluation.py
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import glob

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_filtered_dataset(dataset_file: str) -> List[Dict[str, Any]]:
    """Load filtered dataset từ file JSON"""
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        print(f"✅ Đã load {len(dataset)} test cases từ {dataset_file}")
        return dataset
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {dataset_file}")
        return []
    except json.JSONDecodeError:
        print(f"❌ File JSON không hợp lệ: {dataset_file}")
        return []

def create_mock_evaluator():
    """Tạo mock evaluator để demo (thay thế khi có evaluator thực)"""
    
    class MockRAGEvaluator:
        def __init__(self):
            self.name = "Mock RAG Evaluator"
        
        def evaluate_batch(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Mock evaluation - thay thế bằng evaluator thực"""
            import random
            import time
            
            print("🤖 Đang chạy evaluation (Mock)...")
            
            results = []
            total_retrieval_time = 0
            total_generation_time = 0
            successful_cases = 0
            failed_cases = 0
            
            for i, test_case in enumerate(test_cases):
                print(f"📊 Đang evaluate test case {i+1}/{len(test_cases)}: {test_case.get('id', 'N/A')}")
                
                # Simulate processing time
                time.sleep(0.1)
                
                # Mock metrics (thay thế bằng evaluation thực)
                retrieval_time = random.uniform(0.1, 0.5)
                generation_time = random.uniform(0.5, 2.0)
                
                # Mock scores
                retrieval_score = random.uniform(0.6, 0.95)
                generation_score = random.uniform(0.7, 0.9)
                faithfulness_score = random.uniform(0.75, 0.95)
                
                is_success = retrieval_score > 0.7 and generation_score > 0.75
                
                if is_success:
                    successful_cases += 1
                else:
                    failed_cases += 1
                
                result = {
                    "test_case_id": test_case.get('id', f'test_{i}'),
                    "question": test_case.get('question', ''),
                    "question_type": test_case.get('question_type', 'unknown'),
                    "difficulty": test_case.get('difficulty', 'unknown'),
                    "success": is_success,
                    "retrieval_metrics": {
                        "precision_at_5": retrieval_score,
                        "recall_at_5": retrieval_score * 0.8,
                        "mrr": retrieval_score * 0.9,
                        "retrieval_time": retrieval_time
                    },
                    "generation_metrics": {
                        "faithfulness": faithfulness_score,
                        "relevance": generation_score,
                        "quality": generation_score * 0.95,
                        "generation_time": generation_time
                    },
                    "failure_reason": None if is_success else "Low retrieval/generation score"
                }
                
                results.append(result)
                total_retrieval_time += retrieval_time
                total_generation_time += generation_time
            
            # Tính toán metrics tổng thể
            avg_precision = sum(r["retrieval_metrics"]["precision_at_5"] for r in results) / len(results)
            avg_recall = sum(r["retrieval_metrics"]["recall_at_5"] for r in results) / len(results)
            avg_mrr = sum(r["retrieval_metrics"]["mrr"] for r in results) / len(results)
            avg_faithfulness = sum(r["generation_metrics"]["faithfulness"] for r in results) / len(results)
            avg_relevance = sum(r["generation_metrics"]["relevance"] for r in results) / len(results)
            avg_quality = sum(r["generation_metrics"]["quality"] for r in results) / len(results)
            
            # Phân tích theo loại câu hỏi
            question_type_performance = {}
            difficulty_performance = {}
            
            for result in results:
                q_type = result["question_type"]
                difficulty = result["difficulty"]
                
                if q_type not in question_type_performance:
                    question_type_performance[q_type] = []
                question_type_performance[q_type].append(1 if result["success"] else 0)
                
                if difficulty not in difficulty_performance:
                    difficulty_performance[difficulty] = []
                difficulty_performance[difficulty].append(1 if result["success"] else 0)
            
            # Tính average cho từng loại
            for q_type in question_type_performance:
                scores = question_type_performance[q_type]
                question_type_performance[q_type] = sum(scores) / len(scores)
            
            for difficulty in difficulty_performance:
                scores = difficulty_performance[difficulty]
                difficulty_performance[difficulty] = sum(scores) / len(scores)
            
            # Phân tích lỗi
            failure_reasons = {}
            for result in results:
                if not result["success"] and result["failure_reason"]:
                    reason = result["failure_reason"]
                    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
            
            return {
                "summary": {
                    "total_cases": len(test_cases),
                    "successful_cases": successful_cases,
                    "failed_cases": failed_cases,
                    "success_rate": successful_cases / len(test_cases)
                },
                "metrics": {
                    "retrieval": {
                        "precision_at_5": avg_precision,
                        "recall_at_5": avg_recall,
                        "mrr": avg_mrr
                    },
                    "generation": {
                        "faithfulness": avg_faithfulness,
                        "relevance": avg_relevance,
                        "quality": avg_quality
                    }
                },
                "performance": {
                    "avg_retrieval_time": total_retrieval_time / len(test_cases),
                    "avg_generation_time": total_generation_time / len(test_cases),
                    "total_time": total_retrieval_time + total_generation_time
                },
                "question_type_performance": question_type_performance,
                "difficulty_performance": difficulty_performance,
                "failure_analysis": {
                    "top_reasons": failure_reasons
                },
                "detailed_results": results,
                "recommendations": generate_recommendations(successful_cases / len(test_cases), failure_reasons)
            }
    
    return MockRAGEvaluator()

def generate_recommendations(success_rate: float, failure_reasons: Dict[str, int]) -> List[str]:
    """Tạo recommendations dựa trên kết quả evaluation"""
    
    recommendations = []
    
    if success_rate < 0.7:
        recommendations.append("Tỷ lệ thành công thấp - cần cải thiện retrieval hoặc generation")
    
    if success_rate < 0.5:
        recommendations.append("Cần xem xét lại cấu hình RAG system")
    
    if "Low retrieval/generation score" in failure_reasons:
        count = failure_reasons["Low retrieval/generation score"]
        if count > 5:
            recommendations.append("Nhiều lỗi do retrieval/generation kém - cần fine-tune model")
    
    if success_rate >= 0.8:
        recommendations.append("Performance tốt - có thể tăng độ khó của test cases")
    
    if not recommendations:
        recommendations.append("Kết quả evaluation ổn định - tiếp tục monitor")
    
    return recommendations

def run_comprehensive_evaluation(dataset_file: str) -> Optional[Dict[str, Any]]:
    """Chạy evaluation toàn diện"""
    
    print("🚀 KHỞI TẠO EVALUATION PIPELINE")
    print("=" * 50)
    
    # Load dataset
    test_cases = load_filtered_dataset(dataset_file)
    if not test_cases:
        print("❌ Không thể load dataset")
        return None
    
    print(f"📊 Sẽ evaluate {len(test_cases)} test cases")
    
    # Khởi tạo evaluator
    print("🔧 Khởi tạo evaluator...")
    try:
        # Thử import evaluator thực
        # from src.experts.rag_bot.evaluator import create_rag_evaluator
        # evaluator = create_rag_evaluator()
        
        # Tạm thời dùng mock evaluator
        evaluator = create_mock_evaluator()
        print("✅ Evaluator đã sẵn sàng (Mock mode)")
        
    except Exception as e:
        print(f"⚠️ Không thể khởi tạo evaluator thực, dùng mock: {str(e)}")
        evaluator = create_mock_evaluator()
    
    # Chạy evaluation
    print(f"🧪 Bắt đầu evaluation...")
    start_time = datetime.now()
    
    try:
        results = evaluator.evaluate_batch(test_cases)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Evaluation hoàn thành trong {duration:.2f} giây")
        
        # Thêm metadata
        results["metadata"] = {
            "dataset_file": dataset_file,
            "evaluation_start": start_time.isoformat(),
            "evaluation_end": end_time.isoformat(),
            "duration_seconds": duration,
            "evaluator_type": "mock"  # Thay đổi khi dùng evaluator thực
        }
        
        return results
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy evaluation: {str(e)}")
        return None

def save_evaluation_results(results: Dict[str, Any]) -> tuple:
    """Lưu kết quả evaluation"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Lưu kết quả chi tiết
    detailed_file = f"evaluation_report_{timestamp}.json"
    with open(detailed_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Tạo summary report
    summary_file = f"summary_report_{timestamp}.md"
    create_summary_report(results, summary_file)
    
    # Tạo CSV cho analysis
    csv_file = f"evaluation_data_{timestamp}.csv"
    create_csv_report(results, csv_file)
    
    print(f"📁 Kết quả đã được lưu:")
    print(f"  - Chi tiết: {detailed_file}")
    print(f"  - Tóm tắt: {summary_file}")
    print(f"  - Data CSV: {csv_file}")
    
    return detailed_file, summary_file, csv_file

def create_summary_report(results: Dict[str, Any], output_file: str) -> None:
    """Tạo báo cáo tóm tắt"""
    
    summary = results["summary"]
    metrics = results["metrics"]
    performance = results["performance"]
    
    report = f"""# 📊 Báo Cáo Evaluation RAG System

## 🎯 Tổng Quan Kết Quả

- **Thời gian evaluation:** {results["metadata"]["evaluation_start"]} - {results["metadata"]["evaluation_end"]}
- **Thời lượng:** {results["metadata"]["duration_seconds"]:.2f} giây
- **Dataset:** {results["metadata"]["dataset_file"]}
- **Tổng số test cases:** {summary["total_cases"]}
- **Thành công:** {summary["successful_cases"]}
- **Thất bại:** {summary["failed_cases"]}
- **Tỷ lệ thành công:** {summary["success_rate"]:.2%}

## 📈 Metrics Chi Tiết

### 🔍 Retrieval Performance
- **Precision@5:** {metrics["retrieval"]["precision_at_5"]:.3f}
- **Recall@5:** {metrics["retrieval"]["recall_at_5"]:.3f}
- **MRR (Mean Reciprocal Rank):** {metrics["retrieval"]["mrr"]:.3f}

### 🤖 Generation Performance
- **Faithfulness:** {metrics["generation"]["faithfulness"]:.3f}
- **Relevance:** {metrics["generation"]["relevance"]:.3f}
- **Quality:** {metrics["generation"]["quality"]:.3f}

## ⚡ Performance Metrics
- **Avg Retrieval Time:** {performance["avg_retrieval_time"]:.2f}s
- **Avg Generation Time:** {performance["avg_generation_time"]:.2f}s
- **Total Processing Time:** {performance["total_time"]:.2f}s

## 📊 Performance theo Loại Câu Hỏi

"""
    
    if "question_type_performance" in results:
        for q_type, score in results["question_type_performance"].items():
            report += f"- **{q_type}:** {score:.2%}\n"
    
    report += "\n## 📈 Performance theo Độ Khó\n\n"
    
    if "difficulty_performance" in results:
        for difficulty, score in results["difficulty_performance"].items():
            report += f"- **{difficulty}:** {score:.2%}\n"
    
    report += "\n## 🔍 Phân Tích Lỗi\n\n"
    
    if results["failure_analysis"]["top_reasons"]:
        report += "### Lý do thất bại chính:\n"
        for reason, count in results["failure_analysis"]["top_reasons"].items():
            report += f"- **{reason}:** {count} cases\n"
    else:
        report += "Không có lỗi đáng kể.\n"
    
    report += "\n## 💡 Recommendations\n\n"
    for rec in results["recommendations"]:
        report += f"- {rec}\n"
    
    report += f"""
## 🔄 Bước Tiếp Theo

1. **Phân tích chi tiết:** Xem file `evaluation_report_*.json`
2. **Visualize kết quả:** Chạy `python create_dashboard.py`
3. **Cải thiện system:** Dựa trên recommendations
4. **Re-evaluate:** Sau khi có improvements

---
*Báo cáo được tạo tự động bởi RAG Evaluation Pipeline*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

def create_csv_report(results: Dict[str, Any], output_file: str) -> None:
    """Tạo CSV report cho analysis"""
    
    import csv
    
    detailed_results = results.get("detailed_results", [])
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if not detailed_results:
            return
            
        fieldnames = [
            'test_case_id', 'question_type', 'difficulty', 'success',
            'precision_at_5', 'recall_at_5', 'mrr', 'retrieval_time',
            'faithfulness', 'relevance', 'quality', 'generation_time',
            'failure_reason'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in detailed_results:
            row = {
                'test_case_id': result.get('test_case_id', ''),
                'question_type': result.get('question_type', ''),
                'difficulty': result.get('difficulty', ''),
                'success': result.get('success', False),
                'precision_at_5': result.get('retrieval_metrics', {}).get('precision_at_5', 0),
                'recall_at_5': result.get('retrieval_metrics', {}).get('recall_at_5', 0),
                'mrr': result.get('retrieval_metrics', {}).get('mrr', 0),
                'retrieval_time': result.get('retrieval_metrics', {}).get('retrieval_time', 0),
                'faithfulness': result.get('generation_metrics', {}).get('faithfulness', 0),
                'relevance': result.get('generation_metrics', {}).get('relevance', 0),
                'quality': result.get('generation_metrics', {}).get('quality', 0),
                'generation_time': result.get('generation_metrics', {}).get('generation_time', 0),
                'failure_reason': result.get('failure_reason', '')
            }
            writer.writerow(row)

def find_latest_filtered_dataset() -> Optional[str]:
    """Tìm file filtered dataset mới nhất"""
    
    patterns = [
        "filtered_dataset_*.json",
        "auto_filtered_dataset_*.json"
    ]
    
    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(pattern))
    
    if all_files:
        latest_file = max(all_files, key=os.path.getctime)
        return latest_file
    
    return None

def main():
    """Main function"""
    
    print("🧪 RAG Evaluation Runner")
    print("=" * 50)
    
    # Lấy file dataset
    dataset_file = input("Nhập tên file dataset đã filter (hoặc Enter để dùng file mới nhất): ").strip()
    
    if not dataset_file:
        latest_file = find_latest_filtered_dataset()
        if latest_file:
            dataset_file = latest_file
            print(f"📁 Sử dụng file mới nhất: {dataset_file}")
        else:
            print("❌ Không tìm thấy file filtered dataset nào")
            print("💡 Hãy chạy review_dataset.py trước")
            return
    
    if not os.path.exists(dataset_file):
        print(f"❌ File không tồn tại: {dataset_file}")
        return
    
    # Confirm trước khi chạy
    confirm = input(f"Xác nhận chạy evaluation với file '{dataset_file}'? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Đã hủy evaluation")
        return
    
    # Chạy evaluation
    results = run_comprehensive_evaluation(dataset_file)
    
    if results:
        # Lưu kết quả
        detailed_file, summary_file, csv_file = save_evaluation_results(results)
        
        # Hiển thị kết quả tóm tắt
        print(f"\n🎉 EVALUATION HOÀN THÀNH!")
        print("=" * 50)
        print(f"📊 Tỷ lệ thành công: {results['summary']['success_rate']:.2%}")
        print(f"⚡ Thời gian xử lý: {results['metadata']['duration_seconds']:.2f}s")
        print(f"🔍 Precision@5: {results['metrics']['retrieval']['precision_at_5']:.3f}")
        print(f"🤖 Faithfulness: {results['metrics']['generation']['faithfulness']:.3f}")
        
        print(f"\n📁 Files được tạo:")
        print(f"  - {detailed_file}")
        print(f"  - {summary_file}")
        print(f"  - {csv_file}")
        
        print(f"\n🔄 Bước tiếp theo:")
        print("1. Xem summary report để hiểu kết quả")
        print("2. Chạy python create_dashboard.py để tạo visualization")
        print("3. Phân tích detailed results để cải thiện system")
        
    else:
        print("❌ Evaluation thất bại")

if __name__ == "__main__":
    main() 
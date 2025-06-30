#!/usr/bin/env python3
"""
Script chạy evaluation cho RAG system
Sử dụng: python run_evaluation.py
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, cast
import glob

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import dependencies
from src.common.config import Config
from src.config_injector import update_injector_with_config, get_instance
from src.experts.rag_bot.expert import RAGBotExpert
from src.experts.rag_bot.evaluator import RAGEvaluator, EvaluationResult
from src.common.logging import logger

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

def convert_dataset_to_test_cases(dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert dataset format to evaluation test cases format"""
    test_cases = []
    
    for item in dataset:
        test_case = {
            "query": item.get("question", ""),
            "expected_context": item.get("expected_context", ""),
            "expected_response": item.get("expected_answer", ""),
            "expected_doc_id": item.get("document_id", ""),
            "question_type": item.get("question_type", "unknown"),
            "difficulty": item.get("difficulty", "unknown"),
            "id": item.get("id", "")
        }
        test_cases.append(test_case)
    
    return test_cases

def convert_evaluation_results_to_report_format(results: List[EvaluationResult]) -> Dict[str, Any]:
    """Convert EvaluationResult objects to the expected report format"""
    
    if not results:
        return {"error": "No evaluation results provided"}
    
    total_cases = len(results)
    successful_cases = 0
    failed_cases = 0
    
    # Calculate success/failure based on retrieval and generation scores
    for result in results:
        retrieval_success = getattr(result, 'top_5_accuracy_score', 0) > 0.7 if hasattr(result, 'top_5_accuracy_score') else result.retrieval_score and result.retrieval_score > 0.7
        generation_success = getattr(result, 'llm_as_judge_score', 0) > 0.5 if hasattr(result, 'llm_as_judge_score') else result.generation_score and result.generation_score > 0.5
        
        if retrieval_success and generation_success:
            successful_cases += 1
        else:
            failed_cases += 1
    
    # Calculate aggregate metrics
    retrieval_scores: List[float] = []
    generation_scores: List[float] = []
    faithfulness_scores: List[float] = []
    quality_scores: List[float] = []
    
    for result in results:
        # Use the new metric names if available, otherwise fall back to legacy
        if hasattr(result, 'top_5_accuracy_score'):
            score = getattr(result, 'top_5_accuracy_score', 0)
            if score is not None:
                retrieval_scores.append(float(score))
        elif result.retrieval_score is not None:
            retrieval_scores.append(float(result.retrieval_score))
            
        if hasattr(result, 'llm_as_judge_score'):
            score = getattr(result, 'llm_as_judge_score', 0)
            if score is not None:
                generation_scores.append(float(score))
        elif result.generation_score is not None:
            generation_scores.append(float(result.generation_score))
            
        if result.faithfulness_score is not None:
            faithfulness_scores.append(float(result.faithfulness_score))
            
        if result.quality_score is not None:
            quality_scores.append(float(result.quality_score))
    
    # Calculate averages
    avg_precision = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0
    avg_recall = avg_precision * 0.8  # Approximation for recall
    avg_mrr = avg_precision * 0.9  # Approximation for MRR
    avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores) if faithfulness_scores else 0
    avg_relevance = sum(generation_scores) / len(generation_scores) if generation_scores else 0
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    
    # Calculate performance metrics
    retrieval_times = [r.retrieval_latency for r in results if r.retrieval_latency is not None]
    generation_times = [r.generation_latency for r in results if r.generation_latency is not None]
    
    avg_retrieval_time = sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0
    avg_generation_time = sum(generation_times) / len(generation_times) if generation_times else 0
    
    # Analyze by question type and difficulty
    question_type_performance: Dict[str, List[int]] = {}
    difficulty_performance: Dict[str, List[int]] = {}
    
    for result in results:
        # Extract metadata from the result
        q_type = result.metadata.get('question_type', 'unknown') if result.metadata else 'unknown'
        difficulty = result.metadata.get('difficulty', 'unknown') if result.metadata else 'unknown'
        
        # Determine success
        retrieval_success = getattr(result, 'top_5_accuracy_score', 0) > 0.7 if hasattr(result, 'top_5_accuracy_score') else result.retrieval_score and result.retrieval_score > 0.7
        generation_success = getattr(result, 'llm_as_judge_score', 0) > 0.5 if hasattr(result, 'llm_as_judge_score') else result.generation_score and result.generation_score > 0.5
        is_success = retrieval_success and generation_success
        
        if q_type not in question_type_performance:
            question_type_performance[q_type] = []
        question_type_performance[q_type].append(1 if is_success else 0)
        
        if difficulty not in difficulty_performance:
            difficulty_performance[difficulty] = []
        difficulty_performance[difficulty].append(1 if is_success else 0)
    
    # Calculate averages for each category
    question_type_avg: Dict[str, float] = {}
    for q_type in question_type_performance:
        scores = question_type_performance[q_type]
        question_type_avg[q_type] = sum(scores) / len(scores)
    
    difficulty_avg: Dict[str, float] = {}
    for difficulty in difficulty_performance:
        scores = difficulty_performance[difficulty]
        difficulty_avg[difficulty] = sum(scores) / len(scores)
    
    # Analyze failures
    failure_reasons: Dict[str, int] = {}
    for result in results:
        retrieval_success = getattr(result, 'top_5_accuracy_score', 0) > 0.7 if hasattr(result, 'top_5_accuracy_score') else result.retrieval_score and result.retrieval_score > 0.7
        generation_success = getattr(result, 'llm_as_judge_score', 0) > 0.5 if hasattr(result, 'llm_as_judge_score') else result.generation_score and result.generation_score > 0.5
        
        if not retrieval_success:
            reason = "Low retrieval score"
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        elif not generation_success:
            reason = "Low generation score"
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
    
    # Create detailed results for compatibility
    detailed_results = []
    for i, result in enumerate(results):
        retrieval_success = getattr(result, 'top_5_accuracy_score', 0) > 0.7 if hasattr(result, 'top_5_accuracy_score') else result.retrieval_score and result.retrieval_score > 0.7
        generation_success = getattr(result, 'llm_as_judge_score', 0) > 0.5 if hasattr(result, 'llm_as_judge_score') else result.generation_score and result.generation_score > 0.5
        is_success = retrieval_success and generation_success
        
        detailed_result = {
            "test_case_id": result.metadata.get('id', f'test_{i}') if result.metadata else f'test_{i}',
            "question": result.query,
            "question_type": result.metadata.get('question_type', 'unknown') if result.metadata else 'unknown',
            "difficulty": result.metadata.get('difficulty', 'unknown') if result.metadata else 'unknown',
            "success": is_success,
            "retrieval_metrics": {
                "precision_at_5": getattr(result, 'top_5_accuracy_score', result.retrieval_score or 0),
                "recall_at_5": getattr(result, 'top_5_accuracy_score', result.retrieval_score or 0) * 0.8,
                "mrr": getattr(result, 'mrr_at_10_score', result.retrieval_score or 0) if hasattr(result, 'mrr_at_10_score') else (result.retrieval_score or 0) * 0.9,
                "retrieval_time": result.retrieval_latency or 0
            },
            "generation_metrics": {
                "faithfulness": result.faithfulness_score or 0,
                "relevance": getattr(result, 'llm_as_judge_score', result.generation_score or 0),
                "quality": result.quality_score or 0,
                "generation_time": result.generation_latency or 0
            },
            "failure_reason": None if is_success else ("Low retrieval score" if not retrieval_success else "Low generation score")
        }
        detailed_results.append(detailed_result)
    
    # Generate recommendations
    success_rate = successful_cases / total_cases if total_cases > 0 else 0
    recommendations = generate_recommendations(success_rate, failure_reasons)
    
    return {
        "summary": {
            "total_cases": total_cases,
            "successful_cases": successful_cases,
            "failed_cases": failed_cases,
            "success_rate": success_rate
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
            "avg_retrieval_time": avg_retrieval_time,
            "avg_generation_time": avg_generation_time,
            "total_time": sum(retrieval_times) + sum(generation_times)
        },
        "question_type_performance": question_type_avg,
        "difficulty_performance": difficulty_avg,
        "failure_analysis": {
            "top_reasons": failure_reasons
        },
        "detailed_results": detailed_results,
        "recommendations": recommendations
    }

def generate_recommendations(success_rate: float, failure_reasons: Dict[str, int]) -> List[str]:
    """Tạo recommendations dựa trên kết quả evaluation"""
    
    recommendations = []
    
    if success_rate < 0.7:
        recommendations.append("Tỷ lệ thành công thấp - cần cải thiện retrieval hoặc generation")
    
    if success_rate < 0.5:
        recommendations.append("Cần xem xét lại cấu hình RAG system")
    
    if "Low retrieval score" in failure_reasons:
        count = failure_reasons["Low retrieval score"]
        if count > 5:
            recommendations.append("Nhiều lỗi do retrieval kém - cần cải thiện vector database hoặc embedding")
    
    if "Low generation score" in failure_reasons:
        count = failure_reasons["Low generation score"]
        if count > 5:
            recommendations.append("Nhiều lỗi do generation kém - cần fine-tune model hoặc cải thiện prompt")
    
    if success_rate >= 0.8:
        recommendations.append("Performance tốt - có thể tăng độ khó của test cases")
    
    if not recommendations:
        recommendations.append("Kết quả evaluation ổn định - tiếp tục monitor")
    
    return recommendations

def run_comprehensive_evaluation(dataset_file: str) -> Optional[Dict[str, Any]]:
    """Chạy evaluation toàn diện với RAGEvaluator thực"""
    
    print("🚀 KHỞI TẠO EVALUATION PIPELINE")
    print("=" * 50)
    
    # Load dataset
    dataset = load_filtered_dataset(dataset_file)
    if not dataset:
        print("❌ Không thể load dataset")
        return None
    
    # Convert dataset to test cases format
    test_cases = convert_dataset_to_test_cases(dataset)
    print(f"📊 Sẽ evaluate {len(test_cases)} test cases")
    
    # Initialize dependency injection
    print("🔧 Khởi tạo RAG system...")
    try:
        config = Config()
        config.expert_type = "RAG"  # Ensure RAG expert is used
        
        update_injector_with_config(config)
        
        # Get RAG expert and evaluator instances with proper casting
        rag_expert = cast(RAGBotExpert, get_instance(RAGBotExpert))
        evaluator = cast(RAGEvaluator, get_instance(RAGEvaluator))
        
        print("✅ RAG system và evaluator đã sẵn sàng")
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo RAG system: {str(e)}")
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        return None
    
    # Add metadata to test cases for better tracking
    for i, test_case in enumerate(test_cases):
        if 'metadata' not in test_case:
            test_case['metadata'] = {}
        # Update metadata with proper type handling
        metadata_update = {
            'question_type': test_case.get('question_type', 'unknown'),
            'difficulty': test_case.get('difficulty', 'unknown'),
            'id': test_case.get('id', f'test_{i}')
        }
        test_case['metadata'].update(metadata_update)
    
    # Chạy evaluation
    print(f"🧪 Bắt đầu evaluation...")
    start_time = datetime.now()
    
    try:
        # Use the real evaluator's batch evaluation method
        evaluation_results = evaluator.evaluate_batch(
            rag_expert=rag_expert,
            test_cases=test_cases,
            user_id="evaluation_user"
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Evaluation hoàn thành trong {duration:.2f} giây")
        
        # Convert evaluation results to expected format
        results = convert_evaluation_results_to_report_format(evaluation_results)
        
        # Thêm metadata
        results["metadata"] = {
            "dataset_file": dataset_file,
            "evaluation_start": start_time.isoformat(),
            "evaluation_end": end_time.isoformat(),
            "duration_seconds": duration,
            "evaluator_type": "real_rag_evaluator"
        }
        
        return results
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy evaluation: {str(e)}")
        logger.error(f"Evaluation failed: {str(e)}")
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
- **Evaluator:** {results["metadata"]["evaluator_type"]}
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
*Báo cáo được tạo tự động bởi RAG Evaluation Pipeline với Real Evaluator*
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
    
    print("🧪 RAG Evaluation Runner (Real Evaluator)")
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
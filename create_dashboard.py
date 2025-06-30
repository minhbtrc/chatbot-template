#!/usr/bin/env python3
"""
Script tạo dashboard visualization cho kết quả evaluation RAG system
Sử dụng: python create_dashboard.py
"""

import json
import sys
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    import numpy as np
except ImportError:
    print("❌ Thiếu dependencies để tạo dashboard.")
    print("💡 Cài đặt: pip install matplotlib seaborn pandas numpy")
    sys.exit(1)

def load_evaluation_results(results_file: str) -> Optional[Dict[str, Any]]:
    """Load kết quả evaluation từ file JSON"""
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        print(f"✅ Đã load kết quả từ {results_file}")
        return results
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {results_file}")
        return None
    except json.JSONDecodeError:
        print(f"❌ File JSON không hợp lệ: {results_file}")
        return None

def create_evaluation_dashboard(results: Dict[str, Any], output_file: str) -> None:
    """Tạo dashboard visualization"""
    
    # Setup matplotlib với font hỗ trợ tiếng Việt
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9
    
    # Tạo figure với subplots
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('RAG System Evaluation Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Success Rate Pie Chart
    success_rate = results['summary']['success_rate']
    failed_rate = 1 - success_rate
    
    axes[0,0].pie([success_rate, failed_rate], 
                 labels=['Success', 'Failed'], 
                 autopct='%1.1f%%',
                 colors=['#4CAF50', '#F44336'],
                 startangle=90)
    axes[0,0].set_title('Overall Success Rate')
    
    # 2. Metrics Overview Bar Chart
    metrics_data = {
        'Precision@5': results['metrics']['retrieval']['precision_at_5'],
        'Recall@5': results['metrics']['retrieval']['recall_at_5'],
        'MRR': results['metrics']['retrieval']['mrr'],
        'Faithfulness': results['metrics']['generation']['faithfulness'],
        'Relevance': results['metrics']['generation']['relevance'],
        'Quality': results['metrics']['generation']['quality']
    }
    
    metric_names = list(metrics_data.keys())
    metric_values = list(metrics_data.values())
    
    bars = axes[0,1].bar(metric_names, metric_values, 
                        color=['#2196F3', '#2196F3', '#2196F3', '#FF9800', '#FF9800', '#FF9800'])
    axes[0,1].set_title('Metrics Overview')
    axes[0,1].set_ylim(0, 1)
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars, metric_values):
        height = bar.get_height()
        axes[0,1].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                      f'{value:.3f}', ha='center', va='bottom')
    
    # 3. Performance Times
    time_data = {
        'Retrieval': results['performance']['avg_retrieval_time'],
        'Generation': results['performance']['avg_generation_time']
    }
    
    time_names = list(time_data.keys())
    time_values = list(time_data.values())
    
    bars = axes[0,2].bar(time_names, time_values, color=['#9C27B0', '#E91E63'])
    axes[0,2].set_title('Average Response Times (s)')
    axes[0,2].set_ylabel('Time (seconds)')
    
    # Add value labels
    for bar, value in zip(bars, time_values):
        height = bar.get_height()
        axes[0,2].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                      f'{value:.2f}s', ha='center', va='bottom')
    
    # 4. Question Type Performance
    if 'question_type_performance' in results and results['question_type_performance']:
        q_types = list(results['question_type_performance'].keys())
        q_performance = list(results['question_type_performance'].values())
        
        bars = axes[1,0].bar(q_types, q_performance, color='lightgreen')
        axes[1,0].set_title('Performance by Question Type')
        axes[1,0].set_ylim(0, 1)
        axes[1,0].set_ylabel('Success Rate')
        
        # Add value labels
        for bar, value in zip(bars, q_performance):
            height = bar.get_height()
            axes[1,0].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                          f'{value:.2%}', ha='center', va='bottom')
    else:
        axes[1,0].text(0.5, 0.5, 'No question type data', 
                      ha='center', va='center', transform=axes[1,0].transAxes)
        axes[1,0].set_title('Performance by Question Type')
    
    # 5. Difficulty Level Performance
    if 'difficulty_performance' in results and results['difficulty_performance']:
        difficulties = list(results['difficulty_performance'].keys())
        diff_performance = list(results['difficulty_performance'].values())
        
        axes[1,1].plot(difficulties, diff_performance, marker='o', linewidth=3, markersize=8, color='#FF5722')
        axes[1,1].set_title('Performance by Difficulty')
        axes[1,1].set_ylim(0, 1)
        axes[1,1].set_ylabel('Success Rate')
        axes[1,1].grid(True, alpha=0.3)
        
        # Add value labels
        for x, y in zip(difficulties, diff_performance):
            axes[1,1].text(x, y + 0.02, f'{y:.2%}', ha='center', va='bottom')
    else:
        axes[1,1].text(0.5, 0.5, 'No difficulty data', 
                      ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,1].set_title('Performance by Difficulty')
    
    # 6. Failure Analysis
    if results['failure_analysis']['top_reasons']:
        failure_reasons = list(results['failure_analysis']['top_reasons'].keys())[:5]
        failure_counts = list(results['failure_analysis']['top_reasons'].values())[:5]
        
        # Truncate long reason names
        failure_reasons = [reason[:30] + '...' if len(reason) > 30 else reason 
                          for reason in failure_reasons]
        
        bars = axes[1,2].barh(failure_reasons, failure_counts, color='orange')
        axes[1,2].set_title('Top Failure Reasons')
        axes[1,2].set_xlabel('Count')
        
        # Add value labels
        for bar, value in zip(bars, failure_counts):
            width = bar.get_width()
            axes[1,2].text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                          f'{value}', ha='left', va='center')
    else:
        axes[1,2].text(0.5, 0.5, 'No failure data', 
                      ha='center', va='center', transform=axes[1,2].transAxes)
        axes[1,2].set_title('Top Failure Reasons')
    
    # 7. Detailed Results Heatmap (if available)
    if 'detailed_results' in results and results['detailed_results']:
        detailed_results = results['detailed_results']
        
        # Create dataframe for heatmap
        df_data = []
        for result in detailed_results[:20]:  # Limit to first 20 for readability
            df_data.append({
                'Test Case': result.get('test_case_id', 'N/A')[:10],
                'Precision@5': result.get('retrieval_metrics', {}).get('precision_at_5', 0),
                'Recall@5': result.get('retrieval_metrics', {}).get('recall_at_5', 0),
                'Faithfulness': result.get('generation_metrics', {}).get('faithfulness', 0),
                'Relevance': result.get('generation_metrics', {}).get('relevance', 0)
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            df_numeric = df.select_dtypes(include=[np.number])
            
            if not df_numeric.empty:
                sns.heatmap(df_numeric.T, annot=True, fmt='.2f', cmap='RdYlGn', 
                           ax=axes[2,0], cbar_kws={'shrink': 0.8})
                axes[2,0].set_title('Performance Heatmap (Top 20 Cases)')
                axes[2,0].set_xlabel('Test Cases')
            else:
                axes[2,0].text(0.5, 0.5, 'No numeric data for heatmap', 
                              ha='center', va='center', transform=axes[2,0].transAxes)
        else:
            axes[2,0].text(0.5, 0.5, 'No detailed results', 
                          ha='center', va='center', transform=axes[2,0].transAxes)
    else:
        axes[2,0].text(0.5, 0.5, 'No detailed results', 
                      ha='center', va='center', transform=axes[2,0].transAxes)
    axes[2,0].set_title('Performance Heatmap')
    
    # 8. Score Distribution
    if 'detailed_results' in results and results['detailed_results']:
        detailed_results = results['detailed_results']
        
        precision_scores = [r.get('retrieval_metrics', {}).get('precision_at_5', 0) 
                           for r in detailed_results]
        faithfulness_scores = [r.get('generation_metrics', {}).get('faithfulness', 0) 
                              for r in detailed_results]
        
        axes[2,1].hist([precision_scores, faithfulness_scores], 
                      bins=10, alpha=0.7, label=['Precision@5', 'Faithfulness'],
                      color=['#2196F3', '#FF9800'])
        axes[2,1].set_title('Score Distribution')
        axes[2,1].set_xlabel('Score')
        axes[2,1].set_ylabel('Frequency')
        axes[2,1].legend()
        axes[2,1].grid(True, alpha=0.3)
    else:
        axes[2,1].text(0.5, 0.5, 'No score data', 
                      ha='center', va='center', transform=axes[2,1].transAxes)
        axes[2,1].set_title('Score Distribution')
    
    # 9. Summary Statistics
    axes[2,2].axis('off')
    
    summary_text = f"""
EVALUATION SUMMARY

📊 Total Test Cases: {results['summary']['total_cases']}
✅ Successful: {results['summary']['successful_cases']}
❌ Failed: {results['summary']['failed_cases']}
📈 Success Rate: {results['summary']['success_rate']:.2%}

⚡ Performance:
• Avg Retrieval: {results['performance']['avg_retrieval_time']:.2f}s
• Avg Generation: {results['performance']['avg_generation_time']:.2f}s
• Total Time: {results['performance']['total_time']:.2f}s

🎯 Key Metrics:
• Precision@5: {results['metrics']['retrieval']['precision_at_5']:.3f}
• Faithfulness: {results['metrics']['generation']['faithfulness']:.3f}
• Relevance: {results['metrics']['generation']['relevance']:.3f}

📅 Evaluated: {results.get('metadata', {}).get('evaluation_start', 'N/A')[:16]}
"""
    
    axes[2,2].text(0.05, 0.95, summary_text, transform=axes[2,2].transAxes,
                  fontsize=10, verticalalignment='top', fontfamily='monospace',
                  bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.8))
    
    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    # Save dashboard
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Dashboard đã được tạo: {output_file}")
    
    # Show if possible
    try:
        plt.show()
    except:
        print("💡 Dashboard đã được lưu. Mở file để xem visualization.")

def create_comparison_dashboard(results_files: List[str], output_file: str) -> None:
    """Tạo dashboard so sánh nhiều evaluation results"""
    
    if len(results_files) < 2:
        print("❌ Cần ít nhất 2 file results để so sánh")
        return
    
    all_results = []
    labels = []
    
    for i, file in enumerate(results_files):
        results = load_evaluation_results(file)
        if results:
            all_results.append(results)
            # Extract timestamp from filename for label
            timestamp = file.split('_')[-1].split('.')[0] if '_' in file else f"Run {i+1}"
            labels.append(timestamp)
    
    if len(all_results) < 2:
        print("❌ Không thể load đủ results để so sánh")
        return
    
    # Create comparison plots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('RAG Evaluation Comparison Dashboard', fontsize=16, fontweight='bold')
    
    # 1. Success Rate Comparison
    success_rates = [r['summary']['success_rate'] for r in all_results]
    
    bars = axes[0,0].bar(labels, success_rates, color='skyblue')
    axes[0,0].set_title('Success Rate Comparison')
    axes[0,0].set_ylabel('Success Rate')
    axes[0,0].set_ylim(0, 1)
    
    # Add value labels
    for bar, value in zip(bars, success_rates):
        height = bar.get_height()
        axes[0,0].text(bar.get_x() + bar.get_width()/2., height + 0.01,
                      f'{value:.2%}', ha='center', va='bottom')
    
    # 2. Metrics Comparison
    metrics_names = ['Precision@5', 'Recall@5', 'MRR', 'Faithfulness', 'Relevance', 'Quality']
    
    x = np.arange(len(metrics_names))
    width = 0.35
    
    for i, (results, label) in enumerate(zip(all_results[:2], labels[:2])):  # Limit to 2 for clarity
        metrics_values = [
            results['metrics']['retrieval']['precision_at_5'],
            results['metrics']['retrieval']['recall_at_5'],
            results['metrics']['retrieval']['mrr'],
            results['metrics']['generation']['faithfulness'],
            results['metrics']['generation']['relevance'],
            results['metrics']['generation']['quality']
        ]
        
        offset = width * (i - 0.5)
        bars = axes[0,1].bar(x + offset, metrics_values, width, label=label, alpha=0.8)
    
    axes[0,1].set_title('Metrics Comparison')
    axes[0,1].set_ylabel('Score')
    axes[0,1].set_xticks(x)
    axes[0,1].set_xticklabels(metrics_names, rotation=45)
    axes[0,1].legend()
    axes[0,1].set_ylim(0, 1)
    
    # 3. Performance Time Comparison
    retrieval_times = [r['performance']['avg_retrieval_time'] for r in all_results]
    generation_times = [r['performance']['avg_generation_time'] for r in all_results]
    
    x = np.arange(len(labels))
    width = 0.35
    
    axes[1,0].bar(x - width/2, retrieval_times, width, label='Retrieval', alpha=0.8)
    axes[1,0].bar(x + width/2, generation_times, width, label='Generation', alpha=0.8)
    
    axes[1,0].set_title('Performance Time Comparison')
    axes[1,0].set_ylabel('Time (seconds)')
    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(labels)
    axes[1,0].legend()
    
    # 4. Trend Analysis (if more than 2 results)
    if len(all_results) >= 3:
        success_trend = [r['summary']['success_rate'] for r in all_results]
        precision_trend = [r['metrics']['retrieval']['precision_at_5'] for r in all_results]
        faithfulness_trend = [r['metrics']['generation']['faithfulness'] for r in all_results]
        
        axes[1,1].plot(labels, success_trend, marker='o', label='Success Rate', linewidth=2)
        axes[1,1].plot(labels, precision_trend, marker='s', label='Precision@5', linewidth=2)
        axes[1,1].plot(labels, faithfulness_trend, marker='^', label='Faithfulness', linewidth=2)
        
        axes[1,1].set_title('Performance Trend')
        axes[1,1].set_ylabel('Score')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].tick_params(axis='x', rotation=45)
    else:
        axes[1,1].text(0.5, 0.5, 'Need 3+ results for trend analysis', 
                      ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,1].set_title('Performance Trend')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Comparison dashboard đã được tạo: {output_file}")
    
    try:
        plt.show()
    except:
        print("💡 Dashboard đã được lưu. Mở file để xem visualization.")

def find_latest_evaluation_results() -> Optional[str]:
    """Tìm file evaluation results mới nhất"""
    
    result_files = glob.glob("evaluation_report_*.json")
    
    if result_files:
        latest_file = max(result_files, key=os.path.getctime)
        return latest_file
    
    return None

def main():
    """Main function"""
    
    print("📊 RAG Evaluation Dashboard Creator")
    print("=" * 50)
    
    print("🎯 Chọn loại dashboard:")
    print("1. Single Evaluation Dashboard")
    print("2. Comparison Dashboard (nhiều evaluations)")
    
    choice = input("Chọn (1/2): ").strip()
    
    if choice == "1":
        # Single dashboard
        results_file = input("Nhập tên file evaluation results (hoặc Enter để dùng file mới nhất): ").strip()
        
        if not results_file:
            latest_file = find_latest_evaluation_results()
            if latest_file:
                results_file = latest_file
                print(f"📁 Sử dụng file mới nhất: {results_file}")
            else:
                print("❌ Không tìm thấy file evaluation results nào")
                print("💡 Hãy chạy run_evaluation.py trước")
                return
        
        if not os.path.exists(results_file):
            print(f"❌ File không tồn tại: {results_file}")
            return
        
        # Load và tạo dashboard
        results = load_evaluation_results(results_file)
        if results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"evaluation_dashboard_{timestamp}.png"
            
            print("🎨 Đang tạo dashboard...")
            create_evaluation_dashboard(results, output_file)
            
            print(f"\n🎉 Dashboard hoàn thành!")
            print(f"📁 File: {output_file}")
        
    elif choice == "2":
        # Comparison dashboard
        print("📁 Nhập các file evaluation results để so sánh:")
        print("(Nhập từng file một, Enter trống để kết thúc)")
        
        results_files = []
        while True:
            file = input(f"File {len(results_files)+1}: ").strip()
            if not file:
                break
            if os.path.exists(file):
                results_files.append(file)
                print(f"✅ Đã thêm: {file}")
            else:
                print(f"❌ File không tồn tại: {file}")
        
        if len(results_files) < 2:
            print("❌ Cần ít nhất 2 file để so sánh")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"comparison_dashboard_{timestamp}.png"
        
        print("🎨 Đang tạo comparison dashboard...")
        create_comparison_dashboard(results_files, output_file)
        
        print(f"\n🎉 Comparison dashboard hoàn thành!")
        print(f"📁 File: {output_file}")
    
    else:
        print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    main() 
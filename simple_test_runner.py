#!/usr/bin/env python3
"""
Simple Test Runner for RAG Evaluation with Synthetic Datasets

This script provides easy ways to test your RAG system using existing synthetic datasets.

Basic usage:
1. List datasets: python simple_test_runner.py --list
2. Test one document: python simple_test_runner.py --test document_id user_id  
3. Test all for user: python simple_test_runner.py --test-user user_id
4. Test from file: python simple_test_runner.py --test-file path/to/dataset.json user_id
"""

import argparse
import os
from typing import Any, Dict, List

from src.experts.rag_bot.expert import RAGBotExpert
from src.experts.rag_bot.evaluator import create_evaluator
from src.common.config import Config
from src.base.components import (
    create_embedding,
    create_vector_database, 
    create_memory,
    create_llm_client,
    ToolProvider
)
from src.base.brains import create_brain
from src.common.logging import logger


def setup_rag_system():
    """Setup RAG expert and evaluator."""
    print("🔧 Setting up RAG system...")
    
    config = Config(expert_type="RAG", vector_database_type="CHROMA")
    
    # Create components
    embedding = create_embedding(config)
    vector_database = create_vector_database(config, embedding)
    memory = create_memory(config)
    llm_client = create_llm_client(config)
    tool_provider = ToolProvider()
    brain = create_brain(config, llm_client, tool_provider)
    
    # Create RAG expert and evaluator
    rag_expert = RAGBotExpert(
        config=config,
        embedding=embedding,
        vector_database=vector_database,
        memory=memory,
        brain=brain
    )
    
    evaluator = create_evaluator(
        config=config,
        embedding=embedding,
        vector_database=vector_database,
        brain=brain
    )
    
    print("✅ RAG system ready")
    return rag_expert, evaluator


def list_datasets(rag_expert):
    """List all available synthetic datasets."""
    print("📂 Available Synthetic Datasets:")
    print("=" * 50)
    
    datasets = rag_expert.list_available_synthetic_datasets()
    
    if not datasets:
        print("❌ No synthetic datasets found")
        print("\nTo generate datasets:")
        print("1. Set enable_synthetic_dataset_generation=True in config")
        print("2. Process documents using rag_expert.process_document()")
        return
    
    print(f"Found {len(datasets)} datasets:\n")
    
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. Document: {dataset['document_id']}")
        print(f"   User: {dataset['user_id']}")
        print(f"   File: {dataset['filename']}")
        print(f"   Size: {dataset['file_size']} bytes")
        print()


def test_document(rag_expert, evaluator, document_id, user_id):
    """Test a specific document."""
    print(f"🧪 Testing Document: {document_id} (User: {user_id})")
    print("=" * 60)
    
    # Load test cases
    test_cases = rag_expert.get_synthetic_dataset_for_document(user_id, document_id)
    
    if not test_cases:
        print(f"❌ No dataset found for document '{document_id}' and user '{user_id}'")
        print("\nAvailable datasets:")
        datasets = rag_expert.list_available_synthetic_datasets(user_id)
        for dataset in datasets:
            print(f"  - {dataset['document_id']}")
        return
    
    print(f"📝 Loaded {len(test_cases)} test cases")
    
    # Convert to evaluation format
    evaluation_cases = []
    for test_case in test_cases:
        eval_case = {
            "query": test_case.query,
            "expected_context": test_case.expected_context,
            "expected_doc_id": test_case.expected_doc_id,
            "expected_snippet": test_case.expected_snippet,
            "expected_response": None,
            "metadata": test_case.metadata
        }
        evaluation_cases.append(eval_case)
    
    # Run evaluation
    print("⚡ Running evaluation...")
    results = evaluator.evaluate_batch(
        rag_expert=rag_expert,
        test_cases=evaluation_cases,
        user_id=user_id
    )
    
    # Generate and display report
    report = evaluator.generate_report(results)
    display_results(report)


def test_user_datasets(rag_expert, evaluator, user_id):
    """Test all datasets for a user."""
    print(f"🧪 Testing All Datasets for User: {user_id}")
    print("=" * 60)
    
    datasets = rag_expert.list_available_synthetic_datasets(user_id)
    
    if not datasets:
        print(f"❌ No datasets found for user '{user_id}'")
        return
    
    print(f"📂 Found {len(datasets)} datasets for user '{user_id}'\n")
    
    all_results = []
    
    for dataset in datasets:
        document_id = dataset['document_id']
        print(f"📄 Testing: {document_id}")
        
        test_cases = rag_expert.get_synthetic_dataset_for_document(user_id, document_id)
        
        if not test_cases:
            print(f"   ⚠️  Could not load test cases")
            continue
            
        # Convert to evaluation format
        evaluation_cases: List[Dict[str, Any]]= []
        for test_case in test_cases:
            eval_case = {
                "query": test_case.query,
                "expected_context": test_case.expected_context,
                "expected_doc_id": test_case.expected_doc_id,
                "expected_snippet": test_case.expected_snippet,
                "expected_response": None,
                "metadata": test_case.metadata
            }
            evaluation_cases.append(eval_case)
        
        # Run evaluation
        results = evaluator.evaluate_batch(
            rag_expert=rag_expert,
            test_cases=evaluation_cases,
            user_id=user_id
        )
        
        report = evaluator.generate_report(results)
        all_results.append(report)
        
        # Show brief results for this document
        summary = report.get('summary', {})
        retrieval_success = 100 - summary.get('failure_rate_retrieval', 0)
        generation_success = 100 - summary.get('failure_rate_generation', 0)
        
        print(f"   📊 Retrieval: {retrieval_success:.1f}% | Generation: {generation_success:.1f}%")
    
    # Show aggregate results
    if len(all_results) > 1:
        print(f"\n{'='*60}")
        print("📊 AGGREGATE RESULTS")
        print("=" * 60)
        
        total_evals = sum(r['summary']['total_evaluations'] for r in all_results)
        avg_retrieval = sum(100 - r['summary']['failure_rate_retrieval'] for r in all_results) / len(all_results)
        avg_generation = sum(100 - r['summary']['failure_rate_generation'] for r in all_results) / len(all_results)
        
        print(f"Total Test Cases: {total_evals}")
        print(f"Average Retrieval Success: {avg_retrieval:.1f}%")
        print(f"Average Generation Success: {avg_generation:.1f}%")


def test_from_file(rag_expert, evaluator, file_path, user_id):
    """Test using a specific dataset file."""
    print(f"🧪 Testing from File: {file_path}")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    # Load dataset using synthetic generator
    from src.experts.rag_bot.synthetic_data_generator import SyntheticDataGenerator
    
    # Create a temporary generator to load the file
    synthetic_generator = SyntheticDataGenerator(
        brain=rag_expert.brain,
        vector_database=rag_expert.vector_database
    )
    
    test_cases = synthetic_generator.load_test_cases(file_path)
    
    if not test_cases:
        print(f"❌ Failed to load test cases from {file_path}")
        return
    
    print(f"📝 Loaded {len(test_cases)} test cases from file")
    
    # Convert to evaluation format
    evaluation_cases = []
    for test_case in test_cases:
        eval_case = {
            "query": test_case.query,
            "expected_context": test_case.expected_context,
            "expected_doc_id": test_case.expected_doc_id,
            "expected_snippet": test_case.expected_snippet,
            "expected_response": None,
            "metadata": test_case.metadata
        }
        evaluation_cases.append(eval_case)
    
    # Run evaluation
    print("⚡ Running evaluation...")
    results = evaluator.evaluate_batch(
        rag_expert=rag_expert,
        test_cases=evaluation_cases,
        user_id=user_id
    )
    
    # Generate and display report
    report = evaluator.generate_report(results)
    display_results(report)


def display_results(report):
    """Display evaluation results."""
    print(f"\n{'='*60}")
    print("📊 EVALUATION RESULTS")
    print("=" * 60)
    
    # Summary
    summary = report.get('summary', {})
    print(f"\n📈 SUMMARY:")
    print(f"  Total Test Cases: {summary.get('total_evaluations', 0)}")
    print(f"  Retrieval Failures: {summary.get('failed_retrievals', 0)}")
    print(f"  Generation Failures: {summary.get('low_quality_generations', 0)}")
    print(f"  Retrieval Success Rate: {100 - summary.get('failure_rate_retrieval', 0):.1f}%")
    print(f"  Generation Success Rate: {100 - summary.get('failure_rate_generation', 0):.1f}%")
    
    # Key metrics
    metrics = report.get('metrics', {})
    print(f"\n🎯 KEY METRICS:")
    
    # Retrieval metrics
    if 'top_1_accuracy_score' in metrics:
        print(f"  Top-1 Accuracy: {metrics['top_1_accuracy_score']['average']:.3f}")
    if 'top_3_accuracy_score' in metrics:
        print(f"  Top-3 Accuracy: {metrics['top_3_accuracy_score']['average']:.3f}")
    if 'top_5_accuracy_score' in metrics:
        print(f"  Top-5 Accuracy: {metrics['top_5_accuracy_score']['average']:.3f}")
    if 'mrr_at_10_score' in metrics:
        print(f"  Mean Reciprocal Rank: {metrics['mrr_at_10_score']['average']:.3f}")
    
    # Generation metrics
    if 'llm_as_judge_score' in metrics:
        print(f"  LLM Judge Score: {metrics['llm_as_judge_score']['average']:.3f}")
    if 'faithfulness_score' in metrics:
        print(f"  Faithfulness: {metrics['faithfulness_score']['average']:.3f}")
    if 'quality_score' in metrics:
        print(f"  Quality: {metrics['quality_score']['average']:.3f}")
    
    # Performance
    latency = report.get('latency', {})
    if latency:
        print(f"\n⏱️  PERFORMANCE:")
        if 'retrieval' in latency and latency['retrieval'].get('average', 0) > 0:
            print(f"  Avg Retrieval Time: {latency['retrieval']['average']:.3f}s")
        if 'generation' in latency and latency['generation'].get('average', 0) > 0:
            print(f"  Avg Generation Time: {latency['generation']['average']:.3f}s")
    
    # Sample failures
    failure_cases = report.get('failure_cases', {})
    
    if failure_cases.get('retrieval_failures'):
        print(f"\n❌ SAMPLE RETRIEVAL FAILURES:")
        for i, failure in enumerate(failure_cases['retrieval_failures'][:3]):
            print(f"  {i+1}. {failure['query']}")
    
    if failure_cases.get('generation_failures'):
        print(f"\n❌ SAMPLE GENERATION FAILURES:")
        for i, failure in enumerate(failure_cases['generation_failures'][:3]):
            print(f"  {i+1}. {failure['query']} (Score: {failure.get('llm_rating', 'N/A')})")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple RAG Test Runner")
    parser.add_argument("--list", action="store_true", help="List available datasets")
    parser.add_argument("--test", nargs=2, metavar=("DOCUMENT_ID", "USER_ID"), help="Test specific document")
    parser.add_argument("--test-user", metavar="USER_ID", help="Test all datasets for user")
    parser.add_argument("--test-file", nargs=2, metavar=("FILE_PATH", "USER_ID"), help="Test from specific file")
    
    args = parser.parse_args()
    
    # Setup system
    rag_expert, evaluator = setup_rag_system()
    
    # Handle commands
    if args.list:
        list_datasets(rag_expert)
    elif args.test:
        document_id, user_id = args.test
        test_document(rag_expert, evaluator, document_id, user_id)
    elif args.test_user:
        test_user_datasets(rag_expert, evaluator, args.test_user)
    elif args.test_file:
        file_path, user_id = args.test_file
        test_from_file(rag_expert, evaluator, file_path, user_id)
    else:
        # Show usage and quick overview
        print("🧪 RAG Test Runner")
        print("=" * 30)
        print("\nUsage:")
        print("  --list                                List available datasets")
        print("  --test DOCUMENT_ID USER_ID           Test specific document")
        print("  --test-user USER_ID                  Test all datasets for user")  
        print("  --test-file FILE_PATH USER_ID        Test from file")
        
        print("\n📂 Quick Overview:")
        datasets = rag_expert.list_available_synthetic_datasets()
        if datasets:
            users = set(d['user_id'] for d in datasets)
            print(f"  {len(datasets)} datasets across {len(users)} users")
            for user in sorted(users):
                user_datasets = [d for d in datasets if d['user_id'] == user]
                print(f"    {user}: {len(user_datasets)} datasets")
        else:
            print("  No datasets found")


if __name__ == "__main__":
    main() 
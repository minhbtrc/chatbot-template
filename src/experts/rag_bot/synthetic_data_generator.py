#!/usr/bin/env python3
"""
Synthetic test data generator for RAG evaluation.

This module helps generate synthetic test cases by using an LLM to create
3-5 questions per document chunk, providing ground truth for evaluation.
Integrates with RAGBotExpert.process_document workflow.
"""

import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from injector import inject
from langchain_core.documents import Document

from src.base.components import VectorDatabaseInterface
from src.base.brains import BrainInterface
from src.common.logging import logger
from .prompts import GENERATION_EVALUATION_PROMPT


@dataclass
class SyntheticTestCase:
    """
    Data class for synthetic test cases.
    """
    query: str
    expected_doc_id: str
    expected_snippet: str
    expected_context: str
    difficulty: str  # "easy", "medium", "hard"
    question_type: str  # "factual", "inferential", "conceptual"
    metadata: Dict[str, Any]


class SyntheticDataGenerator:
    """
    Generates synthetic test cases for RAG evaluation using LLM.
    Integrates with RAGBotExpert's document processing workflow.
    """
    
    @inject
    def __init__(self, brain: BrainInterface, vector_database: VectorDatabaseInterface):
        self.brain = brain
        self.vector_database = vector_database
    
    def generate_questions_for_chunk(
        self, 
        document_chunk: str, 
        doc_id: str,
        num_questions: int = 5,
        chunk_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SyntheticTestCase]:
        """
        Generate multiple questions for a single document chunk.
        
        Args:
            document_chunk: The text content of the document chunk
            doc_id: Unique identifier for the document chunk
            num_questions: Number of questions to generate
            chunk_metadata: Optional metadata from the document chunk
        """
        logger.info(f"Generating {num_questions} questions for document chunk: {doc_id}")
        
        generation_prompt = GENERATION_EVALUATION_PROMPT.format(
            num_questions=num_questions, 
            document_chunk=document_chunk
        )
        
        try:
            messages = [{"role": "user", "content": generation_prompt}]
            result = self.brain.think(messages)
            response_text = result.get("content", "").strip()
            
            # Parse the JSON response
            try:
                parsed_result = json.loads(response_text)
                questions_data = parsed_result.get("questions", [])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response for chunk {doc_id}, attempting fallback parsing")
                # Fallback: try to extract questions using regex if JSON fails
                questions_data = self._extract_questions_fallback(response_text)
            
            # Convert to SyntheticTestCase objects
            test_cases: List[SyntheticTestCase] = []
            for q_data in questions_data:
                # Merge chunk metadata with generated metadata
                combined_metadata = {
                    "generated_by": "synthetic_generator",
                    "source_doc_id": doc_id,
                    "generation_timestamp": time.time()
                }
                if chunk_metadata:
                    combined_metadata.update(chunk_metadata)
                
                test_case = SyntheticTestCase(
                    query=q_data.get("question", ""),
                    expected_doc_id=doc_id,
                    expected_snippet=q_data.get("answer_snippet", ""),
                    expected_context=document_chunk,
                    difficulty=q_data.get("difficulty", "medium"),
                    question_type=q_data.get("type", "factual"),
                    metadata=combined_metadata
                )
                test_cases.append(test_case)
            
            logger.info(f"Generated {len(test_cases)} questions for chunk {doc_id}")
            return test_cases
            
        except Exception as e:
            logger.error(f"Failed to generate questions for chunk {doc_id}: {str(e)}")
            return []
    
    def _extract_questions_fallback(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Fallback method to extract questions when JSON parsing fails.
        """
        import re
        
        questions: List[Dict[str, Any]] = []
        # Simple regex patterns to extract information
        question_pattern = r'"question":\s*"([^"]+)"'
        snippet_pattern = r'"answer_snippet":\s*"([^"]+)"'
        difficulty_pattern = r'"difficulty":\s*"([^"]+)"'
        type_pattern = r'"type":\s*"([^"]+)"'
        
        question_matches = re.findall(question_pattern, response_text)
        snippet_matches = re.findall(snippet_pattern, response_text)
        difficulty_matches = re.findall(difficulty_pattern, response_text)
        type_matches = re.findall(type_pattern, response_text)
        
        # Match them up (assuming they appear in order)
        for i in range(min(len(question_matches), len(snippet_matches))):
            questions.append({
                "question": question_matches[i],
                "answer_snippet": snippet_matches[i] if i < len(snippet_matches) else "",
                "difficulty": difficulty_matches[i] if i < len(difficulty_matches) else "medium",
                "type": type_matches[i] if i < len(type_matches) else "factual"
            })
        
        return questions
    
    def generate_questions_from_document_chunks(
        self,
        document_chunks: List[Document],
        questions_per_chunk: int = 3,
        max_chunks: Optional[int] = None
    ) -> List[SyntheticTestCase]:
        """
        Generate questions from Document objects (as used by RAGBotExpert).
        
        Args:
            document_chunks: List of LangChain Document objects with content and metadata
            questions_per_chunk: Number of questions to generate per chunk
            max_chunks: Maximum number of chunks to process (None for all)
        """
        logger.info(f"Generating questions from {len(document_chunks)} document chunks")
        
        all_test_cases: List[SyntheticTestCase] = []
        chunks_to_process = document_chunks[:max_chunks] if max_chunks else document_chunks
        
        for i, doc_chunk in enumerate(chunks_to_process):
            # Extract content and metadata from Document object
            chunk_content = doc_chunk.page_content
            chunk_metadata: Dict[str, Any] = doc_chunk.metadata.copy()
            
            # Generate a unique doc_id from metadata or use index
            doc_id: str = chunk_metadata.get("document_id", f"chunk_{i}")
            if "user_id" in chunk_metadata:
                doc_id = f"{chunk_metadata['user_id']}_{doc_id}_{i}"
            
            if not chunk_content.strip():
                logger.debug(f"Skipping empty chunk {doc_id}")
                continue
            
            # Generate questions for this chunk
            test_cases = self.generate_questions_for_chunk(
                document_chunk=chunk_content,
                doc_id=doc_id,
                num_questions=questions_per_chunk,
                chunk_metadata=chunk_metadata
            )
            
            all_test_cases.extend(test_cases)
            
            # Add a small delay to avoid overwhelming the LLM API
            if i < len(chunks_to_process) - 1:  # Don't delay after the last chunk
                time.sleep(0.5)
        
        logger.info(f"Generated {len(all_test_cases)} total test cases from {len(chunks_to_process)} chunks")
        return all_test_cases
    
    def generate_test_suite_from_documents(
        self,
        document_chunks: List[Dict[str, Any]],
        questions_per_chunk: int = 3,
        max_chunks: int = 50
    ) -> List[SyntheticTestCase]:
        """
        Generate a comprehensive test suite from multiple document chunks.
        This method maintains backward compatibility with the original API.
        
        Args:
            document_chunks: List of document chunks with 'content' and 'id' keys
            questions_per_chunk: Number of questions to generate per chunk
            max_chunks: Maximum number of chunks to process
        """
        logger.info(f"Generating test suite from {min(len(document_chunks), max_chunks)} document chunks")
        
        all_test_cases: List[SyntheticTestCase] = []
        processed_chunks = 0
        
        for chunk_data in document_chunks[:max_chunks]:
            chunk_content = chunk_data.get("content", "")
            chunk_id = chunk_data.get("id", f"chunk_{processed_chunks}")
            
            if not chunk_content.strip():
                continue
            
            # Extract metadata if available
            chunk_metadata = chunk_data.get("metadata", {})
            
            # Generate questions for this chunk
            test_cases = self.generate_questions_for_chunk(
                document_chunk=chunk_content,
                doc_id=chunk_id,
                num_questions=questions_per_chunk,
                chunk_metadata=chunk_metadata
            )
            
            all_test_cases.extend(test_cases)
            processed_chunks += 1
            
            # Add a small delay to avoid overwhelming the LLM API
            time.sleep(0.5)
        
        logger.info(f"Generated {len(all_test_cases)} total test cases from {processed_chunks} chunks")
        return all_test_cases
    
    def generate_edge_case_questions(self, domain_context: str = "") -> List[SyntheticTestCase]:
        """
        Generate edge case questions that are known to be challenging for RAG systems.
        """
        logger.info("Generating edge case questions")
        
        edge_case_prompt = f"""
        Generate challenging edge case questions for a RAG (Retrieval-Augmented Generation) system.
        These should be questions that typically cause problems for RAG systems.
        
        Domain context: {domain_context}
        
        Please create 10 challenging questions that include:
        - Multi-hop reasoning questions (require combining information from multiple sources)
        - Ambiguous questions with multiple possible interpretations
        - Questions about recent events or updates
        - Questions requiring numerical calculations or comparisons
        - Questions about negations or exceptions
        - Questions with common misconceptions
        - Questions requiring domain-specific expertise
        
        For each question, specify why it's challenging and what the expected behavior should be.
        
        Please respond in the following JSON format:
        {{
            "edge_cases": [
                {{
                    "question": "Your challenging question here",
                    "challenge_type": "multi-hop/ambiguous/numerical/etc",
                    "expected_behavior": "What the system should do with this question",
                    "difficulty": "hard"
                }}
            ]
        }}
        """
        
        try:
            messages = [{"role": "user", "content": edge_case_prompt}]
            result = self.brain.think(messages)
            response_text = result.get("content", "").strip()
            
            # Parse the JSON response
            try:
                parsed_result = json.loads(response_text)
                edge_cases_data = parsed_result.get("edge_cases", [])
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response for edge cases")
                return []
            
            # Convert to SyntheticTestCase objects
            test_cases: List[SyntheticTestCase] = []
            for case_data in edge_cases_data:
                test_case = SyntheticTestCase(
                    query=case_data.get("question", ""),
                    expected_doc_id="edge_case",
                    expected_snippet=case_data.get("expected_behavior", ""),
                    expected_context="Edge case - no specific context",
                    difficulty="hard",
                    question_type="edge_case",
                    metadata={
                        "generated_by": "edge_case_generator",
                        "challenge_type": case_data.get("challenge_type", "unknown"),
                        "expected_behavior": case_data.get("expected_behavior", ""),
                        "generation_timestamp": time.time()
                    }
                )
                test_cases.append(test_case)
            
            logger.info(f"Generated {len(test_cases)} edge case questions")
            return test_cases
            
        except Exception as e:
            logger.error(f"Failed to generate edge case questions: {str(e)}")
            return []
    
    def generate_questions_for_processed_document(
        self, 
        file_path: str, 
        user_id: str, 
        document_id: str,
        questions_per_chunk: int = 3,
        max_chunks: Optional[int] = None
    ) -> List[SyntheticTestCase]:
        """
        Generate synthetic questions for a document that has been processed by RAGBotExpert.
        This method retrieves chunks from the vector database rather than processing the file again.
        
        Args:
            file_path: Original file path (used for metadata)
            user_id: User ID associated with the document
            document_id: Document ID used during processing
            questions_per_chunk: Number of questions per chunk
            max_chunks: Maximum number of chunks to process
        """
        logger.info(f"Generating questions for processed document: {document_id}")
        
        try:
            # Retrieve chunks from vector database using metadata
            # This assumes the vector database can retrieve by metadata
            metadata_filter = {"user_id": user_id, "document_id": document_id}
            
            # Use a broad query to get all chunks for this document
            # Note: This might need adjustment based on your vector database implementation
            retrieved_chunks: List[Any] = self.vector_database.retrieve_context(
                query="",  # Empty query to get all chunks
                n_results=max_chunks or 100,
                metadata=metadata_filter
            )
            
            if not retrieved_chunks:
                logger.warning(f"No chunks found for document {document_id} with user {user_id}")
                return []
            
            logger.info(f"Found {len(retrieved_chunks)} chunks for document {document_id}")
            
            # Convert retrieved chunks to Document format for processing
            document_chunks: List[Document] = []
            for i, chunk_content in enumerate(retrieved_chunks):
                doc = Document(
                    page_content=chunk_content,
                    metadata={
                        "user_id": user_id,
                        "document_id": document_id,
                        "chunk_index": i,
                        "source_file": file_path
                    }
                )
                document_chunks.append(doc)
            
            # Generate questions from the retrieved chunks
            return self.generate_questions_from_document_chunks(
                document_chunks=document_chunks,
                questions_per_chunk=questions_per_chunk,
                max_chunks=max_chunks
            )
            
        except Exception as e:
            logger.error(f"Failed to generate questions for processed document {document_id}: {str(e)}")
            return []
    
    def export_test_cases(
        self, 
        test_cases: List[SyntheticTestCase], 
        filename: str = "synthetic_test_cases.json"
    ) -> None:
        """
        Export test cases to a JSON file.
        """
        logger.info(f"Exporting {len(test_cases)} test cases to {filename}")
        
        # Convert test cases to serializable format
        serializable_cases: List[Dict[str, Any]] = []
        for test_case in test_cases:
            case_dict = {
                "query": test_case.query,
                "expected_doc_id": test_case.expected_doc_id,
                "expected_snippet": test_case.expected_snippet,
                "expected_context": test_case.expected_context,
                "difficulty": test_case.difficulty,
                "question_type": test_case.question_type,
                "metadata": test_case.metadata
            }
            serializable_cases.append(case_dict)
        
        # Add export metadata
        export_data = {
            "export_metadata": {
                "total_test_cases": len(test_cases),
                "export_timestamp": time.time(),
                "generator_version": "2.0_integrated_with_rag_expert"
            },
            "test_cases": serializable_cases
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Test cases exported successfully to {filename}")
    
    def load_test_cases(self, filename: str) -> List[SyntheticTestCase]:
        """
        Load test cases from a JSON file.
        """
        logger.info(f"Loading test cases from {filename}")
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if "test_cases" in data:
                cases_data = data["test_cases"]
                logger.info(f"Loaded export metadata: {data.get('export_metadata', {})}")
            else:
                cases_data = data  # Assume old format
            
            test_cases: List[SyntheticTestCase] = []
            for case_data in cases_data:
                test_case = SyntheticTestCase(
                    query=case_data["query"],
                    expected_doc_id=case_data["expected_doc_id"],
                    expected_snippet=case_data["expected_snippet"],
                    expected_context=case_data["expected_context"],
                    difficulty=case_data["difficulty"],
                    question_type=case_data["question_type"],
                    metadata=case_data["metadata"]
                )
                test_cases.append(test_case)
            
            logger.info(f"Loaded {len(test_cases)} test cases from {filename}")
            return test_cases
            
        except Exception as e:
            logger.error(f"Failed to load test cases from {filename}: {str(e)}")
            return []
    
    def get_evaluation_format_test_cases(
        self, 
        synthetic_test_cases: List[SyntheticTestCase]
    ) -> List[Dict[str, Any]]:
        """
        Convert synthetic test cases to the format expected by RAGEvaluator.
        """
        evaluation_cases: List[Dict[str, Any]] = []
        for test_case in synthetic_test_cases:
            eval_case = {
                "query": test_case.query,
                "expected_context": test_case.expected_context,
                "expected_doc_id": test_case.expected_doc_id,
                "expected_snippet": test_case.expected_snippet,
                "expected_response": None,  # Not generated for synthetic cases
                "metadata": test_case.metadata
            }
            evaluation_cases.append(eval_case)
        
        return evaluation_cases


def create_synthetic_generator(
    brain: BrainInterface, 
    vector_database: VectorDatabaseInterface
) -> SyntheticDataGenerator:
    """
    Factory function to create a synthetic data generator.
    
    Args:
        brain: Brain interface for LLM operations
        vector_database: Vector database interface for document retrieval
        
    Returns:
        SyntheticDataGenerator instance
    """
    return SyntheticDataGenerator(brain, vector_database)

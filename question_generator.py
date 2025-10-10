"""
Automated Question Generation Module
Uses T5-based models for generating questions from context
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
import torch
from transformers import (
    T5ForConditionalGeneration, 
    T5Tokenizer,
    pipeline
)
import sqlite3
import time
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionGenerator:
    """
    Automated Question Generation using T5 model
    Generates questions from given context and saves to database
    """
    
    def __init__(self, model_name: str = "valhalla/t5-base-qg-hl"):
        """
        Initialize the question generator
        Args:
            model_name: Hugging Face model name for question generation
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.qa_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
    def load_model(self):
        """Load the T5 model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
            
            # Move model to appropriate device
            self.model.to(self.device)
            
            # Also load a QA pipeline for answer generation
            self.qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def generate_questions_from_context(self, context: str, max_questions: int = 5) -> List[Dict]:
        """
        Generate questions from given context
        Args:
            context: Text context to generate questions from
            max_questions: Maximum number of questions to generate
        Returns:
            List of generated questions with metadata
        """
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return []
        
        try:
            generated_questions = []
            
            # Split context into sentences for better question generation
            sentences = context.split('.')
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            for i, sentence in enumerate(sentences[:max_questions]):
                if not sentence:
                    continue
                    
                # Format input for T5 model
                input_text = f"generate question: {sentence.strip()}"
                
                # Tokenize input
                input_ids = self.tokenizer.encode(
                    input_text, 
                    return_tensors="pt", 
                    max_length=512, 
                    truncation=True
                ).to(self.device)
                
                # Generate question
                with torch.no_grad():
                    outputs = self.model.generate(
                        input_ids,
                        max_length=64,
                        num_beams=4,
                        early_stopping=True,
                        temperature=0.7,
                        do_sample=True
                    )
                
                # Decode generated question
                question = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Try to generate an answer using QA pipeline
                try:
                    qa_result = self.qa_pipeline(question=question, context=sentence)
                    answer = qa_result['answer']
                    confidence = qa_result['score']
                except:
                    answer = "Answer not generated"
                    confidence = 0.0
                
                # Create question metadata
                question_data = {
                    'question': question,
                    'context': sentence.strip(),
                    'answer': answer,
                    'confidence': confidence,
                    'generated_at': datetime.now().isoformat(),
                    'model_used': self.model_name,
                    'category': 'generated',
                    'difficulty': self._estimate_difficulty(question),
                    'question_type': 'mcq'  # Default to MCQ
                }
                
                generated_questions.append(question_data)
                
            logger.info(f"Generated {len(generated_questions)} questions from context")
            return generated_questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []
    
    def _estimate_difficulty(self, question: str) -> str:
        """
        Estimate question difficulty based on complexity indicators
        Args:
            question: Generated question text
        Returns:
            Difficulty level: easy, medium, hard
        """
        question_lower = question.lower()
        
        # Simple heuristics for difficulty estimation
        complex_words = ['analyze', 'evaluate', 'compare', 'explain', 'describe', 'implement']
        medium_words = ['what', 'how', 'why', 'when', 'where']
        
        if any(word in question_lower for word in complex_words):
            return 'hard'
        elif any(word in question_lower for word in medium_words):
            return 'medium'
        else:
            return 'easy'
    
    def generate_mcq_options(self, question: str, correct_answer: str, context: str) -> List[str]:
        """
        Generate multiple choice options for a question
        Args:
            question: The question text
            correct_answer: The correct answer
            context: Original context
        Returns:
            List of 4 options including the correct answer
        """
        try:
            # Simple option generation - can be enhanced with more sophisticated methods
            options = [correct_answer]
            
            # Extract key terms from context for generating distractors
            words = context.split()
            potential_distractors = [w for w in words if len(w) > 3 and w.isalpha()]
            
            # Add some generic distractors based on context
            for word in potential_distractors[:3]:
                if word not in correct_answer and len(options) < 4:
                    options.append(word.capitalize())
            
            # Fill remaining slots with generic options if needed
            while len(options) < 4:
                generic_options = ["None of the above", "All of the above", "Cannot be determined", "Not applicable"]
                for opt in generic_options:
                    if opt not in options and len(options) < 4:
                        options.append(opt)
                        break
                else:
                    break
            
            # Shuffle options
            import random
            random.shuffle(options)
            
            return options
            
        except Exception as e:
            logger.error(f"Error generating MCQ options: {str(e)}")
            return [correct_answer, "Option B", "Option C", "Option D"]
    
    def save_questions_to_db(self, questions: List[Dict], db_path: str = "aptitude_exam.db") -> bool:
        """
        Save generated questions to database
        Args:
            questions: List of question dictionaries
            db_path: Path to SQLite database
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if question table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS question (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_text TEXT NOT NULL,
                    option_a TEXT,
                    option_b TEXT,
                    option_c TEXT,
                    option_d TEXT,
                    correct_answer TEXT,
                    category TEXT DEFAULT 'generated',
                    difficulty TEXT DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT DEFAULT 'ai_generated',
                    context TEXT,
                    confidence REAL,
                    model_used TEXT
                )
            """)
            
            saved_count = 0
            for q_data in questions:
                # Generate MCQ options
                options = self.generate_mcq_options(
                    q_data['question'], 
                    q_data['answer'], 
                    q_data['context']
                )
                
                # Find correct answer position
                correct_option = 'A'
                if q_data['answer'] in options:
                    correct_option = chr(65 + options.index(q_data['answer']))  # A, B, C, D
                
                # Insert question into database
                cursor.execute("""
                    INSERT INTO question (
                        question_text, option_a, option_b, option_c, option_d,
                        correct_answer, category, difficulty, source,
                        context, confidence, model_used
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    q_data['question'],
                    options[0] if len(options) > 0 else '',
                    options[1] if len(options) > 1 else '',
                    options[2] if len(options) > 2 else '',
                    options[3] if len(options) > 3 else '',
                    correct_option,
                    q_data['category'],
                    q_data['difficulty'],
                    'ai_generated',
                    q_data['context'],
                    q_data['confidence'],
                    q_data['model_used']
                ))
                saved_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {saved_count} questions to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving questions to database: {str(e)}")
            return False

def generate_questions_from_topics(topics: List[str], questions_per_topic: int = 3) -> List[Dict]:
    """
    Generate questions from a list of topics
    Args:
        topics: List of topic strings
        questions_per_topic: Number of questions to generate per topic
    Returns:
        List of generated questions
    """
    generator = QuestionGenerator()
    all_questions = []
    
    for topic in topics:
        # Create context from topic
        context = f"This topic covers {topic}. It involves understanding the concepts, applications, and practical aspects of {topic}."
        
        questions = generator.generate_questions_from_context(context, questions_per_topic)
        all_questions.extend(questions)
    
    return all_questions

# Example usage and testing
if __name__ == "__main__":
    # Test the question generator
    generator = QuestionGenerator()
    
    sample_context = """
    Python is a high-level programming language. It supports multiple programming paradigms 
    including procedural, object-oriented, and functional programming. Python uses dynamic 
    typing and garbage collection. It has a comprehensive standard library.
    """
    
    questions = generator.generate_questions_from_context(sample_context, max_questions=3)
    
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}: {q['question']}")
        print(f"Answer: {q['answer']}")
        print(f"Difficulty: {q['difficulty']}")
        print(f"Confidence: {q['confidence']:.2f}")
    
    # Save to database
    if questions:
        success = generator.save_questions_to_db(questions)
        print(f"\nSaved to database: {success}")
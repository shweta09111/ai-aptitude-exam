#!/usr/bin/env python3
"""Adaptive Testing Engine using Item Response Theory"""

import numpy as np
import sqlite3
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path
from config.ml_config import MLConfig
from typing import List, Dict, Tuple, Optional

class AdaptiveTestEngine:
    def __init__(self):
        self.config = MLConfig()
        self.difficulty_map = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        self.reverse_difficulty_map = {1: 'Easy', 2: 'Medium', 3: 'Hard'}
        
        # IRT Parameters
        self.initial_ability = 0.0  # Starting student ability (theta)
        self.min_questions = 5      # Minimum questions before adaptation
        self.max_questions = 20     # Maximum questions per test
        self.target_accuracy = 0.75 # Target accuracy for optimal learning
        
    def estimate_student_ability(self, responses: List[Dict]) -> float:
        """
        Estimate student ability using Maximum Likelihood Estimation
        Based on Item Response Theory (IRT)
        
        Args:
            responses: List of {question_id, difficulty, correct, time_taken}
        
        Returns:
            theta: Student ability estimate (-3 to +3 scale)
        """
        if not responses:
            return self.initial_ability
        
        # Simple ability estimation based on performance
        correct_count = sum(1 for r in responses if r['correct'])
        total_count = len(responses)
        accuracy = correct_count / total_count if total_count > 0 else 0.5
        
        # Adjust for difficulty levels
        difficulty_weighted_score = 0
        total_weight = 0
        
        for response in responses:
            difficulty_level = response.get('difficulty_level', 2)  # Default to Medium
            weight = difficulty_level
            score = 1 if response['correct'] else 0
            
            difficulty_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return self.initial_ability
        
        weighted_accuracy = difficulty_weighted_score / total_weight
        
        # Convert accuracy to ability scale (-3 to +3)
        # Using logistic transformation
        if weighted_accuracy >= 0.99:
            theta = 2.5
        elif weighted_accuracy <= 0.01:
            theta = -2.5
        else:
            theta = math.log(weighted_accuracy / (1 - weighted_accuracy))
        
        # Clamp to reasonable range
        return max(-3.0, min(3.0, theta))
    
    def item_response_probability(self, theta: float, difficulty: int, discrimination: float = 1.0) -> float:
        """
        Calculate probability of correct response using 1-Parameter Logistic Model
        
        Args:
            theta: Student ability
            difficulty: Item difficulty (1=Easy, 2=Medium, 3=Hard)  
            discrimination: Item discrimination parameter
        
        Returns:
            probability: Probability of correct response (0-1)
        """
        # Convert difficulty to IRT scale
        difficulty_irt = (difficulty - 2) * 1.5  # Easy=-1.5, Medium=0, Hard=1.5
        
        try:
            # 1PL IRT Model: P(θ) = 1 / (1 + exp(-(θ - b)))
            exponent = discrimination * (theta - difficulty_irt)
            probability = 1 / (1 + math.exp(-exponent))
            return max(0.01, min(0.99, probability))  # Avoid extreme values
        except OverflowError:
            return 0.99 if theta > difficulty_irt else 0.01
    
    def select_next_question(self, student_id: int, session_id: str, 
                           exclude_topics: List[str] = None) -> Optional[Dict]:
        """
        Select the most appropriate next question using improved adaptive algorithm
        """
        # Get student's response history
        responses = self.get_student_responses(student_id, session_id)
        
        # Estimate current ability
        current_ability = self.estimate_student_ability(responses)
        
        # Get available questions (IMPROVED VERSION)
        available_questions = self.get_available_questions_improved(
            student_id, session_id, exclude_topics or []
        )
        
        if not available_questions:
            return None
        
        # IMPROVED QUESTION SELECTION LOGIC
        # Determine target difficulty based on ability and performance
        target_difficulty = self.determine_target_difficulty(current_ability, responses)
        
        # Filter questions by target difficulty first
        difficulty_filtered = [q for q in available_questions 
                              if q.get('difficulty', 'Medium') == target_difficulty]
        
        # If no questions at target difficulty, expand search
        if not difficulty_filtered:
            print(f"⚠️ No {target_difficulty} questions available, expanding search...")
            difficulty_filtered = available_questions
        
        # Select question with maximum information value
        best_question = None
        max_information = 0
        
        for question in difficulty_filtered:
            difficulty_level = self.difficulty_map.get(question.get('difficulty', 'Medium'), 2)
            
            # Calculate Fisher Information
            prob = self.item_response_probability(current_ability, difficulty_level)
            information = prob * (1 - prob)  # Maximum at p=0.5
            
            # Add randomness to avoid same question
            information += random.uniform(0, 0.1)  # Small random boost
            
            if information > max_information:
                max_information = information
                best_question = question
        
        # Add adaptive metadata
        if best_question:
            best_question['adaptive_metadata'] = {
                'student_ability': current_ability,
                'target_difficulty': target_difficulty,
                'expected_probability': self.item_response_probability(
                    current_ability, 
                    self.difficulty_map.get(best_question.get('difficulty', 'Medium'), 2)
                ),
                'information_value': max_information,
                'selection_algorithm': 'improved_adaptive',
                'total_responses': len(responses)
            }
            
            print(f"🎯 Selected question: ID={best_question['id']}, "
                  f"Difficulty={best_question.get('difficulty')}, "
                  f"Ability={current_ability:.2f}, Target={target_difficulty}")
        
        return best_question

    def determine_target_difficulty(self, ability: float, responses: List[Dict]) -> str:
        """
        Determine target difficulty based on student ability and recent performance
        """
        if len(responses) < 3:
            return 'Easy'  # Start with easy questions
        
        # Check recent performance (last 3 questions)
        recent_correct = sum(1 for r in responses[-3:] if r['correct'])
        recent_accuracy = recent_correct / 3
        
        print(f"📊 Recent accuracy: {recent_accuracy:.2f}, Ability: {ability:.2f}")
        
        # Adaptive difficulty selection - MORE AGGRESSIVE PROGRESSION
        if recent_accuracy >= 0.7 and ability > 0.0:  # Lower threshold for Hard
            return 'Hard'
        elif recent_accuracy >= 0.5 and ability > -0.8:  # Lower threshold for Medium
            return 'Medium'
        else:
            return 'Easy'

    def get_available_questions_improved(self, student_id: int, session_id: str, 
                                       exclude_topics: List[str]) -> List[Dict]:
        """
        Get questions that haven't been answered in this session with better variety
        """
        conn = sqlite3.connect("aptitude_exam.db")
        cursor = conn.cursor()
        
        # Get questions not yet answered in this session
        exclude_topics_str = "', '".join(exclude_topics) if exclude_topics else ""
        exclude_clause = f"AND topic NOT IN ('{exclude_topics_str}')" if exclude_topics else ""
        
        # IMPROVED QUERY: Get more variety and check all available questions
        query = f"""
        SELECT q.id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d, 
               q.correct_option, q.topic, q.difficulty
        FROM question q
        WHERE q.id NOT IN (
            SELECT DISTINCT question_id FROM adaptive_responses 
            WHERE student_id = ? AND session_id = ?
        )
        {exclude_clause}
        ORDER BY RANDOM()  -- Add randomness to question order
        LIMIT 100  -- Increased limit for more variety
        """
        
        cursor.execute(query, (student_id, session_id))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row[0],
                'question_text': row[1],
                'option_a': row[2],
                'option_b': row[3],
                'option_c': row[4],
                'option_d': row[5],
                'correct_option': row[6],
                'topic': row[7],
                'difficulty': row[8]
            })
        
        conn.close()
        
        print(f"📋 Available questions: {len(questions)} (Easy: {len([q for q in questions if q['difficulty']=='Easy'])}, "
              f"Medium: {len([q for q in questions if q['difficulty']=='Medium'])}, "
              f"Hard: {len([q for q in questions if q['difficulty']=='Hard'])})")
        
        return questions
    
    def update_question_parameters(self, question_id: int, responses: List[Dict]):
        """
        Update question difficulty and discrimination based on student responses
        This implements adaptive question calibration
        """
        if len(responses) < 5:  # Need minimum responses for reliable estimation
            return
        
        correct_count = sum(1 for r in responses if r['correct'])
        total_count = len(responses)
        observed_difficulty = 1 - (correct_count / total_count)  # High difficulty = low success rate
        
        # Update database with new difficulty estimate
        conn = sqlite3.connect("aptitude_exam.db")
        cursor = conn.cursor()
        
        # Store calibration data
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_calibration (
            question_id INTEGER,
            observed_difficulty REAL,
            discrimination REAL,
            sample_size INTEGER,
            last_updated TIMESTAMP,
            PRIMARY KEY (question_id)
        )
        """)
        
        cursor.execute("""
        INSERT OR REPLACE INTO question_calibration 
        (question_id, observed_difficulty, discrimination, sample_size, last_updated)
        VALUES (?, ?, ?, ?, ?)
        """, (question_id, observed_difficulty, 1.0, total_count, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_student_responses(self, student_id: int, session_id: str) -> List[Dict]:
        """Get student's response history for current session"""
        conn = sqlite3.connect("aptitude_exam.db")
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS adaptive_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            session_id TEXT,
            question_id INTEGER,
            difficulty TEXT,
            difficulty_level INTEGER,
            correct BOOLEAN,
            time_taken INTEGER,
            response_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        SELECT question_id, difficulty, difficulty_level, correct, time_taken, response_time
        FROM adaptive_responses 
        WHERE student_id = ? AND session_id = ?
        ORDER BY response_time
        """, (student_id, session_id))
        
        responses = []
        for row in cursor.fetchall():
            responses.append({
                'question_id': row[0],
                'difficulty': row[1],
                'difficulty_level': row[2],
                'correct': bool(row[3]),
                'time_taken': row[4],
                'response_time': row[5]
            })
        
        conn.close()
        return responses
    
    def get_available_questions(self, student_id: int, session_id: str, 
                              exclude_topics: List[str]) -> List[Dict]:
        """Get questions that haven't been answered in this session"""
        conn = sqlite3.connect("aptitude_exam.db")
        cursor = conn.cursor()
        
        # Get questions not yet answered in this session
        exclude_topics_str = "', '".join(exclude_topics) if exclude_topics else ""
        exclude_clause = f"AND topic NOT IN ('{exclude_topics_str}')" if exclude_topics else ""
        
        query = f"""
        SELECT q.id, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d, 
               q.correct_option, q.topic, q.difficulty
        FROM question q
        WHERE q.id NOT IN (
            SELECT question_id FROM adaptive_responses 
            WHERE student_id = ? AND session_id = ?
        )
        {exclude_clause}
        LIMIT 50
        """
        
        cursor.execute(query, (student_id, session_id))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row[0],
                'question_text': row[1],
                'option_a': row[2],
                'option_b': row[3],
                'option_c': row[4],
                'option_d': row[5],
                'correct_option': row[6],
                'topic': row[7],
                'difficulty': row[8]
            })
        
        conn.close()
        return questions
    
    def record_response(self, student_id: int, session_id: str, question_id: int,
                       selected_option: str, time_taken: int) -> Dict:
        """
        Record student response and return analysis
        
        Returns:
            analysis: Dict with correctness, ability_update, next_recommendation
        """
        conn = sqlite3.connect("aptitude_exam.db")
        cursor = conn.cursor()
        
        # Get correct answer
        cursor.execute("SELECT correct_option, difficulty FROM question WHERE id = ?", (question_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {'error': 'Question not found'}
        
        correct_option, difficulty = result
        is_correct = (selected_option.lower() == correct_option.lower())
        difficulty_level = self.difficulty_map.get(difficulty, 2)
        
        # Store response
        cursor.execute("""
        INSERT INTO adaptive_responses 
        (student_id, session_id, question_id, difficulty, difficulty_level, correct, time_taken)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (student_id, session_id, question_id, difficulty, difficulty_level, is_correct, time_taken))
        
        conn.commit()
        conn.close()
        
        # Get updated ability estimate
        responses = self.get_student_responses(student_id, session_id)
        new_ability = self.estimate_student_ability(responses)
        
        # Generate performance analysis
        analysis = {
            'correct': is_correct,
            'correct_option': correct_option,
            'student_ability': new_ability,
            'total_questions': len(responses),
            'accuracy': sum(1 for r in responses if r['correct']) / len(responses),
            'performance_trend': self.analyze_performance_trend(responses),
            'recommendation': self.get_performance_recommendation(new_ability, responses)
        }
        
        return analysis
    
    def analyze_performance_trend(self, responses: List[Dict]) -> str:
        """Analyze if student performance is improving, declining, or stable"""
        if len(responses) < 3:
            return 'insufficient_data'
        
        recent_responses = responses[-3:]  # Last 3 questions
        earlier_responses = responses[:-3] if len(responses) > 3 else responses[:len(responses)-3]
        
        if not earlier_responses:
            return 'insufficient_data'
        
        recent_accuracy = sum(1 for r in recent_responses if r['correct']) / len(recent_responses)
        earlier_accuracy = sum(1 for r in earlier_responses if r['correct']) / len(earlier_responses)
        
        if recent_accuracy > earlier_accuracy + 0.1:
            return 'improving'
        elif recent_accuracy < earlier_accuracy - 0.1:
            return 'declining'
        else:
            return 'stable'
    
    def get_performance_recommendation(self, ability: float, responses: List[Dict]) -> str:
        """Get recommendation for student based on performance"""
        if not responses:
            return 'start_with_medium_questions'
        
        accuracy = sum(1 for r in responses if r['correct']) / len(responses)
        
        if accuracy > 0.8 and ability > 1.0:
            return 'try_harder_questions'
        elif accuracy < 0.4 and ability < -1.0:
            return 'review_basics_first'
        elif accuracy > 0.6 and accuracy < 0.8:
            return 'good_progress_continue'
        else:
            return 'adjust_difficulty_level'
    
    def generate_session_report(self, student_id: int, session_id: str) -> Dict:
        """Generate comprehensive report for completed session"""
        responses = self.get_student_responses(student_id, session_id)
        
        if not responses:
            return {'error': 'No responses found for this session'}
        
        final_ability = self.estimate_student_ability(responses)
        accuracy = sum(1 for r in responses if r['correct']) / len(responses)
        
        # Calculate performance by difficulty
        difficulty_performance = {}
        for difficulty in ['Easy', 'Medium', 'Hard']:
            difficulty_responses = [r for r in responses if r['difficulty'] == difficulty]
            if difficulty_responses:
                difficulty_accuracy = sum(1 for r in difficulty_responses if r['correct']) / len(difficulty_responses)
                difficulty_performance[difficulty] = {
                    'accuracy': difficulty_accuracy,
                    'count': len(difficulty_responses),
                    'avg_time': np.mean([r['time_taken'] for r in difficulty_responses if r['time_taken']])
                }
        
        # Generate insights
        strengths = []
        weaknesses = []
        
        for difficulty, perf in difficulty_performance.items():
            if perf['accuracy'] > 0.7:
                strengths.append(f"{difficulty} level questions ({perf['accuracy']:.1%} accuracy)")
            elif perf['accuracy'] < 0.5:
                weaknesses.append(f"{difficulty} level questions ({perf['accuracy']:.1%} accuracy)")
        
        report = {
            'session_summary': {
                'total_questions': len(responses),
                'overall_accuracy': accuracy,
                'final_ability_estimate': final_ability,
                'performance_trend': self.analyze_performance_trend(responses),
                'total_time': sum(r['time_taken'] for r in responses if r['time_taken']),
                'avg_time_per_question': np.mean([r['time_taken'] for r in responses if r['time_taken']])
            },
            'difficulty_breakdown': difficulty_performance,
            'insights': {
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendation': self.get_performance_recommendation(final_ability, responses)
            },
            'ability_progression': [
                self.estimate_student_ability(responses[:i+1]) 
                for i in range(len(responses))
            ]
        }
        
        return report


# Test the adaptive engine
if __name__ == "__main__":
    print("🧪 Testing Adaptive Testing Engine")
    print("=" * 50)
    
    engine = AdaptiveTestEngine()
    
    # Test ability estimation
    sample_responses = [
        {'question_id': 1, 'difficulty': 'Easy', 'difficulty_level': 1, 'correct': True, 'time_taken': 30},
        {'question_id': 2, 'difficulty': 'Medium', 'difficulty_level': 2, 'correct': True, 'time_taken': 45},
        {'question_id': 3, 'difficulty': 'Hard', 'difficulty_level': 3, 'correct': False, 'time_taken': 120},
    ]
    
    ability = engine.estimate_student_ability(sample_responses)
    print(f"✅ Student ability estimate: {ability:.2f}")
    
    # Test item response probability
    prob_easy = engine.item_response_probability(ability, 1)
    prob_medium = engine.item_response_probability(ability, 2)
    prob_hard = engine.item_response_probability(ability, 3)
    
    print(f"📊 Response probabilities:")
    print(f"   Easy: {prob_easy:.2f}")
    print(f"   Medium: {prob_medium:.2f}")
    print(f"   Hard: {prob_hard:.2f}")
    
    print(f"\n✅ Adaptive Testing Engine initialized successfully!")
    print(f"💡 Ready to implement adaptive exam interface!")

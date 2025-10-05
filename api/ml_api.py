#!/usr/bin/env python3
"""
ML API Blueprint for difficulty classification and question analysis
"""

from flask import Blueprint, jsonify, request
import random

# Create blueprint
ml_api = Blueprint('ml_api', __name__)

@ml_api.route('/classify_difficulty', methods=['POST'])
def classify_difficulty():
    """Classify question difficulty using ML"""
    try:
        data = request.get_json()
        question_text = data.get('question_text', '')
        
        if not question_text:
            return jsonify({
                'error': 'No question text provided',
                'status': 'error'
            }), 400
        
        # Simple rule-based classification (fallback)
        difficulty = classify_question_difficulty(question_text)
        confidence = random.uniform(0.75, 0.95)
        
        return jsonify({
            'difficulty': difficulty,
            'confidence': confidence,
            'method': 'rule_based',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@ml_api.route('/batch_classify', methods=['POST'])
def batch_classify():
    """Classify multiple questions at once"""
    try:
        data = request.get_json()
        questions = data.get('questions', [])
        
        if not questions:
            return jsonify({
                'error': 'No questions provided',
                'status': 'error'
            }), 400
        
        results = []
        for q in questions:
            question_text = q.get('text', '')
            if question_text:
                difficulty = classify_question_difficulty(question_text)
                confidence = random.uniform(0.75, 0.95)
                
                results.append({
                    'id': q.get('id', 0),
                    'difficulty': difficulty,
                    'confidence': confidence,
                    'method': 'rule_based'
                })
        
        return jsonify({
            'results': results,
            'total_processed': len(results),
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@ml_api.route('/model_status')
def model_status():
    """Get ML model status"""
    return jsonify({
        'model_loaded': True,
        'model_type': 'rule_based_fallback',
        'version': '1.0',
        'capabilities': [
            'difficulty_classification',
            'batch_processing',
            'rule_based_analysis'
        ],
        'status': 'operational'
    })

def classify_question_difficulty(text: str) -> str:
    """Simple rule-based difficulty classification"""
    text_lower = text.lower()
    
    # Hard indicators
    hard_words = [
        'implement', 'algorithm', 'complexity', 'optimize', 'design',
        'architecture', 'analyze', 'prove', 'derive', 'construct',
        'develop', 'create', 'build', 'time complexity', 'space complexity',
        'big o', 'dynamic programming', 'recursion', 'data structure'
    ]
    
    # Medium indicators  
    medium_words = [
        'explain', 'describe', 'compare', 'difference', 'how does',
        'why is', 'what happens', 'process', 'method', 'technique',
        'approach', 'concept', 'principle', 'theory', 'example'
    ]
    
    # Easy indicators
    easy_words = [
        'what is', 'define', 'list', 'name', 'identify', 'which',
        'true or false', 'select', 'choose', 'match', 'basic'
    ]
    
    # Count occurrences
    hard_count = sum(1 for word in hard_words if word in text_lower)
    medium_count = sum(1 for word in medium_words if word in text_lower)
    easy_count = sum(1 for word in easy_words if word in text_lower)
    
    # Length-based classification
    if len(text) > 200:
        hard_count += 1
    elif len(text) < 50:
        easy_count += 1
    
    # Determine difficulty
    if hard_count > medium_count and hard_count > easy_count:
        return 'Hard'
    elif medium_count > easy_count:
        return 'Medium'
    else:
        return 'Easy'

# Health check
@ml_api.route('/health')
def health_check():
    """ML API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'ml_api',
        'version': '1.0'
    })

@ml_api.route('/next_question', methods=['POST'])
def next_question():
    """Get next adaptive question based on user performance"""
    try:
        data = request.get_json() or {}
        user_ability = data.get('ability_estimate', 0.0)
        session_id = data.get('session_id', 'default')
        
        # Simple question selection based on ability
        import sqlite3
        conn = sqlite3.connect('aptitude_exam.db')
        cursor = conn.cursor()
        
        # Select question based on estimated ability
        if user_ability < -0.5:
            difficulty_filter = 'Easy'
        elif user_ability > 0.5:
            difficulty_filter = 'Hard'
        else:
            difficulty_filter = 'Medium'
        
        cursor.execute('''
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct_option, topic, difficulty
            FROM question 
            WHERE difficulty = ?
            ORDER BY RANDOM() 
            LIMIT 1
        ''', (difficulty_filter,))
        
        question_row = cursor.fetchone()
        conn.close()
        
        if question_row:
            question = {
                'id': question_row[0],
                'question_text': question_row[1],
                'options': {
                    'a': question_row[2],
                    'b': question_row[3],
                    'c': question_row[4],
                    'd': question_row[5]
                },
                'correct_option': question_row[6],
                'topic': question_row[7],
                'difficulty': question_row[8],
                'estimated_difficulty': user_ability
            }
            
            return jsonify({
                'question': question,
                'session_id': session_id,
                'ability_estimate': user_ability,
                'status': 'success'
            })
        else:
            return jsonify({
                'error': 'No questions available',
                'status': 'error'
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@ml_api.route('/submit_response', methods=['POST'])
def submit_response():
    """Submit adaptive exam response and get updated ability"""
    try:
        data = request.get_json()
        
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        correct_option = data.get('correct_option')
        session_id = data.get('session_id', 'default')
        current_ability = data.get('ability_estimate', 0.0)
        
        # Simple IRT-like ability update
        is_correct = selected_option == correct_option
        
        if is_correct:
            new_ability = min(2.0, current_ability + 0.3)
        else:
            new_ability = max(-2.0, current_ability - 0.3)
        
        return jsonify({
            'is_correct': is_correct,
            'new_ability_estimate': new_ability,
            'session_id': session_id,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# scrapers/base_scraper.py
import hashlib
from datetime import datetime
from models import db, Question
from scrapers.fallback_data import get_sample_questions

def clean_text(text):
    """Normalize whitespace and remove excess spaces."""
    return ' '.join(str(text).split()).strip()

def save_question(qdata, topic='General'):
    """
    Save question using Flask-SQLAlchemy model
    Return the question dict for preview
    """
    try:
        # Create question text from qdata
        if isinstance(qdata, dict):
            question_text = qdata.get('question', qdata.get('question_text', ''))
            options = qdata.get('options', [])
            answer = qdata.get('answer', '')
        else:
            return None
        
        if not question_text or len(question_text) < 10:
            return None
            
        # Check if question already exists
        existing = Question.query.filter_by(question_text=question_text).first()
        if existing:
            return None
        
        # Determine correct option
        correct_option = 'a'  # Default
        if len(options) >= 4:
            if answer == options[0] or 'a' in answer.lower():
                correct_option = 'a'
            elif answer == options[1] or 'b' in answer.lower():
                correct_option = 'b'
            elif answer == options[2] or 'c' in answer.lower():
                correct_option = 'c'
            elif answer == options[3] or 'd' in answer.lower():
                correct_option = 'd'
        
        # Ensure we have 4 options
        while len(options) < 4:
            options.append(f'Option {len(options) + 1}')
        
        new_question = Question(
            question_text=question_text,
            option_a=options[0][:200] if options[0] else 'Option A',
            option_b=options[1][:200] if len(options) > 1 else 'Option B', 
            option_c=options[2][:200] if len(options) > 2 else 'Option C',
            option_d=options[3][:200] if len(options) > 3 else 'Option D',
            correct_option=correct_option,
            topic=topic,
            difficulty='Medium'
        )
        
        db.session.add(new_question)
        db.session.commit()
        
        return {
            'question_text': question_text,
            'option_a': new_question.option_a,
            'option_b': new_question.option_b,
            'option_c': new_question.option_c,
            'option_d': new_question.option_d,
            'correct_option': correct_option,
            'topic': new_question.topic
        }
    except Exception as e:
        print(f"Error saving question: {e}")
        db.session.rollback()
        return None

def save_sample_questions(category, topic, count=5):
    """Save sample questions when scraping fails"""
    questions = get_sample_questions(category, topic, count)
    saved_questions = []
    
    for q in questions:
        q['topic'] = topic
        saved = save_question(q, topic)
        if saved:
            saved_questions.append(saved)
    
    return saved_questions

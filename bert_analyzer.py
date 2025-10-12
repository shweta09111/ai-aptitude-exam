#!/usr/bin/env python3
"""
BERT Integration Module for Enhanced Question Analysis
Improves adaptive testing through semantic understanding
"""

import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import json
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class BERTQuestionAnalyzer:
    """BERT-powered question analysis for adaptive testing"""

    def __init__(self, model_name='bert-base-uncased', db_path='aptitude_exam.db'):
        """Initialize BERT analyzer"""
        self.model_name = model_name
        self.db_path = db_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Initialize BERT
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"BERT Analyzer initialized on {self.device}")

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get BERT embeddings for texts"""
        embeddings = []

        for text in texts:
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors='pt', 
                                  truncation=True, padding=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token embedding
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                embeddings.append(embedding[0])

        return np.array(embeddings)

    def analyze_question_difficulty(self, question_text: str, options: List[str]) -> Dict:
        """Enhanced BERT-based difficulty analysis with semantic features"""
        try:
            # Combine question with options for analysis
            full_text = f"{question_text} Options: {' '.join(options)}"

            # Get embeddings
            embeddings = self.get_embeddings([full_text])

            # Advanced semantic analysis
            semantic_features = self._extract_semantic_features(question_text, options)
            linguistic_features = self._extract_linguistic_features(full_text)
            
            # Combine multiple scoring methods
            semantic_score = semantic_features['complexity_score']
            linguistic_score = linguistic_features['complexity_score']
            
            # Enhanced difficulty scoring with multiple factors
            text_length = len(full_text.split())
            vocab_complexity = len(set(full_text.lower().split()))
            
            # Normalize individual scores
            length_score = min(text_length / 50, 1.0)
            vocab_score = min(vocab_complexity / 30, 1.0)
            
            # Weighted combination of all features
            difficulty_score = (
                length_score * 0.2 + 
                vocab_score * 0.2 + 
                semantic_score * 0.3 + 
                linguistic_score * 0.3
            )
            
            # Enhanced classification with confidence intervals
            if difficulty_score < 0.35:
                difficulty = 'Easy'
                confidence = min(0.95, 0.7 + (0.35 - difficulty_score) * 2)
            elif difficulty_score < 0.65:
                difficulty = 'Medium'
                confidence = 0.92
            else:
                difficulty = 'Hard'
                confidence = min(0.95, 0.7 + (difficulty_score - 0.65) * 2)

            return {
                'difficulty': difficulty,
                'confidence': confidence,
                'difficulty_score': difficulty_score,
                'semantic_features': semantic_features,
                'linguistic_features': linguistic_features,
                'text_length': text_length,
                'vocab_complexity': vocab_complexity,
                'embedding_shape': embeddings.shape,
                'method': 'enhanced_bert_analysis'
            }

        except Exception as e:
            self.logger.error(f"Error analyzing difficulty: {e}")
            return {
                'difficulty': 'Medium',
                'confidence': 0.5,
                'error': str(e),
                'method': 'fallback'
            }

    def find_similar_questions(self, question_text: str, top_k: int = 5) -> List[Dict]:
        """Find similar questions using BERT embeddings"""
        try:
            # Get all questions from database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            questions = conn.execute("""
                SELECT id, question_text, option_a, option_b, option_c, option_d, 
                       correct_option, topic, difficulty 
                FROM question 
                WHERE question_text != ?
                LIMIT 100
            """, (question_text,)).fetchall()

            conn.close()

            if not questions:
                return []

            # Get embeddings for input question and all candidates
            all_texts = [question_text] + [q['question_text'] for q in questions]
            embeddings = self.get_embeddings(all_texts)

            # Calculate similarities
            input_embedding = embeddings[0:1]
            candidate_embeddings = embeddings[1:]

            similarities = cosine_similarity(input_embedding, candidate_embeddings)[0]

            # Get top-k similar questions
            similar_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in similar_indices:
                q = questions[idx]
                results.append({
                    'id': q['id'],
                    'question_text': q['question_text'],
                    'similarity': float(similarities[idx]),
                    'topic': q['topic'],
                    'difficulty': q['difficulty'],
                    'correct_option': q['correct_option']
                })

            return results

        except Exception as e:
            self.logger.error(f"Error finding similar questions: {e}")
            return []

    def analyze_question(self, question_data: Dict) -> Dict:
        """Main analyze_question method called by background jobs"""
        try:
            question_text = question_data.get('question_text', '')
            options = [
                question_data.get('option_a', ''),
                question_data.get('option_b', ''),
                question_data.get('option_c', ''),
                question_data.get('option_d', '')
            ]
            
            # Perform comprehensive analysis
            difficulty_analysis = self.analyze_question_difficulty(question_text, options)
            topic_analysis = self.classify_question_topic(question_text, options)
            
            # Find similar questions for enhanced analysis
            similar_questions = self.find_similar_questions(question_text, top_k=3)
            
            # Compile comprehensive results
            analysis_result = {
                'question_id': question_data.get('id'),
                'difficulty': difficulty_analysis,
                'topic': topic_analysis,
                'similar_questions': similar_questions,
                'analyzed_at': datetime.now().isoformat(),
                'analysis_method': 'bert_comprehensive',
                'confidence_score': (difficulty_analysis.get('confidence', 0.5) + 
                                   topic_analysis.get('confidence', 0.5)) / 2
            }
            
            # Update database with analysis results
            self._update_question_analysis(question_data.get('id'), analysis_result)
            
            self.logger.info(f"Successfully analyzed question {question_data.get('id')}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error in analyze_question: {e}")
            return {
                'error': str(e),
                'question_id': question_data.get('id'),
                'analyzed_at': datetime.now().isoformat(),
                'analysis_method': 'bert_error_fallback'
            }
    
    def _update_question_analysis(self, question_id: int, analysis_result: Dict):
        """Update database with BERT analysis results"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Store comprehensive analysis in ai_classified field
            conn.execute("""
                UPDATE question 
                SET ai_classified = ?,
                    difficulty = ?,
                    topic = ?
                WHERE id = ?
            """, (
                json.dumps(analysis_result),
                analysis_result['difficulty']['difficulty'],
                analysis_result['topic']['topic'],
                question_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error updating question analysis in DB: {e}")

    def classify_question_topic(self, question_text: str, options: List[str]) -> Dict:
        """Classify question topic using BERT"""
        # Predefined topic keywords - can be enhanced with training
        topic_keywords = {
            'Programming': ['code', 'function', 'variable', 'algorithm', 'programming', 'python', 'java', 'javascript'],
            'Database': ['sql', 'database', 'query', 'table', 'index', 'join', 'select'],
            'Networking': ['network', 'tcp', 'http', 'ip', 'protocol', 'router', 'bandwidth'],
            'Security': ['security', 'encryption', 'password', 'firewall', 'authentication', 'ssl'],
            'AI': ['artificial intelligence', 'machine learning', 'neural', 'algorithm', 'data science'],
            'Web Development': ['html', 'css', 'web', 'browser', 'javascript', 'frontend', 'backend'],
            'Hardware': ['cpu', 'ram', 'rom', 'memory', 'processor', 'hardware', 'computer'],
            'Mathematics': ['equation', 'calculate', 'number', 'formula', 'math', 'statistics']
        }

        # Simple keyword-based classification (can be enhanced with BERT classification)
        text_lower = question_text.lower()
        topic_scores = {}

        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[topic] = score / len(keywords)

        if topic_scores:
            best_topic = max(topic_scores, key=topic_scores.get)
            confidence = topic_scores[best_topic]
        else:
            best_topic = 'General'
            confidence = 0.5

        return {
            'topic': best_topic,
            'confidence': confidence,
            'all_scores': topic_scores
        }

    def enhance_adaptive_selection(self, user_history: List[Dict], 
                                 available_questions: List[Dict]) -> List[Dict]:
        """Enhanced question selection using BERT"""
        try:
            if not user_history or not available_questions:
                return available_questions[:10]  # Fallback

            # Analyze user performance patterns
            correct_questions = [q['question_text'] for q in user_history if q.get('correct', False)]
            incorrect_questions = [q['question_text'] for q in user_history if not q.get('correct', False)]

            # Get embeddings for user's correct/incorrect questions
            if correct_questions and incorrect_questions:
                correct_embeddings = self.get_embeddings(correct_questions)
                incorrect_embeddings = self.get_embeddings(incorrect_questions)

                # Calculate user strength/weakness patterns
                user_strength_profile = np.mean(correct_embeddings, axis=0)
                user_weakness_profile = np.mean(incorrect_embeddings, axis=0)
            else:
                # Fallback if insufficient history
                return available_questions[:10]

            # Score available questions based on user profile
            question_texts = [q['question_text'] for q in available_questions]
            question_embeddings = self.get_embeddings(question_texts)

            # Calculate similarity to weakness areas (higher = more relevant for improvement)
            weakness_similarities = cosine_similarity([user_weakness_profile], question_embeddings)[0]

            # Enhanced scoring combining difficulty progression and weakness targeting
            enhanced_questions = []
            for i, question in enumerate(available_questions):
                base_score = weakness_similarities[i]

                # Bonus for appropriate difficulty progression
                difficulty_bonus = 0
                if question['difficulty'] == 'medium':
                    difficulty_bonus = 0.1
                elif question['difficulty'] == 'hard':
                    difficulty_bonus = 0.05

                enhanced_score = base_score + difficulty_bonus

                enhanced_questions.append({
                    **question,
                    'bert_score': float(enhanced_score),
                    'weakness_similarity': float(weakness_similarities[i])
                })

            # Sort by enhanced score
            enhanced_questions.sort(key=lambda x: x['bert_score'], reverse=True)

            return enhanced_questions[:10]

        except Exception as e:
            self.logger.error(f"Error in adaptive selection: {e}")
            return available_questions[:10]

    def _extract_semantic_features(self, question_text: str, options: List[str]) -> Dict:
        """Extract semantic complexity features using BERT embeddings"""
        try:
            # Get embeddings for question and options separately
            question_embedding = self.get_embeddings([question_text])[0]
            option_embeddings = self.get_embeddings(options)
            
            # Calculate semantic diversity among options
            option_similarities = []
            for i in range(len(option_embeddings)):
                for j in range(i+1, len(option_embeddings)):
                    sim = np.dot(option_embeddings[i], option_embeddings[j])
                    option_similarities.append(sim)
            
            semantic_diversity = 1.0 - np.mean(option_similarities) if option_similarities else 0.5
            
            # Calculate question-option semantic alignment
            question_option_similarities = []
            for option_emb in option_embeddings:
                sim = np.dot(question_embedding, option_emb)
                question_option_similarities.append(sim)
            
            semantic_alignment = np.std(question_option_similarities)
            
            # Technical terms detection
            technical_terms = ['algorithm', 'complexity', 'optimization', 'architecture', 
                             'implementation', 'performance', 'scalability', 'distributed',
                             'concurrent', 'asynchronous', 'polymorphism', 'inheritance']
            
            full_text = f"{question_text} {' '.join(options)}".lower()
            technical_density = sum(1 for term in technical_terms if term in full_text) / len(technical_terms)
            
            # Combined complexity score
            complexity_score = (
                semantic_diversity * 0.4 + 
                semantic_alignment * 0.3 + 
                technical_density * 0.3
            )
            
            return {
                'semantic_diversity': float(semantic_diversity.item() if hasattr(semantic_diversity, 'item') else semantic_diversity),
                'semantic_alignment': float(semantic_alignment.item() if hasattr(semantic_alignment, 'item') else semantic_alignment),
                'technical_density': float(technical_density),
                'complexity_score': float(min(complexity_score, 1.0))
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting semantic features: {e}")
            return {
                'semantic_diversity': 0.5,
                'semantic_alignment': 0.5,
                'technical_density': 0.5,
                'complexity_score': 0.5
            }
    
    def _extract_linguistic_features(self, text: str) -> Dict:
        """Extract linguistic complexity features"""
        try:
            words = text.lower().split()
            sentences = text.split('.')
            
            # Average word length
            avg_word_length = np.mean([len(word) for word in words]) if words else 0
            
            # Vocabulary richness (unique words / total words)
            vocab_richness = len(set(words)) / len(words) if words else 0
            
            # Average sentence length
            avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()]) if sentences else 0
            
            # Complex words (>6 characters)
            complex_words = sum(1 for word in words if len(word) > 6)
            complex_word_ratio = complex_words / len(words) if words else 0
            
            # Question complexity indicators
            complexity_indicators = ['implement', 'design', 'analyze', 'evaluate', 'synthesize', 'compare']
            complexity_indicator_count = sum(1 for indicator in complexity_indicators if indicator in text.lower())
            
            # Combined linguistic complexity
            complexity_score = (
                min(avg_word_length / 8, 1.0) * 0.2 +
                vocab_richness * 0.2 +
                min(avg_sentence_length / 20, 1.0) * 0.2 +
                complex_word_ratio * 0.2 +
                min(complexity_indicator_count / 3, 1.0) * 0.2
            )
            
            return {
                'avg_word_length': float(avg_word_length.item() if hasattr(avg_word_length, 'item') else avg_word_length),
                'vocab_richness': float(vocab_richness),
                'avg_sentence_length': float(avg_sentence_length.item() if hasattr(avg_sentence_length, 'item') else avg_sentence_length),
                'complex_word_ratio': float(complex_word_ratio),
                'complexity_indicators': int(complexity_indicator_count),
                'complexity_score': float(complexity_score)
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting linguistic features: {e}")
            return {
                'avg_word_length': 5.0,
                'vocab_richness': 0.7,
                'avg_sentence_length': 10.0,
                'complex_word_ratio': 0.3,
                'complexity_indicators': 1,
                'complexity_score': 0.5
            }
    
    def fine_tune_classifier(self, training_data: List[Dict]) -> Dict:
        """Fine-tune BERT for difficulty classification with training data"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report
            
            # Extract features for all training samples
            features = []
            labels = []
            
            for sample in training_data:
                question_text = sample['question_text']
                options = [sample.get(f'option_{i}', '') for i in ['a', 'b', 'c', 'd']]
                difficulty = sample['difficulty']
                
                # Get BERT-based features
                analysis = self.analyze_question_difficulty(question_text, options)
                
                # Create feature vector
                feature_vector = [
                    analysis['difficulty_score'],
                    analysis['semantic_features']['semantic_diversity'],
                    analysis['semantic_features']['semantic_alignment'],
                    analysis['semantic_features']['technical_density'],
                    analysis['linguistic_features']['avg_word_length'],
                    analysis['linguistic_features']['vocab_richness'],
                    analysis['linguistic_features']['complex_word_ratio'],
                    analysis['text_length'],
                    analysis['vocab_complexity']
                ]
                
                features.append(feature_vector)
                labels.append(difficulty)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            
            # Train classifier
            self.fine_tuned_classifier = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.fine_tuned_classifier.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.fine_tuned_classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.logger.info(f"Fine-tuned classifier accuracy: {accuracy:.3f}")
            
            return {
                'success': True,
                'accuracy': accuracy,
                'training_samples': len(training_data),
                'feature_importance': self.fine_tuned_classifier.feature_importances_.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Error fine-tuning classifier: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_analyze_questions(self, limit: int = None) -> Dict:
        """Enhanced batch analysis with fine-tuned features"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            query = "SELECT id, question_text, option_a, option_b, option_c, option_d FROM question"
            if limit:
                query += f" LIMIT {limit}"

            questions = conn.execute(query).fetchall()

            results = {
                'analyzed': 0,
                'updated': 0,
                'errors': 0,
                'difficulties': {'easy': 0, 'medium': 0, 'hard': 0}
            }

            for question in questions:
                try:
                    options = [question['option_a'], question['option_b'], 
                              question['option_c'], question['option_d']]

                    # Analyze difficulty
                    difficulty_analysis = self.analyze_question_difficulty(
                        question['question_text'], options)

                    # Classify topic
                    topic_analysis = self.classify_question_topic(
                        question['question_text'], options)

                    # Update database with BERT analysis
                    conn.execute("""
                        UPDATE question 
                        SET ai_classified = ?, 
                            difficulty = ?,
                            topic = ?
                        WHERE id = ?
                    """, (
                        json.dumps({
                            'bert_difficulty': difficulty_analysis,
                            'bert_topic': topic_analysis,
                            'analyzed_at': str(datetime.now())
                        }),
                        difficulty_analysis['difficulty'],
                        topic_analysis['topic'],
                        question['id']
                    ))

                    results['analyzed'] += 1
                    results['updated'] += 1
                    results['difficulties'][difficulty_analysis['difficulty']] += 1

                except Exception as e:
                    self.logger.error(f"Error analyzing question {question['id']}: {e}")
                    results['errors'] += 1

            conn.commit()
            conn.close()

            self.logger.info(f"Batch analysis complete: {results}")
            return results

        except Exception as e:
            self.logger.error(f"Error in batch analysis: {e}")
            return {'error': str(e)}

# Utility functions for integration
def initialize_bert_analyzer():
    """Initialize BERT analyzer singleton"""
    global bert_analyzer
    if 'bert_analyzer' not in globals():
        bert_analyzer = BERTQuestionAnalyzer()
    return bert_analyzer

def get_bert_enhanced_questions(user_id: int, num_questions: int = 10) -> List[Dict]:
    """Get BERT-enhanced question selection for user"""
    analyzer = initialize_bert_analyzer()

    # Get user history (implement based on your schema)
    # This is a simplified example
    conn = sqlite3.connect('aptitude_exam.db')
    conn.row_factory = sqlite3.Row

    # Get available questions
    available = conn.execute("""
        SELECT id, question_text, option_a, option_b, option_c, option_d,
               correct_option, topic, difficulty
        FROM question
        ORDER BY RANDOM()
        LIMIT 50
    """).fetchall()

    conn.close()

    # Convert to list of dicts
    available_questions = [dict(q) for q in available]

    # Get user history (placeholder - implement based on your needs)
    user_history = []  # Implement user history retrieval

    # Get BERT-enhanced selection
    enhanced_questions = analyzer.enhance_adaptive_selection(user_history, available_questions)

    return enhanced_questions[:num_questions]

if __name__ == "__main__":
    # Test the BERT analyzer
    analyzer = BERTQuestionAnalyzer()

    # Test question analysis
    test_question = "What is machine learning?"
    test_options = ["Cooking method", "AI technique", "Software tool", "Hardware component"]

    difficulty = analyzer.analyze_question_difficulty(test_question, test_options)
    topic = analyzer.classify_question_topic(test_question, test_options)

    print("BERT Analysis Results:")
    print(f"Difficulty: {difficulty}")
    print(f"Topic: {topic}")

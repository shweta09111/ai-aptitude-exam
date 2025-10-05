#!/usr/bin/env python3
"""
Enhanced AI Difficulty Classifier for Recruitment Questions
Supports both ML-based and rule-based classification
"""

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DifficultyClassifier:
    def __init__(self):
        """Initialize the difficulty classifier with multiple models"""
        self.vectorizer = None
        self.model = None
        self.is_trained = False
        self.models_dir = "models"
        self.model_type = "naive_bayes"  # Options: naive_bayes, logistic, random_forest
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Enhanced rule-based classification keywords
        self.difficulty_keywords = {
            'Hard': {
                'algorithms': ['implement', 'algorithm', 'complexity', 'optimize', 'efficient'],
                'system_design': ['design', 'architecture', 'distributed', 'scalability', 'microservices'],
                'advanced_concepts': ['binary tree', 'hash table', 'dynamic programming', 'recursion'],
                'performance': ['performance', 'load balancer', 'caching', 'indexing'],
                'implementation': ['code', 'program', 'solution', 'build', 'create from scratch']
            },
            'Medium': {
                'concepts': ['explain', 'difference', 'compare', 'how does', 'why is'],
                'oop': ['inheritance', 'polymorphism', 'encapsulation', 'abstraction'],
                'technologies': ['framework', 'library', 'api', 'rest', 'http', 'tcp', 'sql'],
                'processes': ['works', 'process', 'lifecycle', 'workflow', 'mechanism'],
                'theory': ['principle', 'concept', 'theory', 'approach', 'methodology']
            },
            'Easy': {
                'basics': ['what is', 'define', 'syntax', 'basic', 'simple', 'introduction'],
                'fundamentals': ['variable', 'function', 'loop', 'condition', 'array'],
                'operations': ['print', 'input', 'output', 'display', 'read'],
                'definitions': ['meaning', 'definition', 'purpose', 'use', 'advantage'],
                'simple_facts': ['true', 'false', 'yes', 'no', 'which one']
            }
        }
        
        # Try to load existing trained models
        self.load_models()
    
    def _evaluate_model_comprehensive(self, questions: List[str], difficulties: List[str]) -> Dict:
        """Comprehensive model evaluation with multiple metrics"""
        try:
            from sklearn.model_selection import cross_val_score, StratifiedKFold
            from sklearn.metrics import precision_recall_fscore_support, confusion_matrix
            import numpy as np
            
            # Preprocess and vectorize
            processed_questions = [self.preprocess_text(q) for q in questions]
            X = self.vectorizer.transform(processed_questions)
            y = np.array(difficulties)
            
            # Cross-validation with stratification
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            
            # Multiple scoring metrics
            accuracy_scores = cross_val_score(self.model, X, y, cv=cv, scoring='accuracy')
            precision_scores = cross_val_score(self.model, X, y, cv=cv, scoring='precision_macro')
            recall_scores = cross_val_score(self.model, X, y, cv=cv, scoring='recall_macro')
            f1_scores = cross_val_score(self.model, X, y, cv=cv, scoring='f1_macro')
            
            # Train on full data for confusion matrix
            self.model.fit(X, y)
            y_pred = self.model.predict(X)
            
            # Confusion matrix
            cm = confusion_matrix(y, y_pred, labels=['Easy', 'Medium', 'Hard'])
            
            # Per-class metrics
            precision, recall, f1, support = precision_recall_fscore_support(
                y, y_pred, labels=['Easy', 'Medium', 'Hard'], average=None
            )
            
            return {
                'accuracy': float(np.mean(accuracy_scores)),
                'accuracy_std': float(np.std(accuracy_scores)),
                'precision_macro': float(np.mean(precision_scores)),
                'recall_macro': float(np.mean(recall_scores)),
                'f1_macro': float(np.mean(f1_scores)),
                'per_class_metrics': {
                    'Easy': {'precision': float(precision[0]), 'recall': float(recall[0]), 'f1': float(f1[0])},
                    'Medium': {'precision': float(precision[1]), 'recall': float(recall[1]), 'f1': float(f1[1])},
                    'Hard': {'precision': float(precision[2]), 'recall': float(recall[2]), 'f1': float(f1[2])}
                },
                'confusion_matrix': cm.tolist(),
                'training_samples': len(questions)
            }
            
        except Exception as e:
            print(f"Evaluation error: {e}")
            return {'accuracy': 0.0, 'error': str(e)}
    
    def create_ensemble_classifier(self, models: List[str] = None) -> bool:
        """Create an ensemble classifier from multiple models"""
        try:
            from sklearn.ensemble import VotingClassifier
            
            if models is None:
                models = ['naive_bayes', 'logistic', 'random_forest']
            
            # Get training data
            questions, difficulties = self.get_enhanced_training_data()
            
            if len(questions) < 10:
                print("❌ Insufficient training data for ensemble")
                return False
            
            # Create individual classifiers
            classifiers = []
            
            for model_type in models:
                if model_type == 'naive_bayes':
                    clf = MultinomialNB()
                elif model_type == 'logistic':
                    clf = LogisticRegression(max_iter=1000, random_state=42)
                elif model_type == 'random_forest':
                    clf = RandomForestClassifier(n_estimators=100, random_state=42)
                else:
                    continue
                
                classifiers.append((model_type, clf))
            
            if len(classifiers) < 2:
                print("❌ Need at least 2 valid classifiers for ensemble")
                return False
            
            # Create ensemble
            self.model = VotingClassifier(classifiers, voting='soft')
            self.model_type = 'ensemble_' + '_'.join(models)
            
            # Train ensemble
            success = self.train_model(questions, difficulties)
            
            if success:
                print(f"✅ Ensemble classifier created with {len(classifiers)} models")
                return True
            else:
                print("❌ Failed to train ensemble classifier")
                return False
                
        except Exception as e:
            print(f"Ensemble creation error: {e}")
            return False

# Global classifier instance (Singleton pattern)
_classifier_instance = None

def get_difficulty_classifier() -> DifficultyClassifier:
    """Get singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DifficultyClassifier()
    return _classifier_instance
import sqlite3
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DifficultyClassifier:
    def __init__(self):
        """Initialize the difficulty classifier with multiple models"""
        self.vectorizer = None
        self.model = None
        self.is_trained = False
        self.models_dir = "models"
        self.model_type = "naive_bayes"  # Options: naive_bayes, logistic, random_forest
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Enhanced rule-based classification keywords
        self.difficulty_keywords = {
            'Hard': {
                'algorithms': ['implement', 'algorithm', 'complexity', 'optimize', 'efficient'],
                'system_design': ['design', 'architecture', 'distributed', 'scalability', 'microservices'],
                'advanced_concepts': ['binary tree', 'hash table', 'dynamic programming', 'recursion'],
                'performance': ['performance', 'load balancer', 'caching', 'indexing'],
                'implementation': ['code', 'program', 'solution', 'build', 'create from scratch']
            },
            'Medium': {
                'concepts': ['explain', 'difference', 'compare', 'how does', 'why is'],
                'oop': ['inheritance', 'polymorphism', 'encapsulation', 'abstraction'],
                'technologies': ['framework', 'library', 'api', 'rest', 'http', 'tcp', 'sql'],
                'processes': ['works', 'process', 'lifecycle', 'workflow', 'mechanism'],
                'theory': ['principle', 'concept', 'theory', 'approach', 'methodology']
            },
            'Easy': {
                'basics': ['what is', 'define', 'syntax', 'basic', 'simple', 'introduction'],
                'fundamentals': ['variable', 'function', 'loop', 'condition', 'array'],
                'operations': ['print', 'input', 'output', 'display', 'read'],
                'definitions': ['meaning', 'definition', 'purpose', 'use', 'advantage'],
                'simple_facts': ['true', 'false', 'yes', 'no', 'which one']
            }
        }
        
        # Advanced feature patterns
        self.complexity_patterns = {
            'Hard': [
                r'O\([^)]*log[^)]*\)',  # Big O notation with log
                r'O\([^)]*n\^2[^)]*\)',  # O(n^2) complexity
                r'implement.*algorithm',
                r'design.*system',
                r'optimize.*performance'
            ],
            'Medium': [
                r'explain.*difference',
                r'how.*work',
                r'what.*advantage',
                r'compare.*between'
            ],
            'Easy': [
                r'what is.*\?',
                r'define.*',
                r'syntax.*'
            ]
        }
        
        # Try to load existing trained models
        self.load_models()
    
    def load_models(self) -> bool:
        """Load trained models if they exist"""
        vectorizer_path = os.path.join(self.models_dir, f"tfidf_vectorizer_{self.model_type}.pkl")
        model_path = os.path.join(self.models_dir, f"difficulty_model_{self.model_type}.pkl")
        
        try:
            if os.path.exists(vectorizer_path) and os.path.exists(model_path):
                with open(vectorizer_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
                
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                
                self.is_trained = True
                print(f"✅ ML models ({self.model_type}) loaded successfully!")
                return True
        except Exception as e:
            print(f"⚠️ Failed to load ML models: {e}")
        
        return False
    
    def save_models(self) -> bool:
        """Save trained models to disk"""
        try:
            vectorizer_path = os.path.join(self.models_dir, f"tfidf_vectorizer_{self.model_type}.pkl")
            model_path = os.path.join(self.models_dir, f"difficulty_model_{self.model_type}.pkl")
            
            with open(vectorizer_path, "wb") as f:
                pickle.dump(self.vectorizer, f)
            
            with open(model_path, "wb") as f:
                pickle.dump(self.model, f)
            
            print(f"✅ ML models ({self.model_type}) saved successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to save models: {e}")
            return False
    
    def get_training_data_from_db(self) -> Tuple[List[str], List[str]]:
        """Get training data from database"""
        try:
            conn = sqlite3.connect("aptitude_exam.db")
            cursor = conn.cursor()
            cursor.execute("SELECT question_text, difficulty FROM question WHERE difficulty IS NOT NULL AND question_text != ''")
            
            training_data = cursor.fetchall()
            conn.close()
            
            questions = [item[0] for item in training_data if item[0] and item[1]]
            difficulties = [item[1] for item in training_data if item[0] and item[1]]
            
            return questions, difficulties
            
        except Exception as e:
            print(f"⚠️ Database error: {e}")
            return [], []
    
    def get_enhanced_training_data(self) -> Tuple[List[str], List[str]]:
        """Get comprehensive training data including samples"""
        questions, difficulties = self.get_training_data_from_db()
        
        # Enhanced training samples for better classification
        sample_data = [
            # Easy questions (30 samples)
            ("What is a variable in programming?", "Easy"),
            ("How do you print in Python?", "Easy"),
            ("What is a function?", "Easy"),
            ("Define a loop", "Easy"),
            ("What is 2+2?", "Easy"),
            ("What is HTML?", "Easy"),
            ("Define CSS", "Easy"),
            ("What is JavaScript?", "Easy"),
            ("What is Python?", "Easy"),
            ("What is Java?", "Easy"),
            ("What is a database?", "Easy"),
            ("Define SQL", "Easy"),
            ("What is HTTP?", "Easy"),
            ("What is IP address?", "Easy"),
            ("What is URL?", "Easy"),
            ("Define array", "Easy"),
            ("What is string?", "Easy"),
            ("What is integer?", "Easy"),
            ("Define boolean", "Easy"),
            ("What is syntax?", "Easy"),
            ("What is compiler?", "Easy"),
            ("Define interpreter", "Easy"),
            ("What is IDE?", "Easy"),
            ("What is debugging?", "Easy"),
            ("Define comment", "Easy"),
            ("What is variable declaration?", "Easy"),
            ("What is assignment operator?", "Easy"),
            ("Define constant", "Easy"),
            ("What is data type?", "Easy"),
            ("What is keyword?", "Easy"),
            
            # Medium questions (30 samples)
            ("Explain object-oriented programming", "Medium"),
            ("What is the difference between list and tuple?", "Medium"),
            ("How does inheritance work?", "Medium"),
            ("What are design patterns?", "Medium"),
            ("Explain HTTP vs HTTPS", "Medium"),
            ("How does garbage collection work?", "Medium"),
            ("What is polymorphism in programming?", "Medium"),
            ("Explain the difference between GET and POST", "Medium"),
            ("How does database normalization work?", "Medium"),
            ("What is the difference between SQL and NoSQL?", "Medium"),
            ("Explain MVC architecture", "Medium"),
            ("How does REST API work?", "Medium"),
            ("What is the difference between stack and queue?", "Medium"),
            ("Explain binary search algorithm", "Medium"),
            ("How does hashing work?", "Medium"),
            ("What is the difference between process and thread?", "Medium"),
            ("Explain TCP vs UDP", "Medium"),
            ("How does DNS work?", "Medium"),
            ("What is the difference between abstract class and interface?", "Medium"),
            ("Explain dependency injection", "Medium"),
            ("How does session management work?", "Medium"),
            ("What is the difference between authentication and authorization?", "Medium"),
            ("Explain synchronous vs asynchronous programming", "Medium"),
            ("How does load balancing work?", "Medium"),
            ("What is the difference between monolithic and microservices?", "Medium"),
            ("Explain database indexing", "Medium"),
            ("How does caching work?", "Medium"),
            ("What is the difference between SQL joins?", "Medium"),
            ("Explain exception handling", "Medium"),
            ("How does memory management work?", "Medium"),
            
            # Hard questions (30 samples)
            ("Implement a binary search algorithm", "Hard"),
            ("Design a distributed system architecture", "Hard"),
            ("Optimize database query performance", "Hard"),
            ("What are the principles of SOLID design?", "Hard"),
            ("Explain microservices architecture", "Hard"),
            ("How to design a load balancer?", "Hard"),
            ("Implement a hash table with collision handling", "Hard"),
            ("What is the time complexity of quicksort?", "Hard"),
            ("Design a scalable chat system", "Hard"),
            ("Implement dynamic programming solution", "Hard"),
            ("Design a URL shortener like bit.ly", "Hard"),
            ("Implement a LRU cache", "Hard"),
            ("Design a distributed file system", "Hard"),
            ("Optimize system for 1 million concurrent users", "Hard"),
            ("Implement graph algorithms like Dijkstra", "Hard"),
            ("Design a recommendation system", "Hard"),
            ("Implement consistent hashing", "Hard"),
            ("Design a rate limiting system", "Hard"),
            ("Implement MapReduce algorithm", "Hard"),
            ("Design a distributed database", "Hard"),
            ("Optimize memory usage for large datasets", "Hard"),
            ("Implement advanced data structures", "Hard"),
            ("Design fault-tolerant systems", "Hard"),
            ("Implement machine learning algorithms", "Hard"),
            ("Design high-availability architecture", "Hard"),
            ("Implement complex sorting algorithms", "Hard"),
            ("Design real-time data processing system", "Hard"),
            ("Optimize network protocols", "Hard"),
            ("Implement advanced security measures", "Hard"),
            ("Design blockchain architecture", "Hard")
        ]
        
        # Add sample data to training set
        for question, difficulty in sample_data:
            questions.append(question)
            difficulties.append(difficulty)
        
        return questions, difficulties
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better feature extraction"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\?\.\-\(\)]', ' ', text)
        
        # Normalize question patterns
        text = re.sub(r'what\s+is\s+the\s+difference\s+between', 'difference between', text)
        text = re.sub(r'how\s+do\s+you', 'how', text)
        text = re.sub(r'what\s+is\s+a', 'what is', text)
        
        return text
    
    def extract_features(self, questions: List[str]) -> Dict[str, List[float]]:
        """Extract advanced features from questions"""
        features = {
            'length': [],
            'complexity_score': [],
            'question_type_score': [],
            'technical_depth_score': []
        }
        
        for question in questions:
            processed_text = self.preprocess_text(question)
            
            # Length feature
            features['length'].append(len(processed_text.split()))
            
            # Complexity score based on keywords
            complexity_score = 0
            for difficulty, categories in self.difficulty_keywords.items():
                weight = 3 if difficulty == 'Hard' else 2 if difficulty == 'Medium' else 1
                for category, keywords in categories.items():
                    for keyword in keywords:
                        if keyword in processed_text:
                            complexity_score += weight
            features['complexity_score'].append(complexity_score)
            
            # Question type score
            question_words = ['what', 'how', 'why', 'when', 'where', 'which', 'explain', 'implement', 'design']
            type_score = sum(1 for word in question_words if word in processed_text)
            features['question_type_score'].append(type_score)
            
            # Technical depth score
            technical_terms = ['algorithm', 'complexity', 'optimization', 'architecture', 'system', 'database', 'network']
            depth_score = sum(1 for term in technical_terms if term in processed_text)
            features['technical_depth_score'].append(depth_score)
        
        return features
    
    def train_model(self, questions: List[str], difficulties: List[str]) -> bool:
        """Train the ML model with given data"""
        try:
            if len(questions) < 10:
                print("❌ Insufficient training data")
                return False
            
            print(f"🤖 Training {self.model_type} model with {len(questions)} questions")
            print(f"📊 Distribution: Easy={difficulties.count('Easy')}, Medium={difficulties.count('Medium')}, Hard={difficulties.count('Hard')}")
            
            # Preprocess questions
            processed_questions = [self.preprocess_text(q) for q in questions]
            
            # Create TF-IDF vectorizer with advanced features
            self.vectorizer = TfidfVectorizer(
                max_features=2000,
                stop_words='english',
                ngram_range=(1, 3),  # Include trigrams
                min_df=1,
                max_df=0.95,
                sublinear_tf=True
            )
            
            # Fit vectorizer and transform questions
            X = self.vectorizer.fit_transform(processed_questions)
            
            # Create and train model based on type
            if self.model_type == "naive_bayes":
                self.model = MultinomialNB(alpha=0.1)
            elif self.model_type == "logistic":
                self.model = LogisticRegression(
                    max_iter=1000,
                    C=1.0,
                    random_state=42,
                    multi_class='multinomial'
                )
            elif self.model_type == "random_forest":
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    max_depth=10
                )
            else:
                self.model = MultinomialNB(alpha=0.1)  # Default fallback
            
            # Train the model
            self.model.fit(X, difficulties)
            
            # Evaluate model performance
            if len(questions) > 10:
                scores = cross_val_score(self.model, X, difficulties, cv=min(5, len(questions)//2))
                print(f"🎯 Cross-validation accuracy: {scores.mean():.2%} (+/- {scores.std() * 2:.2%})")
            
            # Test on training data
            y_pred = self.model.predict(X)
            accuracy = accuracy_score(difficulties, y_pred)
            print(f"📈 Training accuracy: {accuracy:.2%}")
            
            # Save models
            self.save_models()
            self.is_trained = True
            
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            return False
    
    def train_from_database(self) -> bool:
        """Train model using current database questions"""
        questions, difficulties = self.get_enhanced_training_data()
        
        if not questions:
            print("❌ No training data available")
            return False
        
        return self.train_model(questions, difficulties)
    
    def predict(self, question_text: str) -> Dict:
        """Predict difficulty of a question using ML or rule-based approach"""
        try:
            if self.is_trained and self.vectorizer and self.model:
                # Use trained ML model
                processed_text = self.preprocess_text(question_text)
                X = self.vectorizer.transform([processed_text])
                
                prediction = self.model.predict(X)[0]
                probabilities = self.model.predict_proba(X)[0]
                
                # Get confidence (highest probability)
                confidence = max(probabilities)
                
                # Create probability dictionary
                prob_dict = {
                    class_name: float(prob) 
                    for class_name, prob in zip(self.model.classes_, probabilities)
                }
                
                return {
                    'difficulty': prediction,
                    'confidence': float(confidence),
                    'probabilities': prob_dict,
                    'method': f'ml_model_{self.model_type}'
                }
            else:
                raise Exception("Model not trained")
                
        except Exception as e:
            print(f"⚠️ ML prediction failed: {e}, falling back to rule-based")
            return self._rule_based_prediction(question_text)
    
    def _rule_based_prediction(self, question_text: str) -> Dict:
        """Advanced rule-based difficulty prediction"""
        text_lower = self.preprocess_text(question_text)
        
        # Initialize scores
        scores = {'Easy': 0, 'Medium': 0, 'Hard': 0}
        
        # Keyword-based scoring
        for difficulty, categories in self.difficulty_keywords.items():
            for category, keywords in categories.items():
                category_score = 0
                for keyword in keywords:
                    if keyword in text_lower:
                        category_score += 1
                
                # Weight categories differently
                if category in ['algorithms', 'system_design', 'implementation']:
                    category_score *= 2  # Higher weight for technical categories
                
                scores[difficulty] += category_score
        
        # Pattern-based scoring
        for difficulty, patterns in self.complexity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    scores[difficulty] += 2
        
        # Length-based heuristics
        word_count = len(text_lower.split())
        if word_count > 15:
            scores['Hard'] += 1
        elif word_count > 8:
            scores['Medium'] += 1
        else:
            scores['Easy'] += 1
        
        # Determine difficulty based on highest score
        predicted_difficulty = max(scores, key=scores.get)
        
        # Calculate confidence based on score difference
        max_score = max(scores.values())
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        # Normalize probabilities
        if total_score > 0:
            probabilities = {k: v/total_score for k, v in scores.items()}
        else:
            probabilities = {'Easy': 0.33, 'Medium': 0.33, 'Hard': 0.34}
        
        return {
            'difficulty': predicted_difficulty,
            'confidence': float(min(confidence + 0.25, 0.95)),  # Boost confidence slightly
            'probabilities': probabilities,
            'method': 'rule_based_enhanced'
        }
    
    def retrain_and_improve(self) -> bool:
        """Retrain model with latest data and improved features"""
        print("🔄 Retraining ML model with latest data...")
        return self.train_from_database()
    
    def switch_model_type(self, model_type: str) -> bool:
        """Switch to different ML model type"""
        if model_type not in ["naive_bayes", "logistic", "random_forest"]:
            print(f"❌ Invalid model type: {model_type}")
            return False
        
        self.model_type = model_type
        self.is_trained = False
        self.model = None
        self.vectorizer = None
        
        # Try to load existing model of this type
        if not self.load_models():
            # Train new model
            return self.train_from_database()
        
        return True
    
    def get_model_info(self) -> Dict:
        """Get information about current model"""
        return {
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'has_vectorizer': self.vectorizer is not None,
            'has_model': self.model is not None,
            'classes': self.model.classes_.tolist() if self.model and hasattr(self.model, 'classes_') else None
        }
    
    def benchmark_models(self) -> Dict[str, float]:
        """Benchmark different model types"""
        questions, difficulties = self.get_enhanced_training_data()
        
        if len(questions) < 20:
            print("❌ Insufficient data for benchmarking")
            return {}
        
        results = {}
        model_types = ["naive_bayes", "logistic", "random_forest"]
        
        print("🏁 Benchmarking different model types...")
        
        for model_type in model_types:
            try:
                # Temporarily switch model type
                original_type = self.model_type
                self.model_type = model_type
                
                # Train model
                if self.train_model(questions, difficulties):
                    # Test accuracy
                    processed_questions = [self.preprocess_text(q) for q in questions]
                    X = self.vectorizer.fit_transform(processed_questions)
                    scores = cross_val_score(self.model, X, difficulties, cv=3)
                    results[model_type] = scores.mean()
                
                # Restore original type
                self.model_type = original_type
                
            except Exception as e:
                print(f"⚠️ Benchmarking failed for {model_type}: {e}")
                results[model_type] = 0.0
        
        print("📊 Benchmark Results:")
        for model_type, accuracy in results.items():
            print(f"  {model_type}: {accuracy:.2%}")
        
        return results


# Global classifier instance (Singleton pattern)
_classifier_instance = None

def get_difficulty_classifier() -> DifficultyClassifier:
    """Get singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DifficultyClassifier()
        if not _classifier_instance.is_trained:
            print("🤖 Training ML model for first time...")
            _classifier_instance.train_from_database()
    return _classifier_instance

def reset_classifier():
    """Reset classifier instance (for testing)"""
    global _classifier_instance
    _classifier_instance = None


# Test and demonstration
if __name__ == "__main__":
    print("🧪 Testing Enhanced Difficulty Classifier")
    print("=" * 60)
    
    # Get classifier instance
    classifier = get_difficulty_classifier()
    
    # Display model information
    info = classifier.get_model_info()
    print(f"📊 Model Info: {info}")
    
    # Test questions across all difficulty levels
    test_questions = [
        # Easy questions
        "What is a variable?",
        "How do you print in Python?",
        "What is HTML?",
        "Define CSS",
        
        # Medium questions
        "Explain inheritance in OOP",
        "What is the difference between HTTP and HTTPS?",
        "How does database normalization work?",
        "Explain REST API principles",
        
        # Hard questions
        "Implement a balanced binary tree",
        "Design a distributed system for 1 million users",
        "Optimize database query performance for large datasets",
        "What is the time complexity of quicksort algorithm?"
    ]
    
    print(f"\n🔍 Testing {len(test_questions)} questions:")
    print("-" * 60)
    
    for i, question in enumerate(test_questions, 1):
        result = classifier.predict(question)
        print(f"{i:2d}. '{question[:50]}{'...' if len(question) > 50 else ''}'")
        print(f"    🎯 Difficulty: {result['difficulty']} (confidence: {result['confidence']:.1%})")
        print(f"    🔧 Method: {result['method']}")
        
        # Show probabilities for ML predictions
        if 'ml_model' in result['method']:
            probs = result['probabilities']
            print(f"    📊 Probabilities: Easy={probs.get('Easy', 0):.1%}, Medium={probs.get('Medium', 0):.1%}, Hard={probs.get('Hard', 0):.1%}")
        print()
    
    # Benchmark different models if enough data
    print("🏁 Running model benchmark...")
    benchmarks = classifier.benchmark_models()
    
    if benchmarks:
        best_model = max(benchmarks, key=benchmarks.get)
        print(f"🏆 Best model: {best_model} ({benchmarks[best_model]:.2%} accuracy)")
        
        # Switch to best model
        if classifier.switch_model_type(best_model):
            print(f"✅ Switched to {best_model} model")
        else:
            print(f"❌ Failed to switch to {best_model} model")
    
    print(f"\n✅ Enhanced Difficulty Classifier testing completed!")
    print(f"💡 Ready for production use in recruitment platform!")

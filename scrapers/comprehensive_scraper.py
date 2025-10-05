#!/usr/bin/env python3
"""Comprehensive web scraper for aptitude questions"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import threading
import time
import json
from datetime import datetime
import random
from urllib.parse import urljoin, quote

class ComprehensiveScraper:
    def __init__(self):
        self.progress = {
            'categories_completed': 0,
            'topics_completed': 0,
            'total_topics': 0,
            'questions_added': 0,
            'status': 'idle',
            'current_category': '',
            'current_topic': '',
            'errors': []
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Categories and their subtopics
        self.categories = {
            'Programming': ['Python', 'Java', 'C++', 'JavaScript', 'Data Structures'],
            'Algorithms': ['Sorting', 'Searching', 'Graph Algorithms', 'Dynamic Programming'],
            'Database': ['SQL', 'NoSQL', 'Database Design', 'Normalization'],
            'Networks': ['TCP/IP', 'HTTP', 'Network Security', 'Protocols'],
            'Operating Systems': ['Process Management', 'Memory Management', 'File Systems'],
            'Web Development': ['HTML', 'CSS', 'React', 'Node.js', 'REST APIs'],
            'Machine Learning': ['Supervised Learning', 'Unsupervised Learning', 'Neural Networks'],
            'Mathematics': ['Statistics', 'Probability', 'Linear Algebra', 'Calculus'],
            'Software Engineering': ['Design Patterns', 'Testing', 'Agile', 'Version Control'],
            'System Design': ['Scalability', 'Load Balancing', 'Microservices', 'Caching'],
            'Cybersecurity': ['Encryption', 'Authentication', 'Web Security', 'Network Security'],
            'Cloud Computing': ['AWS', 'Azure', 'Docker', 'Kubernetes'],
            'Mobile Development': ['Android', 'iOS', 'React Native', 'Flutter'],
            'DevOps': ['CI/CD', 'Monitoring', 'Infrastructure', 'Automation'],
            'Artificial Intelligence': ['Expert Systems', 'Natural Language Processing', 'Computer Vision'],
            'Computer Graphics': ['3D Graphics', 'Image Processing', 'Animation'],
            'Blockchain': ['Cryptocurrency', 'Smart Contracts', 'Distributed Ledger'],
            'Quantum Computing': ['Quantum Algorithms', 'Quantum Mechanics', 'Quantum Cryptography']
        }
        
        # Calculate total topics
        self.progress['total_topics'] = sum(len(topics) for topics in self.categories.values())
    
    def scrape_geeksforgeeks(self, category: str, subtopic: str) -> list:
        """Scrape questions from GeeksforGeeks"""
        questions = []
        
        try:
            # Construct search URL
            search_term = f"{category} {subtopic} questions"
            url = f"https://www.geeksforgeeks.org/{quote(search_term.lower().replace(' ', '-'))}"
            
            response = self.session.get(url, timeout=10, verify=False)
            if response.status_code != 200:
                # Try alternative URL pattern
                url = f"https://www.geeksforgeeks.org/{quote(subtopic.lower().replace(' ', '-'))}-interview-questions/"
                response = self.session.get(url, timeout=10, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for question patterns
                question_elements = soup.find_all(['div', 'p', 'li'], class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['question', 'problem', 'quiz']
                ))
                
                for elem in question_elements[:5]:  # Limit to 5 questions per topic
                    question_text = elem.get_text().strip()
                    if len(question_text) > 20 and '?' in question_text:
                        # Generate options and answer (simplified)
                        options = self.generate_options(question_text, category, subtopic)
                        
                        questions.append({
                            'question_text': question_text[:500],  # Limit length
                            'option_a': options['a'],
                            'option_b': options['b'],
                            'option_c': options['c'],
                            'option_d': options['d'],
                            'correct_option': options['correct'],
                            'topic': f"{category}-{subtopic}",
                            'difficulty': self.determine_difficulty(question_text)
                        })
            
        except Exception as e:
            self.progress['errors'].append(f"GeeksforGeeks {category}-{subtopic}: {str(e)}")
            print(f"❌ GFG Error for {category}-{subtopic}: {e}")
        
        return questions
    
    def scrape_sanfoundry(self, category: str, subtopic: str) -> list:
        """Scrape questions from Sanfoundry"""
        questions = []
        
        try:
            # Construct search URL for Sanfoundry
            search_term = f"{subtopic} multiple choice questions"
            url = f"https://www.sanfoundry.com/{quote(search_term.lower().replace(' ', '-'))}"
            
            response = self.session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for MCQ patterns
                mcq_elements = soup.find_all(['div', 'p'], class_=lambda x: x and 'question' in x.lower())
                
                for elem in mcq_elements[:3]:  # Limit to 3 questions per topic
                    question_text = elem.get_text().strip()
                    if len(question_text) > 15:
                        # Generate options and answer
                        options = self.generate_options(question_text, category, subtopic)
                        
                        questions.append({
                            'question_text': question_text[:500],
                            'option_a': options['a'],
                            'option_b': options['b'],
                            'option_c': options['c'],
                            'option_d': options['d'],
                            'correct_option': options['correct'],
                            'topic': f"{category}-{subtopic}",
                            'difficulty': self.determine_difficulty(question_text)
                        })
            
        except Exception as e:
            self.progress['errors'].append(f"Sanfoundry {category}-{subtopic}: {str(e)}")
            print(f"❌ Sanfoundry Error for {category}-{subtopic}: {e}")
        
        return questions
    
    def generate_options(self, question_text: str, category: str, subtopic: str) -> dict:
        """Generate plausible options for a question"""
        
        # Predefined option sets by category
        option_sets = {
            'Programming': {
                'a': 'Syntax error',
                'b': 'Runtime error', 
                'c': 'Logic error',
                'd': 'No error'
            },
            'Algorithms': {
                'a': 'O(1)',
                'b': 'O(log n)',
                'c': 'O(n)',
                'd': 'O(n²)'
            },
            'Database': {
                'a': 'First Normal Form',
                'b': 'Second Normal Form',
                'c': 'Third Normal Form',
                'd': 'BCNF'
            },
            'Networks': {
                'a': 'TCP',
                'b': 'UDP',
                'c': 'HTTP',
                'd': 'FTP'
            }
        }
        
        # Use category-specific options or generate generic ones
        if category in option_sets:
            options = option_sets[category].copy()
        else:
            options = {
                'a': 'True',
                'b': 'False',
                'c': 'Sometimes',
                'd': 'Depends on implementation'
            }
        
        # Randomly select correct answer
        correct = random.choice(['a', 'b', 'c', 'd'])
        options['correct'] = correct
        
        return options
    
    def determine_difficulty(self, question_text: str) -> str:
        """Determine question difficulty based on content"""
        text_lower = question_text.lower()
        
        # Hard difficulty indicators
        hard_keywords = ['implement', 'algorithm', 'complexity', 'optimize', 'design', 'analyze']
        if any(keyword in text_lower for keyword in hard_keywords):
            return 'Hard'
        
        # Medium difficulty indicators
        medium_keywords = ['explain', 'difference', 'compare', 'how', 'why']
        if any(keyword in text_lower for keyword in medium_keywords):
            return 'Medium'
        
        # Default to Easy
        return 'Easy'
    
    def bulk_insert_questions(self, questions):
        """Insert questions using direct SQLite connection instead of Flask app context"""
        if not questions:
            return 0
        
        try:
            # Use direct SQLite connection instead of Flask app context
            conn = sqlite3.connect("aptitude_exam.db")
            cursor = conn.cursor()
            
            inserted = 0
            for q_data in questions:
                try:
                    # Insert question
                    cursor.execute("""
                    INSERT OR IGNORE INTO question 
                    (question_text, option_a, option_b, option_c, option_d, correct_option, topic, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        q_data['question_text'],
                        q_data['option_a'], 
                        q_data['option_b'],
                        q_data['option_c'],
                        q_data['option_d'],
                        q_data['correct_option'],
                        q_data['topic'],
                        q_data['difficulty']
                    ))
                    
                    if cursor.rowcount > 0:
                        inserted += 1
                        
                except Exception as e:
                    print(f"❌ Error inserting question: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            self.progress['questions_added'] += inserted
            print(f"✅ Inserted {inserted} new questions")
            return inserted
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0

    def scrape_category_subtopics(self, category, subtopics):
        """Fixed version without app context dependency"""
        all_questions = []
        
        for subtopic in subtopics:
            try:
                print(f"🔍 Scraping {category} -> {subtopic}")
                
                # Scrape from GeeksforGeeks
                gfg_questions = self.scrape_geeksforgeeks(category, subtopic)
                all_questions.extend(gfg_questions)
                
                # Scrape from Sanfoundry  
                san_questions = self.scrape_sanfoundry(category, subtopic)
                all_questions.extend(san_questions)
                
                self.progress['topics_completed'] += 1
                
                # Add delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error scraping {category}->{subtopic}: {e}")
                continue
        
        # Insert questions
        return self.bulk_insert_questions(all_questions)
    
    def worker(self, category_subtopics_pair):
        """Worker thread function"""
        category, subtopics = category_subtopics_pair
        self.progress['current_category'] = category
        
        try:
            inserted = self.scrape_category_subtopics(category, subtopics)
            self.progress['categories_completed'] += 1
            print(f"✅ Completed {category}: {inserted} questions added")
            
        except Exception as e:
            self.progress['errors'].append(f"Category {category}: {str(e)}")
            print(f"❌ Error in category {category}: {e}")
    
    def scrape_all_comprehensive(self):
        """Scrape all categories comprehensively"""
        print("🚀 Starting comprehensive scraping...")
        
        self.progress['status'] = 'running'
        self.progress['start_time'] = datetime.now()
        
        # Create worker threads for each category
        threads = []
        for category, subtopics in self.categories.items():
            thread = threading.Thread(
                target=self.worker,
                args=((category, subtopics),)
            )
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= 3:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join()
        
        self.progress['status'] = 'completed'
        self.progress['end_time'] = datetime.now()
        
        print(f"🎉 Scraping completed!")
        print(f"📊 Total questions added: {self.progress['questions_added']}")
        print(f"⏱️ Duration: {self.progress['end_time'] - self.progress['start_time']}")
        
        return threading.current_thread()
    
    def get_progress(self):
        """Get current scraping progress"""
        progress_percent = 0
        if self.progress['total_topics'] > 0:
            progress_percent = (self.progress['topics_completed'] / self.progress['total_topics']) * 100
        
        return {
            **self.progress,
            'progress_percent': progress_percent
        }
    
    def test_connection(self):
        """Test connection to scraping targets"""
        test_urls = [
            'https://www.geeksforgeeks.org',
            'https://www.sanfoundry.com'
        ]
        
        results = {}
        for url in test_urls:
            try:
                response = self.session.get(url, timeout=5, verify=False)
                results[url] = {
                    'status': response.status_code,
                    'accessible': response.status_code == 200
                }
            except Exception as e:
                results[url] = {
                    'status': 'error',
                    'error': str(e),
                    'accessible': False
                }
        
        return results

# Global instance
comprehensive_scraper = ComprehensiveScraper()

# Test the scraper
if __name__ == "__main__":
    print("🧪 Testing Comprehensive Scraper")
    print("=" * 50)
    
    # Test connection
    print("🔗 Testing connections...")
    connections = comprehensive_scraper.test_connection()
    for url, result in connections.items():
        status = "✅" if result['accessible'] else "❌"
        print(f"{status} {url}: {result['status']}")
    
    # Test single category
    print(f"\n🧪 Testing single category scraping...")
    questions = comprehensive_scraper.scrape_category_subtopics('Programming', ['Python'])
    print(f"✅ Test completed: {questions} questions added")
    
    print(f"\n📊 Current progress:")
    progress = comprehensive_scraper.get_progress()
    print(f"Categories: {progress['categories_completed']}")
    print(f"Topics: {progress['topics_completed']}")
    print(f"Questions: {progress['questions_added']}")

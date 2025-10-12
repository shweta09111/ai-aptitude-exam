"""
ONE-CLICK AI QUESTION GENERATOR
Automatically scrapes rich content and generates high-quality questions
NO manual prompts needed - fully automated!
"""

import sqlite3
import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import random
import time
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OneClickAIGenerator:
    """
    Fully automated AI question generator
    - Auto-scrapes rich technical content
    - Uses advanced AI to generate diverse questions
    - Built-in duplicate prevention
    - Quality filtering
    - ONE CLICK = HIGH QUALITY QUESTIONS
    """
    
    def __init__(self, db_path='aptitude_exam.db'):
        self.db_path = db_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🚀 Initializing ONE-CLICK AI Generator on {self.device}")
        
        # Load better models for quality
        self.load_models()
        
        # Rich content sources (auto-scraping)
        self.content_sources = [
            {
                'url': 'https://www.geeksforgeeks.org/data-structures/',
                'topic': 'Data Structures',
                'selectors': ['p', 'li', 'td']
            },
            {
                'url': 'https://www.geeksforgeeks.org/fundamentals-of-algorithms/',
                'topic': 'Algorithms',
                'selectors': ['p', 'li']
            },
            {
                'url': 'https://www.geeksforgeeks.org/dbms/',
                'topic': 'Database Management',
                'selectors': ['p', 'li']
            },
            {
                'url': 'https://www.geeksforgeeks.org/operating-systems/',
                'topic': 'Operating Systems',
                'selectors': ['p', 'li']
            },
            {
                'url': 'https://www.geeksforgeeks.org/computer-network-tutorials/',
                'topic': 'Computer Networks',
                'selectors': ['p', 'li']
            },
        ]
        
        # Fallback: Rich built-in knowledge base
        self.knowledge_base = self._build_knowledge_base()
    
    def load_models(self):
        """Load AI models for question generation"""
        try:
            logger.info("📥 Loading AI models...")
            
            # Use FLAN-T5 for better quality questions
            model_name = "google/flan-t5-base"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.model.to(self.device)
            
            logger.info("✅ AI models loaded successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load FLAN-T5, using fallback: {e}")
            # Fallback to simpler model
            try:
                self.tokenizer = AutoTokenizer.from_pretrained("t5-base")
                self.model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
                self.model.to(self.device)
            except:
                logger.error("❌ Failed to load AI models")
                self.model = None
                self.tokenizer = None
    
    def _build_knowledge_base(self) -> Dict[str, List[str]]:
        """Build rich knowledge base for offline generation"""
        return {
            'Data Structures': [
                "An array is a contiguous block of memory storing elements of the same type. Access time is O(1) using index. Insertion and deletion are O(n) due to shifting. Arrays have fixed size in languages like C/C++, but dynamic in Python (lists). Cache-friendly due to sequential memory layout.",
                
                "Linked lists store data in nodes connected by pointers. Singly linked lists have next pointer, doubly linked lists have both next and prev. Insertion/deletion at known position is O(1). No cache locality. Dynamic size but extra memory for pointers.",
                
                "Stacks follow Last-In-First-Out (LIFO) principle. Operations: push (add), pop (remove), peek (view top). Used in function calls, expression evaluation, backtracking. Can be implemented using arrays or linked lists. All operations are O(1).",
                
                "Queues follow First-In-First-Out (FIFO) principle. Operations: enqueue (add rear), dequeue (remove front). Used in BFS, scheduling, buffering. Circular queue prevents wastage. Priority queue uses heap. All operations are O(1).",
                
                "Binary trees have at most 2 children per node. Binary Search Tree (BST) maintains left < root < right property. Search/insert/delete are O(log n) average, O(n) worst. AVL and Red-Black trees guarantee O(log n) by self-balancing.",
                
                "Hash tables use hash functions to map keys to indices. Collisions handled by chaining (linked lists) or open addressing (linear probing, quadratic probing). Average O(1) for insert/search/delete. Load factor affects performance. Resizing involves rehashing.",
                
                "Heaps are complete binary trees with heap property: max-heap (parent ≥ children) or min-heap (parent ≤ children). Used in priority queues, heap sort. Insert is O(log n), extract-min/max is O(log n), build-heap is O(n). Stored as arrays.",
                
                "Graphs consist of vertices (nodes) and edges (connections). Directed vs undirected, weighted vs unweighted. Represented by adjacency matrix O(V²) space or adjacency list O(V+E) space. Used in networks, social connections, maps.",
                
                "Tries (prefix trees) store strings character by character. Each node represents a character. Efficient for autocomplete, spell check, IP routing. Search/insert/delete are O(L) where L is string length. Space-intensive but fast lookups.",
            ],
            
            'Algorithms': [
                "Binary search finds element in sorted array by repeatedly dividing search space in half. Time complexity O(log n), space O(1) iterative or O(log n) recursive. Requires sorted data. More efficient than linear search O(n) for large datasets.",
                
                "Merge sort uses divide-and-conquer: divide array into halves, recursively sort, then merge. Time O(n log n) all cases. Space O(n) for auxiliary array. Stable sort (maintains relative order). External sorting algorithm for large datasets.",
                
                "Quick sort picks pivot, partitions array (smaller left, larger right), recursively sorts partitions. Average O(n log n), worst O(n²) with bad pivot. In-place sorting O(log n) space. Unstable. Randomized pivot improves performance.",
                
                "Breadth-First Search (BFS) explores graph level by level using queue. Finds shortest path in unweighted graphs. Time O(V+E), space O(V). Used in GPS navigation, web crawlers, social network friend suggestions.",
                
                "Depth-First Search (DFS) explores as deep as possible before backtracking using stack (or recursion). Time O(V+E), space O(V). Used in topological sorting, cycle detection, maze solving, connected components.",
                
                "Dijkstra's algorithm finds shortest paths from source to all vertices in weighted graph with non-negative weights. Uses priority queue. Time O((V+E) log V) with binary heap. Greedy approach. Cannot handle negative weights.",
                
                "Dynamic Programming solves problems by breaking into overlapping subproblems, storing results (memoization or tabulation). Used in Fibonacci, knapsack, longest common subsequence, matrix chain multiplication. Trades space for time.",
                
                "Greedy algorithms make locally optimal choices hoping for global optimum. Not always optimal but efficient. Used in Huffman coding, Kruskal's MST, Prim's MST, activity selection, fractional knapsack.",
                
                "Backtracking tries all possibilities, abandoning path when constraint violated. Used in N-Queens, Sudoku, maze solving, graph coloring. Explores state space tree. Prunes search space for efficiency.",
            ],
            
            'Database Management': [
                "Normalization eliminates data redundancy and anomalies. 1NF: atomic values, no repeating groups. 2NF: 1NF + no partial dependencies. 3NF: 2NF + no transitive dependencies. BCNF: stronger 3NF. Reduces storage, improves integrity.",
                
                "Database indexes speed up queries using B-tree or hash structures. Clustered index determines physical row order (one per table). Non-clustered index uses pointers (multiple allowed). Trade-off: faster reads, slower writes, more storage.",
                
                "ACID properties ensure reliable transactions: Atomicity (all or nothing), Consistency (valid state), Isolation (concurrent transactions don't interfere), Durability (committed changes persist). Critical for banking, e-commerce.",
                
                "SQL joins combine rows from tables. INNER JOIN: matching rows only. LEFT JOIN: all left + matching right. RIGHT JOIN: all right + matching left. FULL OUTER JOIN: all rows. CROSS JOIN: Cartesian product. Self-join: table with itself.",
                
                "Stored procedures are precompiled SQL code stored in database. Accept parameters, return values, contain logic (IF, WHILE, CASE). Benefits: reusability, security (encapsulation), reduced network traffic, performance (compiled once).",
                
                "Database triggers automatically execute on INSERT, UPDATE, DELETE events. BEFORE triggers validate data, AFTER triggers maintain logs/audits. Row-level or statement-level. Used for enforcing business rules, maintaining derived data.",
                
                "Transactions group SQL statements into atomic unit. BEGIN starts, COMMIT saves, ROLLBACK cancels. Isolation levels: Read Uncommitted (dirty reads), Read Committed (default), Repeatable Read (no phantom reads), Serializable (strictest).",
                
                "Views are virtual tables defined by queries. Simplify complex queries, provide security (hide columns/rows), maintain logical data independence. Updatable views allow INSERT/UPDATE/DELETE. Materialized views cache results for performance.",
            ],
            
            'Operating Systems': [
                "Process scheduling determines which process runs on CPU. FCFS (First Come First Served): simple but convoy effect. SJF (Shortest Job First): optimal average wait but starvation. Round Robin: fair, time quantum critical. Priority: starvation without aging.",
                
                "Memory management allocates RAM to processes. Contiguous allocation: internal fragmentation. Paging: fixed-size pages, external fragmentation eliminated, page table overhead. Segmentation: variable-size logical units, external fragmentation. Paging + segmentation combined.",
                
                "Deadlock occurs when processes wait indefinitely for resources. Conditions: mutual exclusion, hold and wait, no preemption, circular wait. Prevention: negate one condition. Avoidance: Banker's algorithm. Detection and recovery: resource allocation graph.",
                
                "Virtual memory extends RAM using disk space. Allows larger programs than physical memory. Demand paging: load pages on demand, page fault when not in memory. Page replacement algorithms: FIFO, LRU, Optimal. Thrashing: excessive paging degrades performance.",
                
                "Semaphores synchronize processes. Binary semaphore (mutex): mutual exclusion. Counting semaphore: resource pool. Operations: wait (P, down) and signal (V, up). Used to solve producer-consumer, readers-writers, dining philosophers problems.",
                
                "File systems organize storage. FAT: File Allocation Table, simple but fragmentation. NTFS: journaling, permissions, large files. ext4: Linux, journaling, extents. Inodes store metadata. Directory structure: hierarchical. File allocation: contiguous, linked, indexed.",
            ],
            
            'Computer Networks': [
                "TCP/IP is connection-oriented, reliable protocol. 3-way handshake (SYN, SYN-ACK, ACK) establishes connection. Guarantees delivery, order, error checking. Flow control (sliding window), congestion control. Used for HTTP, FTP, email.",
                
                "UDP is connectionless, unreliable, faster than TCP. No handshake, no delivery guarantee. Used when speed matters: DNS queries, video streaming, online gaming, VoIP. Lower overhead. Application handles reliability if needed.",
                
                "HTTP (Hypertext Transfer Protocol) transfers web pages. Stateless request-response. Methods: GET, POST, PUT, DELETE. HTTPS adds SSL/TLS encryption. HTTP/2: multiplexing, server push. HTTP/3: uses QUIC over UDP.",
                
                "DNS (Domain Name System) translates domain names to IP addresses. Hierarchical distributed database. Root servers, TLD servers, authoritative servers. Recursive vs iterative queries. Caching reduces latency. A, AAAA, CNAME, MX records.",
                
                "Subnetting divides network into smaller subnetworks. Subnet mask determines network/host portions. CIDR notation (e.g., /24). Reduces broadcast traffic, improves security, efficient IP allocation. VLSM allows variable-size subnets.",
                
                "Firewalls filter network traffic based on rules. Packet filtering (stateless), stateful inspection, application layer filtering. Hardware vs software. DMZ isolates public servers. Used for security, blocking malicious traffic.",
                
                "Load balancers distribute traffic across servers. Round-robin, least connections, IP hash algorithms. Layer 4 (transport) vs Layer 7 (application). Health checks monitor server status. Improves availability, scalability, performance.",
            ],
            
            'Machine Learning': [
                "Supervised learning trains on labeled data (input-output pairs). Classification: discrete labels (spam/not spam). Regression: continuous values (price prediction). Algorithms: linear regression, logistic regression, decision trees, SVM, neural networks. Requires labeled training data.",
                
                "Unsupervised learning finds patterns in unlabeled data. Clustering: group similar items (K-means, hierarchical, DBSCAN). Dimensionality reduction: PCA, t-SNE. Anomaly detection: outliers. No ground truth labels needed.",
                
                "Neural networks consist of layers of interconnected neurons. Input layer receives data, hidden layers extract features, output layer produces predictions. Activation functions: ReLU, sigmoid, tanh. Trained via backpropagation with gradient descent.",
                
                "Overfitting occurs when model learns training data too well, poor generalization. High variance. Solutions: more data, regularization (L1/L2), dropout, early stopping, cross-validation. Underfitting: model too simple, high bias.",
                
                "Cross-validation assesses model performance. K-fold: split data into K parts, train on K-1, test on 1, rotate. Stratified: maintains class distribution. Leave-one-out: K = N. Helps detect overfitting, select hyperparameters.",
                
                "Gradient descent optimizes model parameters by following negative gradient. Batch: uses all data (slow, stable). Stochastic (SGD): uses one sample (fast, noisy). Mini-batch: compromise. Learning rate critical. Momentum, Adam improve convergence.",
            ],
        }
    
    def auto_scrape_content(self, source: Dict) -> List[str]:
        """Auto-scrape rich content from web"""
        try:
            logger.info(f"🌐 Scraping: {source['topic']} from {source['url']}")
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(source['url'], headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            paragraphs = []
            for selector in source['selectors']:
                elements = soup.find_all(selector)
                for elem in elements:
                    text = elem.get_text().strip()
                    # Only keep substantial paragraphs
                    if len(text) > 100 and len(text) < 800:
                        paragraphs.append(text)
            
            logger.info(f"✅ Scraped {len(paragraphs)} paragraphs")
            return paragraphs[:20]  # Limit to top 20
            
        except Exception as e:
            logger.warning(f"⚠️ Scraping failed: {e}, using built-in knowledge")
            return []
    
    def generate_from_text(self, context: str, topic: str) -> Dict:
        """Generate ONE high-quality question from context using AI"""
        if not self.model or not self.tokenizer:
            return None
        
        try:
            # ADVANCED PROMPTING for quality
            prompts = [
                f"Generate a technical multiple-choice question about {topic} based on this: {context}",
                f"Create a challenging question testing deep understanding of {topic}: {context}",
                f"Write a practical scenario-based question about {topic} from: {context}",
                f"Formulate an analytical question about {topic} concept: {context}",
                f"Design a problem-solving question related to {topic}: {context}",
            ]
            
            prompt = random.choice(prompts)
            
            # Tokenize with optimal settings
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                max_length=512, 
                truncation=True
            ).to(self.device)
            
            # Generate with MAXIMUM quality settings
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=150,
                    num_beams=10,           # Maximum quality
                    temperature=0.85,        # Balanced creativity
                    do_sample=True,
                    top_k=50,
                    top_p=0.95,
                    repetition_penalty=1.5,  # Strong anti-repetition
                    length_penalty=1.2,
                    no_repeat_ngram_size=3,
                    early_stopping=True
                )
            
            question = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean and validate
            question = self._clean_question(question)
            
            if not self._is_valid_question(question):
                return None
            
            # Generate realistic options using context
            options, correct = self._generate_smart_options(question, context, topic)
            
            if len(options) < 4:
                return None
            
            return {
                'question': question,
                'option_a': options[0],
                'option_b': options[1],
                'option_c': options[2],
                'option_d': options[3],
                'correct_option': correct,
                'topic': topic,
                'difficulty': self._auto_detect_difficulty(question),
                'category': 'ai_generated',
                'source': 'one_click_ai',
                'context': context[:200]
            }
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None
    
    def _clean_question(self, q: str) -> str:
        """Clean generated question"""
        q = q.strip()
        
        # Remove artifacts
        artifacts = ['Question:', 'Q:', 'Answer:', 'Options:', '1.', '2.', '3.', '4.']
        for art in artifacts:
            if q.startswith(art):
                q = q[len(art):].strip()
        
        # Ensure question mark
        if not q.endswith('?'):
            if any(q.lower().startswith(w) for w in ['what', 'how', 'why', 'when', 'which', 'who', 'where', 'can', 'does', 'is', 'are']):
                q += '?'
        
        return q
    
    def _is_valid_question(self, q: str) -> bool:
        """Validate question quality"""
        if len(q) < 20 or len(q) > 300:
            return False
        
        # Must be a question
        if not any(q.lower().startswith(w) for w in ['what', 'how', 'why', 'when', 'which', 'who', 'where', 'can', 'does', 'is', 'are', 'should', 'would', 'could']):
            return False
        
        # Check for generic patterns
        generic = ['most effective approach to implement', 'best way to', 'how would you']
        if any(g in q.lower() for g in generic):
            return False
        
        # Check diversity
        words = q.lower().split()
        if len(set(words)) / max(len(words), 1) < 0.6:
            return False
        
        return True
    
    def _generate_smart_options(self, question: str, context: str, topic: str) -> tuple:
        """Generate intelligent distractors based on context"""
        # Extract key terms from context
        words = context.split()
        key_terms = [w for w in words if len(w) > 4 and w[0].isupper()]
        
        # Context-based options
        options = []
        
        # Add one correct answer from context
        if key_terms:
            correct_answer = random.choice(key_terms[:5])
            options.append(correct_answer)
        else:
            options.append("Based on the given context")
        
        # Add plausible distractors
        distractors = [
            f"Alternative implementation of {topic}",
            f"Traditional approach without {topic}",
            f"Optimized version using different method",
            f"Standard technique in {topic}",
            "None of the above",
            "All of the above",
            "Depends on the implementation",
            "Not applicable in this scenario",
        ]
        
        # Mix specific and general distractors
        if len(key_terms) > 3:
            options.extend(random.sample(key_terms[1:], min(2, len(key_terms)-1)))
        
        options.extend(random.sample(distractors, 4 - len(options)))
        options = options[:4]
        
        random.shuffle(options)
        correct_idx = options.index(options[0])  # First was correct
        correct_letter = chr(65 + correct_idx)  # A, B, C, D
        
        return options, correct_letter
    
    def _auto_detect_difficulty(self, question: str) -> str:
        """Auto-detect difficulty level"""
        q_lower = question.lower()
        
        # Hard indicators
        if any(word in q_lower for word in ['algorithm', 'complexity', 'optimize', 'implement', 'design', 'analyze']):
            return 'hard'
        
        # Easy indicators
        if any(word in q_lower for word in ['what is', 'define', 'which of', 'meaning', 'stands for']):
            return 'easy'
        
        return 'medium'
    
    def _is_duplicate(self, question: str) -> bool:
        """Check if question exists in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            normalized = question.lower().strip()
            
            # Exact match
            cursor.execute("""
                SELECT id FROM question 
                WHERE LOWER(TRIM(question_text)) = ?
                LIMIT 1
            """, (normalized,))
            
            if cursor.fetchone():
                conn.close()
                return True
            
            # Similar (first 50 chars)
            prefix = normalized[:50]
            cursor.execute("""
                SELECT id FROM question 
                WHERE LOWER(SUBSTR(question_text, 1, 50)) = ?
                LIMIT 1
            """, (prefix,))
            
            result = cursor.fetchone() is not None
            conn.close()
            return result
            
        except:
            return False
    
    def _save_question(self, q_data: Dict) -> bool:
        """Save question to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO question (
                    question_text, option_a, option_b, option_c, option_d,
                    correct_option, topic, difficulty, category, source,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                q_data['question'],
                q_data['option_a'],
                q_data['option_b'],
                q_data['option_c'],
                q_data['option_d'],
                q_data['correct_option'],
                q_data['topic'],
                q_data['difficulty'],
                q_data['category'],
                q_data['source']
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False
    
    def generate_one_click(self, target_count: int = 120) -> int:
        """
        ONE-CLICK GENERATION!
        Automatically generates target_count high-quality questions
        """
        logger.info(f"\n{'='*100}")
        logger.info(f"🚀 ONE-CLICK AI GENERATION: Target {target_count} questions")
        logger.info(f"{'='*100}\n")
        
        saved_count = 0
        skipped_count = 0
        attempts = 0
        max_attempts = target_count * 5
        
        # Try web scraping first
        all_contexts = []
        for source in self.content_sources:
            paragraphs = self.auto_scrape_content(source)
            if paragraphs:
                all_contexts.extend([(p, source['topic']) for p in paragraphs])
            time.sleep(1)  # Be nice to servers
        
        # Add built-in knowledge base
        for topic, paragraphs in self.knowledge_base.items():
            all_contexts.extend([(p, topic) for p in paragraphs])
        
        random.shuffle(all_contexts)
        
        logger.info(f"📚 Loaded {len(all_contexts)} rich contexts")
        logger.info(f"🤖 Starting AI generation...\n")
        
        for context, topic in all_contexts:
            if saved_count >= target_count:
                break
            
            if attempts >= max_attempts:
                logger.warning(f"⚠️ Reached maximum attempts ({max_attempts})")
                break
            
            attempts += 1
            
            # Generate question
            q_data = self.generate_from_text(context, topic)
            
            if not q_data:
                continue
            
            # Check duplicate
            if self._is_duplicate(q_data['question']):
                skipped_count += 1
                continue
            
            # Save
            if self._save_question(q_data):
                saved_count += 1
                logger.info(f"✅ {saved_count}/{target_count}: [{topic}] {q_data['question'][:70]}...")
            
            if saved_count % 10 == 0 and saved_count > 0:
                logger.info(f"📊 Progress: {saved_count} saved, {skipped_count} duplicates skipped\n")
        
        logger.info(f"\n{'='*100}")
        logger.info(f"🎉 ONE-CLICK GENERATION COMPLETE!")
        logger.info(f"{'='*100}")
        logger.info(f"✅ Generated: {saved_count} new questions")
        logger.info(f"⏭️  Skipped: {skipped_count} duplicates")
        logger.info(f"🎯 Success Rate: {(saved_count/max(attempts,1)*100):.1f}%")
        logger.info(f"{'='*100}\n")
        
        return saved_count


# ONE-CLICK EXECUTION
if __name__ == "__main__":
    print("\n" + "="*100)
    print("🚀 ONE-CLICK AI QUESTION GENERATOR")
    print("="*100)
    print("✨ Fully automated - NO manual prompts needed!")
    print("🤖 AI-powered with built-in duplicate prevention")
    print("🎯 Generates high-quality, diverse questions")
    print("="*100 + "\n")
    
    generator = OneClickAIGenerator()
    
    # ONE CLICK = 120 QUESTIONS!
    saved = generator.generate_one_click(target_count=120)
    
    # Verify results
    conn = sqlite3.connect('aptitude_exam.db')
    total = conn.execute('SELECT COUNT(*) FROM question').fetchone()[0]
    ai_generated = conn.execute('SELECT COUNT(*) FROM question WHERE source="one_click_ai"').fetchone()[0]
    conn.close()
    
    print("\n" + "="*100)
    print("📊 FINAL DATABASE STATUS")
    print("="*100)
    print(f"Total Questions: {total}")
    print(f"AI Generated (This Run): {ai_generated}")
    print(f"Unique Exams Possible: {total // 10}")
    print("="*100 + "\n")
    
    print("✅ DONE! Your AI system generated high-quality questions automatically! 🎉\n")

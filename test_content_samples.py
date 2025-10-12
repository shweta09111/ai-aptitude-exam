"""
READY-TO-USE TEST CONTENT SAMPLES
Copy-paste these into the question generator for immediate testing
No manual input needed - just select and generate!
"""

# ============================================================================
# 📋 SAMPLE 1: MACHINE LEARNING FUNDAMENTALS
# ============================================================================

SAMPLE_1_CONTEXT = """
Machine Learning is a subset of artificial intelligence that enables computers to learn 
and improve from experience without being explicitly programmed. It uses algorithms to 
parse data, identify patterns, and make decisions with minimal human intervention.

Supervised learning trains models on labeled data, where each example has input features 
and a known output. Common algorithms include linear regression, logistic regression, 
decision trees, and support vector machines. The model learns to map inputs to outputs 
and can then predict outputs for new, unseen inputs.

Unsupervised learning works with unlabeled data to discover hidden patterns or structures. 
Clustering algorithms like K-means group similar data points together. Dimensionality 
reduction techniques like PCA compress data while preserving important information.

Reinforcement learning trains agents to make sequences of decisions by rewarding desired 
behaviors and punishing undesired ones. The agent learns a policy that maximizes cumulative 
reward over time. Applications include game playing, robotics, and autonomous vehicles.

Neural networks are inspired by biological neurons and consist of layers of interconnected 
nodes. Deep learning uses neural networks with many hidden layers to learn hierarchical 
representations. Convolutional neural networks excel at image processing, while recurrent 
neural networks handle sequential data like text and speech.
"""

SAMPLE_1_TOPICS = """Machine Learning
Supervised Learning
Unsupervised Learning
Neural Networks
Deep Learning"""

# ============================================================================
# 📋 SAMPLE 2: CLOUD COMPUTING & DISTRIBUTED SYSTEMS
# ============================================================================

SAMPLE_2_CONTEXT = """
Cloud computing delivers computing services over the internet, including servers, storage, 
databases, networking, software, and analytics. It offers scalability, flexibility, and 
cost-effectiveness by allowing organizations to rent resources on-demand rather than 
maintaining physical infrastructure.

The three main service models are Infrastructure as a Service (IaaS), Platform as a Service 
(PaaS), and Software as a Service (SaaS). IaaS provides virtualized computing resources like 
AWS EC2. PaaS offers development platforms like Google App Engine. SaaS delivers complete 
applications like Salesforce and Gmail.

Distributed systems spread computing tasks across multiple machines that coordinate through 
message passing. They provide scalability, fault tolerance, and resource sharing. Challenges 
include network latency, partial failures, and maintaining consistency across nodes. The CAP 
theorem states that distributed systems can guarantee only two of three properties: Consistency, 
Availability, and Partition tolerance.

Microservices architecture breaks applications into small, independent services that communicate 
via APIs. Each service handles a specific business capability and can be developed, deployed, 
and scaled independently. This improves agility and makes systems more resilient, though it 
adds complexity in service coordination and monitoring.

Containerization packages applications with their dependencies into isolated containers. Docker 
is the leading containerization platform. Kubernetes orchestrates containers across clusters, 
handling deployment, scaling, and management. Containers are lightweight, portable, and enable 
consistent environments from development to production.
"""

SAMPLE_2_TOPICS = """Cloud Computing
Distributed Systems
Microservices
Docker
Kubernetes"""

# ============================================================================
# 📋 SAMPLE 3: CYBERSECURITY FUNDAMENTALS
# ============================================================================

SAMPLE_3_CONTEXT = """
Cybersecurity protects computer systems, networks, and data from unauthorized access, theft, 
and damage. As cyber threats evolve, organizations must implement defense-in-depth strategies 
with multiple layers of security controls.

Authentication verifies user identity through passwords, biometrics, or multi-factor 
authentication (MFA). Authorization determines what authenticated users can access. The 
principle of least privilege grants users only the minimum access needed for their roles.

Encryption transforms readable data into unreadable ciphertext using algorithms and keys. 
Symmetric encryption uses the same key for encryption and decryption (AES), while asymmetric 
encryption uses public-private key pairs (RSA). SSL/TLS encrypts web traffic, HTTPS secures 
websites, and end-to-end encryption protects messaging apps.

Firewalls filter network traffic based on rules, blocking unauthorized access while allowing 
legitimate communication. Intrusion Detection Systems (IDS) monitor networks for suspicious 
activity. Intrusion Prevention Systems (IPS) actively block detected threats. Security 
Information and Event Management (SIEM) systems aggregate and analyze security logs.

Common attacks include malware (viruses, ransomware, spyware), phishing (fake emails to steal 
credentials), SQL injection (exploiting database queries), cross-site scripting (XSS), and 
Distributed Denial of Service (DDoS) attacks that overwhelm systems with traffic. Regular 
security patches, employee training, and incident response plans are essential defenses.
"""

SAMPLE_3_TOPICS = """Cybersecurity
Encryption
Network Security
Authentication
Malware"""

# ============================================================================
# 📋 SAMPLE 4: SOFTWARE ENGINEERING BEST PRACTICES
# ============================================================================

SAMPLE_4_CONTEXT = """
Software engineering applies systematic, disciplined approaches to developing reliable and 
maintainable software. Best practices improve code quality, team productivity, and project 
success rates.

Version control systems like Git track code changes, enable collaboration, and maintain 
project history. Developers work in branches for new features, then merge changes through 
pull requests with code review. This prevents conflicts and catches bugs early.

Test-driven development (TDD) writes tests before code. Developers write a failing test, 
implement code to pass it, then refactor. Unit tests verify individual functions, integration 
tests check component interactions, and end-to-end tests validate complete workflows. 
Automated testing catches regressions and enables confident refactoring.

Continuous Integration (CI) automatically builds and tests code when changes are pushed. 
Continuous Deployment (CD) automatically deploys passing builds to production. CI/CD pipelines 
include linting, testing, security scanning, and deployment stages. This accelerates delivery 
while maintaining quality.

Code reviews improve quality through peer feedback. Reviewers check for bugs, style issues, 
security vulnerabilities, and design problems. Good reviews are constructive, focus on code 
not people, and help teams share knowledge. Pair programming provides real-time review benefits.

Technical debt accumulates when quick fixes and shortcuts create future maintenance burdens. 
Refactoring improves code structure without changing behavior, paying down technical debt. 
Design patterns provide proven solutions to common problems. SOLID principles guide 
object-oriented design for maintainable systems.
"""

SAMPLE_4_TOPICS = """Software Engineering
Version Control
Testing
CI/CD
Code Review"""

# ============================================================================
# 📋 SAMPLE 5: WEB DEVELOPMENT MODERN STACK
# ============================================================================

SAMPLE_5_CONTEXT = """
Modern web development uses powerful frameworks and tools to build fast, responsive, and 
scalable applications. Full-stack developers work on both frontend and backend components.

Frontend frameworks like React, Angular, and Vue.js build interactive user interfaces using 
component-based architectures. Components are reusable pieces with their own state and logic. 
React uses JSX to mix HTML and JavaScript. Virtual DOM optimizes rendering performance. 
State management libraries like Redux manage application state centrally.

Backend development provides APIs and business logic. Node.js with Express.js creates 
JavaScript servers. RESTful APIs use HTTP methods (GET, POST, PUT, DELETE) on resources. 
GraphQL provides flexible query languages where clients specify exactly what data they need. 
WebSockets enable real-time bidirectional communication for chat and live updates.

Databases store application data. Relational databases (PostgreSQL, MySQL) use SQL and 
enforce schemas. NoSQL databases (MongoDB, Redis) offer flexibility and horizontal scaling. 
ORMs (Object-Relational Mappers) like Sequelize and Prisma abstract database operations into 
programming language constructs.

Authentication and authorization secure applications. JWT (JSON Web Tokens) are compact tokens 
containing user claims, signed to prevent tampering. OAuth 2.0 delegates authentication to 
providers like Google or GitHub. Session-based authentication stores user state on the server. 
CORS (Cross-Origin Resource Sharing) controls which domains can access APIs.

Performance optimization improves user experience. Code splitting loads only needed JavaScript. 
Lazy loading defers non-critical resources. CDNs (Content Delivery Networks) serve static 
assets from locations near users. Caching strategies reduce server load. Compression reduces 
file sizes. Server-side rendering improves initial page load and SEO.
"""

SAMPLE_5_TOPICS = """Web Development
React
Node.js
REST API
Authentication"""

# ============================================================================
# 📋 SAMPLE 6: DATA STRUCTURES & ALGORITHMS
# ============================================================================

SAMPLE_6_CONTEXT = """
Data structures organize and store data efficiently for different operations. Choosing the 
right data structure significantly impacts algorithm performance and system scalability.

Arrays store elements in contiguous memory locations, providing O(1) access time using indices. 
However, insertion and deletion operations take O(n) time due to element shifting. Dynamic 
arrays like Python lists or Java ArrayLists grow automatically when capacity is exceeded, 
typically doubling in size.

Linked lists store elements in nodes connected by pointers. Singly linked lists have a next 
pointer, while doubly linked lists also have a previous pointer. Insertion and deletion at 
known positions take O(1) time, but searching requires O(n) time. They use extra memory for 
pointers but offer dynamic sizing.

Hash tables use hash functions to map keys to array indices, providing O(1) average-case time 
for insertion, deletion, and lookup. Collisions occur when multiple keys hash to the same 
index, resolved by chaining (linked lists) or open addressing (probing). Good hash functions 
distribute keys uniformly to minimize collisions.

Binary search trees (BST) maintain sorted order where left children are smaller and right 
children are larger than their parent. Balanced BSTs like AVL trees and Red-Black trees 
guarantee O(log n) operations through rotations. B-trees are optimized for disk storage with 
multiple keys per node.

Graphs consist of vertices connected by edges. They're represented using adjacency matrices 
(O(V²) space, O(1) edge lookup) or adjacency lists (O(V+E) space, better for sparse graphs). 
Directed graphs have one-way edges, while undirected graphs have bidirectional edges. Weighted 
graphs assign costs to edges.
"""

SAMPLE_6_TOPICS = """Data Structures
Arrays
Linked Lists
Hash Tables
Binary Trees
Graphs"""

# ============================================================================
# 📋 SAMPLE 7: BLOCKCHAIN & CRYPTOCURRENCY
# ============================================================================

SAMPLE_7_CONTEXT = """
Blockchain is a distributed ledger technology that maintains a secure, decentralized record 
of transactions. Each block contains transaction data, a timestamp, and a cryptographic hash 
of the previous block, forming an immutable chain.

Consensus mechanisms ensure all network participants agree on the blockchain state. Proof of 
Work (PoW), used by Bitcoin, requires miners to solve computational puzzles to add blocks. 
Proof of Stake (PoS), used by Ethereum 2.0, selects validators based on staked tokens. Other 
mechanisms include Delegated Proof of Stake (DPoS) and Practical Byzantine Fault Tolerance (PBFT).

Smart contracts are self-executing programs on blockchains that automatically enforce agreements 
when conditions are met. Ethereum popularized smart contracts using Solidity programming language. 
Decentralized Applications (DApps) run on blockchains, offering transparency and censorship 
resistance. Use cases include DeFi (decentralized finance), NFTs (non-fungible tokens), and 
supply chain tracking.

Cryptocurrencies are digital currencies secured by cryptography. Bitcoin was the first 
cryptocurrency, using PoW consensus. Altcoins like Ethereum, Cardano, and Solana offer different 
features. Stablecoins like USDC maintain pegs to fiat currencies. Central Bank Digital Currencies 
(CBDCs) are government-issued digital currencies.

Blockchain security relies on cryptographic hashing and digital signatures. 51% attacks occur 
when entities control majority network power. Double-spending attacks attempt to use the same 
coins twice. Private blockchains restrict participation, while public blockchains are permissionless. 
Hybrid blockchains combine aspects of both.
"""

SAMPLE_7_TOPICS = """Blockchain
Cryptocurrency
Smart Contracts
Consensus Mechanisms
Bitcoin"""

# ============================================================================
# 📋 SAMPLE 8: MOBILE APP DEVELOPMENT
# ============================================================================

SAMPLE_8_CONTEXT = """
Mobile app development creates applications for smartphones and tablets. Native, hybrid, and 
cross-platform approaches offer different trade-offs between performance, development speed, 
and code reuse.

Native development uses platform-specific languages and tools. iOS apps use Swift or Objective-C 
with Xcode and UIKit. Android apps use Kotlin or Java with Android Studio and Jetpack. Native 
apps offer best performance and full access to device features, but require separate codebases 
for each platform.

Cross-platform frameworks enable code sharing across platforms. React Native uses JavaScript 
and React to build near-native apps. Flutter uses Dart and renders with its own graphics engine 
for consistent UI. Xamarin uses C# and .NET. These frameworks reduce development time but may 
have performance overhead for complex features.

Mobile UI design follows platform-specific guidelines. iOS uses Human Interface Guidelines with 
navigation bars and tab bars. Android uses Material Design with navigation drawers and floating 
action buttons. Responsive design adapts to different screen sizes. Accessibility features like 
screen readers, high contrast, and large text improve usability.

Mobile apps interact with device hardware including GPS, camera, sensors, and storage. Push 
notifications re-engage users with timely updates. Background tasks handle updates when apps 
aren't active. Deep linking opens specific app screens from URLs. App stores require approval 
processes, with Apple's App Store being more restrictive than Google Play.

Mobile app architecture patterns include MVC (Model-View-Controller), MVVM (Model-View-ViewModel), 
and Clean Architecture. State management handles data flow. Local databases like SQLite or Realm 
store data offline. REST APIs and GraphQL sync with backend servers. Authentication uses OAuth 
or JWT tokens.
"""

SAMPLE_8_TOPICS = """Mobile Development
React Native
Flutter
iOS Development
Android Development"""

# ============================================================================
# 📋 SAMPLE 9: ARTIFICIAL INTELLIGENCE & NLP
# ============================================================================

SAMPLE_9_CONTEXT = """
Artificial Intelligence (AI) creates systems that perform tasks requiring human intelligence. 
Machine learning, deep learning, and natural language processing are key AI subfields driving 
modern applications.

Natural Language Processing (NLP) enables computers to understand, interpret, and generate 
human language. Tokenization splits text into words or subwords. Part-of-speech tagging labels 
words as nouns, verbs, etc. Named Entity Recognition (NER) identifies people, places, and 
organizations. Sentiment analysis determines emotional tone.

Language models predict text based on context. Earlier models like Word2Vec and GloVe created 
word embeddings capturing semantic relationships. Modern transformer models like BERT, GPT, and 
T5 use attention mechanisms to understand context bidirectionally. These models are pre-trained 
on vast text corpora and fine-tuned for specific tasks.

Transfer learning uses pre-trained models as starting points for specific tasks, requiring less 
data and training time. Fine-tuning adjusts model weights on task-specific data. Few-shot learning 
enables models to learn from just a few examples. Zero-shot learning performs tasks without 
specific training examples.

NLP applications include machine translation (translating between languages), question answering 
(finding answers in text), text summarization (creating concise summaries), chatbots (conversational 
agents), and speech recognition (transcribing audio to text). These technologies power virtual 
assistants, customer service automation, and content generation.

Challenges include handling ambiguity, context dependence, idioms, sarcasm, and multilingual text. 
Bias in training data can lead to unfair or harmful outputs. Privacy concerns arise with personal 
data. Model interpretability helps understand and trust AI decisions.
"""

SAMPLE_9_TOPICS = """Artificial Intelligence
Natural Language Processing
Machine Learning
BERT
GPT"""

# ============================================================================
# 📋 SAMPLE 10: DEVOPS & INFRASTRUCTURE
# ============================================================================

SAMPLE_10_CONTEXT = """
DevOps combines software development (Dev) and IT operations (Ops) to shorten development cycles 
and deliver features, fixes, and updates frequently and reliably. It emphasizes automation, 
collaboration, and continuous improvement.

Infrastructure as Code (IaC) manages infrastructure through machine-readable files rather than 
manual processes. Terraform uses declarative configuration to provision cloud resources across 
providers. Ansible automates configuration management with YAML playbooks. CloudFormation manages 
AWS infrastructure. IaC enables version control, reproducibility, and automation.

Container orchestration manages containerized applications at scale. Kubernetes is the leading 
platform, providing deployment, scaling, load balancing, and self-healing. Pods are the smallest 
deployable units. Services provide stable networking. ConfigMaps and Secrets manage configuration. 
Helm packages Kubernetes applications.

Monitoring and observability provide visibility into system behavior. Metrics track quantitative 
measurements like CPU usage and request rates. Logs record events for debugging. Distributed 
tracing follows requests across services. Prometheus collects metrics, Grafana visualizes them, 
and ELK stack (Elasticsearch, Logstash, Kibana) processes logs.

CI/CD pipelines automate building, testing, and deploying code. Jenkins, GitLab CI, GitHub Actions, 
and CircleCI are popular tools. Pipelines run on code commits, executing stages like linting, unit 
tests, integration tests, security scans, and deployment. Blue-green deployments and canary releases 
minimize deployment risks.

Site Reliability Engineering (SRE) applies software engineering to operations. SLAs (Service Level 
Agreements) define expected service quality. SLOs (Service Level Objectives) set measurable targets. 
Error budgets balance reliability and velocity. Incident management procedures handle outages. 
Post-mortems identify root causes and improvements.
"""

SAMPLE_10_TOPICS = """DevOps
Kubernetes
Infrastructure as Code
CI/CD
Monitoring"""

# ============================================================================
# 🚀 QUICK USAGE GUIDE
# ============================================================================

USAGE_INSTRUCTIONS = """
HOW TO USE THESE SAMPLES:

METHOD 1: Generate from Context
1. Navigate to Admin → Question Generator
2. Click "Generate from Context [MANUAL]" tab
3. Copy any SAMPLE_X_CONTEXT above
4. Paste into "Context Text" field
5. Select number of questions (e.g., 5 Questions)
6. Click "Generate Questions"

METHOD 2: Generate from Topics
1. Navigate to Admin → Question Generator
2. Click "Generate from Topics [MANUAL]" tab
3. Copy any SAMPLE_X_TOPICS above
4. Paste into "Topics (one per line)" field
5. Select questions per topic (e.g., 3 Questions)
6. Click "Generate from Topics"

TIPS FOR BEST RESULTS:
- Use SAMPLE_1 through SAMPLE_10 for comprehensive coverage
- Each sample has 300-400 words of rich technical content
- Topics are carefully selected for question generation
- Mix different samples for variety
- Test with 3-5 questions first, then scale up

RECOMMENDED TESTING SEQUENCE:
1. Start with SAMPLE_1 (ML) - Generate 5 questions
2. Try SAMPLE_6 (DSA) - Generate 5 questions  
3. Test SAMPLE_2 (Cloud) - Generate 5 questions
4. Once comfortable, use ONE-CLICK AI for bulk generation

⚡ For fastest results: Use ONE-CLICK AI Generator (50 questions in 2-3 minutes)
🎯 For manual testing: Copy-paste these samples
📚 For learning: Review the comprehensive content in each sample
"""

# Print usage when run directly
if __name__ == "__main__":
    print("="*80)
    print("📋 READY-TO-USE TEST CONTENT SAMPLES")
    print("="*80)
    print("\nAvailable Samples:")
    print("1. Machine Learning Fundamentals")
    print("2. Cloud Computing & Distributed Systems")
    print("3. Cybersecurity Fundamentals")
    print("4. Software Engineering Best Practices")
    print("5. Web Development Modern Stack")
    print("6. Data Structures & Algorithms")
    print("7. Blockchain & Cryptocurrency")
    print("8. Mobile App Development")
    print("9. Artificial Intelligence & NLP")
    print("10. DevOps & Infrastructure")
    print("\n" + "="*80)
    print(USAGE_INSTRUCTIONS)

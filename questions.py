"""
Question bank for technical assessments
"""

class TechnicalQuestions:
    """Comprehensive technical question database"""
    
    QUESTION_BANK = {
        # Programming Languages
        'python': {
            'beginner': [
                "What are the basic data types in Python?",
                "Explain the difference between list and tuple.",
                "How do you handle exceptions in Python?",
                "What is the purpose of the '__init__' method?",
                "Explain the concept of indentation in Python."
            ],
            'intermediate': [
                "What is a decorator in Python and how would you implement one?",
                "Explain the concept of generators and the yield keyword.",
                "How does Python's garbage collection work?",
                "What are list comprehensions and when would you use them?",
                "Explain the difference between shallow and deep copy."
            ],
            'advanced': [
                "Explain Python's Global Interpreter Lock (GIL) and its implications.",
                "How would you implement a metaclass in Python?",
                "Describe the descriptor protocol in Python.",
                "Explain the asyncio module and asynchronous programming in Python.",
                "How would you optimize Python code for better performance?"
            ]
        },
        
        'javascript': {
            'beginner': [
                "What are the primitive data types in JavaScript?",
                "Explain the difference between var, let, and const.",
                "How do you create a function in JavaScript?",
                "What is the DOM and how do you interact with it?",
                "Explain event handling in JavaScript."
            ],
            'intermediate': [
                "What is closure in JavaScript and provide an example.",
                "How does the event loop work in JavaScript?",
                "Explain promises and async/await.",
                "What is the difference between == and === in JavaScript?",
                "How does prototype inheritance work in JavaScript?"
            ],
            'advanced': [
                "Explain the concept of hoisting in JavaScript.",
                "How would you implement a polyfill for Array.prototype.map?",
                "Describe the execution context and call stack in JavaScript.",
                "Explain memory management and garbage collection in JavaScript.",
                "How would you implement a custom Promise from scratch?"
            ]
        },
        
        'java': {
            'beginner': [
                "What are the main principles of Object-Oriented Programming?",
                "Explain the difference between abstract class and interface.",
                "What is the purpose of the 'static' keyword?",
                "How do you handle exceptions in Java?",
                "Explain the concept of inheritance in Java."
            ],
            'intermediate': [
                "How does Java's garbage collection work?",
                "Explain the concept of multithreading in Java.",
                "What are Java Collections and when would you use each type?",
                "Describe the difference between HashMap and TreeMap.",
                "What is the Java Memory Model?"
            ],
            'advanced': [
                "Explain the concept of Java Reflection and its use cases.",
                "How would you implement a custom thread pool in Java?",
                "Describe JVM internals and the class loading mechanism.",
                "Explain Java's concurrency utilities and atomic operations.",
                "How would you optimize Java application performance?"
            ]
        },
        
        # Frameworks
        'react': {
            'beginner': [
                "What is React and why is it used?",
                "Explain the concept of components in React.",
                "What is JSX and how does it work?",
                "How do you handle events in React?",
                "What are props and how are they used?"
            ],
            'intermediate': [
                "Explain the virtual DOM and how React uses it.",
                "What are React hooks and why were they introduced?",
                "Describe the component lifecycle in React.",
                "How would you manage state in a React application?",
                "Explain the difference between controlled and uncontrolled components."
            ],
            'advanced': [
                "How would you optimize a React application's performance?",
                "Explain React's reconciliation algorithm.",
                "How would you implement server-side rendering with React?",
                "Describe advanced patterns like render props and HOCs.",
                "How would you implement a custom hook for data fetching?"
            ]
        },
        
        'django': {
            'beginner': [
                "What is Django and what are its main features?",
                "Explain Django's MTV (Model-Template-View) architecture.",
                "How do you create a simple Django model?",
                "What is Django's admin interface?",
                "How do you handle URL routing in Django?"
            ],
            'intermediate': [
                "What are Django models and how do they relate to databases?",
                "How does Django's ORM work?",
                "Explain Django's middleware and provide an example.",
                "How do you handle forms in Django?",
                "What are Django's authentication and authorization systems?"
            ],
            'advanced': [
                "How would you optimize Django application performance?",
                "Explain Django's caching framework and strategies.",
                "How would you implement custom middleware in Django?",
                "Describe Django's signal system and its use cases.",
                "How would you scale a Django application for high traffic?"
            ]
        },
        
        'angular': {
            'beginner': [
                "What is Angular and how is it different from AngularJS?",
                "Explain the concept of components in Angular.",
                "What is TypeScript and why does Angular use it?",
                "How do you create a simple Angular service?",
                "What are Angular directives?"
            ],
            'intermediate': [
                "Explain Angular's dependency injection system.",
                "How does data binding work in Angular?",
                "What are Angular pipes and how do you create custom pipes?",
                "Describe the Angular component lifecycle hooks.",
                "How do you handle HTTP requests in Angular?"
            ],
            'advanced': [
                "How would you implement lazy loading in Angular?",
                "Explain Angular's change detection strategy.",
                "How would you optimize Angular application performance?",
                "Describe Angular's testing framework and best practices.",
                "How would you implement state management in Angular?"
            ]
        },
        
        # Databases
        'sql': {
            'beginner': [
                "What is SQL and what are its main components?",
                "Explain the difference between INNER JOIN and LEFT JOIN.",
                "How do you create a table in SQL?",
                "What are primary and foreign keys?",
                "How do you write a basic SELECT query with WHERE clause?"
            ],
            'intermediate': [
                "What are database indexes and how do they improve performance?",
                "Describe ACID properties in database transactions.",
                "How do you write complex queries with subqueries?",
                "What are stored procedures and functions?",
                "Explain different types of database relationships."
            ],
            'advanced': [
                "How would you optimize a slow SQL query?",
                "Explain database normalization and denormalization.",
                "How would you handle database concurrency and locking?",
                "Describe database partitioning strategies.",
                "How would you implement database backup and recovery?"
            ]
        },
        
        'mongodb': {
            'beginner': [
                "What is MongoDB and how is it different from relational databases?",
                "Explain the concept of documents and collections.",
                "How do you insert and query documents in MongoDB?",
                "What is BSON and how does it relate to JSON?",
                "How do you update and delete documents?"
            ],
            'intermediate': [
                "How does indexing work in MongoDB?",
                "Explain the aggregation pipeline in MongoDB.",
                "How do you handle relationships in MongoDB?",
                "What are MongoDB's consistency and durability guarantees?",
                "How do you perform text search in MongoDB?"
            ],
            'advanced': [
                "How would you design a MongoDB schema for optimal performance?",
                "Explain MongoDB's sharding and replication strategies.",
                "How would you handle transactions in MongoDB?",
                "Describe MongoDB's memory management and storage engine.",
                "How would you monitor and optimize MongoDB performance?"
            ]
        },
        
        # Cloud & DevOps
        'aws': {
            'beginner': [
                "What is AWS and what are its main services?",
                "Explain the difference between EC2 and Lambda.",
                "What is S3 and what are its use cases?",
                "How do you secure AWS resources?",
                "What is the AWS Free Tier?"
            ],
            'intermediate': [
                "How does auto-scaling work in AWS?",
                "Explain VPC and its components.",
                "What are the different types of load balancers in AWS?",
                "How do you manage AWS costs and billing?",
                "Describe AWS IAM and its best practices."
            ],
            'advanced': [
                "How would you design a highly available architecture on AWS?",
                "Explain AWS disaster recovery strategies.",
                "How would you implement CI/CD pipelines using AWS services?",
                "Describe AWS networking and security best practices.",
                "How would you optimize AWS costs for a large-scale application?"
            ]
        },
        
        'docker': {
            'beginner': [
                "What is Docker and why is it used?",
                "Explain the difference between containers and virtual machines.",
                "How do you create a simple Dockerfile?",
                "What are Docker images and containers?",
                "How do you run a Docker container?"
            ],
            'intermediate': [
                "What is a Dockerfile and how do you write one?",
                "How do you manage persistent data in Docker containers?",
                "Explain Docker networking and different network types.",
                "What is Docker Compose and when would you use it?",
                "How do you handle environment variables in Docker?"
            ],
            'advanced': [
                "How would you optimize Docker images for production?",
                "Explain Docker Swarm and container orchestration.",
                "How would you implement multi-stage builds in Docker?",
                "Describe Docker security best practices.",
                "How would you monitor and debug Docker containers?"
            ]
        },
        
        'kubernetes': {
            'beginner': [
                "What is Kubernetes and what problems does it solve?",
                "Explain the basic components of a Kubernetes cluster.",
                "What are pods and how are they different from containers?",
                "How do you deploy an application to Kubernetes?",
                "What is kubectl and how do you use it?"
            ],
            'intermediate': [
                "Explain Kubernetes services and ingress controllers.",
                "How do you manage configuration and secrets in Kubernetes?",
                "What are deployments and how do they differ from pods?",
                "How does Kubernetes handle scaling and load balancing?",
                "Describe Kubernetes storage concepts and persistent volumes."
            ],
            'advanced': [
                "How would you implement monitoring and logging in Kubernetes?",
                "Explain Kubernetes security policies and RBAC.",
                "How would you design a CI/CD pipeline for Kubernetes?",
                "Describe advanced Kubernetes networking concepts.",
                "How would you troubleshoot common Kubernetes issues?"
            ]
        },
        
        # Additional Technologies
        'git': {
            'beginner': [
                "What is Git and why is version control important?",
                "How do you initialize a Git repository?",
                "Explain the basic Git workflow (add, commit, push).",
                "What is the difference between Git and GitHub?",
                "How do you check the status of your Git repository?"
            ],
            'intermediate': [
                "How do you create and merge branches in Git?",
                "Explain the difference between merge and rebase.",
                "How do you resolve merge conflicts?",
                "What are Git hooks and how do you use them?",
                "How do you undo changes in Git?"
            ],
            'advanced': [
                "How would you implement a Git workflow for a team?",
                "Explain advanced Git commands like cherry-pick and bisect.",
                "How would you handle large repositories and Git LFS?",
                "Describe Git internals and how objects are stored.",
                "How would you optimize Git performance for large projects?"
            ]
        },
        
        'redis': {
            'beginner': [
                "What is Redis and what are its main use cases?",
                "Explain the basic data types supported by Redis.",
                "How do you set and get values in Redis?",
                "What is the difference between Redis and traditional databases?",
                "How do you configure Redis for basic usage?"
            ],
            'intermediate': [
                "How does Redis handle persistence and durability?",
                "Explain Redis pub/sub functionality.",
                "What are Redis transactions and how do you use them?",
                "How do you implement caching strategies with Redis?",
                "Describe Redis clustering and high availability."
            ],
            'advanced': [
                "How would you optimize Redis performance for high throughput?",
                "Explain Redis memory management and eviction policies.",
                "How would you implement distributed locking with Redis?",
                "Describe Redis security best practices.",
                "How would you monitor and troubleshoot Redis issues?"
            ]
        }
    }
    
    @classmethod
    def get_questions_for_technology(cls, tech: str, experience_level: str = 'intermediate', count: int = 3):
        """Get questions for a specific technology and experience level"""
        tech_lower = tech.lower().strip()
        
        if tech_lower in cls.QUESTION_BANK:
            questions = cls.QUESTION_BANK[tech_lower].get(experience_level, 
                                                        cls.QUESTION_BANK[tech_lower].get('intermediate', []))
            return questions[:count] if questions else []
        
        # Return generic questions if technology not found
        return cls._get_generic_questions(tech, count)
    
    @classmethod
    def _get_generic_questions(cls, tech: str, count: int = 3):
        """Generate generic questions for unknown technologies"""
        return [
            f"Describe your experience with {tech} and its main features.",
            f"What are the key advantages of using {tech} in development?",
            f"Can you explain a challenging project where you used {tech}?",
            f"How do you stay updated with the latest developments in {tech}?",
            f"What best practices do you follow when working with {tech}?"
        ][:count]
    
    @classmethod
    def get_experience_level_from_years(cls, years: float):
        """Determine experience level based on years of experience"""
        if years < 2:
            return 'beginner'
        elif years < 5:
            return 'intermediate'
        else:
            return 'advanced'
    
    @classmethod
    def get_all_supported_technologies(cls):
        """Get list of all supported technologies"""
        return list(cls.QUESTION_BANK.keys())
    
    @classmethod
    def get_questions_for_tech_stack(cls, tech_stack: list, experience_years: float = 3.0, max_questions: int = 5):
        """Get balanced questions across the entire tech stack"""
        experience_level = cls.get_experience_level_from_years(experience_years)
        all_questions = []
        
        # Calculate questions per technology
        questions_per_tech = max(1, max_questions // len(tech_stack)) if tech_stack else 1
        
        for tech in tech_stack:
            tech_questions = cls.get_questions_for_technology(tech, experience_level, questions_per_tech)
            all_questions.extend(tech_questions)
        
        # If we have too many questions, trim to max_questions
        if len(all_questions) > max_questions:
            # Try to keep at least one question per technology
            trimmed_questions = []
            for i, tech in enumerate(tech_stack):
                if i < len(all_questions):
                    trimmed_questions.append(all_questions[i])
            
            # Add remaining questions up to max_questions
            remaining_slots = max_questions - len(trimmed_questions)
            for question in all_questions[len(tech_stack):]:
                if remaining_slots <= 0:
                    break
                trimmed_questions.append(question)
                remaining_slots -= 1
            
            return trimmed_questions
        
        return all_questions[:max_questions]

"""Seed course data, ported from the design project's learnflow-data.js."""

# Public-domain sample clips rotated across "video" lessons in seed.py so the
# demo has something real to play — not meant to match each lesson's subject
# matter. Verified reachable (200, video/mp4) as of 2026-08-17; Google's old
# gtv-videos-bucket sample set now returns 403 AccessDenied, so this uses
# W3Schools' and MDN's own <video>-element demo assets instead.
SAMPLE_VIDEO_URLS = [
    "https://www.w3schools.com/html/mov_bbb.mp4",
    "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
    "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/friday.mp4",
]

DEFAULT_COURSES = [
    {
        "title": "Prompt Engineering Fundamentals", "category": "Generative AI", "level": "Beginner",
        "instructor_name": "Maya Chen", "duration_hrs": 4, "rating": 4.8, "students": 1240, "swatch": 0,
        "description": "Learn to write reliable prompts for large language models: structuring instructions, giving examples, and controlling tone and format for consistent output.",
        "lessons": [
            {"title": "Why prompts matter", "type": "video", "duration": 12, "body": "An overview of how language models interpret instructions, and why small wording changes produce very different results."},
            {"title": "Structuring an effective prompt", "type": "text", "duration": 15, "body": "Break requests into role, context, task and format. We walk through rewriting a vague prompt into a precise one step by step."},
            {"title": "Few-shot examples", "type": "video", "duration": 14, "body": "Showing the model examples of the input and output pattern you want is often more reliable than describing the rule in words."},
        ],
        "quiz": [
            {"type": "mcq", "text": 'What is a "few-shot" prompt?', "options": ["A prompt with no examples", "A prompt that includes example input/output pairs", "A prompt written in shorthand", "A prompt sent to multiple models"], "answer": 1},
            {"type": "tf", "text": 'Giving the model a role (e.g. "You are an editor") can change the style of its output.', "answer": True},
            {"type": "mcq", "text": "Which element is NOT part of a well-structured prompt?", "options": ["Context", "Task", "Desired format", "The model API key"], "answer": 3},
            {"type": "short", "text": "In one word, what do we call showing the model examples of the pattern you want?", "answer": "few-shot"},
        ],
    },
    {
        "title": "Machine Learning with Python", "category": "Machine Learning", "level": "Beginner",
        "instructor_name": "Daniel Osei", "duration_hrs": 8, "rating": 4.7, "students": 2310, "swatch": 1,
        "description": "A hands-on introduction to supervised learning using Python and scikit-learn: regression, classification, and evaluating model performance.",
        "lessons": [
            {"title": "Setting up your environment", "type": "text", "duration": 10, "body": "Installing Python, pandas and scikit-learn, and loading your first dataset into a notebook."},
            {"title": "Linear regression from scratch", "type": "video", "duration": 18, "body": "How linear regression fits a line to data by minimizing squared error, with a worked example."},
            {"title": "Classification and accuracy", "type": "video", "duration": 16, "body": "Moving from predicting numbers to predicting categories, and why accuracy alone can be misleading."},
        ],
        "quiz": [
            {"type": "mcq", "text": "What does linear regression predict?", "options": ["A category", "A continuous number", "An image", "A distribution over words"], "answer": 1},
            {"type": "tf", "text": "Accuracy is always the best metric for an imbalanced classification dataset.", "answer": False},
            {"type": "mcq", "text": "Which library is used for classical ML models in this course?", "options": ["TensorFlow", "scikit-learn", "React", "Pandas only"], "answer": 1},
            {"type": "short", "text": "Which Python library is commonly used to load and clean tabular data?", "answer": "pandas"},
        ],
    },
    {
        "title": "Deep Learning and Neural Networks", "category": "Machine Learning", "level": "Intermediate",
        "instructor_name": "Daniel Osei", "duration_hrs": 10, "rating": 4.9, "students": 1870, "swatch": 0,
        "description": "Understand how neural networks learn: layers, activations, backpropagation, and training your first network on image data.",
        "lessons": [
            {"title": "From neurons to networks", "type": "video", "duration": 15, "body": "How a single artificial neuron works, and how stacking them into layers lets a network learn complex patterns."},
            {"title": "Backpropagation intuitively", "type": "text", "duration": 20, "body": "Backpropagation adjusts every weight in the network by tracing how much it contributed to the final error."},
            {"title": "Training your first network", "type": "video", "duration": 22, "body": "A guided walkthrough training a small network to classify handwritten digits."},
        ],
        "quiz": [
            {"type": "mcq", "text": "What does an activation function introduce into a network?", "options": ["Randomness", "Non-linearity", "Extra data", "Compression"], "answer": 1},
            {"type": "tf", "text": "Backpropagation computes how much each weight contributed to the error.", "answer": True},
            {"type": "mcq", "text": "Which of these is a common activation function?", "options": ["ReLU", "SELECT", "JOIN", "CSV"], "answer": 0},
            {"type": "short", "text": "What is the process of adjusting weights based on error called?", "answer": "backpropagation"},
        ],
    },
    {
        "title": "Natural Language Processing Essentials", "category": "NLP", "level": "Intermediate",
        "instructor_name": "Priya Nair", "duration_hrs": 7, "rating": 4.6, "students": 1420, "swatch": 1,
        "description": "Core NLP techniques for working with text: tokenization, embeddings, and building a simple text classifier.",
        "lessons": [
            {"title": "Tokenization and vocabulary", "type": "text", "duration": 12, "body": "How raw text is split into tokens, and why vocabulary size affects model behavior."},
            {"title": "Word embeddings", "type": "video", "duration": 17, "body": "Representing words as vectors so that similar words end up close together in space."},
            {"title": "Building a text classifier", "type": "video", "duration": 19, "body": "Combining embeddings with a simple classifier to label text, such as sentiment analysis."},
        ],
        "quiz": [
            {"type": "mcq", "text": "What is a token in NLP?", "options": ["A security credential", "A unit of text like a word or subword", "A trained model", "A database row"], "answer": 1},
            {"type": "tf", "text": "Word embeddings place semantically similar words close together in vector space.", "answer": True},
            {"type": "mcq", "text": "Sentiment analysis is an example of which task?", "options": ["Text classification", "Image segmentation", "Audio transcription", "Database indexing"], "answer": 0},
            {"type": "short", "text": "What do we call a numeric vector representation of a word?", "answer": "embedding"},
        ],
    },
    {
        "title": "Computer Vision in Practice", "category": "Computer Vision", "level": "Intermediate",
        "instructor_name": "Lucas Ferreira", "duration_hrs": 9, "rating": 4.7, "students": 980, "swatch": 0,
        "description": "Practical image classification and object detection using convolutional neural networks.",
        "lessons": [
            {"title": "How convolutions see images", "type": "video", "duration": 16, "body": "Convolutional filters slide over an image detecting edges, textures and shapes at increasing levels of abstraction."},
            {"title": "The image classification pipeline", "type": "text", "duration": 14, "body": "From raw pixels to a predicted label: preprocessing, augmentation, and evaluation."},
            {"title": "Object detection basics", "type": "video", "duration": 20, "body": "Detecting and localizing multiple objects in a single image, and the tradeoffs between speed and accuracy."},
        ],
        "quiz": [
            {"type": "mcq", "text": "What does a convolutional filter detect?", "options": ["Database schemas", "Local patterns like edges and textures", "Text sentiment", "Network latency"], "answer": 1},
            {"type": "tf", "text": "Object detection only tells you if an object is present, never where it is.", "answer": False},
            {"type": "mcq", "text": "Which technique expands training data by transforming images?", "options": ["Augmentation", "Tokenization", "Normalization only", "Compression"], "answer": 0},
            {"type": "short", "text": "Which kind of neural network is standard for image tasks?", "answer": "convolutional"},
        ],
    },
    {
        "title": "MLOps: Deploying AI Systems", "category": "MLOps", "level": "Advanced",
        "instructor_name": "Sofia Kowalski", "duration_hrs": 11, "rating": 4.5, "students": 640, "swatch": 1,
        "description": "Take a trained model to production: versioning, CI/CD for models, monitoring, and rollback strategies.",
        "lessons": [
            {"title": "The model lifecycle", "type": "text", "duration": 13, "body": "From experiment tracking to packaging, deployment and eventual retraining, the full loop a model goes through in production."},
            {"title": "CI/CD for machine learning", "type": "video", "duration": 18, "body": "Automating tests and deployment for models, not just code, including data validation checks."},
            {"title": "Monitoring and drift", "type": "video", "duration": 17, "body": "Detecting when a deployed model degrades because the real world has changed."},
        ],
        "quiz": [
            {"type": "mcq", "text": 'What is "model drift"?', "options": ["A bug in the training code", "Degrading performance as real-world data changes", "A type of neural network", "A GPU scheduling issue"], "answer": 1},
            {"type": "tf", "text": "CI/CD pipelines for ML should also validate data, not just code.", "answer": True},
            {"type": "mcq", "text": "A rollback strategy is used when:", "options": ["A new model performs worse in production", "Training finishes early", "The dataset is too small", "The UI changes"], "answer": 0},
            {"type": "short", "text": "What term covers automated build and deployment pipelines?", "answer": "ci/cd"},
        ],
    },
    {
        "title": "Generative AI for Product Teams", "category": "Generative AI", "level": "Beginner",
        "instructor_name": "Maya Chen", "duration_hrs": 3, "rating": 4.8, "students": 1560, "swatch": 0,
        "description": "A non-technical guide for product managers and designers to identify, scope and ship generative AI features responsibly.",
        "lessons": [
            {"title": "What generative AI can and cannot do", "type": "video", "duration": 11, "body": "A realistic look at current capabilities and common failure modes, so teams set the right expectations."},
            {"title": "Scoping an AI feature", "type": "text", "duration": 13, "body": "Choosing a narrow, high-value use case and defining success metrics before writing a single prompt."},
            {"title": "Shipping and iterating", "type": "video", "duration": 12, "body": "Launching with guardrails, collecting feedback, and iterating on prompts and UX together."},
        ],
        "quiz": [
            {"type": "mcq", "text": "What should a team define before building an AI feature?", "options": ["The marketing slogan", "Success metrics and scope", "The company logo", "Nothing, just ship"], "answer": 1},
            {"type": "tf", "text": "Generative AI models are always factually accurate.", "answer": False},
            {"type": "mcq", "text": "A good first AI feature is usually:", "options": ["Broad and ambiguous", "Narrow and high-value", "Untestable", "Unrelated to user needs"], "answer": 1},
            {"type": "short", "text": "What term describes a model confidently producing false information?", "answer": "hallucination"},
        ],
    },
    {
        "title": "AI Ethics and Responsible Design", "category": "AI Ethics", "level": "Beginner",
        "instructor_name": "Priya Nair", "duration_hrs": 5, "rating": 4.6, "students": 890, "swatch": 1,
        "description": "Bias, fairness, transparency and privacy considerations for teams building AI-powered products.",
        "lessons": [
            {"title": "Where bias comes from", "type": "video", "duration": 14, "body": "Bias can enter through training data, labeling decisions, or the objective a model is optimized for."},
            {"title": "Transparency and explainability", "type": "text", "duration": 12, "body": "Helping users understand what a system can do and why it produced a given output builds trust."},
            {"title": "Privacy by design", "type": "video", "duration": 13, "body": "Minimizing data collection and giving users control are easier to build in early than to retrofit."},
        ],
        "quiz": [
            {"type": "mcq", "text": "A common source of model bias is:", "options": ["The programming language used", "Biased training data", "Slow servers", "Too much documentation"], "answer": 1},
            {"type": "tf", "text": "Explainability only matters for regulators, not everyday users.", "answer": False},
            {"type": "mcq", "text": '"Privacy by design" means:', "options": ["Adding privacy features after launch", "Building privacy protections in from the start", "Ignoring privacy for speed", "Leaving privacy to the legal team"], "answer": 1},
            {"type": "short", "text": "What is the term for systematic unfairness in a model’s predictions?", "answer": "bias"},
        ],
    },
    {
        "title": "Reinforcement Learning Foundations", "category": "Reinforcement Learning", "level": "Advanced",
        "instructor_name": "Lucas Ferreira", "duration_hrs": 10, "rating": 4.5, "students": 410, "swatch": 0,
        "description": "Agents, rewards and policies: the core ideas behind systems that learn from trial and error.",
        "lessons": [
            {"title": "Agents, states and rewards", "type": "video", "duration": 15, "body": "A reinforcement learning agent takes actions in an environment and learns from the rewards it receives."},
            {"title": "Exploration versus exploitation", "type": "text", "duration": 14, "body": "An agent must balance trying new actions against using what already seems to work well."},
            {"title": "Policies and value functions", "type": "video", "duration": 18, "body": "A policy maps states to actions; a value function estimates how good a state or action is in the long run."},
        ],
        "quiz": [
            {"type": "mcq", "text": "What does an RL agent learn from?", "options": ["Labeled examples only", "Rewards from its own actions", "Static documents", "Pre-written rules"], "answer": 1},
            {"type": "tf", "text": "An agent should always exploit the best known action and never explore.", "answer": False},
            {"type": "mcq", "text": "A policy in RL is:", "options": ["A legal document", "A mapping from states to actions", "A database schema", "A type of loss function"], "answer": 1},
            {"type": "short", "text": "What is the tradeoff between trying new actions and using known good ones called?", "answer": "exploration"},
        ],
    },
    {
        "title": "Data Engineering for AI Pipelines", "category": "Data Engineering", "level": "Intermediate",
        "instructor_name": "Sofia Kowalski", "duration_hrs": 9, "rating": 4.4, "students": 730, "swatch": 1,
        "description": "Build the data pipelines that feed AI systems: ingestion, cleaning, feature stores and dataset versioning.",
        "lessons": [
            {"title": "From raw data to features", "type": "text", "duration": 14, "body": "Turning messy raw data into clean, well-defined features a model can consume reliably."},
            {"title": "Feature stores", "type": "video", "duration": 16, "body": "A feature store keeps features consistent between training and serving, avoiding subtle mismatches."},
            {"title": "Versioning data, not just code", "type": "video", "duration": 15, "body": "Reproducible experiments require tracking which dataset version produced which model."},
        ],
        "quiz": [
            {"type": "mcq", "text": "A feature store primarily helps with:", "options": ["UI design", "Consistency between training and serving features", "Password hashing", "Video encoding"], "answer": 1},
            {"type": "tf", "text": "Reproducibility requires versioning datasets as well as code.", "answer": True},
            {"type": "mcq", "text": '"Raw data to features" is best described as:', "options": ["A deployment step", "A data preparation step", "A UI review step", "A marketing step"], "answer": 1},
            {"type": "short", "text": "What do we call tracking dataset versions over time?", "answer": "versioning"},
        ],
    },
    {
        "title": "Fine-Tuning Large Language Models", "category": "Generative AI", "level": "Advanced",
        "instructor_name": "Maya Chen", "duration_hrs": 8, "rating": 4.7, "students": 520, "swatch": 0,
        "description": "When and how to fine-tune a large language model on your own data, versus relying on prompting alone.",
        "lessons": [
            {"title": "Fine-tuning versus prompting", "type": "video", "duration": 14, "body": "Fine-tuning changes model weights; prompting only changes the instructions. Each fits different problems."},
            {"title": "Preparing a training dataset", "type": "text", "duration": 16, "body": "Quality and consistency of examples matter more than sheer volume for most fine-tuning tasks."},
            {"title": "Evaluating a fine-tuned model", "type": "video", "duration": 15, "body": "Comparing the fine-tuned model against the base model on held-out examples before shipping it."},
        ],
        "quiz": [
            {"type": "mcq", "text": "Fine-tuning primarily changes:", "options": ["The user interface", "The model weights", "The internet connection", "The pricing plan"], "answer": 1},
            {"type": "tf", "text": "More training examples always beats better-quality training examples.", "answer": False},
            {"type": "mcq", "text": "Before shipping a fine-tuned model you should:", "options": ["Skip evaluation", "Evaluate against held-out examples", "Delete the base model", "Raise the price"], "answer": 1},
            {"type": "short", "text": "What do we call examples set aside only for evaluation?", "answer": "held-out"},
        ],
    },
    {
        "title": "Building AI Agents and Tool Use", "category": "Generative AI", "level": "Intermediate",
        "instructor_name": "Daniel Osei", "duration_hrs": 6, "rating": 4.6, "students": 860, "swatch": 1,
        "description": "Design agents that can call tools, use memory, and take multi-step actions to complete tasks.",
        "lessons": [
            {"title": "What makes something an agent", "type": "video", "duration": 13, "body": "An agent plans, acts, observes results and decides its next step, rather than answering in one shot."},
            {"title": "Giving agents tools", "type": "text", "duration": 15, "body": "Tools let an agent search, calculate or call an API instead of relying only on what it already knows."},
            {"title": "Memory and multi-step tasks", "type": "video", "duration": 16, "body": "Persisting context across steps lets an agent complete tasks that take more than one action."},
        ],
        "quiz": [
            {"type": "mcq", "text": "What distinguishes an agent from a single model call?", "options": ["It uses more memory hardware", "It plans and takes multiple steps toward a goal", "It only works with images", "It never makes mistakes"], "answer": 1},
            {"type": "tf", "text": "Giving a model access to tools can let it take real actions, like searching or calculating.", "answer": True},
            {"type": "mcq", "text": "Persisting context across steps is called:", "options": ["Memory", "Compression", "Tokenization", "Rendering"], "answer": 0},
            {"type": "short", "text": "What do we call functions an agent can call, like search or a calculator?", "answer": "tools"},
        ],
    },
]

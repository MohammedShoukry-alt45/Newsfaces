# Newsfaces
Bibliotheca Alexandrina Image Naming System
# Bibliotheca Alexandrina Image Naming System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)]()

## 📋 Overview

The Bibliotheca Alexandrina Image Naming System is an advanced, automated solution for naming images extracted from WARC (Web ARChive) files. The system leverages sophisticated face recognition technology, natural language processing, and dynamic enrollment mechanisms to automatically generate descriptive names for images based on their content and associated article metadata.

## 🎯 Key Features

- **Automated Image Processing**: Extract and process images from WARC files
- **Dynamic Face Recognition**: AI-powered face detection and recognition with automated enrollment
- **Intelligent Naming**: Generate descriptive names using face recognition and text metadata
- **Streamlit GUI**: User-friendly interface for system interaction and monitoring
- **Scalable Architecture**: Modular, pipeline-based design for easy scaling
- **Minimal Human Intervention**: Automated processes reduce manual curation needs

## 🏗️ System Architecture

The system follows a modular, pipeline-based approach with the following core components:

```
WARC Files → Content Extraction → Text Analysis → Dynamic Enrollment → Face Recognition → Image Naming → Database Storage
                                                                                                            ↓
                                                                                                      Streamlit GUI
```

### Core Components

1. **WARC Parsing & Content Extraction**
2. **Text Metadata Extraction**
3. **Dynamic Enrollment & Face Database Management**
4. **Image Processing & Face Tagging**
5. **Image Naming Logic**
6. **Database Storage**
7. **Streamlit GUI**

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Required libraries (see requirements.txt)
- Access to image search APIs (Google Custom Search API or Bing Image Search API)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ba-image-naming-system.git
cd ba-image-naming-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Initial Setup

1. **Bulk Enrollment (One-time setup)**:
   ```bash
   python bulk_enrollment.py --dataset lfw --database-path ./data/known_faces.db
   ```

2. **Start the Streamlit Interface**:
   ```bash
   streamlit run app.py
   ```

## 📊 Data Flow

### 1. WARC File Processing
- Parse WARC files to extract HTML content and images
- Identify and download linked images
- Store extracted content with unique identifiers

### 2. Text Metadata Extraction
- **Named Entity Recognition (NER)**: Identify persons, organizations, locations
- **Keyword Extraction**: Extract relevant keywords and phrases
- **Sentiment Analysis**: Analyze emotional tone
- **Topic Classification**: Categorize content into predefined topics
- **Fact vs. Opinion Classification**: Distinguish factual statements from opinions

### 3. Dynamic Face Database Management

#### Phase 1: Initial Bulk Enrollment
- Seed database with Labeled Faces in the Wild (LFW) dataset
- Generate face encodings for thousands of public figures
- One-time setup process for baseline recognition capability

#### Phase 2: Automated Dynamic Enrollment
- Identify prominent individuals from NER analysis
- Automatically search for high-quality images using external APIs
- Apply automated quality checks:
  - Single face detection
  - Face quality assessment (resolution, clarity)
  - Pose estimation (front-facing preference)
  - Content analysis (portrait vs. non-portrait)
- Automatically enroll qualified candidates

### 4. Image Processing & Face Recognition
- Detect faces in extracted images
- Compare against dynamically updated known_faces database
- Generate confidence scores for matches

### 5. Image Naming Convention

Generated names follow the pattern:
```
[recognized_faces]_[keywords]_[named_entities]_[article_topic]_[date]_[image_hash].jpg
```

**Example**: `barack_obama_healthcare_reform_washington_politics_20231026_abc123def456.jpg`

## 💾 Database Schema

### Articles Table
- `article_id` (Primary Key)
- `warc_url`, `warc_date`, `title`, `full_text`
- `sentiment`, `category`, `keywords`, `named_entities`
- `fact_opinion_summary`

### Images Table
- `image_id` (Primary Key)
- `article_id` (Foreign Key)
- `original_url`, `local_path`, `generated_name`
- `face_count`, `detected_faces`, `image_hash`

### Known_Faces Table
- `person_id` (Primary Key)
- `person_name`, `face_encodings`
- `source`, `enrollment_date`

## 🛠️ Configuration

### Environment Variables
```bash
# API Configuration
GOOGLE_CUSTOM_SEARCH_API_KEY=your_api_key
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_engine_id
BING_SEARCH_API_KEY=your_bing_api_key

# Database Configuration
DATABASE_URL=sqlite:///data/ba_image_system.db

# Processing Configuration
FACE_RECOGNITION_TOLERANCE=0.6
MIN_FACE_SIZE=100
MAX_IMAGES_PER_SEARCH=20
```

### Quality Check Parameters
- **Minimum face resolution**: 100x100 pixels
- **Face recognition tolerance**: 0.6 (adjustable)
- **Maximum API results per search**: 20 images
- **Blur detection threshold**: Configurable variance threshold

## 📈 Performance Characteristics

### Processing Times
- **API latency**: 1-3 seconds per search
- **Image quality checks**: <1 second per image
- **Face recognition**: Milliseconds per comparison
- **Database operations**: Milliseconds per operation

### Scalability
- Handles thousands of known faces efficiently
- Modular design supports horizontal scaling
- No model retraining required for new enrollments

## 🔧 API Integration

### Supported Image Search APIs
1. **Google Custom Search API**
   - High-quality results
   - Comprehensive coverage
   - Rate limits apply

2. **Bing Image Search API (Microsoft Azure)**
   - Alternative to Google
   - Good performance
   - Different rate limit structure

## 📱 Streamlit GUI Features

### Main Dashboard
- **WARC Processing Control**: Upload and trigger processing
- **Image Gallery**: View processed images with metadata
- **Search & Filter**: Find images by person, keyword, or topic
- **System Monitoring**: Track processing progress and enrollment status

### Monitoring Features
- Processing pipeline status
- Dynamic enrollment statistics
- Failed enrollment logs
- System performance metrics

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Generate coverage report
python -m pytest --cov=src tests/
```

## 📝 Usage Examples

### Processing a WARC File
```python
from src.warc_processor import WARCProcessor

processor = WARCProcessor(config_path="config.yaml")
results = processor.process_warc_file("path/to/file.warc")
print(f"Processed {len(results)} images")
```

### Manual Face Enrollment
```python
from src.face_enrollment import FaceEnrollment

enrollor = FaceEnrollment(database_path="data/known_faces.db")
enrollor.enroll_person("John Doe", "path/to/john_doe.jpg")
```

## 🚨 Troubleshooting

### Common Issues

1. **API Rate Limits**
   - Implement exponential backoff
   - Consider multiple API providers

2. **Face Recognition Accuracy**
   - Adjust tolerance parameters
   - Ensure high-quality enrollment images

3. **Database Performance**
   - Index frequently queried columns
   - Consider PostgreSQL for large datasets

## 🔮 Future Enhancements

- [ ] Advanced pose estimation for better quality filtering
- [ ] Multi-language NER support
- [ ] Real-time processing capabilities
- [ ] Integration with additional image sources
- [ ] Enhanced GUI with advanced analytics
- [ ] API endpoint for external integrations

## 📚 Dependencies

### Core Libraries
- `face_recognition`: Face detection and recognition
- `warcio`: WARC file processing
- `spacy`: Natural language processing
- `streamlit`: Web interface
- `opencv-python`: Image processing
- `requests`: HTTP requests for API calls

### Machine Learning & NLP
- `transformers`: Hugging Face models
- `nltk`: Natural language toolkit
- `scikit-learn`: Machine learning utilities

### Database & Storage
- `sqlalchemy`: Database ORM
- `sqlite3`: Default database (included in Python)


##  Acknowledgments

- Labeled Faces in the Wild (LFW) dataset contributors
- Face recognition library developers
- Streamlit community


## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team


---

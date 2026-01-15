import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.rag.ingestion import IngestionService
from app.rag.factory import RAGFactory

def main():
    print("Initializing RAG...")
    # Trigger initialization
    RAGFactory.get_vector_store()
    
    cv_text = """
    John Doe
    Senior Software Engineer

    EXPERIENCE

    TechCorp Solutions
    Senior Backend Engineer | Jan 2020 - Present
    - Lead developer for the Core Platform System, used by 25+ internal applications.
    - Built reusable components using Python and React.
    - Improved build times by 40%.

    StartupInc
    Software Developer | Mar 2017 - Dec 2019
    - Developed core modules.
    - Migrated legacy code to Modern Stack.

    EDUCATION
    MSc Computer Science, Tech University
    2011 - 2016
    """
    
    print("Ingesting Mock CV...")
    try:
        nodes = IngestionService.process_text(
            text=cv_text,
            metadata={"filename": "cv_mock.txt", "category": "CV"}
        )
        print(f"Successfully ingested {len(nodes)} nodes.")
    except Exception as e:
        print(f"Ingestion failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

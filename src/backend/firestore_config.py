import os
from google.cloud import firestore
from google.oauth2 import service_account
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FirestoreConfig:
    """Configuration and initialization for Firestore database."""
    
    def __init__(self, project_id: Optional[str] = None, credentials_path: Optional[str] = None):
        """
        Initialize Firestore configuration.
        
        Args:
            project_id: Google Cloud project ID
            credentials_path: Path to service account credentials JSON file
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        self.credentials_path = credentials_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not self.project_id:
            raise ValueError("Google Cloud Project ID is required. Set GOOGLE_CLOUD_PROJECT_ID environment variable.")
        
        # Initialize Firestore client
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
                self.db = firestore.Client(project=self.project_id, credentials=credentials)
                logger.info(f"Firestore initialized with service account: {self.project_id}")
            else:
                # Use default credentials (for local development or GCP deployment)
                self.db = firestore.Client(project=self.project_id)
                logger.info(f"Firestore initialized with default credentials: {self.project_id}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {str(e)}")
            raise
    
    def get_db(self) -> firestore.Client:
        """Get the Firestore database client."""
        return self.db 
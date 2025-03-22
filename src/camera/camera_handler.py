import cv2
import logging
import numpy as np
from typing import Optional, Tuple

class CameraHandler:
    """Handles camera operations including initialization, frame capture, and error handling."""
    
    def __init__(self, camera_id: int = 0, resolution: Tuple[int, int] = (640, 480)):
        """
        Initialize the camera handler.
        
        Args:
            camera_id (int): ID of the camera to use (default: 0 for primary camera)
            resolution (tuple): Desired resolution as (width, height)
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.camera = None
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the camera handler."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('CameraHandler')
        
    def initialize(self) -> bool:
        """
        Initialize the camera connection.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            if not self.camera.isOpened():
                self.logger.error("Failed to open camera")
                return False
            
            # Set resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            self.logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing camera: {str(e)}")
            return False
    
    def capture_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Capture a single frame from the camera.
        
        Returns:
            tuple: (success (bool), frame (numpy array) or None if capture failed)
        """
        if self.camera is None or not self.camera.isOpened():
            self.logger.error("Camera is not initialized")
            return False, None
            
        try:
            success, frame = self.camera.read()
            if not success:
                self.logger.error("Failed to capture frame")
                return False, None
                
            return True, frame
            
        except Exception as e:
            self.logger.error(f"Error capturing frame: {str(e)}")
            return False, None
    
    def release(self):
        """Release the camera resources."""
        if self.camera is not None:
            self.camera.release()
            self.logger.info("Camera released") 
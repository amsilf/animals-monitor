import cv2
import numpy as np
import logging
from typing import Tuple, List, Optional

class ObjectDetector:
    """Handles object detection using motion detection technique."""
    
    def __init__(self, 
                 min_area: int = 500,
                 threshold: int = 30,
                 blur_size: int = 21,
                 dilate_iterations: int = 2):
        """
        Initialize the object detector.
        
        Args:
            min_area (int): Minimum area for motion detection
            threshold (int): Threshold for motion detection
            blur_size (int): Gaussian blur kernel size
            dilate_iterations (int): Number of dilate iterations
        """
        self.min_area = min_area
        self.threshold = threshold
        self.blur_size = blur_size
        self.dilate_iterations = dilate_iterations
        self.background = None
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the object detector."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('ObjectDetector')

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for motion detection.
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            np.ndarray: Preprocessed frame
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)
        return blurred

    def detect_objects(self, frame: np.ndarray) -> Tuple[List[Tuple[int, int, int, int]], np.ndarray]:
        """
        Detect objects in the frame using motion detection.
        
        Args:
            frame (np.ndarray): Input frame
            
        Returns:
            tuple: (List of bounding boxes [(x, y, w, h)], processed frame with boxes drawn)
        """
        processed_frame = frame.copy()
        preprocessed = self.preprocess_frame(frame)

        # Initialize background model if not exists
        if self.background is None:
            # Convert to float32 and proper shape
            self.background = np.float32(preprocessed)
            self.logger.info("Background model initialized")
            return [], processed_frame

        # Calculate difference between current frame and background
        frame_delta = cv2.absdiff(cv2.convertScaleAbs(self.background), preprocessed)
        thresh = cv2.threshold(frame_delta, self.threshold, 255, cv2.THRESH_BINARY)[1]

        # Dilate threshold image to fill in holes
        thresh = cv2.dilate(thresh, None, iterations=self.dilate_iterations)

        # Find contours on thresholded image
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize list for detected objects
        detected_objects = []

        # Process each contour
        for contour in contours:
            if cv2.contourArea(contour) < self.min_area:
                continue

            # Compute the bounding box for the contour
            x, y, w, h = cv2.boundingRect(contour)
            detected_objects.append((x, y, w, h))

            # Draw the bounding box
            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Update background model (ensure both images are float32)
        cv2.accumulateWeighted(np.float32(preprocessed), self.background, 0.2)

        return detected_objects, processed_frame

    def draw_debug_info(self, frame: np.ndarray, objects: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Draw debug information on the frame.
        
        Args:
            frame (np.ndarray): Input frame
            objects (list): List of detected object coordinates
            
        Returns:
            np.ndarray: Frame with debug information
        """
        debug_frame = frame.copy()
        
        # Draw number of detected objects
        cv2.putText(debug_frame, f"Objects: {len(objects)}", 
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return debug_frame 
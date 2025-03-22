import argparse
import logging
from pathlib import Path
import cv2
import time

from src.camera.camera_handler import CameraHandler
from src.camera.object_detector import ObjectDetector
from src.utils.storage import ImageStorage

def parse_args():
    parser = argparse.ArgumentParser(description='Animal Detection Service')
    parser.add_argument('--no-ui', action='store_true', 
                       help='Run without UI display (headless mode)')
    parser.add_argument('--config', type=Path, default=Path('config.json'),
                       help='Path to configuration file')
    return parser.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize components
    camera = CameraHandler()
    detector = ObjectDetector()
    storage = ImageStorage()
    
    # Initialize camera
    if not camera.initialize():
        logger.error("Failed to initialize camera")
        return
    
    logger.info("Starting detection loop")
    try:
        while True:
            # Capture frame
            success, frame = camera.capture_frame()
            if not success:
                logger.error("Failed to capture frame")
                continue
            
            # Detect objects
            objects, processed_frame = detector.detect_objects(frame)
            
            # Save detected objects
            for bbox in objects:
                storage.save_detected_object(frame, bbox)
            
            # Display if UI is enabled
            if not args.no_ui:
                # Add debug information
                display_frame = detector.draw_debug_info(processed_frame, objects)
                cv2.imshow('Animal Detection', display_frame)
                
                # Check for quit command
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # Small sleep to prevent CPU overuse in headless mode
                time.sleep(0.01)
                
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        camera.release()
        if not args.no_ui:
            cv2.destroyAllWindows()
        logger.info("Cleanup complete")

if __name__ == "__main__":
    main() 
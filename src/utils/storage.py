import os
import json
from datetime import datetime
import shutil
from pathlib import Path
import logging
from typing import Dict, Any, Tuple, Union
import cv2

class ImageStorage:
    def __init__(self, base_path="storage", max_storage_gb=10):
        """Initialize the image storage system.
        
        Args:
            base_path (str): Base directory for storing images
            max_storage_gb (float): Maximum storage limit in gigabytes
        """
        # Setup logging first
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Then initialize paths
        self.base_path = Path(base_path)
        self.images_path = self.base_path / "images"
        self.max_storage_bytes = max_storage_gb * 1024 * 1024 * 1024
        
        # Add last save timestamp tracking
        self.last_save_timestamp = None
        self.min_save_interval = 10  # seconds
        
        # Finally, create directory structure
        self._init_directory_structure()

    def _init_directory_structure(self):
        """Create the necessary directory structure."""
        try:
            # Create main directories
            self.images_path.mkdir(parents=True, exist_ok=True)
            
            # Create today's directory
            today_dir = self.images_path / datetime.now().strftime("%Y-%m-%d")
            today_dir.mkdir(exist_ok=True)
            
            # Update 'latest' symlink
            latest_link = self.images_path / "latest"
            try:
                if latest_link.exists():
                    latest_link.unlink()
                latest_link.symlink_to(today_dir, target_is_directory=True)
            except OSError as e:
                self.logger.warning(f"Could not create symlink: {e}. Continuing without symlink.")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize directory structure: {e}")
            raise

    def generate_filename(self, object_id: str) -> Tuple[str, Path]:
        """Generate a unique filename for the image.
        
        Args:
            object_id: Identifier for the detected object
        
        Returns:
            tuple: (filename, full_path)
        """
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"{timestamp}_object_{object_id}.jpg"
        current_date = datetime.now().strftime("%Y-%m-%d")
        full_path = self.images_path / current_date / filename
        return filename, full_path

    def save_detected_object(self, frame: Any, bbox: Tuple[int, int, int, int]) -> bool:
        """Save a detected object and its metadata.
        
        Args:
            frame: Frame containing the detected object
            bbox: Bounding box tuple (x, y, w, h)
        
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Check rate limiting
            current_time = datetime.now()
            if self.last_save_timestamp is not None:
                time_diff = (current_time - self.last_save_timestamp).total_seconds()
                if time_diff < self.min_save_interval:
                    self.logger.info(f"Skipping save: minimum interval ({self.min_save_interval}s) not reached. Only {time_diff:.1f}s elapsed.")
                    return False

            if not self._check_storage_space():
                self.cleanup_old_files()
                if not self._check_storage_space():
                    raise RuntimeError("Insufficient storage space")

            # Generate unique object ID using timestamp
            object_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            
            # Create metadata
            x, y, w, h = bbox
            metadata = {
                'object_id': object_id,
                'timestamp': datetime.now().isoformat(),
                'bbox': {
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h
                },
                'frame_size': {
                    'width': frame.shape[1],
                    'height': frame.shape[0]
                }
            }

            # Generate filename and paths
            _, full_path = self.generate_filename(object_id)
            
            # Draw rectangle around detected object
            frame_with_box = frame.copy()
            cv2.rectangle(frame_with_box, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add timestamp to the image
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame_with_box, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Save the full frame with bounding box
            cv2.imwrite(str(full_path), frame_with_box)

            # Save metadata
            metadata_path = full_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Update last save timestamp after successful save
            self.last_save_timestamp = current_time
            self.logger.info(f"Saved frame with detected object to {full_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save detected object: {e}")
            return False

    def _check_storage_space(self) -> bool:
        """Check if there's enough storage space available."""
        total, used, free = shutil.disk_usage(self.base_path)
        return free > self.max_storage_bytes * 0.1  # Keep 10% buffer

    def cleanup_old_files(self, days_to_keep: int = 7) -> None:
        """Remove files older than specified days."""
        try:
            current_time = datetime.now()
            for date_dir in self.images_path.iterdir():
                if not date_dir.is_dir() or date_dir.name == "latest":
                    continue
                    
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                    if (current_time - dir_date).days > days_to_keep:
                        shutil.rmtree(date_dir)
                        self.logger.info(f"Removed old directory: {date_dir}")
                except ValueError:
                    continue

        except Exception as e:
            self.logger.error(f"Failed to cleanup old files: {e}") 
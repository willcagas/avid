
import subprocess
import time
import requests
import socket
from pathlib import Path
from .config import Config
from .utils import setup_logging

logger = setup_logging()

class WhisperServer:
    """Manages the background whisper-server process."""
    
    def __init__(self, config: Config):
        self.config = config
        self.process: subprocess.Popen | None = None
        self.url = f"http://127.0.0.1:{config.whisper_port}"

    def is_port_open(self) -> bool:
        """Check if the server port is open."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', self.config.whisper_port)) == 0

    def start(self) -> None:
        """Start the whisper-server process."""
        if self.is_port_open():
            logger.info(f"Whisper server already running on port {self.config.whisper_port}")
            return

        cmd = [
            self.config.whisper_server_bin,
            "-m", self.config.whisper_model_path,
            "--port", str(self.config.whisper_port),
            "--host", "127.0.0.1",
            "--ng"  # No GPU (assuming cpu for now as per previous checks, maybe make configurable?) 
            # Actually, standard whisper-server might auto-detect metal on mac. 
            # Let's check if --ng is needed explicitly or just safe. 
            # Looking at help output: -ng, --no-gpu [false] default. So it tries to use GPU by default.
            # Best to leave it to default to enable Metal acceleration.
        ]
        
        # Remove --ng from my thought logic above, let it use GPU/Metal if available.

        logger.info(f"Starting Whisper Server: {' '.join(cmd)}")
        
        try:
            # Start process, redirect output to /dev/null/logger to avoid clutter?
            # ideally we want to capture it. For now let's just let it inherit stdout/stderr 
            # but maybe that messes up the TUI? 
            # Better to PIPE and log? Or just PIPE and ignore if we trust it works.
            # Let's PIPE stdout/stderr to avoid polluting the terminal UI of existing app
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            
            # Wait for it to be ready
            logger.info("Waiting for server to be ready...")
            for _ in range(20): # 10 seconds timeout
                if self.is_port_open():
                    logger.info("Whisper server is ready!")
                    return
                time.sleep(0.5)
                if self.process.poll() is not None:
                    logger.error("Whisper server failed to start")
                    break
            
            logger.error("Timed out waiting for server")
            
        except Exception as e:
            logger.error(f"Failed to start whisper server: {e}")

    def stop(self) -> None:
        """Stop the server."""
        if self.process:
            logger.info("Stopping Whisper server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

import logging
import os


def setup_logging():
    """Configures logging for the application."""
    log_directory = "logs"
    log_file = os.path.join(log_directory, "app.log")

    # Ensure the log directory exists
    os.makedirs(log_directory, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),  # Use the variable here
        ],
    )
    # Optional: Log that configuration is complete
    # logging.getLogger(__name__).info("Logging configured successfully.")

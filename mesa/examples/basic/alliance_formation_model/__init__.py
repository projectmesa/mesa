import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Example usage of logging
logger = logging.getLogger(__name__)
logger.info("Logging is configured and ready to use.")

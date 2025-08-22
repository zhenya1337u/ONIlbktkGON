import logging
import os
import sys
import tempfile

log_file = os.path.join(tempfile.gettempdir(), "system_service.log")

is_frozen = getattr(sys, 'frozen', False)

log_handlers = [logging.FileHandler(log_file)]

if not is_frozen:
    log_handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=log_handlers
)



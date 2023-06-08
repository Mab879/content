from datetime import datetime
from uuid import uuid4

from trestle.oscal.common import Metadata


def get_uuid() -> str:
    return str(uuid4())


def create_metadata(title: str) -> Metadata:
    metadata = Metadata(title=title,
                        last_modified=datetime.now().astimezone(),
                        version="0.1.69",
                        oscal_version='1.0.4')
    return metadata

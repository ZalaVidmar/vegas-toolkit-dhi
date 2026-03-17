import os
import json
import logging
from mutagen import File as MutagenFile
from mutagen.id3 import ID3NoHeaderError

# Configure logging
logging.basicConfig(level=logging.INFO)

class MetadataExtractor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.metadata = {}

    def extract_metadata(self):
        """Extract metadata from the media file."""
        if not os.path.exists(self.filepath):
            logging.error(f"File not found: {self.filepath}")
            return {"error": "File not found"}

        try:
            media = MutagenFile(self.filepath, easy=True)
            if media is None:
                logging.warning("Could not read the media file.")
                return {"error": "Could not read media file"}

            # Gather metadata
            self.metadata['filename'] = os.path.basename(self.filepath)
            self.metadata['extension'] = os.path.splitext(self.filepath)[1]
            self.metadata['size'] = os.path.getsize(self.filepath)

            # Extracting specific metadata
            if 'title' in media:
                self.metadata['title'] = media['title'][0]
            if 'artist' in media:
                self.metadata['artist'] = media['artist'][0]
            if 'album' in media:
                self.metadata['album'] = media['album'][0]
            if hasattr(media, 'info') and media.info and hasattr(media.info, 'length'):
                self.metadata['duration'] = media.info.length

            logging.info(f"Metadata extracted for {self.filepath}")
            return self.metadata

        except ID3NoHeaderError:
            logging.error("No ID3 header found. This might not be an MP3 file.")
            return {"error": "No ID3 header found"}
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return {"error": str(e)}

def save_metadata(metadata, output_file):
    """Save extracted metadata to a JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        logging.info(f"Metadata saved to {output_file}")
    except Exception as e:
        logging.error(f"Failed to save metadata: {e}")

# TODO: Add support for more file types and metadata fields.
# TODO: Implement command-line interface for easier usage.
# TODO: Write unit tests to ensure reliability of the extraction process.

if __name__ == "__main__":
    # This will be called from main.py, so it's left empty intentionally.
    pass

import os
import json
import exifread

def get_image_metadata(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
    return tags

def extract_coordinates(metadata):
    latitude = None
    longitude = None
    if 'GPS GPSLatitude' in metadata and 'GPS GPSLongitude' in metadata:
        lat_deg = metadata['GPS GPSLatitude'].values[0].num / metadata['GPS GPSLatitude'].values[0].den
        lat_min = metadata['GPS GPSLatitude'].values[1].num / metadata['GPS GPSLatitude'].values[1].den
        lat_sec = metadata['GPS GPSLatitude'].values[2].num / metadata['GPS GPSLatitude'].values[2].den
        latitude = lat_deg + lat_min / 60.0 + lat_sec / 3600.0

        lon_deg = metadata['GPS GPSLongitude'].values[0].num / metadata['GPS GPSLongitude'].values[0].den
        lon_min = metadata['GPS GPSLongitude'].values[1].num / metadata['GPS GPSLongitude'].values[1].den
        lon_sec = metadata['GPS GPSLongitude'].values[2].num / metadata['GPS GPSLongitude'].values[2].den
        longitude = lon_deg + lon_min / 60.0 + lon_sec / 3600.0
    return latitude, longitude

def read_metadata(metadata_file):
    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print("Error reading metadata file:", e)
        metadata = {}
    return metadata

def create_json_ld(image_path, location_name, latitude, longitude, subjects):
    # Construct relative path of the image file
    relative_path = os.path.relpath(image_path, os.getcwd())

    # Construct raw URL of the image file on GitHub
    prefix = "https://raw.githubusercontent.com/jsimonclark/FjordHealthDashboard/main/"
    raw_url = prefix + relative_path.replace("\\", "/")  # Replace backslashes with forward slashes
    
    json_ld = {
        "@context": "http://schema.org",
        "@type": "ImageObject",
        "contentUrl": raw_url,
        "locationCreated": {
            "@type": "Place",
            "name": location_name,
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": latitude,
                "longitude": longitude
            }
        },
        "keywords": subjects,
        "about": {
            "@id": "https://www.wikidata.org/wiki/Q45701",
            "@type": "Thing",
            "name": "trash"
        }
    }
    return json_ld

def main():
    # Get directory containing the script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Specify the directory containing the images relative to the script directory
    images_dir = os.path.join(script_dir, "data", "img", "trondheimsfjord", "2024-03-02")

    # Read metadata from metadata.json file
    metadata_file = os.path.join(images_dir, "metadata.json")
    metadata = read_metadata(metadata_file)

    # Extract location information from metadata
    location_name = metadata.get("locationCreated", {}).get("name", "")
    latitude = metadata.get("locationCreated", {}).get("geo", {}).get("latitude", "")
    longitude = metadata.get("locationCreated", {}).get("geo", {}).get("longitude", "")

    # Example subjects
    subjects = ["trash"]

    # Iterate through image files
    for image_file in os.listdir(images_dir):
        if image_file.endswith(".jpg") or image_file.endswith(".jpeg"):  # Adjust file extension as needed
            # Get image path
            image_path = os.path.join(images_dir, image_file)

            # Get image metadata
            metadata = get_image_metadata(image_path)

            # Extract latitude and longitude from image metadata
            latitude_img, longitude_img = extract_coordinates(metadata)

            # Override location information if available in image metadata
            if latitude_img is not None and longitude_img is not None:
                latitude = latitude_img
                longitude = longitude_img

            # Create JSON-LD metadata
            json_ld = create_json_ld(image_path, location_name, latitude, longitude, subjects)

            # Convert JSON-LD to string
            json_ld_string = json.dumps(json_ld, indent=4)

            # Write JSON-LD to a file (with the same name as the image file but with .json extension)
            json_file_path = os.path.splitext(image_path)[0] + ".json"
            try:
                with open(json_file_path, "w") as f:
                    f.write(json_ld_string)
            except Exception as e:
                print("Error writing JSON file:", e)

if __name__ == "__main__":
    main()

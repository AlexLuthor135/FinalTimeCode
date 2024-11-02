import xml.etree.ElementTree as ET


def main():

    # Load and parse the XML file
    tree = ET.parse('D:\Projects\FinalTimecode\Info.fcpxml')
    root = tree.getroot()

    # Get the FCPXML version
    fcpxml_version = root.get('version')
    print("FCPXML Version:", fcpxml_version)

    # Extract information from the resources section
    resources = root.find('resources')
    for format_tag in resources.findall('format'):
        format_id = format_tag.get('id')
        width = format_tag.get('width')
        height = format_tag.get('height')
        print(f"Format ID: {format_id}, Width: {width}, Height: {height}")

    # Extract information from assets in resources
    for asset_tag in resources.findall('asset'):
        asset_id = asset_tag.get('id')
        asset_name = asset_tag.get('name')
        src = asset_tag.find('media-rep').get('src')  # Get media source URL
        print(f"Asset ID: {asset_id}, Name: {asset_name}, Source: {src}")

    # Extract project information
    library = root.find('library')
    for event in library.findall('event'):
        event_name = event.get('name')
        for project in event.findall('project'):
            project_name = project.get('name')
            print(f"Event: {event_name}, Project: {project_name}")

    # Extract sequence details
    for project in event.findall('project'):
        sequence = project.find('sequence')
        if sequence is not None:
            duration = sequence.get('duration')
            audio_rate = sequence.get('audioRate')
            print(f"Sequence Duration: {duration}, Audio Rate: {audio_rate}")

    # Extract chapter markers from asset-clips
    for asset_clip in sequence.find('spine').findall('asset-clip'):
        for chapter_marker in asset_clip.findall('chapter-marker'):
            start = chapter_marker.get('start')
            value = chapter_marker.get('value')
            print(f"Chapter Marker: {value}, Start: {start}")


if __name__ == '__main__':
    main()
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
import bs4
import concurrent.futures

def html_to_dict(html_file):
    with open(html_file, 'r') as file:
        file_content = file.read()
        if file_content.startswith('<?xml'):
            try:
                soup = BeautifulSoup(file_content, 'xml')
            except bs4.builder.ParserRejectedMarkup:
                print(f"Skipping file: {html_file} due to parsing error")
                return None
        else:
            try:
                soup = BeautifulSoup(file_content, 'html.parser')
            except bs4.builder.ParserRejectedMarkup:
                print(f"Skipping file: {html_file} due to parsing error")
                return None

    # Extract the title
    title = soup.title.string if soup.title else ''

    sections = []
    current_section = {}

    # Find the first h tag of any number
    first_h_tag = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    # If no h tag is found, return an empty result
    if first_h_tag is None:
        return {'title': title, 'sections': []}

    # If title is empty, use the first h tag text as the title
    if not title:
        title = first_h_tag.get_text(strip=True)

    # Start processing from the first h tag
    for tag in first_h_tag.find_all_next(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        if tag.name.startswith('h'):
            # Start a new section for each h tag
            if current_section:
                sections.append(current_section)
            current_section = {
                'section_title': tag.get_text(strip=True),
                'section_body': ''
            }
        else:
            # Add the text of each 'p' tag to the current section body
            if 'section_body' in current_section:
                current_section['section_body'] += tag.get_text(strip=True) + '\n'
            else:
                current_section['section_body'] = tag.get_text(strip=True) + '\n'

    # Add the last section
    if current_section:
        sections.append(current_section)

    result = {
        'title': title,
        'sections': sections
    }

    return result

def batch_convert(directory):
    # Get the current date and time
    now = datetime.now()

    # Format it as a string
    timestamp = now.strftime('%Y%m%d%H%M%S')

    # Get the output directory path
    output_directory = directory

    # Open the output file
    with open(os.path.join(output_directory, f'output_{timestamp}.json'), 'w') as outfile:
        # Parse multiple HTML files concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            html_files = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith('.html')]
            for html_dict in executor.map(html_to_dict, html_files):
                # Write each JSON object to the file separately, followed by a newline
                json.dump(html_dict, outfile)
                outfile.write('\n')

    # Calculate the number of processed files
    num_files = len(html_files)

    # Calculate the processing time in seconds
    processing_time = (datetime.now() - now).total_seconds()

    # Print the result
    print(f"Processed {num_files} files in {processing_time} seconds")

# Use the function
# batch_convert('/Users/christopherdickson/Downloads/Biztory.com')
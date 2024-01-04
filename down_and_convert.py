from htmldown import download_html
from htmltojson import batch_convert

# Set the URL and filepath
url = 'https://developer.harness.io/docs/'
depth = 5
download_filepath = '/Users/christopherdickson/Downloads/harness'

# Call the download_html function
# download_html(url, depth, download_filepath)

# Call the batch_convert function
batch_convert(download_filepath)
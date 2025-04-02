This porject is trying to convert PDF files into MD format by using an agentic approach using autogen and the agentic framework. Here's are instructions about this this project "PDF to Markdown Converter - Setup and Usage Instructions
Prerequisites
Python 3.8 or higher installed on your system
Poppler for PDF processing (required for image extraction)
macOS: brew install poppler
Linux: sudo apt-get install -y poppler-utils
Windows: Download from http://blog.alivate.com.au/poppler-windows/ and add to PATH
Setup Instructions
Clone the repository:
Apply to config.py
Run
converter
Create and activate a virtual environment:
Apply to config.py
Run
activate
Install dependencies:
Apply to config.py
Run
txt
Configure Azure OpenAI settings:
Create a .env file in the project root with the following content:
Apply to config.py
40000
Testing the Configuration
Before running the main application, test the Azure OpenAI configuration:
Apply to config.py
Run
py
This will verify that your Azure OpenAI connection is working correctly.
Running the Converter
Run the converter script:
Apply to config.py
Run
py
Input file:
The script is currently configured to use a hardcoded input file path:
/Users/mannamraju/localCode/DMAIO-ST-One-Data-Feed-Kubernetes-Edge-270325-191539.pdf
To use a different file, edit src/run_converter.py and change the input_file variable.
Output:
The converted markdown will be saved to the output directory with the same name as the input file but with a .md extension.
Project Structure
Apply to config.py
md
Troubleshooting
If you encounter API errors, check your Azure OpenAI configuration in the .env file
Ensure you're using the correct model name and API version
The model doesn't support some parameters like temperature, so they've been removed from the configuration
Always run the test script first to verify your configuration before running the main application"
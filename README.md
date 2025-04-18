

Install Python.

Clone this repository.

Create the virtual environment.

 python -m venv env

Activate the virtual environment.

 env/Scripts/activate.bat

Install streamlit using pip.

 pip install streamlit

Install langchain and groq using pip.

 pip install langchain-groq

Install requests using pip

pip install requests

Set an environment variable for the Groq API Key

In Command Prompt(cmd)

set GROQ_API_KEY=your_api_key_here

In Powershell

$env:GROQ_API_KEY = "your_api_key_here"

Verifying whether the environment variable is set

In Command Prompt(cmd)

echo %GROQ_API_KEY%

In Powershell

echo $env:GROQ_API_KEY

If set it will show your original API key.

If required, you can upgrade pip(optional)

python -m pip install --upgrade pip


how to run 

 streamlit run legalAI.py

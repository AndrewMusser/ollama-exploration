# OVERVIEW
This repo showcases a simple Python app that retrieves machine logs from a B&R PLC, and uses an LLM to ask questions related to the machine status. What makes this particularly interesting is that the LLM here is 100% local: we're using Ollama to run Meta's Llama3.1 8B model on a local workstation. 

# SETUP
You will need to first install Ollama locally: https://ollama.com/. Once installed, you'll need to pull the desired model. This app uses `llama3.1`. 

Next you will need to have an Ethernet connection from your workstation to a B&R PLC. This can be ARsim or a physical machine. Make sure you can ping the PLC.

Install the Python requirements from the requirements.txt file. 

# USAGE
Spin up the app from the `src` folder with the following command: `streamlit run app.py`. This will pull up a web page, and you can start chatting with the bot. You should ask questions that can be answered with information from the PLC's logbook, and you should specify the machine's IP address in the question so the app can pull the logs. Here's an example prompt: 'Maintenance reported an error earlier this week on our bagger machine with IP address 127.0.0.1. What happened?'


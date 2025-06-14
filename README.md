
# TDS Virtual TA (using RAG)

This repository provides a minimal end-to-end example of a RAG pipeline using:

- Sentence-Transformers for embeddings
- FAISS for vector similarity search
- httpx for querying OpenAI-compatible APIs
- FastAPI to serve the end user API



## Installation

1. **Clone this repository**  
   ```bash
   git clone https://github.com/arjun-pukale-iitm/tds-project-1-rag
   cd tds-project-1-rag
   ```

2. **Create a virtual environment and activate it**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
3. **Install PyTorch (CPU version) separately**  
   We will use a lightweight torch cpu package
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```
   
4. **Install other dependencies**  
   ```bash
   pip install -r requirements.txt
   ```



## Environment Variables

Create a `.env` file in the root directory with the following entries:

```dotenv
OPENAI_API_KEY=your_openapi_key

OPENAI_API_URL=https://aipipe.org/openrouter/v1/chat/completions

OPENAI_MODEL=gpt-4o-mini

DISCOURSE_COOKIE_STRING="ga_MXPR4XHYG9=GS2.1.s1749004062; _ga=GA1.1.251; _ga_5HTJMW67XK=GS2.1.s174; _ga_WGM85Z9ZZV=GS1.1.1723427; _ga_08NPRH5L4M=GS1.1.17196; _t=zC%2Fzfnh2PunFrDtR6t2oeXUcdHb; _gcl_au=1.1.6450; _gid=GA1.3.17076; _forum_session=xhm4TEUxyfE%2BZ8qyI7ZUUTul"
```
⚠️ Replace the above `OPENAI_API_KEY` , `OPENAI_API_URL` with your own openapi credentials.

⚠️ Replace the above `DISCOURSE_COOKIE_STRING` with your own valid Discourse cookie string, which you can extract from browser DevTools while logged into the forum.

## Steps to download and train the RAG model (optional)

1. Run the `discourse_downloader.py` script to download the discourse content. 

    ```python -m discourse_downloader```

2. Run the `website_downloader.py` script to download the course website content. 

    ```python -m website_downloader```

3. Run the `train_rag.py` script to train the RAG model on the downloaded data and save the model. 

    ```python -m train_rag```

**Note**: This repo already contains a saved RAG model in the ```rag_model``` directory.

##  Start the FAST API server
```uvicorn app:app ```

##  API Request

 - url: ```http://localhost:<port>/api```
 - method: ```POST``` 
 - request body:
	```
	{
	  "question":"I know Docker but have not used Podman before. Should I use Docker for this course?"
	}
	```
 - response body:

	```
	{
	  "answer": "While Docker is the industry standard, the course recommends using Podman due to its compatibility with Docker and better security features. If you are familiar with Docker, you should find it easy to transition to Podman, as it works in a similar way. Therefore, it would be beneficial to try using Podman for this course.",
	  "links": [
	    {
	      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga2-deployment-tools-discussion-thread-tds-jan-2025/161120/22",
	      "text": "Thank you, Sir! What is the Docker image URL? It should look like: https://hub.docker.com/repository/docker/$USER/$REPO/general If I use Podman, will the answer be correct assuming I have done all ste"
	    },
	    {
	      "url": "https://tds.s-anand.net/#/docker",
	      "text": "Title: Containers: Docker, Podman\nContent: Containers: Docker, Podman Docker and Podman are containerization tools that package your application and its dependencies into a standardized unit for softw"
	    },
	    {
	      "url": "https://discourse.onlinedegree.iitm.ac.in/t/project-1-llm-based-automation-agent-discussion-thread-tds-jan-2025/164277/502",
	      "text": "There has been an outage in some parts of the country related to cloudflare servers. What helped some students (and us) is using a completely different network eg. instead of using your home wifi, use"
	    }
	  ]
	}
	```

## License

MIT License

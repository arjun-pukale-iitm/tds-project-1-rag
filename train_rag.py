import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from application.rag import RAG


DISCOURSE_BASE_URL = "https://discourse.onlinedegree.iitm.ac.in/"


def cleanHtmlTags(text):
  try:
    clean_text = BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)
  except:
    clean_text = text
  return clean_text




def cleanDataAndTrain():


    # Discourse Threads
    thread_docs = []
    with open('discourse_content.json', 'r') as f:
        all_thread_posts = json.load(f)
        for post_data in all_thread_posts:
            title = cleanHtmlTags(post_data['title'])
            question = post_data['question']
            answer = cleanHtmlTags(post_data['body'])

            if(post_data['post_replied_to']):
                question = post_data['post_replied_to']

            question = cleanHtmlTags(question)
            doc_text = f"Title: {title}\nQuestion: {question[:300]}\nAnswer: {answer}"
            doc_url = urljoin(DISCOURSE_BASE_URL, post_data['url'])
            thread_docs.append({"text": doc_text, "url": doc_url, "answer":answer})

        print("\nCreated thread_docs from all_thread_posts:")
        print(f"\nTotal thread_docs created: {len(thread_docs)}")

    # Website content
    content_docs = []
    with open('website_content.json', 'r') as f:
        website_content = json.load(f)
        for content in website_content:
            title = cleanHtmlTags(content['title'])
            text = content['content']
            doc_url = content['original_url']
            answer = ""
            doc_text = f"Title: {title}\nContent: {text[:1000]}"
            content_docs.append({"text": doc_text, "url": doc_url, "answer":answer})

    print("\nCreated content_docs !")
    print(f"\nTotal content_docs created: {len(content_docs)}")


    combined_docs = []
    combined_docs.extend(thread_docs)
    combined_docs.extend(content_docs)
    print(f"\nTotal combined docs: {len(combined_docs)}")

    print("\nRAG Training started...")
    rag = RAG(combined_docs)
    rag.save()
    print("RAG model saved !")


if __name__ == '__main__':
   cleanDataAndTrain()

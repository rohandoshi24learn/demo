#Final app.py 
#import files
import os
import sys
from dotenv import load_dotenv
from termcolor import colored
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from flask import Flask, render_template, request
import io
import requests
import sounddevice as sd
import wavio
import openai

load_dotenv('.env.example')
openai.api_key = "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"

documents = []
# Create a List of Documents from all of our files in the ./docs folder
for file in os.listdir("docs"):
    if file.endswith(".pdf"):
        pdf_path = "./docs/" + file
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
    elif file.endswith('.docx') or file.endswith('.doc'):
        doc_path = "./docs/" + file
        loader = Docx2txtLoader(doc_path)
        documents.extend(loader.load())
    elif file.endswith('.txt'):
        text_path = "./docs/" + file
        loader = TextLoader(text_path)
        documents.extend(loader.load())

# Split the documents into smaller chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
documents = text_splitter.split_documents(documents)

# Convert the document chunks to embedding and save them to the vector store
vectordb = Chroma.from_documents(documents, embedding=OpenAIEmbeddings(), persist_directory="./data")
vectordb.persist()

# create our Q&A chain
pdf_qa = ConversationalRetrievalChain.from_llm(
    ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'),
    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
)
#import openai
app = Flask(__name__)
#openai.api_key  = "<place your openai_api_key>"
chat_history = []
def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response=""
    response = pdf_qa({"question": prompt, "chat_history": chat_history})
    chat_history.append((prompt, response["answer"]))
    return  response["answer"]
@app.route("/")
def home():    
    return render_template("index.html")
@app.route("/get")
def get_bot_response():    
    userText = request.args.get('msg')  
    response = get_completion(userText)  
    #return str(bot.get_response(userText)) 
    return response
if __name__ == "__main__":
    app.run()

@app.route("/record1")
def record_audio1(filename, duration, fs):
    print("Recording audio...")
    return "Hello Test"

@app.route("/record")
def record_audio(filename, duration, fs):
    print("Recording audio...")
    duration=5
    fs=16000
    filename="test.mp3"
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    wavio.write(filename, recording, fs, sampwidth=2)
    print("Audio recorded and saved as", filename)
    transcribtion=transcribe_audio(filename)
    return transcribtion


# Transcribe audio using Whisper ASR API
def transcribe_audio(filename):
    print("Transcribing audio...")
    with open(filename, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            file = audio_file,
            model = "whisper-1",
            response_format="text",
            language="en"
        )
    print(transcript)

    
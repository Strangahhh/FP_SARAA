from django.shortcuts import render
import ollama

def resx(message):
    prompt = message
    output = ollama.generate(model="strangex/saraa-s:latest", prompt=prompt)
    output = output['response']
    return output



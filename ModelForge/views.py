from django.shortcuts import render
import ollama

def resx(message):
    prompt = message
    output = ollama.generate(model="Saraa-s", prompt=prompt)
    output = output['response']
    return output

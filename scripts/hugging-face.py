from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("I love you")
print(result)
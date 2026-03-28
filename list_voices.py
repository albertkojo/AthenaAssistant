import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty("voices")

for i, v in enumerate(voices):
    print(f"[{i}] Name: {v.name}")
    print(f"    ID:   {v.id}")
    print(f"    Lang: {v.languages}")
    print()
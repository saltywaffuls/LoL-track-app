




"""
Goal: Use OpenAI’s API to translate raw stats into coaching advice.

Setup OpenAI API

pip install openai

Store your OpenAI key in .env.

Prompt Crafting

Write a function that, given your numeric metrics, builds a prompt like:

“I averaged 5.2 CS/min, a 2.0 KDA, and 45% win rate last week. Provide three actionable tips to improve.”

Call the API

Exercise:

Integrate this into your CLI so python main.py advice YourSummonerName fetches stats and returns ChatGPT tips.

"""
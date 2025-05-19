

champion_list = ["Syndra", "Syalas", "viktor", "LeBlanc", "Orrianna"]

def check_KDA(kda):

   if kda <= 1.0:
       return "Needs Work"
   elif kda <= 2.0:
       return "Okay"
   else:
         return "Good"

def game_duration():

    gameTime = [15,25,35,45,60]

    for i in gameTime:
        if i > 30:
            print(f"Game time is {i} minutes")
        else:
            print("Game time is less than 30 minutes")

            
class PerformanceAnalyzer:
    def __init__(self, kda):
        self.kda = kda

    def analyzerKDA(self):
        return check_KDA(self.kda)




"""
Core Concepts in Practice

Variables & Data Types: write a script that stores your top 5 ranked champions in a list and prints them.

Control Flow: write a function that, given a numeric “KDA” value, returns a string “good”, “okay”, or “needs work”.

Loops & Functions: write a loop that reads a list of game durations (ints) and prints how many are over 30 minutes.

Classes & Modules: bundle that KDA logic into a PerformanceAnalyzer class in its own file, then import it into your main script.

"""
import pickle
import random
from dictionary import negativeWordsInRoman, apologiseComments, happyComments, greetingsList, highRating, lowRating, helpline
from dictionary import helplineFeedback, negativeSuggestionFeedback, positiveSuggestionFeedback, namingDict, positiveWordsInRoman
import os

def getModelandVector():
    model_path = "model.pkl"
    vectorizer_path = "vectorizer.pkl"

    model = ""
    vectorizer = ""

    if not os.path.exists(model_path):
      print(f"File not found: {model_path}")
    elif not os.access(model_path, os.R_OK):
      print(f"No read permissions for file: {model_path}")
    else:
      try:
        with open(model_path, "rb") as file:
          model = pickle.load(file)
          print("Model loaded successfully!")
      except pickle.PickleError as e:
        print(f"Error loading pickle file: {e}")
      except Exception as e:
        print(f"An unexpected error occurred: {e}")

    
    with open(vectorizer_path, "rb") as file:
        vectorizer = pickle.load(file)

    return model, vectorizer

def generateResponse(name, comment, predictedRating):
  temp = name
  temp = temp.lower()
  greetings = ""
  if temp in namingDict:
     name = "Valuable Customer"
     greetings = "Dear"
  elif len(temp) > 30:
     name = "Valuable Customer"
     greetings = "Dear"
  else:
     greetings = random.choice(greetingsList)
  

  if(predictedRating == 1.0 or predictedRating == 2.0):
      response = random.choice(apologiseComments)
      finalResponse = greetings + " " + name + ", " +  response
      return finalResponse

  elif(predictedRating == 3.0):
      response = random.choice(highRating)
      #greetings = random.choice(greetingsList)
      finalResponse = greetings + " " + name + ", " +  response
      return finalResponse

  elif(predictedRating == 4.0 or predictedRating == 5.0):
      response = random.choice(happyComments)
      #greetings = random.choice(greetingsList)
      finalResponse = greetings + " " + name + ", " +  response
      return finalResponse


def preprocessComment(comment):
    #print("PREPROCESS", comment)
    comment = comment.lower()

    for word in helpline:
      #print(word)
      if word in comment:
          #comment = comment.replace(word, "bakwas")
          comment = "helpline number"
          return comment
    #print("PREPROCESS 2", comment)
    for word in negativeWordsInRoman:
      #print(word)
      if word in comment:
          #comment = comment.replace(word, "bakwas")
          comment = "bakwas"
          return comment
      
    for word in positiveWordsInRoman:
      #print(word)
      if word in comment:
          #comment = comment.replace(word, "bakwas")
          comment = "good"
          return comment
    #print("PREPROCESS 3", comment)

    return comment


def getResponse(name, comment):
    model, vectorizer = getModelandVector()
    processedComment = preprocessComment(comment)
    print(processedComment)
    if(processedComment == "helpline number"):
        response = helplineFeedback
        greetings = random.choice(greetingsList)
        finalResponse = greetings + " " + name + " , " +  response
        return finalResponse, "Help"
    else:
        category = ""
        if(processedComment == "bakwas"):
           category="Negative Comment"
        else:
           category="Positive Comment"
        new_query = [processedComment]
        new_query_tfidf = vectorizer.transform(new_query)
        predicted_star_rating = model.predict(new_query_tfidf)
        predictedRating = float(predicted_star_rating[0])
        finalResponse = generateResponse(name, processedComment, predictedRating)
        return finalResponse, category
      


#print(preprocessComment("app is not good"))

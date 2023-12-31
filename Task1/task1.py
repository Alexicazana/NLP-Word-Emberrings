import gensim.downloader as api
import pandas as pd
import numpy as np

# Function to find closest synonym;
# Take each row of the dataset
# Extract the question word and compare it with each of the four guess words (0 to 3)
# Determine which guess word is most similar to the question word based on the model's similarity measure
# Compare the most similar guess word with the answer word to determine if 
# the guess is correct, wrong, or a guess (if the words are not found in the model)
def find_closest_synonym(row, model):
    question_word = row['question']
    answer_word = row['answer']
    guess_words = [row[str(i)] for i in range(4)]

    # Check if question word is in model
    if question_word not in model.key_to_index:
        return question_word, answer_word, None, 'guess'

    # Filter out guess words not in the model
    valid_guess_words = [word for word in guess_words if word in model.key_to_index]

    # If no valid guess words, return guess label
    if not valid_guess_words:
        return question_word, answer_word, None, 'guess'

    # Compute similarities and find guess word with highest similarity
    similarities = [model.similarity(question_word, guess_word) for guess_word in valid_guess_words]
    best_guess = valid_guess_words[np.argmax(similarities)]

    # Determine label according to reqs
    label = 'correct' if best_guess == answer_word else 'wrong'

    return question_word, answer_word, best_guess, label


model = api.load("word2vec-google-news-300")

# Loading dataset
synonym_data = pd.read_csv('synonym.csv', dtype=str)

# Apply function to each row in dataset
synonym_data['results'] = synonym_data.apply(lambda row: find_closest_synonym(row, model), axis=1)
# Extract results
synonym_data[['question-word', 'answer-word', 'guess-word', 'label']] = pd.DataFrame(synonym_data['results'].tolist(), index=synonym_data.index)

# Drop original columns and results column
synonym_data.drop(columns=['question', 'answer', '0', '1', '2', '3', 'results'], inplace=True)

# Save to CSV
details_file_path = 'word2vec-google-news-300-details.csv'
synonym_data.to_csv(details_file_path, index=False)

# analysis data
model_name = "word2vec-google-news-300"
vocab_size = len(model.key_to_index)
correct_count = synonym_data['label'].value_counts().get('correct', 0)
total_questions = len(synonym_data)
non_guess_questions = total_questions - synonym_data['label'].value_counts().get('guess', 0)
accuracy = correct_count / non_guess_questions if non_guess_questions > 0 else 0

# analysis dataframe for output
analysis_data = pd.DataFrame({
    "model_name": [model_name],
    "vocab_size": [vocab_size],
    "correct_count": [correct_count],
    "non_guess_questions": [non_guess_questions],
    "accuracy": [accuracy]
})

# Save analysis data to CSV
analysis_file_path = '../analysis.csv'
analysis_data.to_csv(analysis_file_path, index=False)

details_file_path, analysis_file_path

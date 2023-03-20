import pickle

# Replace 'your_pickle_file.pkl' with the path to your pickle file
with open('gunViolenceMetadata.pickle', 'rb') as file:
    data = pickle.load(file)

# Now, 'data' contains the contents of the pickle file
print(data)
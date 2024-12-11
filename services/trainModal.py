import numpy as np
import pickle

# Compute Term Frequency (TF) for each document
def compute_tf(documents):
    """
    Computes the Term Frequency (TF) for each document in the collection.
    TF is the count of each word's occurrences in the document.

    Parameters:
        documents (list): A list of documents, where each document is a string.

    Returns:
        list: A list of dictionaries, where each dictionary contains word counts for each document.
    """
    tf = []
    for doc in documents:
        word_count = {}  # Initialize an empty dictionary to store word frequencies
        for word in doc.split():  # Split document into words
            word_count[word] = word_count.get(word, 0) + 1  # Count the occurrences of each word
        tf.append(word_count)  # Append the word count for each document
    return tf


# Compute Inverse Document Frequency (IDF) for each word
def compute_idf(documents):
    """
    Computes the Inverse Document Frequency (IDF) for each word in the corpus.
    IDF measures the importance of a word in the entire corpus.

    Parameters:
        documents (list): A list of documents, where each document is a string.

    Returns:
        dict: A dictionary where the key is a word and the value is its IDF.
    """
    total_docs = len(documents)  # Total number of documents
    word_document_count = {}  # Dictionary to track the number of documents containing each word
    for doc in documents:
        unique_words = set(doc.split())  # Get unique words in each document
        for word in unique_words:
            word_document_count[word] = word_document_count.get(word, 0) + 1  # Count the document occurrences of each word

    idf = {}
    for word, count in word_document_count.items():
        # Calculate IDF as the logarithm of the ratio of total documents to the document count for each word
        idf[word] = np.log(total_docs / count)
    return idf


# Compute Term Frequency-Inverse Document Frequency (TF-IDF) for each document
def compute_tfidf(documents, word_index, idf):
    """
    Computes the TF-IDF for each document using the provided word index and IDF.

    Parameters:
        documents (list): A list of documents, where each document is a string.
        word_index (dict): A dictionary where the key is a word and the value is its index.
        idf (dict): A dictionary containing the IDF values for each word.

    Returns:
        numpy.ndarray: A matrix where each row corresponds to a document, and each column corresponds to a word's TF-IDF value.
    """
    tf = compute_tf(documents)  # Calculate TF for each document

    # Initialize an empty TF-IDF matrix with shape (num_documents, num_words)
    tfidf_matrix = np.zeros((len(documents), len(word_index)))

    # Populate the TF-IDF matrix
    for doc_idx, doc in enumerate(documents):
        tf_dict = tf[doc_idx]  # Get the TF for the current document
        for word, count in tf_dict.items():
            if word in word_index:  # Check if the word is in the word index
                tfidf_matrix[doc_idx, word_index[word]] = count * idf.get(word, 0)  # Multiply TF by IDF

    return tfidf_matrix


# K-means clustering algorithm
def kmeans(tfidf_features, k=3, max_iters=100):
    """
    Applies the K-means clustering algorithm to the TF-IDF features to group documents into k clusters.

    Parameters:
        tfidf_features (numpy.ndarray): A matrix of TF-IDF features.
        k (int): The number of clusters to form.
        max_iters (int): The maximum number of iterations for the algorithm.

    Returns:
        list: A list of clusters, where each cluster is a list of document indices.
        numpy.ndarray: A matrix of cluster centers.
    """
    # Randomly select k initial cluster centers
    centers = tfidf_features[np.random.choice(tfidf_features.shape[0], k, replace=False)]

    for _ in range(max_iters):
        # Step 1: Assign each document to the nearest cluster center
        clusters = [[] for _ in range(k)]
        for i, doc in enumerate(tfidf_features):
            distances = np.linalg.norm(tfidf_features[i] - centers, axis=1)  # Compute the distance to each center
            closest_center = np.argmin(distances)  # Find the index of the closest center
            clusters[closest_center].append(i)  # Add the document to the corresponding cluster

        # Step 2: Update the cluster centers to the mean of the assigned documents
        new_centers = []
        for cluster in clusters:
            if cluster:  # If the cluster is not empty
                new_center = np.mean(tfidf_features[cluster], axis=0)  # Compute the mean of the assigned documents
                new_centers.append(new_center)
            else:
                new_centers.append(np.zeros_like(centers[0]))  # Handle empty clusters by assigning a zero vector

        centers = np.array(new_centers)  # Update the centers

    return clusters, centers


def train_modal():
    """
    Trains a model on a set of example documents using TF-IDF features and K-means clustering.
    Saves the trained model to a file if it's not already saved.

    The model includes the word index, IDF values, and the cluster centers from K-means.

    If the model already exists, it loads the model from the file.
    """
    # Example comments (documents) for training
    comments = [
        "a tad bit anxious, and the winter in london has not been helpful",
        "feeling good",
        "feeling sad",
        "I am really happy",
        "stressed out from work",
        "feeling balanced and focused",
        "a bit anxious about the future",
        "feeling calm and relaxed",
        "feeling low, depressed"
    ]

    # Extract all unique words from the documents and create a word index
    all_words = set(word for doc in comments for word in doc.split())  # Extract all words
    word_index = {word: idx for idx, word in enumerate(all_words)}  # Map each word to an index
    idf = compute_idf(comments)  # Compute IDF values for the words in the documents

    # Calculate the TF-IDF matrix for the documents
    tfidf_features = compute_tfidf(comments, word_index, idf)

    # Apply K-means clustering with 5 clusters
    clusters, centers = kmeans(tfidf_features, k=5)

    # Save the model (word index, IDF, and cluster centers) to a file
    model = {
        'word_index': word_index,
        'idf': idf,
        'centers': centers
    }

    # Check if the model file already exists
    try:
        with open('emotion_model.pkl', 'rb') as f:
            model = pickle.load(f)  # Load the existing model from file
        print("Model loaded successfully.")
    except FileNotFoundError:
        with open('emotion_model.pkl', 'wb') as f:
            pickle.dump(model, f)  # Save the new model to a file
        print("Model saved successfully.")

if __name__ == "__main__":
    train_modal()
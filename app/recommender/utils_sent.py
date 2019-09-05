import re

def rescale(value, old_min = -1, old_max = 1, new_min = 0, new_max = 5):

    new_v = (new_max - new_min) / (old_max - old_min) * (value - old_min) + new_min

    return new_v

def round_of_rating(number):

    return round(round(number,1) * 2) / 2

def data_clean():
    pass


def clean_text(text, remove_stopwords=True):
    '''Clean the text, with the option to remove stopwords'''
    
    # Convert words to lower case and split them
    text = text.lower()

    # Optionally, remove stop words
    #if remove_stopwords:
    #    stops = set(stopwords.words("english"))
    #    text = [w for w in text if not w in stops]
    
    #text = " ".join(text)

    # Clean the text
    #text = BeautifulSoup(text, "html.parser").get_text() #delete html
    text = re.sub(r"[^a-z]", " ", text) #only letters
    text = re.sub(r'\s+', ' ', text) # Remove any extra spaces 
    text = re.sub(r"(.)\1+", r"\1\1", text) #n letter -> two letter
    text = text.strip()
    # Return a list of words
    return(text)

#def text_stem(s):
#
#    stem = PorterStemmer()
#
#    s = s.split()
#
#    stem_sentence=[]
#
#    for word in s:
#        stem_sentence.append(stem.stem(word))
#
#    s = " ".join(stem_sentence)
#    return(s)
#
#def text_lemmatizer(s):
#
#    lem = WordNetLemmatizer()
#
#    s = s.split()
#
#    lem_sentence=[]
#
#    for word in s:
#        lem_sentence.append(lem.lemmatize(word,"v"))
#
#    s = " ".join(lem_sentence)
#    return(s)
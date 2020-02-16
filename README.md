# haiku-generator
Deeply meaningful and life changingly inspirational haiku with related image overlay generator.
Generates a random Haiku in customisable format.

## Functionality
A haiku is a very short form Japanese poem format. Poems consist of a 17 syllables over N lines. The standard Haiku format is 3 lines, consisting of 5, 7, and 5 syllables respectively.
This python function generates a completely random Haiku, using syllable data from the Nettalk Syllable Data Set Corpus, whilst only including words found in Google's 10,000 most common English words list. 
One word is selected by random, and a PIXABAY API search is done to retrieve associated images.
The haiku is then overlayed on the image, resulting in an inspirational uplifting poster.. almost?

## Datasets
### Nettalk Corpus Syllable Data Set - 
- https://rdrr.io/cran/qdapDictionaries/man/DICTIONARY.html
> Sejnowski, T.J., and Rosenberg, C.R. (1987). "Parallel networks that learn to pronounce English text" in Complex Systems, 1, 145-168. Retrieved from: http://archive.ics.uci.edu/ml/datasets/Connectionist+Bench+(Nettalk+Corpus)

### Google 10,000 most common words Data Set
- https://github.com/first20hours/google-10000-english

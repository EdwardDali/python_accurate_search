# python_accurate_search
port of accurate search in python


Port of https://github.com/florin-dumitrescu/accurate-search in python

You can use this class in a similar way to the JavaScript

'''

# Create an instance of AccurateSearch
search = AccurateSearch()

# Add some movies to the search index
movies = ['The Lighthouse', 'Marriage Story', 'The Irishman', 'Parasite']
for i, movie in enumerate(movies):
    search.add_text(i, movie)

# Perform a search
results = search.search('the')

# Print the results
for id in results:
    print(movies[id])

# Get suggestions
suggestions = search.suggestions('mar', 5)
print(suggestions)

'''

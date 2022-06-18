## About 'whash'

_whash_ is a word-hashing text-file, that contains a single header line, and the remaining lines are pairs of
- word
- hash value

It usually it has more words than hashes (hash value usually between 0 and 999).
The header is created by the class `WHashEnvelope`, as follow:
1. `head = f"{nick}:{fix}.{stats['#nwords-used']}/{stats['#nwords']}"`
1. `head += f".C{stats['#preferred-capital']}"`
1. `head += f":{stats['#len-dots']}/{stats['data-size']}"`

Example:
- `# en:V1.2105/91621.C0:561.405.34.0/18462`
Where:
- nick is a two letter language name;
- fix is "V1" (fixed string);
- '#nwords-used' indicates the number of _best words_, as indicated by the function `best_words()` of `WordHash`;
- '#nwords' are the total words that the original 'strict-??.lst' file has;
- C0 indicates no preferred capital word; Cn indicates the number of preferred capital words (algorithm de-selects longer words in favor of shorter words that start with a capital letter);
- 561.405.34.0 in the example are statistics (also named _len-dots_):
  + 561 indicates that there were 561 words with size 3,
  + .405 indicates 405 words with size 4,
  + .34 indicates 34 words of size 5,
  + .0 indicates that there no words of size 6 nor 7
  + (note that this may end with .0.1 in case there is 1 word with size 7);
- 2146 indicates the size, in octets, of the entire file, excluding the first line (header).

## Creating _whash_ (word-hashing text-file)
Example, using a strict list:
- `python pcreatewhash.py -f ../../results/strict-en.lst`
  + will create ../../results/whash-en.txt
  + `-f` forces creation of whash-en.txt, even if file already exists.

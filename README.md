Basically a boolean search automation. 
Gets HTML code of URLs found by a prompt you enter and gets anything that matches an email regex in the code.
Exports a .csv file with columns: query, email, link (where an email was found).
Advantages: all emails found are 100% real.
Disadvantages: may find emails not related to the subject if to search buy just a keyword instead of link.

[1] - parsing by single prompt
[2] - parsing by multiple prompts from .csv file. Reads the first column of the file
[s] - search engine switch: Google API (requires Google custom SE API key and SE ID), DuckDuckGo
[p] - prompt mode: '"Keyword"' - better for words, 'site:keyword.com' - better for links, 
      both - both variants, but 2 times more prompts, so works more slowly and more likely to meet search engine limitations

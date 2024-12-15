import arxiv
from datetime import datetime, timedelta, timezone
from pylatexenc.latex2text import LatexNodes2Text

CHARLIM = 300

client = arxiv.Client()

subcats = ['CO','EP','GA','HE','IM','SR']
subcat_emoji = ['🔮','🪐','🌀','🎆','🛠️','✨']
emojidict = dict(zip(subcats, subcat_emoji))

def formatTex(s):
    """
    pre-pre-processs and then convert any TeX -> Unicode
    """
    deamp = s.replace('&', '＆')
    return LatexNodes2Text().latex_to_text(deamp)

def formatAuthors(authors, shortnames=False):
    """
    format the author list
    """
    namestring = ''
    trunc = None
    nauth = len(authors)
    if nauth > 3:
        trunc = 1
        delims = []
    elif nauth != 1:
        delims = [","]*(len(authors[:trunc]) - 2) + [" &"]
    else:
        delims = []
    delims += [""]
    i = 0
    for auth in authors[:trunc]:
        if shortnames:
            # can shorten names for space, but
            # seems hard to do this reliably everywhere
            fullname = auth.name.split(' ')
            for name in fullname[:-1]:
                if name[0].islower():
                    namestring += f"{name}"
                else:
                    namestring += f"{name[0]}. "
                if '-' in name:
                    namestring += f"-{name.split('-')[-1][0]}. "
            namestring += f"{fullname[-1]}{delims[i]} "
        else:
            namestring += f"{auth.name}{delims[i]} "
        i+=1
    if trunc:
        namestring = namestring[:-1] + " et al."
    return namestring

now = datetime.now(timezone(timedelta(hours=-5)))
query = "cat:astro-ph.*"

search = arxiv.Search(
  query = query,
  max_results = 200,
  sort_by = arxiv.SortCriterion.SubmittedDate
)

results = client.results(search)

posts = []
feeds = []

for paper in results:
    post = []
    if (now-paper.published).days >= 1:
        continue
    emojis = ''
    feedlist = []
    for c in paper.categories:
        if "astro-ph." in c:
            feed = c.split('.')[-1]
            # add emoji!
            emojis += emojidict[feed]
            feedlist.append(feed)
    post.append(f"{formatTex(paper.title)}")
    namestring = formatAuthors(paper.authors, shortnames=False)
    post.append(f"{namestring}")
    # don't need https:// prefix for bsky
    abs_url = paper.pdf_url.split('//')[-1].replace("pdf", "abs")
    post.append(f"{abs_url} {emojis}")
    full_len = len('\n'.join(post))
    if full_len > CHARLIM:
        char_surplus =  full_len - CHARLIM + 3
        title_words = post[0].split(" ")
        while char_surplus >= 0 :
            char_surplus -= len(title_words[-1])
            del title_words[-1]
        post[0] = ' '.join(title_words) + "..."
    post_string = '\n'.join(post)
    posts.append(post_string)
    feeds.append(feedlist)
    print(post_string)
    print(f"[posted {paper.published} - was {full_len} of {CHARLIM} characters, reduced by {full_len-len(post_string)}]\n")

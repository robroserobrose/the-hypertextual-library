import sys
import json
import os

# this will build the html that makes up the library of books
library_book_elt_html_template = """
<div class="col-md-3 col-height book" book-title="{title}" uniquename="{uniquename}">
    <a href="{uniquename}/">
        <div class="pic-wrapper">
            <img src="{picture}" class="img-rounded pic" width="175" height="250">
            <br>
            <p class="regular text-center">{title} - {author}</p>
        </div>
    </a>
</div>
"""

# given a phrase, makes it linked so that it is clickable
# to beused when creating html pages for each book
def linkify(phrase):
	phrase = phrase.split(" ")
	res = "<a class=\"word\">"
	for word in phrase:
		res += word + "</a> <a class=\"word\">"
	res += "</a>"
	return res

# returns a string in the form:
#    lastname firstname title
# to be used for sorting the books
def book_sort_string(book):
	author = book["author"].split()
	author_str = ""
	if len(author) > 1:
		author_str += " ".join(author[1:])
		author_str += " " + author[0]
	author_str += " " + book["title"]
	return author_str

# per book html template
html_template = open("template/template.html", "r").read()
js_text_file_template = open("template/raw_text.js", "r").read()


# json objects of all the books
books = open("books.json", "r").read()
books = json.loads(books)

# sort the books by author, then title
books = sorted(books["books"], key = book_sort_string)

# start the html by opening the elements
book_list_html = "<div class=\"row\"><div class=\"row-height\">"

col_per_row = 4
for i, book in enumerate(books):

	uniquename = book["uniquename"]

	# validate all the info
	if (not os.path.isdir(uniquename)):
		sys.stderr.write("Error: no directory named %s -- Site won't be generated\n" % uniquename)
		continue;

	tfile = "%s/text.txt" % (uniquename)
	if (not os.path.isfile(tfile)):
		sys.stderr.write("Error: no file %s -- Site won't be generated\n" % tfile)
		continue;

	pfile = "%s/%s.jpg" % (uniquename, uniquename)
	if (not os.path.isfile(pfile)):
		sys.stderr.write("Error: no file %s -- Site won't be generated\n" % pfile)
		continue;

	# this will be where we write the generated index file per book
	html_outfile_name = "%s/index.html" % uniquename
	html_outfile = open(html_outfile_name, "w")

	# linkified, so the titles are clickable
	title = linkify(book["title"])
	author = linkify(book["author"])

	# creation of the per book html page
	html = html_template.format(
		title = title,
		author = author,
		raw_text_file = "%s_text.js" % uniquename,
		title_picture = "%s.jpg" % uniquename
	)

	html_outfile.write(html)

	# this will be the js file that holds all the text
	raw_text_file_name = "%s/text.txt" % uniquename
	raw_text_file = open(raw_text_file_name, "r")
	raw_text = raw_text_file.read()

	js_text = js_text_file_template.format(text = raw_text)

	js_text_outfile_name = "%s/%s_text.js" % (uniquename, uniquename)
	js_text_outfile = open(js_text_outfile_name, "w")

	js_text_outfile.write(js_text)

	# constructing the library html
	library_book_elt_html = library_book_elt_html_template.format(
		uniquename = uniquename,
		title = book["title"],
		author = book["author"],
		picture = "%s/%s.jpg" % (uniquename, uniquename)
	)

	# adds row to the bootsrap as needed
	if i and i % col_per_row == 0:
		book_list_html += "</div></div><div class=\"row\"><div class=\"row-height\">"

	book_list_html += library_book_elt_html
	book["html"] = library_book_elt_html

# make the index for the library
library = open("template/library.html", "r").read()
outfile = open("index.html", "w")

# close elts of the lib html
book_list_html += "</div></div>"

outfile.write(library.format(book_list=book_list_html))

# create a file to be used by the index.js file
books_js_file = open("books.js", "w")
books_js_file.write("book_list = ")
books_js_file.write(json.dumps(books))

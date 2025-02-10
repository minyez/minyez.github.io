---
author: Min-Ye Zhang
categories: tool
comments: true
date: "2025-02-10 20:00:28 +0800"
math: false
tags: Python pikepdf PDF ghostscript
title: Add outline bookmarks and page labels in PDF programmatically
---

## Background

PDF files of scanned books or merged file sometimes do not have proper
bookmarks for chapters and sections. This is inconvenient when one wants
to jump between different parts. Furthermore, it is usually the case
that the actual page number of the scanned document is not equal to the
internal page index (an integer) of the PDF. This can be fixed by
specifying a page label to identify each page, supported by PDF from
specification 1.3.

Many PDF readers provide a graphical way to edit outline and page
labels. For example, in PDF expert, outline bookmarks can be added using
the \"+\" button at the upper right corner of the outline view. Page
labels can be added in `Edit->Page Labels`, which provides Arabic and
Roman numerals. Theses functions are quite handy.

Then why programmatically? Flexibility is one thing. While graphical
editors may provide different levels of editing functionality, a script
can essentially do anything that its backend allows. In some sense, this
also indicates portability because you can get the same thing with the
script on any OS wherever the backend and the script language is
available. Of course, script is the best friend to relieve you from
repeated work where many documents with the same content structure needs
to be modified, or the same document needs to be re-generated and
marked.

In this note I will briefly explain how to add outline and page labels
by writing script and running command line. To make it easier to
understand, suppose we have a PDF file `input.pdf` with the following
structure:

    Page  1 - 4 : cover, copyright, etc

    Page  5 - 7 : content

    Page  8 - 12: Chapter 1
          9 - 11: Section 1.1
         11 - 12: Section 1.2
    Page 13 - 17: Chapter 2
         14 - 15: Section 2.1
         16 - 17: Section 2.2

It contains three parts: cover, content (unnecessarily long) and body.
Pages in each part needs to be labeled separately. The first part should
be numbered by uppercase alphabet letters, *A, B, C*, content by
lowercase roman, *i, ii, iii*, and the main body by normal arabic
numerals.

## Add structured outline

### Use ghostscript and pdfmarks

[ghostscript](https://www.ghostscript.com/) is an interpreter for
PostScript and PDF. It also provides a few conversion tools to process
these files. For our case, a `pdfmarks` file should be prepared as
follows

    [ /Title (Cover) /Page 1 /View [/Fit] /OUT pdfmark
    [ /Title (Content) /Page 5 /View [/Fit] /OUT pdfmark
    [ /Count 2 /Title (Chapter 1) /Page 8 /View [/Fit] /OUT pdfmark
    [ /Title (Section 1.1) /Page 9 /View [/Fit] /OUT pdfmark
    [ /Title (Section 1.2) /Page 11 /View [/Fit] /OUT pdfmark
    [ /Count 2 /Title (Chapter 2) /Page 13 /View [/Fit] /OUT pdfmark
    [ /Title (Section 2.1) /Page 14 /View [/Fit] /OUT pdfmark
    [ /Title (Section 2.2) /Page 16 /View [/Fit] /OUT pdfmark

Then use command line tool `gs` of ghostscript to combine it and
`input.pdf`

``` shell
gs -o output.pdf -sDEVICE=pdfwrite -dBATCH -dNOPAUSE input.pdf pdfmarks
```

Note that if there are CJK characters in bookmarks, they have to be
converted to UTF-16-BE hex encoding before inserted to `pdfmarks`. A
python function can be used to achieve this:

``` python
import sys

def utf16_hex(text):
    """Convert text to UTF-16-BE hex format."""
    hex_string = text.encode("utf-16-be").hex().upper()
    return f"<FEFF{hex_string}>"

s = u"你好，世界！"  # "Hello World" in Chinese
print("Original :", s)
print("UTF-16-BE:", utf16_hex(s))
```

``` plain
Original : 你好，世界！
UTF-16-BE: <FEFF4F60597DFF0C4E16754CFF01>
```

However, I failed to embed page labels using ghostscript after trying
several SO answers or with help from ChatGPT. This made me look
elsewhere and I found `pikepdf` a great alternative.

### Use pikepdf

[pikepdf](https://pikepdf.readthedocs.io) is a Python library to handle
PDF files based on [qpdf](https://github.com/qpdf/qpdf), a C++ library
for content-preserving processing of PDF. It can be installed by any
sensible Python package manager, e.g. `micromamba install pikepdf`.

To create and add outline, the `OutlineItem` class in pikepdf is useful.
The outline structure we would like can be created with the following
script.

``` python
import pikepdf

# Open PDF file
pdf = pikepdf.open("input.pdf")

# Alias the OutlineItem class
OI = pikepdf.OutlineItem
with pdf.open_outline() as outline:
    # Page of OutlineItem starts from 0
    outline.root.append(OI("Cover", 0))
    outline.root.append(OI("Content", 4))

    # Chapter 1 and its sections
    item = OI("Chapter 1", 7)
    outline.root.append(item)
    children = [OI("Section 1.1", 8), OI("Section 1.2", 10),]
    item.children.extend(children)

    # Chapter 2 and its sections
    item = OI("Chapter 2", 12)
    outline.root.append(item)
    children = [OI("Section 2.1", 13), OI("Section 2.2", 15),]
    item.children.extend(children)

# Export the modified PDF
pdf.save("output.pdf")
```

The method `pdf.open_outline()` returns an `Outline` object. Its `root`
attribute, which is a list of `OutlineItem`, contains the top-level
outline bookmarks. After creating `OutlineItem` object with title and
page number, we append it to `outline.root` to add a outline bookmark.
The nested structure is realized by adding `OutlineItem` objects to
`children` attribute of the same class. This design is very handy and
makes recursively creating outline structure easy.

## Add page labels with pikepdf

pikepdf also allows to add page labels. The following snippet adds the
required page labels to the input PDF file.

``` python
from pikepdf import open as open_pdf
from pikepdf import Name, NumberTree, Dictionary

# Open PDF file
pdf = open_pdf("input.pdf")

# Overwrite current page labels
nt = NumberTree.new(pdf)
pdf.Root.PageLabels = nt.obj
pagelabels = NumberTree(pdf.Root.PageLabels)

# Cover, uppercase alphabet
pagelabels[0] = Dictionary(S=Name.A)
# Content, lowercase roman, counts start from 1
pagelabels[4] = Dictionary(S=Name.r, St=1)
# Body, arabic numeral, counts start from 1
pagelabels[7] = Dictionary(S=Name.D, St=1)

# Export the modified PDF
pdf.save("output.pdf")
```

In pikepdf, page labels are controlled by the `pdf.Root.PageLabels`
object. To handle the labels, it should be first converted to
`NumberTree` type, which reflects the number tree structure of page
labels in PDFs. A page label is represented by a `Dictionary` object,
just like the actual dictionary used in PDF. The style of the label is
controlled by the key `S` which is a PDF Name object. Key `St` specifies
the starting number of label count and is always an integer. For other
relevant keys, refer to \"12.4.2 Page Labels\" of [PDF 1.7 ISO
Specification](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf).

The created dictionary is then assigned to the `NumberTree` object as a
`dict`. The key is the index (begins with 0) of starting page of the
pages to label.

## A general script to do both

To make it more general, I wrote a script to read a JSON file containing
information about outline and page labels. The one for our example is
like below.

``` json
{
  "PageLabels": {
    "1": { "style": "A" },
    "3": { "style": "r", "start": 1 },
    "8": { "style": "D", "start": 1 }
  },
  "Outline": [
    {
      "title": "Cover", "page": 1
    },
    {
      "title": "Content", "page": 5
    },
    {
      "title": "Chapter 1", "page": 8, "children": [
        {
          "title": "Section 1.1", "page": 9
        },
        {
          "title": "Section 1.2", "page": 11
        }
      ]
    },
    {
      "title": "Chapter 2", "page": 13, "children": [
        {
          "title": "Section 2.1", "page": 14
        },
        {
          "title": "Section 2.2", "page": 16
        }
      ]
    }
  ]
}
```

All page indices, including the keys of \"PageLabels\" dict, start from
1, which is consistent with page index in PDF readers. This file, say
`input.json`, can be processed by the following script
`embed_bookmark_pagelabels.py`, which uses `argparse` to pass command
line arguments. It supports nested children outline bookmarks without
depth limit.

``` python
import json
import argparse
import pathlib
import warnings
try:
    import pikepdf
except ImportError:
    raise ImportError("Require pikepdf to work")


def _process_outline_recursive(root: list[pikepdf.OutlineItem], *entries):
    for e in entries:
        title = e["title"]
        page = e["page"] - 1
        item = pikepdf.OutlineItem(title, page)
        root.append(item)
        if "children" in e:
            children = e["children"]
            if isinstance(children, (list, tuple)) and len(children) > 0:
                _process_outline_recursive(item.children, *children)


def process_outline(pdf: pikepdf.Pdf, *entries):
    with pdf.open_outline() as outline:
        _process_outline_recursive(outline.root, *entries)


STYLES = {
    "D": pikepdf.Name.D,
    "R": pikepdf.Name.R,
    "r": pikepdf.Name.r,
    "A": pikepdf.Name.A,
    "a": pikepdf.Name.a,
}


def process_pagelabels(pdf: pikepdf.Pdf, pagelabels):
    if pagelabels is not None:
        # Retrieve current page labels
        # Clean up current labels
        nt = pikepdf.NumberTree.new(pdf)
        pdf.Root.PageLabels = nt.obj
        pagelabels_cur = pikepdf.NumberTree(pdf.Root.PageLabels)

        for k, v in pagelabels.items():
            # page in JSON starts from 1, while pikepdf from 0
            page = int(k) - 1
            d = {}

            # Style
            s = v.get("style", None)
            if s is not None:
                d["S"] = STYLES[s]

            # Prefix
            prefix = v.get("prefix", None)
            if prefix is not None:
                d["P"] = prefix

            # Starting page
            st = v.get("start", None)
            if st is not None:
                d["St"] = st

            pagelabels_cur[page] = pikepdf.Dictionary(**d)


def process_json(pdf: pikepdf.Pdf, jsonfile):
    with open(jsonfile, 'r') as h:
        data = json.load(h)

    pagelabels = data.get("PageLabels", None)
    outline = data.get("Outline", [])

    process_pagelabels(pdf, pagelabels)
    process_outline(pdf, *outline)


def _parser():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input_pdf", help="Input PDF file")
    p.add_argument("json", type=str, help="JSON file with outline and page labels")
    p.add_argument("-o", "--output", default="output.pdf", type=str,
                   help="Path of output PDF, default to filename.embed.pdf")
    return p


if __name__ == '__main__':
    args = _parser().parse_args()
    input_pdf = pathlib.Path(args.input_pdf)
    pdf = pikepdf.open(input_pdf)
    process_json(pdf, args.json)

    # Export to new pdf
    output = pathlib.Path(args.output)
    if output.exists():
        warnings.warn("Overwriting {}".format(output))

    pdf.save(output)
```

To generate the target output, I can simply run

``` shell
python embed_bookmark_pagelabels.py input.pdf input.json -o output.pdf
```

#MarkdownHighlighter

MarkdownHighlighter is a simple syntax highlighter for Markdown syntax. MarkdownHighlighter is written in Python and Qt by subclassing QSyntaxHighlighter. A sample editor application is also included which is a stripped down version of ReText.

##Features

1. Syntax highlighting for most Markdown formatting including:

 * ATX & Setex style headers
 * Inline formatting: bold, emphasis and code spans
 * Links
 * Images
 * Lists
 * Horizontal rules
 * Code blocks
 * Blockquotes
 * Markdown elements inside Blockquotes
 * Html elements 

2. Support for themes:
 
Themes are specified as json style dicts. For example the default theme is:

    {"background-color":"#d7d7d7", "color":"#191970", "bold": {"color":"#859900", "font-weight":"bold", "font-style":"normal"}, "emphasis": {"color":"#b58900", "font-weight":"bold", "font-style":"italic"}, "link": {"color":"#cb4b16", "font-weight":"normal", "font-style":"normal"}, "image": {"color":"#cb4b16", "font-weight":"normal", "font-style":"normal"}, "header": {"color":"#2aa198", "font-weight":"bold", "font-style":"normal"}, "unorderedlist": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "orderedlist": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "blockquote": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "codespan": {"color":"#dc322f", "font-weight":"normal", "font-style":"normal"}, "codeblock": {"color":"#ff9900", "font-weight":"normal", "font-style":"normal"}, "line": {"color":"#2aa198", "font-weight":"normal", "font-style":"normal"}, "html": {"color":"#c000c0", "font-weight":"normal", "font-style":"normal"}}

##Screenshot

![Screenshot](https://github.com/rupeshk/MarkdownHighlighter/raw/master/screenshot.png)

##Requirements

MarkdownHighlighter has only been tested on Linux. However, it should run on any platform where Qt and PyQt are installed. MarkdownHighlighter requires the following packages to run:
* python
* python-qt4

##Credits

The initial code for MarkdownHighlighter was taken from niwmarkdowneditor by John Schember <http://john.nachtimwald.com/category/programming/niwmarkdowneditor/> 
The code for the sample application was taken from ReText which is a full featured Markdown editor with previews and multiple export options <http://sourceforge.net/p/retext/home/ReText/>
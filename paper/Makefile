LATEX=pdflatex
CONVERT_DVI=dvipdf
default: paper open

open:
	open paper.pdf

paper: paper.tex
	$(LATEX) paper.tex
	$(LATEX) paper.tex
	rm -rf paper.log
	rm -rf paper.aux

paper-clean:
	rm -f paper.dvi
	rm -f paper.aux
	rm -f paper.log
	rm -f paper.pdf
	rm -f paper.toc

spell:
	aspell check -t paper.tex

clean: paper-clean

%.pdf : %.svg
	rsvg-convert -f pdf -o $@ $<

%.png : %.svg
	rsvg-convert -f png -o $@ $<

self_doc:
	@echo "make run_test"
	@echo "make images (needs dep2pict)"
	@echo "make rhapsodie (need a local [symlink to a] directory SUD_French-Rhapsodie)"

run_test:
	python3 sb_to_db.py test/sb_test.conllu test/db_test.conllu

images: run_test
	dep2pict_dev test/sb_test.conllu -p 1 test/sb_test_1.svg 
	dep2pict_dev test/sb_test.conllu -p 2 test/sb_test_2.svg
	dep2pict_dev test/db_test.conllu test/db_test.svg

pdf:
	find test -name "*.svg" -type f -print | sed "s/.svg$$//" | xargs -I {} make "{}.pdf"

png:
	find test -name "*.svg" -type f -print | sed "s/.svg$$//" | xargs -I {} make "{}.png"

clean:
	rm -f test/db_test.conllu
	rm -f test/*.svg test/*.pdf test/*.png

rhapsodie:
	mkdir -p SUD_French-Rhapsodie_db
	for infile in SUD_French-Rhapsodie/*.conllu ; do \
		outfile=`echo $$infile | sed "s+SUD_French-Rhapsodie/+SUD_French-Rhapsodie_db/+"` ; \
		echo "$$infile --> $$outfile" ; \
		python3 sb_to_db.py $$infile $$outfile ; \
	done

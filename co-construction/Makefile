%.pdf : %.svg
	rsvg-convert -f pdf -o $@ $<

%.png : %.svg
	rsvg-convert -f png -o $@ $<

self_doc:
	@echo "make run_test"
	@echo "make images (needs dep2pict)"
	@echo "make rhapsodie (need a local [symlink to a] directory SUD_French-Rhapsodie)"

run_test_guidelines:
	python3 sb_to_db.py test/guidelines/speaker_based.conllu test/guidelines/dependency_based.conllu

run_test_rhap:
	python3 sb_to_db.py test/Rhapsodie/sb_test.conllu test/Rhapsodie/db_test.conllu

images: run_test_guidelines run_test_rhap
	dep2pict_dev test/guidelines/speaker_based.conllu -p 1 test/guidelines/speaker_based_1.svg 
	dep2pict_dev test/guidelines/speaker_based.conllu -p 2 test/guidelines/speaker_based_2.svg
	dep2pict_dev test/guidelines/speaker_based.conllu -p 3 test/guidelines/speaker_based_3.svg
	dep2pict_dev test/guidelines/dependency_based.conllu test/guidelines/dependency_based.svg
	dep2pict_dev test/Rhapsodie/sb_test.conllu -p 1 test/Rhapsodie/sb_test_1.svg 
	dep2pict_dev test/Rhapsodie/sb_test.conllu -p 2 test/Rhapsodie/sb_test_2.svg
	dep2pict_dev test/Rhapsodie/db_test.conllu test/Rhapsodie/db_test.svg

pdf:
	find test -name "*.svg" -type f -print | sed "s/.svg$$//" | xargs -I {} make "{}.pdf"

png:
	find test -name "*.svg" -type f -print | sed "s/.svg$$//" | xargs -I {} make "{}.png"

clean:
	rm -f test/*/*.svg test/*/*.pdf test/*/*.png
	rm -f test/*/*.svg test/*/*.pdf test/*/*.png

rhapsodie:
	mkdir -p SUD_French-Rhapsodie_db
	for infile in SUD_French-Rhapsodie/*.conllu ; do \
		outfile=`echo $$infile | sed "s+SUD_French-Rhapsodie/+SUD_French-Rhapsodie_db/+"` ; \
		echo "$$infile --> $$outfile" ; \
		python3 sb_to_db.py --config sud $$infile $$outfile ; \
	done

upload:
	scp -o "ProxyJump guillaum@ssh-nge.inria.fr" SUD_French-Rhapsodie_db/*.conllu guillaum@grew-host.loria.fr:/home/guillaum/resources/SUD_French-Rhapsodie_db

kiparla:
	mkdir -p test/kiparla_db
	python3 sb_to_db.py test/kiparla/BOA3017.conllu test/kiparla_db/BOA3017.conllu 
	python3 sb_to_db.py test/kiparla/BOD2018.conllu test/kiparla_db/BOD2018.conllu 

guidelines:
	python3 sb_to_db.py test/guidelines/speaker_based.conllu test/guidelines/dependency_based.conllu



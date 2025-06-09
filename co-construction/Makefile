doc:
	@echo "make run_test"
	@echo "make images (needs dep2pict)"
	@echo "make rhapsodie (need a local [symlink to a] directory SUD_French-Rhapsodie)"

run_test:
	python3 sb_to_db.py test/sb_test.conllu test/db_test.conllu

images: test
	dep2pict test/sb_test.conllu -p 1 test/sb_test_1.svg
	dep2pict test/sb_test.conllu -p 2 test/sb_test_2.svg
	dep2pict test/db_test.conllu test/db_test.svg

rhapsodie:
	mkdir -p SUD_French-Rhapsodie_db
	python3 sb_to_db.py SUD_French-Rhapsodie/fr_rhapsodie.sud.dev.conllu SUD_French-Rhapsodie_db/fr_rhapsodie.sud.dev.conllu
	python3 sb_to_db.py SUD_French-Rhapsodie/fr_rhapsodie.sud.test.conllu SUD_French-Rhapsodie_db/fr_rhapsodie.sud.test.conllu
	python3 sb_to_db.py SUD_French-Rhapsodie/fr_rhapsodie.sud.train.conllu SUD_French-Rhapsodie_db/fr_rhapsodie.sud.train.conllu


doc:
	@echo "make naija   --> run the toy example"
	@echo "make kiparla --> compute the unshared kiparla corpus in './kiparla_unshared'"

naija:
	python3 unshare_metadata.py shared_metadata unshared_metadata

kiparla:
	python3 unshare_metadata.py ../co-construction/test/kiparla ./kiparla_unshared

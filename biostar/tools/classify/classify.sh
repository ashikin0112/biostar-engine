INPUT_DATA = {{data.path}
INPUT_SAMPLE_INFO = {{sampleinfo.path}}
REFERENCE= {{ reference.path }}
THREADS ={{ threads.value}}

#
# Internal parameters after this.
#
DATA_DIR = data
RESULT_DIR  = results
UPDATED_SAMPLE_INFO = updated_sampleinfo.txt


all:classify


extract:
	#
	# extract data	
	#
	tar -xzvf $(INPUT_DATA)

#
# ============== Update sample sheet ==============
# Read1 and Read2 file names will be added to updated samplesheet.
#

updated_sample_info: extract
	#
	# Make new sample sheet named $(UPDATED_SAMPLE_INFO)
	#
	python -m biostar.tools.data.samplesheet $(INPUT_SAMPLE_INFO) $(DATA_DIR) > $(UPDATED_SAMPLE_INFO)


classify: updated_sample_info
	#
	# classify data
	#
	mkdir -p $(RESULT_DIR)
	cat $(UPDATED_SAMPLE_INFO) |parallel --verbose --progress -j $(THREADS)  --header : --colsep '\t' centrifuge \
	-x $(REFERENCE) -q -1 $(DATA_DIR)/{file1} -2 $(DATA_DIR)/{file2} --report-file \
	$(RESULT_DIR)/{sample_name}_report.txt -S $(RESULT_DIR)/{sample_name}_classify.txt


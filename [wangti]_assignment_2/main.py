# Author: Ting-Chen Wang
# Computational Biology Spring 2020
# Assignment 2
# Due Date: 2/2/2020
# main

import os
import requests
import sys


# convert the size of a file from bytes to mega bytes
def convert_size(size_in_bytes):
    return size_in_bytes / (1024 * 1024)


# return the size of a file in mega bytes
def get_file_size(file_name):
    size_of_file = os.path.getsize(file_name)
    return convert_size(size_of_file)


# the main function
def main():
    if len(sys.argv) == 3:
        # get the sequence id
        sequence_number = sys.argv[1]
        # get the file name
        file_name = sys.argv[2]
        # retrieve the prefix
        prefix = sequence_number[0:2]
        # endpoint used
        server_0 = "https://biodbnet-abcc.ncifcrf.gov/webServices/rest.php/biodbnetRestApi.json?"
        server_1 = "https://rest.ensembl.org"
        ext = "/sequence/id/"

        # identify if a search is successful
        valid_search = False
        # identify if a file is from a tax_id
        tax_file = False

        # lists of refSeq prefixes
        list1 = ['NM', 'NR', 'XM', 'XR']
        list2 = ['AC', 'NC', 'NG', 'NT', 'NW', 'NS', 'NZ']
        list3 = ['AP', 'NP', 'YP', 'XP', 'ZP']

        # check if a sequence id is valid
        if not sequence_number.isdigit():
            if prefix not in (list1 + list2 + list3) or sequence_number[2] != '_' or not sequence_number[3:].isdigit():
                # exit the program if it's not valid
                sys.exit("The search id is not valid.")
            else:
                # for rna sequences
                if prefix in list1:
                    number = sequence_number.split('.')
                    # find the url extension
                    extension = "method=db2db&input=refseqmrnaaccession&inputValues=" + number[
                        0] + "&outputs=ensemblgeneid&taxonId=&format=row"
                # for genomic sequences
                elif prefix in list2:
                    number = sequence_number.split('.')
                    # find the url extension
                    extension = "method=db2db&input=refseqgenomicaccession&inputValues=" + number[
                        0] + "&outputs=ensemblgeneid&taxonId=&format=row"
                # for protein sequences
                elif prefix in list3:
                    number = sequence_number.split('.')
                    # find the url extension
                    extension = "method=db2db&input=refseqproteinaccession&inputValues=" + number[
                        0] + "&outputs=ensemblgeneid&taxonId=&format=row"
                # use requests to get the sequence information from the end point
                response = requests.get(server_0 + extension)
                # format the result from the end point in json style
                response_obj = response.json()
                # get the ensembl id
                ensemble_id_list = response_obj[0]['Ensembl Gene ID']
                # use the ensembl id to download the sequence in fasta file format
                r = requests.get(server_1 + ext + ensemble_id_list + '?', headers={"Content-Type": "text/x-fasta"})
                # check if the request is valid
                if not r.ok:
                    r.raise_for_status()
                    sys.exit('unsuccessful')
                else:
                    valid_search = True
        else:
            # the input is a tax_id
            ext_1 = "/info/genomes/taxonomy/"
            tax_id = sequence_number
            print(tax_id)
            # request the information from ensembl according to the sequence_id
            r = requests.get(server_1 + ext_1 + tax_id + "?", headers={"Content-Type": "application/json"})
            # check if the request is valid
            if not r.ok:
                r.raise_for_status()
                sys.exit('unsuccessful')
            else:
                valid_search = True
                tax_file = True
            # request the file path from the tax id
            decoded = r.json()
            ensemble_id_list = decoded[0]['assembly_accession']
            ensemble_assembly_name = decoded[0]['assembly_name']
            server_2 = "https://ftp.ncbi.nlm.nih.gov/genomes/all/"
            extension_1 = ensemble_id_list[0:3] + "/" + ensemble_id_list[4:7] + "/" + ensemble_id_list[7:10] + "/" + \
                          ensemble_id_list[10:13] + "/" + ensemble_id_list + "_" + ensemble_assembly_name + "/" + \
                          ensemble_id_list + "_" + ensemble_assembly_name + "_genomic.fna.gz"
            response = requests.get(server_2 + extension_1)

        if valid_search:
            # indicate that this search is successful
            print('True')
            if tax_file:  # write the sequence to a file (if sequence number is a tax id)
                f = open(file_name, 'wb')
                f.write(response.content)
                f.close()
            else:  # write the sequence to a file (if sequence number is a refSeq id)
                f = open(file_name, "w")
                f.write(r.text)
                f.close()

            # get file size in MB
            size = get_file_size(file_name)
            print('Size of file is : ', size, 'MB')
        else:
            sys.exit('Invalid request.')
    else:  # print out an error message indicating the wrong number of commandline arguments
        sys.exit("The number of arguments is not correct.")


if __name__ == '__main__':
    main()

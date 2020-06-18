import os
import base64
import hashlib
hash
def split_file_to_pieces(filename):
	fin = open(filename,"rb")
	j = 1
	BUFFER_LENGTH = 50*1024*1024
	foutconfig = open(filename+".CONFIG","w")
	fin.seek(0,2)
	totallength = fin.tell()
	fin.seek(0,0)
	foutconfig.write("TOTALLENGTHOFORGINALFILE : "+str(totallength)+"\n")

	no_of_files = totallength//BUFFER_LENGTH
	if totallength%BUFFER_LENGTH!=0:
		no_of_files+=1
	foutconfig.write("TOTALNOOFPIECES : "+str(no_of_files)+"\n")

	i = 0
	hcheck = ""
	while fin.tell()<totallength:
		if fin.tell()+BUFFER_LENGTH>totallength:
			BUFFER_LENGTH = totallength - fin.tell() + 1
		k = fin.read(BUFFER_LENGTH)
		fout = open(filename+".PIECE{fileno}".format(fileno=j),"wb")
		fout.write(k)
		fout.close()
		fintmp = open(filename+".PIECE{fileno}".format(fileno=j),"rb")
		fout = open(filename+".PIECE{fileno}.dat".format(fileno=j),"wb")
		base64.encode(fintmp,fout)
		fintmp.close()
		fout.close()
		os.remove(filename+".PIECE{fileno}".format(fileno=j))
		hcheck = hcheck+str(hashlib.sha256(str(k).encode()).hexdigest())
		foutconfig.write("FILENAME{fileno} : {file}.PIECE{fileno}.dat\n".format(file=filename,fileno=j))
		j = j+1
		i = i+BUFFER_LENGTH
		print(str(i/(1024*1024))+" MB processed!....")

	foutconfig.write("HASH : "+(hcheck+str(hashlib.sha256(hcheck.encode()).hexdigest()))+"\n");
	foutconfig.close()
	fin.close()
	print("File Splitting Completed!...")

def read_config_file(configfilename):
	fin = open(configfilename,"r")
	filedata = {(i.split(":")[0].strip()):(i.split(":")[1].strip()) for i in fin.readlines()}
	filedata['TOTALLENGTHOFORGINALFILE'] = int(filedata['TOTALLENGTHOFORGINALFILE'])
	filedata['TOTALNOOFPIECES'] = int(filedata['TOTALNOOFPIECES'])
	return filedata

def calculate_hash(filename):
	fin = open(filename,"rb")
	BUFFER_LENGTH = 50*1024*1024
	fin.seek(0,2)
	totallength = fin.tell()
	fin.seek(0,0)
	hcheck = ""
	while fin.tell()<totallength:
		if fin.tell()+BUFFER_LENGTH>totallength:
			BUFFER_LENGTH = totallength - fin.tell() + 1
		k = fin.read(BUFFER_LENGTH)
		hcheck = hcheck+str(hashlib.sha256(str(k).encode()).hexdigest())
	fin.close()
	return (hcheck+str(hashlib.sha256(hcheck.encode()).hexdigest()))

def combine_pieces_to_file(configfilename):
	config = read_config_file(configfilename)
	no_of_pieces = config['TOTALNOOFPIECES']
	filename = configfilename.replace(".CONFIG","")
	fout = open(filename,"wb")
	BUFFER_LENGTH = 50*1024*1024
	try:
		for i in range(1,no_of_pieces+1,1):
			fin = open(filename+".PIECE{fileno}.dat".format(fileno=i),"rb")
			fouttmp = open(filename+".PIECE{fileno}".format(fileno=i),"wb")
			base64.decode(fin,fouttmp)
			fin.close();
			fouttmp.close()
			fin = open(filename+".PIECE{fileno}".format(fileno=i),"rb")
			fin.seek(0,2)
			k = fin.tell()
			if k<BUFFER_LENGTH:
				BUFFER_LENGTH = k
			fin.seek(0,0)
			data = fin.read(BUFFER_LENGTH)
			fout.write(data)
			fin.close();
			os.remove(filename+".PIECE{fileno}".format(fileno=i))
			print("Read DATA from '"+filename+".PIECE{fileno}.dat'".format(fileno=i))
	except Exception as e:
		fout.close()
		os.remove(filename)
		print(e)
		return
	fout.close()
	#print("File hash : "+calculate_hash(filename))
	if config["HASH"]!=calculate_hash(filename):
		print("File Corruption Detected!...")
		os.remove(filename)
	else:
		print("File rebuilding Completed!...")
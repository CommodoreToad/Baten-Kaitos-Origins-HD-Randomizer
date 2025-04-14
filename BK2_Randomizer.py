import zlib
import os
import sys
import random
import copy
import csv
import math
import hashlib
import time
import argparse

def main(seed, mode):
	key = 0x00000000000000000078DA
	key = key.to_bytes(11, 'big')
	table_offsets = []
	byte_list = []
	script_offsets = []
	inflator = []
		
	sCount = 0

	if seed == '':
		seed = rand_seed()
	else:
		seed = int(seed)

	random.seed(seed)
	
	seed = hex(seed)[2:]

	if getattr(sys, 'frozen', False):
		scriptPath = os.path.dirname(os.path.realpath(sys.executable))
	else:
		scriptPath = os.path.dirname(os.path.realpath(__file__))

	folder = os.path.join(scriptPath, 'Seeds', seed)

	try:
		os.mkdir(folder)
	except:
		pass

	iMetaFile = os.path.join(scriptPath, 'original_files', 'global-metadata.dat')
	oMetaFile = os.path.join(folder, 'global-metadata.dat')
	timeFile = os.path.join(scriptPath, 'data', 'BK_mag_time.csv')
	oDllFile = os.path.join(folder, 'GameAssembly.dll')
	iDllFile = os.path.join(scriptPath, 'original_files', 'GameAssembly.dll')

	iMetaHash= hashlib.md5(open(iMetaFile,'rb').read()).hexdigest()
	iDllHash = hashlib.md5(open(iDllFile,'rb').read()).hexdigest()
	
	metaHash = hex(0x65FD027FD79AB051B4A49922C1F84F55)[2:]
	dllHash = hex(0x3A636051106B00EB4CB5579378E49DCF)[2:]
	
	if dllHash != iDllHash:
		inp = input('Warning, unexpected hash for "GameAssembly.dll". Please place the original  dll file in "original files" folder. Input "y" to ignore and continue.')
		if inp != 'y':
			exit()
	if metaHash != iMetaHash:
		inp = input('Warning!, unexpected hash for "global-metadata.dat". Please place the original  metadata file in "original files" folder. Input "y" to ignore and continue.')
		if inp != 'y':
			exit()

	print('Generating Seed. Please Wait.')
	print()
	
	pacman = False
	if mode == 'pac':
		mode = 'rando'
		pacman = True
	
	if mode == 'full': mode = 'rando'
	
	f = open(iMetaFile, 'rb')
	if mode == 'rando':
		f2 = open(oMetaFile, 'wb')
	f4 = open(timeFile)		
	
	if mode == 'rando':
		location, orig_location, progression = rando()
		
		scripts = [row[2] for row in location]

		bBuffer = f.read()
		
		metaObj = bBuffer
		found = True
		currentPos = 0
		ids = []

		while found:
			
			index= bBuffer.find(key, currentPos) - 3

			if index < 0:
				break

			f.seek(index)
			start = index - 4
			length = f.read(3)
			length = int.from_bytes(length, 'little')
			f.seek(index+12)
			myBytes = f.read(length+10)
			
			decomp = zlib.decompress(myBytes)

			
			checksum = zlib.adler32(decomp).to_bytes(4, 'big')
			fileID = int.from_bytes(decomp[4:8],'big')
			fileID = str(hex(fileID))[2:]

			counter = 0
			iterator = True
			while iterator:
				if fileID + '_' + str(counter) in ids:
					counter += 1
				else:
					fileID = fileID + '_' + str(counter)
					iterator = False
			
			
			ids.append(fileID)

			currentPos = bBuffer.find(checksum) +4
			
			f.seek(currentPos)
			
			zero = (currentPos - start)%8
			
			if zero ==0:
				d_len = currentPos - start + 8
				zero=8
			else:
				d_len = currentPos - start - zero + 8
				zero = 8-zero

			if fileID in scripts:

				current_script = []
				
				for x in location:
					if x[2] == fileID:
						current_script.append(x)
				
				f.seek(index+12)
				myBytes = f.read(currentPos-index-12)

				decomp = (0).to_bytes(20,'big') + decomp[20:]
				
				for x in current_script:
					offset = int('0x' + x[3],16)
					magType = int(x[6])
					if x[7] != '':
						add1 = int('0x' + x[7],16)
					else:
						add1 = ''
					if x[8] != '':	
						add2 = int('0x' + x[8],16)
					else:
						add2=''
					
					mag = x[4]

					if pacman and fileID == '441e61c5_0' and offset == 0x6f64:
						mag = 549
					
					decomp = patch(decomp, offset, magType, add1, add2, mag)

				obj = zlib.compress(decomp,9)

				count = 0
				while (len(obj))%8 !=0:
					count +=1
					obj = obj + (0).to_bytes(1, 'big')
				
				for x in range(zero):
					myBytes = myBytes + (0).to_bytes(1, 'big')
			
				while len(obj) < len(myBytes):
					obj = obj + (0).to_bytes(1, 'big')
				
				if len(obj) > len(myBytes):
					print(fileID)
					print('Warning compression too large. Please generate a new seed')
					exit()
					

		
				metaObj = metaObj.replace(myBytes, obj)
				metaObj = metaObj[:start+4] + len(decomp).to_bytes(4,'little') + metaObj[start+8:]

			sCount += 1
			
			
		f2.write(metaObj)

		f2.close()
	

	
	f2 = open(oDllFile, 'wb')
	f = open(iDllFile, 'rb')

	fBuffer = f.read()
	newBuffer = fBuffer

	pos =0x14DD0E2
	k1 = (0x66c784).to_bytes(3, 'big') #1
	k2 = (0x66c744).to_bytes(3, 'big') #12

	f.seek(pos)


	# Update Magnus Mix
	if mode == 'rando':
	
		qmag_list = []
		for x in range(len(location)):
			if location[x][0] == 'Magnus Mix' and location[x][0] not in qmag_list:
				qmag_list.append(location[x])

	# Update Magnus Mix/Improve Magnus Mixer
	for x in range(50):
		temp_array = []
		pos = fBuffer.find(k1,pos)
		f.seek(pos+8)
		temp_array.append(int.from_bytes(f.read(2), 'little'))

		newBuffer = qol(temp_array[-1], newBuffer, pos+8)

		pos = fBuffer.find(k2,pos)
		f.seek(pos+5)
		temp_array.append(int.from_bytes(f.read(2), 'little'))
		
		# Update Magnus Mix
		if mode == 'rando':
		
			newBuffer = mix_random(newBuffer, pos+5,qmag_list[x][4])

		pos += 7
		
		for y in range(11):
			pos = fBuffer.find(k2,pos)
			f.seek(pos+5)
			temp_array.append(int.from_bytes(f.read(2), 'little'))
			
			if y%2 ==0:
				newBuffer = qol(temp_array[-1], newBuffer, pos+5)
			
			pos += 7
		
		f.seek(pos)
		temp = f.read(1)
		
		if temp.hex() =='45':
			f.read(3)
			temp_array.append(0)
		else: 
			f.read(2)
			temp_array.append(int.from_bytes(f.read(2), 'little'))
			f.read(1)
		
		f.read(2)
		temp_array.append(int.from_bytes(f.read(2), 'little'))

		
		f.read(2)
		temp_array.append(int.from_bytes(f.read(2), 'little'))


	
	# Make Items droppable
	pos =0x14A8314
	k1 = (0xc7442428).to_bytes(4, 'big') #1

	if mode == 'rando':
		f.seek(pos)
		#Skip Royal Mirror
		for x in range(170):
			temp_array = []
			pos = fBuffer.find(k1,pos)
			f.seek(pos+7)

			flag= int.from_bytes(f.read(1),'little')

			if flag == 64:

				newBuffer = newBuffer[:pos+7] + (80).to_bytes(1, 'little') + newBuffer[pos+8:]
			
			pos += 10	

	lines = f4.readlines()
	
	# Update Magnus time
	qMag = []
	for line in lines:
		line = line.strip('\n')
		temp = line.split(',')
		temp_array = []
		for x in range(len(temp)):
			temp_array.append(temp[x])
		qMag.append(temp_array)


	pos =0x14A818F
	k1 = (0xc7842458010000).to_bytes(7, 'big') #1

	f.seek(pos)

	for x in range(1,len(qMag)):
		k1_temp = k1 + int(qMag[x][1]).to_bytes(2,'little')
		pos = fBuffer.find(k1_temp,pos)

		nTime = int(qMag[x][2])
		newBuffer = newBuffer[:pos+7] + (nTime).to_bytes(2, 'little') + newBuffer[pos+9:]
		pos += 1	

	# Ballet Dancer
	pos = 0x12d9bee
	newBuffer = newBuffer[:pos] + (69).to_bytes(2, 'little') + newBuffer[pos+2:]
	
	pos = 0x12d9c8f
	newBuffer = newBuffer[:pos] + (69).to_bytes(2, 'little') + newBuffer[pos+2:]
	
	pos = 0x12d9d38
	newBuffer = newBuffer[:pos] + (69).to_bytes(2, 'little') + newBuffer[pos+2:]

	# Wingdash
	pos = 0x14A7EDD
	newBuffer = newBuffer[:pos] + (30).to_bytes(1, 'little') + newBuffer[pos+1:]

	pos = 0x14A7ED2
	newBuffer = newBuffer[:pos] + (1).to_bytes(1, 'little') + newBuffer[pos+1:]


	# Upgrades

	pos =0x1655710
	f.seek(pos)
	k = (0xc74424 << 8)  + 0x2c
	for x in range(4):
		k1 = k.to_bytes(4,'big')
		pos = fBuffer.find(k1,pos)+4
		f.seek(pos+4)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

			
	k = (0xc745 << 8) + 0x8c
	for x in range(5):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+3
		f.seek(pos+3)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = 0x48c74504
	k1 = k.to_bytes(4,'big')
	pos = fBuffer.find(k1,pos)+4
	f.seek(pos+4)
	newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]

	
	k = (0xc745 << 8) + 0x1c
	for x in range(5):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+3
		f.seek(pos+3)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24
	
	k = (0xc785 << 8) + 0x94
	for x in range(5):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	

	k = (0xc785 << 8) + 0x0c
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	
		
	k = (0xc785 << 8) + 0x14
	for x in range(10):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24		
		
	k = (0xc785 << 8) + 0x04
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		y = f.read(4)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	
		
	k = (0xc785 << 8) + 0x0c
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	
		
	k = (0xc785 << 8) + 0x14
	for x in range(10):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	
		
	k = (0xc785 << 8) + 0x04
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	
		
	k = (0xc785 << 8) + 0x0c
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	
		
	k = (0xc785 << 8) + 0x14
	for x in range(10):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24	

	k = (0xc785 << 8) + 0x04
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24
		
	k = (0xc785 << 8) + 0x0c
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = 0x48c785140b
	k1 = k.to_bytes(5,'big')
	pos = fBuffer.find(k1,pos)+7
	f.seek(pos+7)
	newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]

	k = (0xc785 << 8) + 0x2c
	for x in range(9):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = (0xc785 << 8) + 0x04
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = (0xc785 << 8) + 0x0c
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = (0xc785 << 8) + 0x14
	for x in range(10):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = (0xc785 << 8) + 0x04
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = (0xc785 << 8) + 0x0c
	for x in range(11):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24

	k = (0xc785 << 8) + 0x14
	for x in range(10):	
		k1 = k.to_bytes(3,'big')
		pos = fBuffer.find(k1,pos)+6
		f.seek(pos+6)
		newBuffer = newBuffer[:pos] + (0x03fffe).to_bytes(4, 'little') + newBuffer[pos+4:]
		k += 24
		
		
	f2.write(newBuffer)

	f.close()
	f2.close()
	f4.close() 
	
	if mode == 'rando':
		if pacman == True: mode = 'Pac-Man'
		generate_spoiler(location, orig_location, progression, seed,mode)
	else:
		if getattr(sys, 'frozen', False):
			scriptPath = os.path.dirname(os.path.realpath(sys.executable))
		else:
			scriptPath = os.path.dirname(os.path.realpath(__file__))
		
		metaFile = os.path.join(scriptPath, 'Seeds', seed, 'meta.txt')	
		dllFile = os.path.join(scriptPath, 'Seeds', seed, 'GameAssembly.dll')
		cTime = time.ctime(time.time())
		dllHash = hashlib.md5(open(dllFile,'rb').read()).hexdigest()
		
		f5 = open(metaFile ,'w')
		f5.write('Baten Kaitos Origins Randomizer v0.2\n')
		f5.write('Created: ' + cTime + '\n')
		f5.write('Mode :\t' + mode + '\n')
		f5.write('dll MD5 Hash :\t' + str(dllHash))
		f5.close()

def patch(decomp, offset, magType, add1, add2,mag):
	

	mag = int(mag)
	
	if magType != 6 and magType != 7:
		decomp = decomp[:offset] + (mag).to_bytes(4,'big') + decomp[offset+4:]
	else:
		decomp = decomp[:offset] + (mag).to_bytes(2,'big') + decomp[offset+2:] 
	if add1 != '':
		decomp = decomp[:add1] + (offset).to_bytes(4,'big') + decomp[add1+4:]
	if add2 != '':
		decomp = decomp[:add2] + (offset).to_bytes(4,'big') + decomp[add2+4:]	

	return (decomp)

def qol(nBat, newBuffer, add):

	if nBat == 3:
		newBuffer = newBuffer[:add] + (1).to_bytes(2,'little') + newBuffer[add+2:]
	return(newBuffer)
	
def mix_random(newBuffer, add, mag):

	newBuffer = newBuffer[:add] + (int(mag)).to_bytes(2,'little') + newBuffer[add+2:]
	return(newBuffer)


def rando():

	if getattr(sys, 'frozen', False):
		scriptPath = os.path.dirname(os.path.realpath(sys.executable))
	else:
		scriptPath = os.path.dirname(os.path.realpath(__file__))

	randoFile = os.path.join(scriptPath, 'data', 'BK_rando.csv')

	f3 = open(randoFile)

	lines = f3.readlines()

	location = []
	for line in lines:
		temp = line.split(',')
		temp_array = []
		for x in range(len(temp)):
			temp_array.append(temp[x].replace('\n',''))
		location.append(temp_array)

	del(location[0])

	temp_array = copy.deepcopy(location)
	rand_location = []
	new_location = []

	failed_seeds =0
	error = True
	while error:
		rand_location = copy.deepcopy(location)
		random.shuffle(rand_location)
		new_location = []
		rand_mag = [row[4] for row in rand_location]
		orig_mag = copy.deepcopy(rand_mag)


		while '670' in rand_mag: rand_mag.remove('670')
		rand_mag.remove('640')
		rand_mag.remove('641')	
		rand_mag.remove('660')
		rand_mag.remove('529')
		rand_mag.remove('647')
		rand_mag.remove('501')
		rand_mag.remove('686')
		rand_mag.remove('503')
		rand_mag.remove('534')
		# Stone Chick Tree Overwrites
		rand_mag.remove('514')
		rand_mag.remove('514')
		
		orig_mag = copy.deepcopy(rand_mag)
		
		random.shuffle(rand_mag)
		

		accessible_mags = []
		accessible_loc = []
	
		try:
			# Dark Service Water
			state = ['2'],['']
			mags = ['503']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)

			# Dark Service Flame
			state = ['2'],['3'],['']
			mags = ['506']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)
			
			# Palace Rubber
			state = ['14'],['']
			mags = ['552']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)

			# Palace Any Water
			state = ['14'],['']
			mags = ['501','502','503']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)

			# Mintaka Mchina Oil
			state = ['15'],['']
			mags = ['563']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)
			
			# Fresh/Foul Air
			state = (['2'],['3'],['4'],['5'], ['7'], ['8'],['10'],['11'],['12'],['13'],['14'],['15'],['16'],['17'],['18'],['19'],['20'],['21'],['23'],
					['24'],['27'],['30'],['30a'],['33'],['34'],['35'],['36'],['38'],['39'],['40'],['41'],['42'],['43'],['44'],['45'],['46'],['47'],['48'],['49'],['50'],['51'],['52'],[''])
			mags = ['640','641']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)

			# Yesterbean
			state = ['24'], ['']
			mags = ['651']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)

			# Mountain Apple
			state = ['24'], ['27'],['']
			mags = ['529']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)

			# Thornflower Nectar
			state = ['24'], ['27'],['']
			mags = ['617']
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc)

			# Randomize Mixes
			index = [] 

			for x in range(len(rand_location)-1):
				c = 0

				if rand_location[x][0] == 'Magnus Mix':
					mix_valid = False
					# Check if unique quest magnus is not required to make itself
					while not mix_valid:
						if rand_mag[x+c] in rand_location[x] and rand_mag.count(rand_mag[x + c]) == 1:
							c+=1			
						else:
							mix_valid = True
								
					rand_location[x][4] = rand_mag[x+c]
					index.append(x)

			for indexes in sorted(index, reverse=True):
				del rand_mag[indexes]

			# Lily
			state = ['24'], ['27'], ['30'], ['']
			mags = ['647']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 4
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Any drinkable water
			
			state = ['24'], ['27'], ['30'], ['30a'],['']
			mags = ['501','502','503']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 4
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Balmsand
			state = ['48'], ['']
			mags = ['638']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6
			rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Any Water
			
			state = ['2'], ['3'], ['15'], ['16'], ['17'], ['19'], ['']
			mags = ['501','502','503', '525']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Tags
			
			state = (['2'],['3'],['4'],['5'], ['7'], ['8'],['10'],['11'],['12'],['13'],['14'],['15'],['16'],['17'],['18'],['19'],['20'],['21'],['23'],
					['24'],['27'],['30'],['30a'],['33'],['34'],['35'],['36'],['38'],['39'],['40'],['41'],['42'],['43'],['44'],['45'],['46'],['47'],['48'],['49'],['50'],['51'],['52'],[''])
			mags = ['666']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

				
			# Medic Kit
			
			state = ['2'], ['3'], ['15'], ['16'], ['17'], ['19'], ['']
			mags = ['652']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

				
			# Fruit
			
			state = ['2'], ['3'], ['15'], ['16'], ['17'], ['19'], ['']
			mags = ['535']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Comminicator
			
			state = ['2'], ['3'], ['5'], ['8'], ['10'], ['15'], ['16'], ['17'], ['19'], ['20'], ['23'], ['']
			mags = ['627']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				

			# Metal Device
			
			state = ['2'], ['3'], ['5'], ['8'], ['10'], ['15'], ['16'], ['17'], ['19'], ['20'], ['23'], ['']
			mags = ['667']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Mallo's Testimony
			
			state = ['2'], ['3'], ['5'], ['8'], ['10'], ['15'], ['16'], ['17'], ['19'], ['20'], ['23'], ['']
			mags = ['544']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Juwar's Testimony
			
			state = ['2'], ['3'], ['5'], ['8'], ['10'], ['15'], ['16'], ['17'], ['19'], ['20'], ['23'], ['']
			mags = ['541']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Rockfly Corpse
			
			state = (['2'],['3'],['4'],['5'], ['7'], ['8'],['10'],['11'],['12'],['13'],['14'],['15'],['16'],['17'],['18'],['19'],['20'],['21'],['23'],
					['24'],['27'],['30'],['30a'],['33'],['34'],['35'],['36'],['38'],['39'],['40'],['41'],['42'],['43'],['44'],['45'],['46'],['47'],['48'],['49'],['50'],['51'],['52'],['54'],[''])
			mags = ['669']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
			
			# Eau de Mouce
			
			state = ['2'], ['3'], ['5'], ['8'], ['10'], ['15'], ['16'], ['17'], ['19'], ['20'], ['23'], ['']
			mags = ['660']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Diadem Cloud
			state = ['2'], ['3'], ['5'], ['8'], ['10'], ['11'], ['12'], ['13'], ['14'], ['15'], ['16'], ['17'], ['18'], ['19'], ['20'], ['21'], ['23'], ['24'], ['27'], ['30'], ['30a'], ['31'], ['33'], ['']
			mags = ['548']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Gust Boulder
			state = ['2'], ['3'], ['5'], ['8'], ['10'], ['11'], ['12'], ['13'], ['14'], ['15'], ['16'], ['17'], ['18'], ['19'], ['20'], ['21'], ['23'], ['24'], ['27'], ['30'], ['30a'], ['31'], ['33'], ['']
			mags = ['650']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Bloodstained Crest
			state =  ['31'], ['32'], ['33'],['34'], ['']
			mags = ['559']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Billowsmoke
			state = (['2'], ['3'], ['5'], ['8'], ['10'], ['11'], ['12'], ['13'], ['14'], ['15'], ['16'], ['17'], ['18'], ['19'], ['20'], ['21'], ['23'], ['24'], ['27'], ['30'],['30a'], ['33'], 
			['34'], ['35'], ['36'], ['38'], [''])
			mags = ['680']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Flame Ice
			state = (['2'], ['3'], ['5'], ['8'], ['10'], ['11'], ['12'], ['13'], ['14'], ['15'], ['16'], ['17'], ['18'], ['19'], ['20'], ['21'], ['23'], ['24'], ['27'], ['30'], ['30a'], ['33'], 
			['34'], ['35'], ['38'], [''])
			mags = ['665']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Light Powder
			state = ['46'], ['47'], ['48'], ['49'], ['50'], ['']
			mags = ['643']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Nectar
			
			state = ['41'], ['42'], ['']
			mags = ['682']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Stone
			
			state = ['41'], ['']
			mags = ['514']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Fruit
			
			state = ['41'], ['']
			mags = ['681']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Traditional Coockies
			
			state = ['39'], ['41'], ['42'],  ['']
			mags = ['644']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Good Times
			
			state = ['39'], ['41'], ['42'],  ['']
			mags = ['659']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Rotten Food
			
			state = ['39'], ['41'], ['42'],  ['']
			mags = ['520']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Woodfellah
			
			state = ['39'], ['40'], ['41'], ['42'], ['43'],  ['']
			mags = ['679']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Fire Dagroot
			
			state = ['39'], ['40'], ['41'], ['42'], ['43'], ['44'],  ['']
			mags = ['632']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Ice Dagroot
			
			state = ['39'], ['40'], ['41'], ['42'], ['43'], ['44'],  ['']
			mags = ['633']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Lightning Dagroot
			
			state = ['39'], ['40'], ['41'], ['42'], ['43'], ['44'],  ['']
			mags = ['634']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Dark Dagroot
			
			state = ['39'], ['40'], ['41'], ['42'], ['43'], ['44'],  ['']
			mags = ['635']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Holy Dagroot
			
			state = ['39'], ['40'], ['41'], ['42'], ['43'], ['44'],  ['']
			mags = ['636']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 6 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				
			# Fellbranch
			
			state = ['39'], ['40'], ['41'], ['42'], ['43'], ['44'], ['45'],  ['']
			mags = ['631']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 8 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Lotus
			
			state = (['2'],['3'],['4'],['5'], ['7'], ['8'],['10'],['11'],['12'],['13'],['14'],['15'],['16'],['17'],['18'],['19'],['20'],['21'],['23'],
					['24'],['27'],['30'],['30a'],['33'],['34'],['35'],['36'],['38'],['39'],['40'],['41'],['42'],['43'],['44'],['45'],['46'],['47'],['48'],['49'],['50'],['51'],['52'],[''])
			mags = ['646']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 8 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)

			# Heartenbrace
			
			state = (['2'],['3'],['4'],['5'], ['7'], ['8'],['10'],['11'],['12'],['13'],['14'],['15'],['16'],['17'],['18'],['19'],['20'],['21'],['23'],
					['24'],['27'],['30'],['30a'],['33'],['34'],['35'],['36'],['38'],['39'],['40'],['41'],['42'],['43'],['44'],['45'],['46'],['47'],['48'],['49'],['50'],['51'],['52'],['54'],[''])
			mags = ['628']
			updated = True
			while updated:
				state, updated = update_state(state, accessible_mags, accessible_loc)
			limit = 8 
			accessible = False
			for x in mags:
				if x in state:
					accessible = True
			if not accessible:
				rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
				

			progression = copy.deepcopy(new_location)
			

			found = True
			while found:
				found = False
				for x in range(len(rand_location)):
					if int(rand_location[x][6]) > 99:
						for y in range(len(rand_location)-1,-1,-1):
							if rand_location[x][6] == rand_location[y][6]:
								if rand_location[x][9] == '1':
									for z in range(len(rand_mag)):
										if rand_mag.count(rand_mag[z]) > 1:
											new_mag = rand_mag[z]
											del(rand_mag[z])
											break
								else:
									new_mag = rand_mag[0]
									del(rand_mag[0])
								rand_location[x][4] = new_mag
								rand_location[y][4] = new_mag
								new_location.append(rand_location[x])
								new_location.append(rand_location[y])
								del(rand_location[y])
								del(rand_location[x])
								found = True
								break
						if found:
							break
					if found:
						break


			for x in range(len(rand_location)-1,-1,-1):
				if rand_location[x][9] == '1':
					for z in range(len(rand_mag)):
						if rand_mag.count(rand_mag[z]) > 1:
							new_location.append(rand_location[x])
							new_location[-1][4] = rand_mag[z]
							del(rand_location[x])
							del(rand_mag[z])
							break
			
			
			while len(rand_location) > 0:
				if rand_location[0][9] == '0':
					new_location.append(rand_location[0])
					del(rand_location[0])
				elif rand_location[0][0] == 'Magnus Mix':
					if rand_location[0] in new_location:
						del(rand_location[0])
					else:
						new_location.append(rand_location[0])
						del(rand_location[0])
				else:
					new_location.append(rand_location[0])
					new_location[-1][4] = rand_mag[0]
					del(rand_location[0])
					del(rand_mag[0])
			

			if len(rand_mag) != 0 or len(rand_location) !=0:
				raise Exception()

			# Place the quest magnus back in order
			qmag = []
			for x in  range(len(location)-1,-1,-1):
				for y in  range(len(new_location)-1,-1,-1):
					if location[x][0] == 'Magnus Mix' and new_location[y][5] == location[x][5] and  new_location[y][0] == 'Magnus Mix':
						if new_location[y][5] not in qmag:
							qmag.append(new_location[y])
						del(new_location[y])

			
			qmag = qmag[::-1]
			for x in qmag:
				new_location.append(x)


			new_mag = [row[4] for row in new_location]
			for x in orig_mag:
				if x not in new_mag:
					raise Exception() 

		
		
			error = False
	
		except:
			failed_seeds +=1


	return(new_location, location, progression)

def find_location(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc):
	
	abort =False
	for x in range(len(rand_location)):
		if [rand_location[x][9]] in state and [rand_location[x][10]] in state and rand_location[x][0] != 'Magnus Mix':
			for y in range(len(rand_mag)):
				if rand_mag[y] in mags and not abort:
					new_location.append(rand_location[x])
					new_location[-1][4] = rand_mag[y]
					new_mag = rand_mag[y]
					del(rand_location[x])
					del(rand_mag[y])
					abort = True
					if int(new_location[-1][6]) > 99:
						for z in range(len(rand_location)):
							if new_location[-1][6] == rand_location[z][6]:
								rand_location[z][4] = new_mag
								new_location.append(rand_location[z])
								del(rand_location[z])
								break
					break

		if abort:
			break
	if abort == False:
		return()
	
	accessible_mags.append(new_location[-1][4])
	accessible_loc.append(new_location[-1][9])	
	
	return(rand_location,rand_mag, new_location,accessible_mags,accessible_loc)
	
def find_location2(state, mags, rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit):

	abort =False
	for x in range(len(rand_location)):
		
		if rand_location[x][0] == 'Magnus Mix' and rand_location[x][limit+6] != [''] and rand_location[x][4] in mags:
				if not abort:
					new_location.append(rand_location[x])
					new_location[-1][4] = rand_location[x][4]
					length = len(new_location)-1
					for z in range(7,15):
						if [new_location[length][z]] not in state and new_location[length][z] !='':
							rand_location,rand_mag, new_location,accessible_mags,accessible_loc = find_location2(state, new_location[length][z], rand_location, rand_mag, new_location,accessible_mags,accessible_loc, limit)
							updated = True
							while updated:
								state, updated = update_state(state, accessible_mags, accessible_loc)

					
					abort = True
					break

			
		elif  [rand_location[x][9]] in state and [rand_location[x][10]] in state and rand_location[x][0] != 'Magnus Mix':
			for y in range(len(rand_mag)):
				if rand_mag[y] in mags and not abort:
					new_location.append(rand_location[x])
					new_location[-1][4] = rand_mag[y]
					new_mag = rand_mag[y]
					del(rand_location[x])
					del(rand_mag[y])
					if int(new_location[-1][6]) > 99:
						for z in range(len(rand_location)):
							if new_location[-1][6] == rand_location[z][6]:
								rand_location[z][4] = new_mag
								new_location.append(rand_location[z])
								del(rand_location[z])
								break
								
					abort = True
					break
		
		if abort:
			break
	
	
	if not abort:
		return()

		
	accessible_mags.append(new_location[-1][4])
	accessible_loc.append(new_location[-1][9])	
	
	return(rand_location,rand_mag, new_location,accessible_mags,accessible_loc)
	
	
def update_state(state, accessible_mags, accessible_loc):
	updated = False
	for x in range(len(accessible_loc)):
		if [accessible_loc[x]] in state and [accessible_mags[x]] not in state:
			state = list(state)
			state.append([accessible_mags[x]])
			state = tuple(state)
			updated = True
		
	return(state,updated)

def rand_seed():
	seed = random.randint(0x1000000000,0xFFFFFFFFFF)
	return(seed)

def generate_spoiler(new_location, location, progression, seed,rMode):
	
	if getattr(sys, 'frozen', False):
		scriptPath = os.path.dirname(os.path.realpath(sys.executable))
	else:
		scriptPath = os.path.dirname(os.path.realpath(__file__))
		
	metaFile = os.path.join(scriptPath, 'Seeds', seed, 'global-metadata.dat')
	dllFile = os.path.join(scriptPath, 'Seeds', seed, 'GameAssembly.dll')
	spoilerFile = os.path.join(scriptPath, 'Seeds', seed, 'spoiler.txt')
	oMetaFile = os.path.join(scriptPath, 'Seeds', seed, 'meta.txt')
	maglistFile = os.path.join(scriptPath, 'data', 'BK_mag_list.csv')
	
	metaHash= hashlib.md5(open(metaFile,'rb').read()).hexdigest()
	dllHash = hashlib.md5(open(dllFile,'rb').read()).hexdigest()
	f5 = open(spoilerFile ,'w')
	f6 = open(oMetaFile ,'w')
	
	with open(maglistFile, mode='r', newline='', encoding='utf-8') as file:
		reader = csv.reader(file)
		mag_list = {rows[0]: rows[1] for rows in reader} 
	
	cTime = time.ctime(time.time())
	if rMode == 'rando': rMode = 'Full'
	
	f5.write('Baten Kaitos Origins Randomizer v0.2\n')
	f5.write('Created: ' + cTime + '\n')
	f5.write('Seed :\t' + seed + '\n')
	f5.write('Mode :\t' + rMode + '\n')
	f5.write('Meta MD5 Hash :\t' + str(metaHash) + '\n')
	f5.write('dll MD5 Hash :\t' + str(dllHash) + '\n\n')
	
	f6.write('Baten Kaitos Origins Randomizer v0.2\n')
	f6.write('Created: ' + cTime + '\n')
	f6.write('Seed :\t' + seed + '\n')
	f6.write('Mode :\t' + rMode + '\n')
	f6.write('Meta MD5 Hash :\t' + str(metaHash) + '\n')
	f6.write('dll MD5 Hash :\t' + str(dllHash)+ '\n\n')

	header = location[0][0]
	f5.write(header)
	f5.write('\n---------------------------------------------------------------------------------------\n')
	f5.write('Sub-Location                    Original Magnus                 New Magnus\n')
	f5.write('------------                    ---------------                 ----------\n')
	for x in range(len(location)):
		if header != location[x][0]:
			header = location[x][0]
			f5.write('\n\n' + header)
			f5.write('\n---------------------------------------------------------------------------------------\n')
			if location[x][0] == 'Magnus Mix':
				f5.write('Original Magnus         New Magnus\n')
				f5.write('---------------         ----------\n')
			else:
				f5.write('Sub-Location                    Original Magnus                 New Magnus\n')
				f5.write('------------                    ---------------                 ----------\n')
		if location[x][0] != 'Magnus Mix':
			for y in range(len(new_location)):
				if (location[x][:4] == new_location[y][:4]):
					if rMode == 'Pac-Man' and location[x][2:4] == ['441e61c5_0','6f60']:
						mag = '549'
						break
					else:
						mag = new_location[y][4]
						break
		else:
			for y in range(len(new_location)):
				if (location[x][6:15] == new_location[y][6:15]):
					mag = new_location[y][4]
					break
					
		if location[x][0] != 'Magnus Mix' and location[x][5] != 'Overwrite' :
			length1 = 4-int(math.floor(len(location[x][1])/8))
			length2 = 4-int(math.floor(len(location[x][5])/8))
			f5.write(location[x][1] + '\t'*length1 + location[x][5] + '\t'*length2  +  mag_list[mag]+'\n')
		
		elif location[x][0] == 'Magnus Mix':
			length1 = 3-int(math.floor(len(location[x][5])/8))
			f5.write(location[x][5] + '\t'*length1  +  mag_list[mag]+'\n')			

	f5.write('\n\nProgression')
	f5.write('\n--------------------------------------------------------------------------------------------------------------------------\n')
	f5.write('    Location                            Sub-Location                    Orignal Magnus                  New Magnus\n')
	f5.write('    --------                            ------------                    --------------                  ----------\n')
		
	for x in range(len(progression)):
		if location[x][0] != 'Magnus Mix':
			for y in range(len(location)):
				if (location[y][:4] == progression[x][:4]):
					mag = progression[x][4]
					break
		else:
			for y in range(len(location)):
				if (location[y][6:15] == progression[x][6:15]):
					mag = progression[x][4]
					break
		
		if x > 9:
			shift = 1
		else:
			shift = 2
			
		if progression[x][0] != 'Magnus Mix':
			length1 = 5-int(math.floor((len(progression[x][0])+4)/8))
			length2 = 4-int(math.floor(len(progression[x][1])/8))
			length3 = 4-int(math.floor(len(progression[x][5])/8))
			f5.write(str(x+1) + ')' + ' ' *shift+ progression[x][0] + '\t'*length1 + progression[x][1] + '\t'*length2  + progression[x][5] + '\t'*length3 +  mag_list[mag] +'\n')
		
		elif progression[x][0] == 'Magnus Mix':
			length1 = 9-int(math.floor((len(progression[x][0])+4)/8))
			length2 = 4-int(math.floor(len(progression[x][5])/8))
			f5.write(str(x+1) + ')' + ' ' *shift +progression[x][0] + '\t'*length1  +  progression[x][5] + '\t'*length2 +  mag_list[mag] +'\n' )

if __name__ == "__main__":
		

	parser = argparse.ArgumentParser()
	parser.add_argument('--seed', '-s', default = '',  help = 'Enter seed number. Default is blank')
	parser.add_argument('--mode', '-m', default = 'full',  help = 'Randomizer mode. Options are "full" or "qol"')
        
	args = parser.parse_args()
	
	if args.seed != '':
		args.seed = int('0x' + args.seed,16)
	
 
	main(seed=args.seed, mode=args.mode)	

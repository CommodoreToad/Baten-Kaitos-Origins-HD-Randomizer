import time
import csv
import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog

def main(mode):

	if getattr(sys, 'frozen', False):
		scriptPath = os.path.dirname(os.path.realpath(sys.executable))
	else:
		scriptPath = os.path.dirname(os.path.realpath(__file__))
	
	
	data0File = os.path.join(scriptPath, 'data0_loc.txt')
	
	path = check_data0(data0File)
	
	f = os.path.join(scriptPath, 'data', 'BK_mag_list.csv')

	mag_list = []
	exclusion = [31,37,38,39,40,41,42,43,44,45,48,49,50,58,81,83,84,85,86,87,88,89,90,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,114,126,128,153,156,165,166,167,169,170,171,178]

	with open(f, mode='r', newline='', encoding='utf-8') as file:
		reader = csv.reader(file)
		for row in reader:
			mag_list.append(row[1])
	
	while True:
		eaten = []
		found = 0
		os.system('cls' if os.name == 'nt' else 'clear')
		print('Missing Magnus')
		print('')
		f1 = open(path, 'rb')
		f1.seek(0x10394)
		for x in range(199):
			byte = f1.read(2)
			
			count = int.from_bytes(byte, 'big')
			
			if count == 0 and x not in exclusion:
				eaten.append(mag_list[x])
				#print(x,mag_list[x])
			elif x not in exclusion:
				found+=1
		
		eaten = sorted(eaten)
		n= 50
		for i in range(0, len(eaten), 4):
			line = eaten[i:i+4]
			print("{:<32} {:<32} {:<32} {:<32}".format(*line, *[""] * (4 - len(line))))

		print()
		print('Pac-Man has eaten ' + str(found) + ' of 147')
		
		if mode == 'manual':
			input('Press "Enter" to update')
		else:
			time.sleep(30)


def check_data0(data0File):
  
	if os.path.exists(data0File):
		f = open(data0File, 'r')
		path = f.readline().strip()
		return(path)
    
	print(r'data0 not found. Please open \steamapps\common\BatenKaitos HD Remaster\Batenkaitos2\Batenkaitos_Data\sd\py\data0')
	root = tk.Tk()
	root.withdraw()  # Hide the main window
	path = filedialog.askopenfilename(title="Open data0")
    
	if os.path.basename(path) != 'data0':
		print('Selected file is not data0, exiting')
		exit()

	f = open(data0File, 'w')
	f.write(path)
    
	return(path)


if __name__ == "__main__":
		

	parser = argparse.ArgumentParser()
	parser.add_argument('--mode', '-m', default = 'manual',  help = 'Choose Mode: "auto", "manual"')
        
	args = parser.parse_args()

	
 
	main(mode=args.mode)	

Baten Kaitos Origins Randomizer v0.2

Instructions:
1) Make a backup and copy the following files to "original_files" folder:
	a) "\steamapps\common\BatenKaitos HD Remaster\Batenkaitos2\GameAssembly.dll"
	b) "\steamapps\common\BatenKaitos HD Remaster\Batenkaitos2\Batenkaitos_Data\il2cpp_data\Metadata\global-metadata.dat"

2) The release files contain BK2_Randomizer.py and BK2_Randomizer.exe. BK2_Randomizer.py requires Python 3 to run.

3) In a command line, run "BK2_Randomizer.exe" or "py BK2_Randomizer.py". The '-s <seed#>' argument may be used for a specific seed. The '-m <mode>' may be used for the mode.
   
| Mode  | Description                                                      |
|-------|------------------------------------------------------------------|
| full  | This is the default mode. This mode shuffles all of the Magnus locations and Magnus Mixes. |
| qol   | This mode only adds the quality of life features.                 |

4) In the "Seeds" folder, the patch files will be generated under the folder with that seed name. To run the game, copy those files and overwrite the normal game files.
   The game can be returned to its original state by placing the original files in their original locations.

Notes:
1) This mod randomizes all of the quest Magnus found in the world, including the result of Magnus mixes. Each quest Magnus should be obtainable from a persistent location.
2) Magnus mixes are in logic, and it is possible chained mixes are required for progression.
3) Temporary or one time Magnus are not unique. 

Changes to the base game:
1) Updated the magnus age time to be faster or slower. This is still being balanced.
2) All quest Magnus may be thrown away at anytime except the Royal mirror. These Magnus can be obtained again.
3) The cookie thugs will no longer bother you (full mode only for now).
4) Ballet Dancer has been added to the Colesium, Rank 5: Nukerz.
5) All Magnus Mixers now behave as Prototype Mixers.
6) Shops can now update any Magnus.

Pac-Man Script:

This script will monitor your autosave file for what Magnus Pac-Man still needs to eat.

In the command line, run "pac-man.exe" or pac-man.py". The script can be run with argument '-m <mode>'

| Mode   | Description                                                                 |
|--------|-----------------------------------------------------------------------------|
| manual | This is the default mode. This mode shuffles all of the Magnus locations and Magnus Mixes. |
| auto   | This mode automatically updates the list after 30 seconds.|


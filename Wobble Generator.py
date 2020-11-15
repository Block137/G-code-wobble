axial_strength  = 0.0  # mm
axial_offset    = 0.0   # mm
radial_strength = 0.3   # mm !!BEWARE!! G-code boundary will expand by this amount horizontally
radial_offset   = 0.0   # mm

screw_pitch     = 4.0   # mm
# how many mm of travel in Z per 1 revolution of Z screw

screw_direction = True
# not required if radial_strength is 0.0
# True:  looking down, screw truns CCW when nozzle and bed diverge
# False: opposite of above

Z_min = 0.0
# limit

XY_decimalplaces = 3    # adjust output resolution
Z_decimalplaces  = XY_decimalplaces # yes, you can do this

# SANITY CHECK
axial_strength   = max(min(screw_pitch, axial_strength), 0.0)
axial_offset     = max(min(axial_offset, screw_pitch), -screw_pitch)
radial_strength  = max(min(radial_strength, 20.0), -20)
radial_offset    = max(min(radial_offset, screw_pitch), -screw_pitch)
XY_decimalplaces = max(XY_decimalplaces, 0)
Z_decimalplaces  = max(Z_decimalplaces, 0)

import os
import time
import math

print('\n-------------GCODE Modifier-------------')
print(  '----------Z-Wobble Compensator----------')

def getX(gcode):
    return float(gcode.strip().split('X')[-1].split()[0])
def getY(gcode):
    return float(gcode.strip().split('Y')[-1].split()[0])
def getZ(gcode):
    return float(gcode.strip().split('Z')[-1].split()[0])

file_list = os.listdir()
file_path = [file for file in file_list if file.endswith('.gcode') and not file.endswith('_EDITED.gcode')]
if len(file_path) == 0:
    print('.gcode file not found. Please place the .gcode file in the same folder with this script')
    print('Press Enter to close')
    input()
    exit()
else:
    print('Found',len(file_path),'gcode file(s) :')
    print(file_path,'\n')

# assume initial values
X = 0.0
Y = 0.0
Z = 0.0
K_mm_to_rad = (2.0 * math.pi) / screw_pitch
K_radial_offset = K_mm_to_rad * radial_offset
K_axial_offset = K_mm_to_rad * axial_offset

screw_pos = K_mm_to_rad * Z
radial_mod_X = radial_strength * math.cos(screw_pos + K_radial_offset)
radial_mod_Y = radial_strength * math.sin(screw_pos + K_radial_offset)
axial_mod_Z  = axial_strength  * math.sin(screw_pos + K_axial_offset)

for gfile in file_path: #for each file....
    print("Scanning file: ["+gfile+"] . . .")
    gcodes = open(gfile, 'r').readlines()

    new_gcodes = list()
    time1 = time.time()
    
    for i in range(len(gcodes)):
    
        if gcodes[i].startswith('G0') or gcodes[i].startswith('G1'):
            p = dict([(x[0],x[1:]) for x in gcodes[i].split(';')[0].split()])
            if 'Z' in p:
                Z = float(p['Z'])
                screw_pos = K_mm_to_rad * Z
                while screw_pos >= (2.0 * math.pi):
                    screw_pos = screw_pos - (2.0 * math.pi)
                radial_mod_X = radial_strength * math.cos(screw_pos + K_radial_offset)
                if screw_direction :
                    radial_mod_Y = radial_strength * math.sin(screw_pos + K_radial_offset)
                else :
                    radial_mod_Y = -radial_strength * math.sin(screw_pos + K_radial_offset)
                axial_mod_Z  = axial_strength  * math.sin(screw_pos + K_axial_offset)
                p['Z'] = str( round(max(Z_min, Z + axial_mod_Z),Z_decimalplaces) )
            
            if 'X' in p:
                p['X'] = str( round(float(p['X']) + radial_mod_X, XY_decimalplaces) )
                
            if 'Y' in p:
                p['Y'] = str( round(float(p['Y']) + radial_mod_Y, XY_decimalplaces) )
            
            p = list(p.items())
            new_gcode = ' '.join([x[0]+str(x[1]) for x in p]) + '\n'
            new_gcodes.append(new_gcode)
    
        else :
            new_gcodes.append(gcodes[i])

    time2 = time.time()
    print("\tScan finished\t(took {:.2f}s)".format(time2 - time1))
    print("\tline count:       {:,}".format(i))

    print("\tWriting file: ["+gfile+ "_EDITED.gcode] . . .")
    # Write a new file ending with .edited.gcode
    edited = open(gfile[:-6] + '_EDITED' + gfile[-6:],'w')
    edited.writelines(new_gcodes)
    edited.close()
    
    time3= time.time()
    print("\tSuccess!\t(took {:.2f}s,  ".format(time3-time2) + "{:.2f}s total)\n".format(time3-time1))
    
print("All done!\n")
print("Press Enter to close")
input()

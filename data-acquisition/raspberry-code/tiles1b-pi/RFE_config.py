#!/usr/bin/python

###### RFEXPLORER CONFIG AND I/O ######
###### J.RASTI 13/10/2015


### HOST SETTINGS ###

##Map tile names to USB indexes
##TODO change these for each pi, after testing inputs
tiles = {0:'tile00',1:'tile01',2:'tile02',3:'tile03',4:'tile04',5:'tile05',6:'tile06',7:'tile07',8:'tile08',9:'tile09',10:'tile10',11:'tile11'}
##TODO match pols with tile names
pols = {0:'XX',1:'XX',2:'XX',3:'XX',4:'XX',5:'XX',6:'XX',7:'XX',8:'YY',9:'YY',10:'YY',11:'YY'}



physical_map = {'1-1.4.6':'S33XX','1-1.4.5.1':'S33YY','1-1.4.5.2':'S35YY','1-1.4.5.3':'S35XX',
                '1-1.4.5.4':'S34YY','1-1.4.5.5':'S36YY','1-1.4.5.6':'S36XX','1-1.4.5.7':'S34XX'}

usb_map = {}
for line in open('usb_port_names.txt','r').read().split('\n'):
    if line == '':
        pass
    else:
        phys_addr,usbport = line.split()
        usb_map[usbport] = phys_addr

# Host settings
gateway = 'jrasti@cerberus.mwa128t.org'
users = {'rec':'jrasti', 'ref':'mwa'}

#hosts = ["%s@%s"%(user[n[0][0:3]],n[0] if n[0]!='ref' else 'allskypie')
#         for n in nodes if n[2]]

# Record parameters
file_flush = 36000       #maximum record time per file


### SWEEP PARAMETERS ###

start_freq = '0137150'   #7 ASCII digits  #'0136800'
end_freq   = '0138550'   #7 ASCII digits  #0138200'
amp_top    = '+005'      #4 ASCII digits
amp_bottom = '-120'      #4 ASCII digits

S_pars = ','.join([start_freq,end_freq,amp_top,amp_bottom])


### RFE SERIAL I/O ###

# File output (eg. to RFExplorer)
send = {"Resume"   :'#\x04C0',         #request current config
        "Hold"     :'#\x04CH',         #stop current data dump
        "Reboot"   :'#\x03r',          #reboot
        "Baudrate" :'#\x04c',          #+<boardrate_code>
        "LCD_off"  :'#\x04L0',         #disable LCD
        "LCD_on"   :'#\x04L1',         #enable LCD
        "Dump"     :'#\x04D1',         #screendump (continuous)
        "End_dump" :'#\x04D0',         #end screendump
        "Mod_Main" :'#\x05CM\x00',     #enable mainboard module
        "Mod_Exp"  :'#\x05CM\x01',     #enable expansion module
        "Set_calc" :'#\x05C+',         #+<CalcMode> set calcmode
        "Trackstep":'#\x05k',          #+<TrackingStep> measure freq
        "Config"   :'# C2-F:'+S_pars}  #reconfig RFE with sweep pars

# File input (eg. from RFExplorer)
read = {"#C2-M:" :"Model",           #device setup (3 objects)
        "#C2-F:" :"Config",          #sweep config (13 objects)
        "$S"     :"Sweep"}           #+<steps><-2AdB>... (binary)


### OUTPUT PARSING (FIRMWARE v1.12) ###

M_data = ("Model", "Exp_Model", "Firmware")

F_data = ("Start_Freq" , "Freq_Step"  , "Amp_Top"    , "Amp_Bottom" ,
          "Sweep_steps", "ExpModule"  , "CurrentMode", "Min_Freq"   ,
          "Max_Freq"   , "Max_Span"   , "ResBwidth"  , "AmpOffset"  ,
          "CalcMode"   )

## Collecting data
The main data collection will only work if you have RF Explorers plugged into USB hubs, _and_ you're running with root privileges, otherwise you can't automagically access the USB ports. I typically scheduled a few nights in a row, to do which I used the wrapper script
```sh
source make_night_schedule.sh
```
which will in turn write the `bash` script `obs_2019-08-13-18:16_to_2019-08-13-18:18.sh`. The arguments in `make_night_schedule.sh` allow you to chunk your observations into whatever length you want (in seconds, using `--time_obs`). Then you just tell it when you want the observations to start (`--start_date`) and when to finish (`--finish_date`) and it will write a script to launch the appropraite amount of observations to fill that length of time. `--num_tiles` let's you set how many inputs you have - this will be different from raspberry pi to raspberry pi.

`obs_2019-08-13-18:16_to_2019-08-13-18:18.sh` will then contain commands to write scripts that are fed to the `at` command with the appropraite starting date, and launches the `at` jobs. There is even a queue checker `atq` which tells you everything that's queued which can use after to check your jobs got launched properly.

There is a settings file `RFE_config_tiles.py` which contains confusing RF Explorer settings that our genius previous students came up with, that are used to drive the RF Explorers. The bit I changed, that we will change on site, are the two dictionaries:

```python
tiles = {0:'tile00',1:'tile01',2:'tile02',3:'tile03',4:'tile04',5:'tile05',6:'tile06',7:'tile07',8:'tile08',9:'tile09',10:'tile10',11:'tile11'}

pols = {0:'XX',1:'XX',2:'XX',3:'XX',4:'XX',5:'XX',6:'XX',7:'XX',8:'YY',9:'YY',10:'YY',11:'YY'}
```
which map the USB port number to the correct tile number and polarisation (USB port numbers get listed here /dev/ttyUSB* if you're curious). We'll have to disconnect the tiles from the RF Explorers one by one during an observation to be exactly sure of which tile maps to which USB port.

**TODO** - if we want to be paranoid, I believe once everything is hooked up, there is a software way of manually forcing specific hardware connections to specific ports - this way if there is a power cut onsite, and the whole thing gets rebooted into a different allocation, we can swap everything back to the way we want to do it. If memory serves it's hard to get correct, but I do have software for it on one of the pis.

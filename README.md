# River_bifurcation

## Notes about install of geofeather and nhdnet
I found it easiest to install geofeather and nhdnet in command line. I had quite a few errors, so it was easier to troubleshoot in terminal.

### Geofeather install
    $ pip install geofeather
This worked just fine.

### NHDnet (see https://pypi.org/project/nhdnet/)
Check that you are running python > 3.6.

    $ python --version

If python is not 3.7 or higher, upgrade with Homebrew (https://brew.sh/). See the following link for more detailed instructions: https://realpython.com/installing-python/#macos-mac-os-x

Once brew is installed, upgrade Python.

    $ brew install python3

This returned the error:
> Error: The following directories are not writable by your user:
> /usr/local/bin
/usr/local/include
/usr/local/lib
/usr/local/share
/usr/local/share/info
/usr/local/share/locale
/usr/local/share/man
/usr/local/share/man/man1
/usr/local/share/man/man7

> You should change the ownership of these directories to your user.
>  sudo chown -R $(whoami) /usr/local/bin /usr/local/include /usr/local/lib /usr/local/share /usr/local/share/info /usr/local/share/locale /usr/local/share/man /usr/local/share/man/man1 /usr/local/share/man/man7

> And make sure that your user has write permission.
>  chmod u+w /usr/local/bin /usr/local/include /usr/local/lib /usr/local/share /usr/local/share/info /usr/local/share/locale /usr/local/share/man /usr/local/share/man/man1 /usr/local/share/man/man7

I followed the commands as given. Then, the brew install command worked.
> ==> python
>  Python has been installed as
>  /usr/local/bin/python3

> Unversioned symlinks `python`, `python-config`, `pip` etc. pointing to
`python3`, `python3-config`, `pip3` etc., respectively, have been installed into
>  /usr/local/opt/python/libexec/bin

> You can install Python packages with
>  pip3 install <package>
>They will install into the site-package directory
>  /usr/local/lib/python3.7/site-packages

> See: https://docs.brew.sh/Homebrew-and-Python

Check that the pip3 commands are available

    $ pip3

Next, I tried

    $ pip install nhdnet

This returned the following error:
> Collecting nhdnet
>  Using cached nhdnet-0.2.0-py3-none-any.whl (20 kB)
> Requirement already satisfied: pandas in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from nhdnet) (0.25.3)
> Requirement already satisfied: requests in /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages (from nhdnet) (2.22.0)
> Collecting rtree
  > Using cached Rtree-0.9.4.tar.gz (62 kB)
    ERROR: Command errored out with exit status 1:
     command: /Library/Frameworks/Python.framework/Versions/3.8/bin/python3 -c 'import sys, setuptools, tokenize; sys.argv[0] = '"'"'/private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-install-8ok8aflg/rtree/setup.py'"'"'; __file__='"'"'/private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-install-8ok8aflg/rtree/setup.py'"'"';f=getattr(tokenize, '"'"'open'"'"', open)(__file__);code=f.read().replace('"'"'\r\n'"'"', '"'"'\n'"'"');f.close();exec(compile(code, __file__, '"'"'exec'"'"'))' egg_info --egg-base /private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-pip-egg-info-vieov9ui
         cwd: /private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-install-8ok8aflg/rtree/
    Complete output (15 lines):
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-install-8ok8aflg/rtree/setup.py", line 3, in <module>
        import rtree
      File "/private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-install-8ok8aflg/rtree/rtree/__init__.py", line 1, in <module>
        from .index import Rtree
      File "/private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-install-8ok8aflg/rtree/rtree/index.py", line 6, in <module>
        from . import core
      File "/private/var/folders/zz/khmq029s47sdmy5mfd4btz880000gn/T/pip-install-8ok8aflg/rtree/rtree/core.py", line 143, in <module>
        rt.Error_GetLastErrorNum.restype = ctypes.c_int
      File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/ctypes/__init__.py", line 386, in __getattr__
        func = self.__getitem__(name)
      File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/ctypes/__init__.py", line 391, in __getitem__
        func = self._FuncPtr((name_or_ordinal, self))
    AttributeError: dlsym(RTLD_DEFAULT, Error_GetLastErrorNum): symbol not found
    ----------------------------------------
ERROR: Command errored out with exit status 1: python setup.py egg_info Check the logs for full command output.

This error is noted by the nhdnet creators and they provide a fix here: https://pypi.org/project/nhdnet/  I followed this and typed

    $ brew install spatialindex

And then,

    $ pip install nhdnet

Success!
> Installing collected packages: rtree, nhdnet
    Running setup.py install for rtree ... done
Successfully installed nhdnet-0.2.0 rtree-0.9.4

Now, the ipynb should be able to execute the first code block.

## Notes about the lineID created by Ward

The lineID is created in the notebook 'extract_flowlines_waterbodies'. In the ReadME of that folder, Ward states:
> flowlines are identified using `lineID` from this point forward; this is a unique ID assigned to this specific run of the data extraction. These ids are NOT durable from one extraction to the next. These are used because the flowlines are cut, yet we retain the original NHDPlusID of each original segment to be able to relate it back to NHD.

The analysis with the waterbodies must cut the flowlines, so he creates new IDs. Then these IDs can be referred to in case one flow line gets split into two and they have the same NHDPlusID.

The lineIDs are created in the *flowlines.py* script, which I think comes from the nhdnet tool. lineIDs were used in the processing of the data *prepare_flowlines_waterbodies.py*. Upstream_id and downstream_id from joins was used in *find_nhd_dams.py* and *merge_waterbodies.py*. I still don't get how all these IDs relate.

## Serialize
I think this refers to the change in data structure. They create a feather file in this case.

## NABD join
Join NHD Reachcode with NABD

## June 16, 2020 update
We decided to use NHD V2 over HR because it contains COMID, so we will not have to merge HR and V2 to get the COMID. And for our purposes, we do not need the high res; moderate res is good enough for our purposes. However, the Flowlines in the V2 dataset are too large to read in as a geodataframe.

I think that if we convert the flowline feature class to a csv, it will be easier to read in. However, I am trying to figure out how to keep the geometry of the features. As of now, the features do not have the geometry, which is necessary to plot in space. But we can read in the data!!!

## June 22, 2020
The upstream count is working. I copied it from SARP 'stats.py'; however, it is counting wrong. I checked it with the data subset (small1019.csv).

I also need to figure out the plotting. The geometry is a list of coordinates in the csv. I also need to figure out how to plot by different colors based on if there is a dam present or not on a given flowline.

## July 10, 2020
Laura has written a code that walks us up and down the networks. Now, we need to test it and make sure it works on large and small basins.

We need to preprocess the dam data to get rid of duplicates. The dams will be filtered like this:
  - If the duplicates have the same storage values, we will keep the first entry and delete the others.
  - If the duplicates have different storage values, we will add the storage together and make a single entry.
  - If there is no storage, we will delete the duplicates.

The indices from Grill's paper that we are using are:
  - Degree of Fragmentation (DOF)
    - Variables needed:
      - Natural average discharge of river reach (QC_MA)
      - Natural average discharge at the barrier ()
      - Mazimum discharge range beyond which no fragmentation effects are expected (calculate a percentage?)

  - Degree of Regulation
    - Variables needed:
      - storage volume upstream of river reach (Normal or Maximum storage)
      - natural average discharge volume per year  (QC_MA)

  - Consumptive Water Use (USE)
    - Variables needed:
      - natural long-term discharge without human influences (QC_MA)
      - average long-term discharge after human abstractions and use (QA_MA or QE_MA)

## July 21, 2020
Laura's code has been tested and it works on different configurations of dams. There were two bugs associated with the
Hydroseq value/index and the ftemp == 0. Turns out that ftemp had negative values in the small test basin. Still
working on the Hydroseq bug.

I grouped the HUC 2s by major U.S. river basins as thus:
- 'California' : [18]
- 'Colorado' : [14, 15]
- 'Columbia' : [17]
- 'Great Basin' : [16]
- 'Great Lakes' : [4]
- 'Gulf Coast' : [12]
- 'Mississippi' : [5, 6, 7, 8, 10, 11]
- 'North Atlantic' : [1, 2]
- 'Red' : [9]
- 'Rio Grande' : [13]
- 'South Atlantic' : [3]

We determined that the dam duplicates all have the same storage. Thus, we will keep the first dam entry and its storage value.
We will delete the rest of the duplicates and mention it in our report. We are going to filter out all dam entries with zero
storage because the the NIDID documentation says, ' For normally dry flood control dams, the normal storage will be a zero value.'
Thus, the dams are mainly for flood control and are not affecting the river flow as much. We will keep blanks because their
storage value is unknown. Again from the NIDID documentation, 'If unknown, the value will be blank and not zero.'

I need to figure out if the script will be affected by loops in the flowlines and how that will affect our result. I also 
need to check for underground conduits. We will most likely keep those because they connect otherwise discontinuous streams.
We ARE KEEPING isolated lines because they are added to the fexit variable as not having a fragment ID. In this sense, they
are already accounted for. Also where did the discharge estimates come from in NHD.

### About discharge measurements
- EROM is only valid from 1971 - 2000
- They used USGS gage estimates of flow
- Created runoff grids using a water balance that included precip, PET, ET, and soil moisture
  - ET losses not allowed to exceed precip
- Used a regression to develop an unit runoff equation

## July 28, 2020
Two bugs were found in the code this week. There are duplicate hydrosequence values because multiple dams lie on the same flowline.
To account for this, we will only report the largest DamID of the duplicates. We will sum the storage of all the dams and add the total
number of duplicates to the number of dams upstream. The second bug was that the Fragment index is a list of values, not a list of the IDs.

We will filter out coastlines because we do not want to worry about what happens when the downstream flowline is a coastline.
We also decided to keep zero storage values, so we can turn those on and off for comparison.

We determined that we need to discuss what metrics and indices we want to include in our analysis. 

## August 11, 2020
We had a discussion about metrics for the study. We decided we would for sure use RRI and RFI to show the degree of connectivity. RFI is conceptually equivalent to RCI, so we will only use RFI. We have most of the variables needed to calculate these two metrics. Jun is checking what discharge value we want to use from NHD because there are multiple.

The GRanD database will be used to compare NABd to. 

### *NOTE:* 
When an error occurs with the ftemp variable (line 95 in bifurcate.py), it could be multiple things. I have had the following issues:
- Hydroseq is duplicated
- Negative values (from lat/long not being in the right column)
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

I also need to figure out the plotting. The geometry is a list of corrdinates in the csv. I also need to figure out how to plot by different colors based on if there is a dam present or not on a given flowline.

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

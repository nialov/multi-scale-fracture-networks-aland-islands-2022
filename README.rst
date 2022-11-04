Multi-scale fracture networks at Åland Islands - data analysis
==============================================================

This is an open-source repository that enables the reproducibility of
tables and figures in the article XXX.

Software and data
-----------------

The workflow declared in this repository requires the use of ``nix``
(https://nixos.org/) which guarantees binary reproducibility of the
software used. Consequently, the analysis declared here should be
reproducible in any Linux-machine that has ``nix`` installed.

Some data is downloaded from several public APIs:

-  Åland Islands Geta shoreline orthomosaics used in fracture digitizing
   are downloaded from ``zenodo``
   (https://zenodo.org/record/4719627/files/geta_orthomosaics.zip?download=1)
-  Glacial striations collected by the Geological Survey of Finland are
   downloaded from the ``gtkdata.gtk.fi`` WFS service
   (http://gtkdata.gtk.fi/arcgis/services/Rajapinnat/GTK_Maapera_WFS/MapServer/WFSServer?)
-  Administrative boundaries of countries are downloaded from
   ``public.opendatasoft.com``
   (https://public.opendatasoft.com/explore/dataset/world-administrative-boundaries/download/?format=geojson&timezone=Europe/Helsinki&lang=en)
-  Bedrock of Finland 1:200 000 by the Geological Survey of Finland is
   downloaded from the ``gtkdata.gtk.fi`` WFS service
   (http://gtkdata.gtk.fi/arcgis/services/Rajapinnat/GTK_Kalliopera_WFS/MapServer/WFSServer?)
-  Global shoreline data is downloaded from ``www.ngdc.noaa.gov``
   (https://www.ngdc.noaa.gov/mgg/shorelines/data/gshhg/latest/gshhg-shp-2.3.7.zip)

Rights and copyright of the downloaded data belong to the representative
organizations.

Rest of the data is included in the ``git`` repository and is the
property of the author and the Geological Survey of Finland KYT KARIKKO
-project. See folder ``./data/`` for this static data.

Installation and reproduction of tables and figures
---------------------------------------------------

Downloading of the repository:

.. code:: bash

   # Use git to download repository and associated submodules
   git clone https://github.com/nialov/multi-scale-fracture-networks-aland-islands-2022.git --recurse-submodules
   # Change directory to the repository
   cd multi-scale-fracture-networks-aland-islands-2022

With ``nix`` installed:
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   # Enter development shell (installs main software dependencies)
   nix develop
   # Install Python dependencies with poetry
   poetry install

Without ``nix`` installed:
~~~~~~~~~~~~~~~~~~~~~~~~~~

Without ``nix`` you need to have several software installed on your
system. Installation of these software will depend on the ``linux``
system you are using. The project dependencies are listed in
``./flake.nix`` as such (check the file for most up-to-date
dependencies):

.. code:: nix

   # Scroll to the below section in ./flake.nix
   packages = with pkgs; [
      pre-commit # Not required, only for development
      pandoc
      poetry-wrapped # I.e. poetry
      imagemagick
      fontconfig # Probably not required
      dos2unix # Not required
      gdal
      watchexec # Not required
      wget
      unzip
   ];

After installing the dependencies, you can try installing the ``python``
dependencies with ``poetry`` and run analyses:

.. code:: bash

   # Install Python dependencies with poetry
   poetry install

Installing without ``nix`` is not supported as the reproducibility is
compromised as the versions of software can vary and things will
invariably break at some point.

Running analyses
~~~~~~~~~~~~~~~~~

After installation:

.. code:: bash

   # If installed with nix, you need to be in nix develop -shell
   nix develop
   # Download all data and run all analyses declared in dodo.py as tasks
   # Note: this will take time. Download of data is circa 10 GB
   # and is subject to restrictions by zenodo.org and
   # fracture network analysis with fractopo of all Geta fracture trace
   # data (n=~40000) can take several minutes depending on system.
   poetry run doit
   # To run tasks in parallel (faster) add the -n
   # flag to doit with the number of cpu cores
   # Can also reduce verbosity with -v flag
   # Example with 12 cpu cores and as low verbosity as possible:
   poetry run doit -n 12 -v 0

Main tables and figures that appear in the article should be populated
in the ``outputs/final`` directory.

To run a subset of tasks defined in ``dodo.py`` you can specify the
tasks as such:

.. code:: bash

   # To create table 4
   poetry run doit -n 12 -v 0 final_tab04_azimuth_set_table
   # To create tables 4 and 5:
   poetry run doit -n 12 -v 0 final_tab04_azimuth_set_table final_tab02_data_count_table

Caveats
-------

-  ``poetry`` is used alongside ``nix``. ``poetry`` does not guarantee
   binary reproducibility but should practically guarantee that the same
   python packages are installed every time through ``poetry.lock``.
-  Some figures are created using ``QGIS 3.18``. This creation could be
   automated but has not been due to time constraints. Consequently, the
   ``QGIS``-based figures are not guaranteed to be reproducible but
   should be reasonably "recreatable" by opening the project files in
   the ``qgis/`` folder. Tasks related to ``QGIS`` are not defined when
   the environment does not match the authors (hardcoded paths).
-  ``task_final_fig02_add_index_to_drone_rasters`` requires too much
   disk space on ``GitHub Actions`` so it is disabled there. Should work
   fine locally.

.. _package-development:

Package Development: A "How-to Guide" for Developing Packages for Others to Use
================================================================================

The purpose of this page is to get your mesa package sharing as quickly as possible. The authoritative guide for python package development is through the `Python 
Packaging User Guide <https://packaging.python.org/>`_. This will take you through the entire process necessary for getting you package on the Python Package Index.

This "How-to Guide" uses GitHub to walk you through the process. However, other repositories will be able to provide similar services.


Package Development Checklist (basic): Sharing your modules in seven steps
----------------------------------------------------------------------------

**1. Take your module(s) from your ABM and make sure it is callable from Mesa in a simple, easy to understand way**
   
**2. Think about the structure of your package**

We recommend `Hitchhiker's Guide to Python <http://docs.python-guide.org/en/latest/writing/structure/>`_

**3. Using GitHub, create a new repository**

   A. Name your repository
   B. Select a license (not sure-- click the blue 'i' next to the i for a great run down of licenses) 
   C. Create a readme.md file (this contains a description of the package) see an example: `Bilateral Shapley <https://github.com/tpike3/bilateralshapley/blob/master/README.md>`_

      
**4. COMMIT a requirements.txt to the repository**

   - This can be created automatically from your python environment using the command: 
         
.. code:: bash
          
               pip freeze > requirements.txt


               #if using Anaconda install pip first
               conda install pip

. 
   - For more information on environments see the user guide: :ref:`user-guide` 

**5. COMMIT a setup.py file**

      Python Package Authority Setup `Example <https://github.com/pypa/sampleproject/blob/master/setup.py>`_
      or start with a set up file from a package you like

**6. COMMIT the module(s) or folder(s) to the git hub repository**

      Don't forgot to follow a good `structure <http://docs.python-guide.org/en/latest/writing/structure/>`_

**7. Add a page to Mesa Packages WIKI page**

      - `Build your package page <https://github.com/projectmesa/mesa/wiki>`_  
      - Edit the Mesa Packages wiki page to add your package name
   
.. toctree::
   :hidden:
   :maxdepth: 1

   Package Template  <package template.rst>	
   


   


   
   

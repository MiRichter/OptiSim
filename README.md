What is OptiSim?
================

OptiSim is a scientific simulation tool with graphic user interface written in Python / PyQt. It allows calculation of the optical behavior of single or multiple layers of thin or thick films in one dimension. The definition of each layer consists of name, thickness, complex refractive index, and, if regarded, carrier collection function.
The calculation model accounts for multiple reflections, interference effects, roughness, scattering, and gradients in optical constants. 
The simulations gives information about how much light is reflected, transmitted and also how much light is absorbed at any point within the structure.
OptiSim is particularly developed to investigate thin-film solar cells. Thus, it calculates quantum efficiency spectra, generation rate, layerwise absorption, and short circuit current and loss ratios.
However, OptiSim is designed to deal with any one-dimensional optical thin or thick layer stack issue. Its intuitive handling, fast calculation algorithms, extensive plotting options, and comprehensive structure and result treatment makes it the perfect tool for solving optical problems.

How to run?
===========

Easiest way is via Eric IDE. Just run the project file.

For execution the following site-packages are necessary:
Python 3.4.3 - PyQt 5.5.1 - Numpy 1.9.3 - Scipy 0.16.1 - Matplotlib 1.5.0 - Colorpy 0.1.0 for Python 3

What else?
==========

For detailed information see www.uni-oldenburg.de/physik/forschung/ehf/lcp/optisim/

OptiSim is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the License for more details.

Thanks to:
==========

Volker Lorrmann for first ideas, Steven Byrnes' python tmm package for giving input especially for angle dependency, Mark Knees for python package Colorpy I took some lines from, 
developer of ERIC IDE, and many more ... 

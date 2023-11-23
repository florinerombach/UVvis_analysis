Thin Film Absorbance Calculator
by Florine Rombach (CMP, University of Oxford)

This program calculates absorptance, absorbance and optionally the 
absorption coefficient of thin films/stacks from transmittance and 
reflectance measurements. The following relations are used:

Absorptance = 1 - Transmittance - Reflectance
Absorbance = - ln ( Transmittance + Reflectance )
Absorption coefficient = Absorbance / d (cm-1)

The following packages are needed to run this program:
- Gooey
- numpy
- matplotlib

Input data requirements:

- All of your transmittance and reflectance data must be saved in 
  the same input file (.csv).

- The transmittance and reflectance measurements for one sample 
  must have exactly the same name, and names should not be duplicated.

Notes:

- If all of your films have the same thickness, you can enter it 
  to calculate an absorbance coefficient.

- This calculates the absorption for the complete stack (i.e.: 
  glass/perovskite, or ITO/PTAA/perovskite) that you are
  measuring, and should be cited as such.

- The geometry of our integrating sphere is such that light scattered 
  at very wide angles can fail to be caught by the sphere. This can 
  occasionally account for some small unexpected absorption (ex. 
  below bandgap).

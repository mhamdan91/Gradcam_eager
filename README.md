# GradCAM Visualization Example
### Implementation
The code provided herein is implemented in TF1.12 and compatible with **Eager mode**.
Gradcamm visualization in tesorflow with eager execution.
## To run the code
Simply run the **visualize_cam.py** with specifying the following arguments directly in terminal.
If you would like to visualize a paritcular image, make sure to place the image in this directory */images/input/*

### Args
* '-i', '--input_image', default='sample.bmp', type=str, help= '(Full name of the input image -- default set to sample.bmp'
* '-o', '--output_image', default='sample.png', type=str,   help='Full name of output image (should be .png) -- default set to input_image.png '

### Simplist use  
This runs the cam with **sample.bmp** image located in *_/images/input/_* 
 - python3 visualize_cam.py

#### Output
This code produces an CAM image for input image in this directory */images/ouput*

##### Acknowledgements
Part of the code was adapted from:
TF session implementation.
https://github.com/adityac94/Grad_CAM_plus_plus


# Author
Muhammad K.A. Hamdan

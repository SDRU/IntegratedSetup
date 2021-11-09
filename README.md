Slowly integrating all devices at BLOG, University of Basel. 
This script controls:
    - irrigation system TESCOM ER5000
    - air flow controller Eleveflow OB1
    - thermal camera FLIR A655
    - shutter Thorlabs SH1
    
Irrigation: always on

Camera: If maximum temperature from the entire image exceeds the thresholdT, air is switched off. Otherwise the air is on and deflects the water jet.
Adaptive threshold: The program looks at maximum temperature from n samples in the past measurements. It makes and average and scales it by scaling factor. 
This value becomes the new treshold temperature.
    
Shutter: Is open for a predefined time

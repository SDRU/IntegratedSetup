Feedback-driven irrigation system. Irrigation starts only based on feedback from the thermal camera - when current temperature exceeds a threshold. Threshold is continuously adapting based on previous measurements.


This script controls:
* irrigation system TESCOM ER5000
* air flow controller Eleveflow OB1
* thermal camera FLIR A655
* shutter Thorlabs SH1
    
Irrigation: always on

Camera: If maximum temperature from the entire image exceeds the thresholdT, air is switched off. Otherwise the air is on and deflects the water jet.
Adaptive threshold: The program looks at maximum temperature from n samples in the past measurements. It makes and average and scales it by scaling factor. 
This value becomes the new treshold temperature.
    
Shutter: Is open for a predefined time

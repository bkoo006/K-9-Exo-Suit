# K-9ExoSuit

Demo video: https://www.youtube.com/watch?v=KosmdjRvXV4&ab_channel=BadrAsi

Today, the current solution for dogs with disabled or missing legs is to provide either a crutch or wheelchair for the remainder of its life. The goal of this project is to provide a more innovative solution to this issue, giving disabled dogs the chance for a more natural mode of movement. 

This project acts as a wearable prosthetic that provides support to the dog’s hind legs, as well as give real time updates to the owner about the patterns and performance exhibited by the subject. It will record these readings and recognize possible corrections for the subject’s exo-assisted movement, using it to improve the product’s performance with continued use.  

## CAD 
The CAD files were created in Autodesk Fusion 360. Files are provided under the “CAD” folder.

## Artificial Neural Network


## Servos
Dynamixel AX-12A servo motors were used as the hip and knee joints of the prosthetic model. The servo motors were programmed using the Dynamixel SDK and Raspberry Pi.

## Remote Web App
The Web Application is run through phpMyAdmin which is connected by an Apache2 web server. A SQL server database stores the data obtained by the suit and communicates with the web server to display on phpMyAdmin. 

Tutorial links are below for setting up the web server and database with Raspberry Pi 4:

Setting up Apache2:
https://www.raspberrypi.org/documentation/remote-access/web-server/apache.md

Setting up MySQL Database:
https://pimylifeup.com/raspberry-pi-mysql/

Installing PHPMyAdmin:
https://pimylifeup.com/raspberry-pi-phpmyadmin/

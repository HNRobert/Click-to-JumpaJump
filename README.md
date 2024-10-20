# Click-to-JumpaJump

 Just a click on your screen and you can decide where to jump exactly! (Using OpenCV and Raspberry Pi GPIO Control)

https://github.com/user-attachments/assets/f031f215-b5cf-4481-b5ca-7a6e7bd5b126

## Introduction

### How Exact is it:

Well, currently this is the Highest score I got using this:

![Result](https://github.com/user-attachments/assets/6b898581-5b20-4682-94c4-0988765dbf7f)

After 1000 points, it allows less error, so, even a single misclick or OpenCV error could result in failure.

And, you can set a better scale persentage (a parameter which means how many pixels the character will jump across after pressing for 0.1s) using ```sd``` command to adjust the test result and improve accuracy.

### Materials you need to achieve this:

 - A Computer (PC or Mac, use the one you are famailar with)
 - A RPi (it could be replaced by anything on which you can control a cable's voltage level output, while the code also has to be changed slightly) connected to your computer through network, meanwhile get its ip address, as well as yor personal computer's (within the same LAN).
 - Some lead (wire, any conductor), conductive sucker (or any piece of conductor which could stick on your mobile phone screen), PC817 Photo-Coupler IC, a shell to assemble the above three(optional), electric resistance (≈500Ω), light-emitting diodes(optional, it just indicates the working status of touching system) 【x1 each per auto-touch-screen set (That's gotta be cooler)】


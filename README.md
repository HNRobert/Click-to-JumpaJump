# Click-to-JumpaJump

 Just a click on your screen and you can decide where to jump exactly! (Using OpenCV and Raspberry Pi GPIO Control)

<https://github.com/user-attachments/assets/f031f215-b5cf-4481-b5ca-7a6e7bd5b126>

## Introduction

### Materials you need to achieve this

- A Computer (PC or Mac, use the one you are familiar with)
- A RPi (it could be replaced by anything on which you can control a cable's voltage level output, while the code also has to be changed slightly) connected to your computer through network, meanwhile get its ip address, as well as yor personal computer's (within the same LAN).
- Some lead (wire, any conductor, I prefer dupont lines), conductive sucker (or any piece of conductor which could stick on your mobile phone screen), PC817 Photo-Coupler IC (to isolate microcurrents), a shell to assemble the above three(optional), electric resistance (≈500Ω), light-emitting diodes(optional, it just indicates the working status of touching system) **【x1 each per auto-touch-screen set (That's gotta be cooler)】**

### How Exact is it

Well, currently this is the Highest score I got using this:

![Result](https://github.com/user-attachments/assets/6b898581-5b20-4682-94c4-0988765dbf7f)

After 1000 points, it allows less error, so, even a single mistake or OpenCV error could result in failure.

And, you can set a better scale percentage (a parameter which means how many pixels the character will jump across after pressing for 0.1s) using ```sd``` command to adjust the test result and improve accuracy.

## Assemble Tutorial

### Local computer setup

See: [Local-Control-Client Branch](https://github.com/HNRobert/Click-to-JumpaJump/tree/Local-Control-Client)

### RPi setup

See: [RPi-Controller Branch](https://github.com/HNRobert/Click-to-JumpaJump/tree/RPi-Controller)

### Peripherals

1. See [*Materials you need to achieve this*](#materials-you-need-to-achieve-this) #3
2. Assemble them. Detailed tutorial of this part can be found: [Here(Text&Graphical)](https://binux.blog/2022/08/cat-planet-bot-part-1-touch-simulation/) and [Here(bilibili video version)](https://www.bilibili.com/video/BV1Fb4y1Q78Y/?spm_id_from=333.999.0.0&vd_source=4f4fb5cd7d568ce886720291334a16b1). That's also where I found this programme feasible and got the idea. Thanks to [Roy Binux](https://github.com/binux) and [小楼童鞋想睡觉](https://space.bilibili.com/287810776).
3. Connect them to your RPi GPIO port, remember its GPIO Number. e.g. No.40 == GPIO 21.
   ![GPIO-Map](https://github.com/user-attachments/assets/bd60bfb1-797d-4e6a-a306-01843e76cbc4)
4. Stick the sucker on your mobile, make sure the mobile is placed at the center of your RPi's camera view.

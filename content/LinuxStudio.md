Title: Linux Music Studio
Date: 2016-08-20 18:00
Category: Music
Tags: music, linux, tutorial

When starting playing music with Linux, it might look scary and very complicated
due to this jungle of softwares available and you can waste a lot of time until
you find the setup that fits you the most.

This guide will try to help you having a basic setup to start having fun 
quickly.

[TOC]

# Hardware
Before starting playing, you need some different pieces of hardware, like a fast
enough computer, a soundcard with few I/Os, some MIDI controlers and of course
some music instruments!

To avoid [buffer over/under flow](https://en.wikipedia.org/wiki/Buffer_underrun)
while recording, you should have a decent machine with a good CPU. Especially
if you have few channels, it takes time to process each of them. As reference,
I'm running an **intel i5 running at 2.5GHz** and this provides good enough
performances using 44KHz sampling rate.

If you have more than one instrument, you should have a sound card with more
than one input. I recommend M-Audio devices that are available for a reasonable
price and have very good Linux compatibility. Mine is an **M-Audio Fast Track
ultra** that has an USB interface, 8 I/O channels and XLR connectors:

![Fast Track Ultra](../images/linuxStudio/fastTrackUltra.jpg)

You probably also want some MIDI controlers to start or stop recording, change
volumes on the fly, mute channels, ... You can also find some USB/MIDI
controlers for a reasonable price, I'm using a **KORG nano kontrol** that has
some knobs, sliders, buttons and support four different scenes:

![Korg nano kontrol](../images/linuxStudio/korgNanoKontrol.jpg)

At least but not last you should have some instruments. Pick up your favorites
one that you can plug into your sound card such as **synthesizers, guitares, 
microphones, ...** You can also use a MIDI keyboard to play with a software
synthesizer.

# Improve your latency
It is not mandatory to configure your system to be perfect but this will improve
your experience and avoid XRuns. This is pretty much an endless topic and is
dependent on the distribution you are using. It is not the purpose of this
article to explain everything in detail, I will probably write one dedicated to
this topic someday but here some my quick pointers:

* Use a **low latency kernel** or better, apply the **RT patch** and compile your
kernel with an higher timer frequency. 

* In case you are using an RT kernel, configure your **limits and RT 
permissions** correctly.

* Make sure also that you **share your IRQs correctly**, avoid using a mouse on
the same IRQ channel as your sound card.

If you have no idea on how to achieve this, use a dedicated Linux distribution
that does it already for you, 
[see below]({filename}LinuxStudio.md#other-notable-softwares)

# JACK sound server
For a Linux studio, I strongly recommend using
[jackd](http://www.jackaudio.org/). It provides the possibility to 
**interconnect the audio I/Os** of your different softwares with your sound 
card. It is able to provide a **time synchronization mechanism**, this is useful
if you want to syncrhonize your drum machine with a looper as explained further.
You can also configure the sample rate in order to improve the latency in the
cost of the audio quality depending on your computer performances and what you
want to achieve.

Using jackd on the command line can be a bit cumbersome, especially if you have
a lot of channels. I recommend using 
[qjacktcl](http://qjackctl.sourceforge.net/) that is a nice QT frontend. Here is
how it looks like on my Desktop:

![qjackctl](../images/linuxStudio/qjackctl.png)

# Let's start with some rythm
You will probably need some drum machine to conduct your song. My favorite
software is [hydrogen](http://www.hydrogen-music.org/). It is pretty easy to use,
is highly configurable, has a faire amount of free samples available in the
repository and can serve as **jack time master**. You can also create your sound
library if you already have some samples available. I also map some buttons of
my MIDI controler to start or stop playing and also to mute or unmute the audio
output. In case of live performance, it helps doing breaks or if you want to
play an instrument in solo.

![hydrogen](../images/linuxStudio/hydrogen.png)

# Let's start looping
If like me you don't have any musician friend and want to perform with more than
one instrument, the best way to do this is using a looper. 
[sooperlooper](http://essej.net/sooperlooper/) is the software that suits me the
best. It allows recording loops in live and can be **synchronized with a jack
time master** like hydrogen. You can map some buttons on your MIDI controler to
start recording, mute, trigger, change the volume on the fly of your loops.

Once you have a basic idea of what you wanna play, you can record a bass line,
some melodies, loop them and let yourself improvising something nice on top of
this!

![sooperlooper](../images/linuxStudio/sooperlooper.png)

# Immortalize your song
If you are happy with your performance and want to share or keep an audio 
version as a souvenir, you can start recording it. To do that, I use 
[Ardour](https://ardour.org/). This is a pretty complex software, I myself don't
event use 1% of its functionalities but can do my tasks pretty easily.

It is able to record different channels and if you are not happy with one of
your solo, you can record again single track, like in a real studio. It has the
possibility to add sound effects and do some post production like balancing your
channels, apply a compressor, ... and finally export your work into your
favorite audio format.

![ardour](../images/linuxStudio/ardour.png)

# Other notable softwares
Until here I showed the minimal set of software I use but there are a lot
available out there, here are some that worse having a look:

* [zynaddsubfx](http://zynaddsubfx.sourceforge.net/): A software synthesizer
* [jack-rack](http://jack-rack.sourceforge.net/): An audio effects stack
* [guitarix](http://guitarix.org/): Like jack-rack but more guitare players 
oriented
* [hexter](http://dssi.sourceforge.net/hexter.html): A Yamaha DX-7 emulator
* [bristol](https://sourceforge.net/projects/bristol/): A vintage keyboards
emulator
* [lingot](http://www.nongnu.org/lingot/): A guitare tuner
* [patchage](http://drobilla.net/software/patchage/): A frontend to patch your 
I/Os with jack

In case you are not a Linux beast and don't know much how to tweak your system,
there are some **Linux distributions** with everything configured and installed
for you:

* [Ubuntu studio](https://ubuntustudio.org/): Based on Ubuntu
* [kxstudio](http://kxstudio.linuxaudio.org/): Yet another Ubuntu based distro

# Conclusion
At first glance, playing music under Linux might look very complicated and can
scare out some neophytes. However, once you have found your marks and your
habits, using the jack server and some of your favorite softwares offers a lot
of flexibility! This is the Unix philosophy, different softwares that do a
single task very well!

I hope this small guide will help some of you finding your marks and wake up
some creative spirits!

Enjoy your personal Linux studio!

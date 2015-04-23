UPDATE (as of April 23rd, 2015)
===========

We have a newer version of PyResonance, now called Kinetic. Kinetic is based on Pyretic, and we have made significant changes and improvements to the code base. We will discontinue support for PyResonance; further development and support will happen in the Kinetic repository. 

More information can be found here:
https://www.kinetic.noise.gatech.edu


Resonance
===========

Resonance is an SDN control platform that advocates event-driven network control. Resonance makes networks easier to manage by automating many tasks that are currently performed by manually modifying multiple distributed device configuration files in face of various network events, where configuration files are expressed in low-level, vendor-specific CLI commands. More information on the Resonance project can be found [here](http://resonance.noise.gatech.edu/).


PyResonance
===========

PyResonance is Resonance implemented with [Pyretic](http://frenetic-lang.org/pyretic/). Pyretic provides a better programmer-friendly environment with high-level APIs, libraries, and constructs. Pyretic's composition operators (parallel and sequential) add great value for composing modular programs. 
  - **Updated (Nov.22.2013)**
    - Master branch now works with updated Pyretic master branch code.
      - It may still complain about ipaddr python module. In case you get this error, do:
        - ``sudo easy_install ipaddr``
    - Old master branch now moved to branch called "pyretic-deprecated".
  - **Getting ready**
    - Pre-configured VM with PyResonance installed (updated Nov.25.2013)
      - [32-bit VM (VirtualBox OVA file)](http://resonance.noise.gatech.edu/data/PyResonance_0.2.0_32bit.ova)
      - [64-bit VM (VirtualBox OVA file)](http://resonance.noise.gatech.edu/data/PyResonance_0.2.0_64bit.ova)
    - [Downloading PyResonance in Pyretic VM](https://github.com/Resonance-SDN/pyresonance/wiki/Downloading-PyResonance-Module-in-Pyretic-VM)
  - **Running PyResonance**
    - [Running PyResonance with existing examples](https://github.com/Resonance-SDN/pyresonance/wiki/Running-PyResonance)
    - [Step-by-step tutorial for implementing your own PyResonance task (app)](https://github.com/Resonance-SDN/pyresonance/wiki/How-to-write-a-PyResonance-Task:-Step-by-step-tutorial)

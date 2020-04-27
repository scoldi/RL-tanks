## Tanks + Flags 

Teaching a Reinforcement Learning agent play a simple "Capture the flag" game. 

The objective is rather straightforward: 

![basics](/img/readme/diag0.png)

An agent in RL is the component that is "making decisions" on what to do next, based on the "reward" that it got for the previous instances. Depending on whether the agent receives a positive or negative reward, the actions that lead to it  will be more or less likely to be taken in a similar set of circumstances (or state) in the future. The state that we pass to the agent contains information about the current situation and look like this: 

![state](/img/readme/diag1.png)

The neural network that the agent is based on has 17 input nodes (as there are 17 state values), 3 hidden layers with 120 neurons each, and 4 output nodes(as there are 4 possible direction for the agent to move). 
For now, the positive rewards are received for getting to the flag, and delivering the flag to the base, while crashing into the walls and obstacles yields a negative reward.  

![state](/img/readme/diag2.png)

1) First, I tried to train the agent in an environment without obstacles, with the flag spawning in the top half and the tank in the bottom half. The first positive outcome will have to happen pretty much by chance, since the agent does not yet associate moving to the flag with getting rewards. Because of that, it makes sense to take some decisions randomly, either during the whole course of training or only in the beginning stages. I chose the first 50 games (epochs) to have some chance of making a random move instead of the one predicted by the network, with the chance decreasing over time.  

![phase 1](/img/gifs/phase1.gif)

Then the base's location was randomized between the sides and center. The tank spawned near the base and the flag's location was randomized. The agent became delivering consistent results by the 100th epoch. 

![phase 1](/img/gifs/phase2.gif)

The next step was to add the obstacles. Using the network trained on an environment without obstacles, predictably, led to the agent crashing into obstacles on the first iterations, however, that did not seem to change over the course of training. Not using a pre-trained network, on the other hand, meant that the agent will have to stumble on the winning conditions randomly, which is unlikely with the obstacles around.

to be continued...

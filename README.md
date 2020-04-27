# Tanks + Flags 

Teaching a Reinforcement Learning agent play a simple "Capture the flag" game. 

The objective is rather straightforward: 

![basics](/img/readme/diag0.png)

An agent in RL is the component that is "making decisions" on what to do next, based on the "reward" that it got for the previous instances. Depending on whether the agent receives a positive or negative reward, the actions that lead to it  will be more or less likely to be taken in a similar set of circumstances (or state) in the future. The state that we pass to the agent contains information about the current situation and look like this: 

![state](/img/readme/diag1.png)

For now, the positive rewards are received for getting to the flag, and delivering the flag to the base, while crashing into the walls and obstacles yields a negative reward.  

![state](/img/readme/diag2.png)





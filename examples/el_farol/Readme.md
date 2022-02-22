# El Farol

This folder contains an implementation of El Farol restaurant model. Agents (simulated restaurant customers) decide whether to go to the restaurant or not based on their memory and reward from previous trials. Implications from the model have been used to explain how individual decision-making affects overall performance and fluctuation.

Besides, it demonstrates how to deploy a cognitive model (Instance-Based Learning) under the mesa environment. IBL model reflects the recency and frequency effect in decision-making with memory. Agent actively learns from the environment and updates their preference(blending value) for each decision. IBL model could be used as a substitute for an agent whose decision-making is more realistic and closer to human decision-making. 
This example has 2 versions of the model: the pure Mesa version without IBL (named as ElFarolBar), and the version with IBL that integrates with PyIBL (named as ElFarolBarIBLT). The latter version replicates the result of Kumar 2016.



## How to Run

Launch the model: Please check el_farol.ipynb for more information
Please see this [link](http://pyibl.ddmlab.com/) to install pyibl package 

## Files
* [el_farol/el_farol.ipynb](el_farol/el_farol.ipynb): Test the model and vitulization in a Jupyter notebook
* [el_farol/model.py](el_farol/model.py): Core model file.
* [flockers/agent.py](el_farol/agent.py): The agent class and also contain a cognitive model for el_farol problem. 

## Further Reading

=======
[1] Kumar, Shikhar, and Cleotilde Gonzalez. "Heterogeneity of Memory Decay and Collective Learning in the El Farol Bar Problem." (2016).

# El Farol

An implementation of El Farol restaurant model. Agents (simulated restaurant customers) try to make decision based on their memory and reward from previous trials. 
It also demonstrates how to deploy a cognitive model with the mesa environment. A cognitive modeling was used from PyIBL package to replicate research paper [1]

## How to Run

Launch the model:
```
Please check el_farol.ipynb for more information
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

## Files
* [el_farol/el_farol.ipynb](el_farol/el_farol.ipynb): Test the model and vitulization in a Jupyter notebook
* [el_farol/model.py](el_farol/model.py): Core model file.
* [flockers/agent.py](el_farol/agent.py): The agent class and also contain a cognitive model for el_farol problem. 

## Further Reading
[1] Kumar, Shikhar, and Cleotilde Gonzalez. "Heterogeneity of Memory Decay and Collective Learning in the El Farol Bar Problem." (2016).
=======

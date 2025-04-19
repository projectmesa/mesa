# Getting started
Mesa is a modular framework for building, analyzing and visualizing agent-based models.

**Agent-based models** are computer simulations involving multiple entities (the agents) acting and interacting with one another based on their programmed behavior. Agents can be used to represent living cells, animals, individual humans, even entire organizations or abstract entities. Sometimes, we may have an understanding of how the individual components of a system behave, and want to see what system-level behaviors and effects emerge from their interaction. Other times, we may have a good idea of how the system overall behaves, and want to figure out what individual behaviors explain it. Or we may want to see how to get agents to cooperate or compete most effectively. Or we may just want to build a cool toy with colorful little dots moving around.

## Tutorials
If you want to get a quick start on how to build agent based models with MESA, check the overview and tutorials:

- [Overview of the MESA library](overview): Learn about the core concepts and components of Mesa.
- [Creating Your First Model](tutorials/0_first_model): Learn how to create your first Mesa model.
- [Adding Space](tutorials/1_adding_space): Learn how to add space to your Mesa model and understand Mesa's space architecture.
- [Collecting Data](tutorials/2_collecting_data): Learn how to collect model level and agent level data with Mesa' DataCollector.
- [AgentSet](tutorials/3_agentset): Learn how to more effectively manage agents with  Mesa's AgentSet.
- [Basic Visualization](tutorials/4_visualization_basic): Learn how to build an interactive dashboard with Mesa's visualization module.
- [Dynamic Agent Visualization](tutorials/5_visualization_dynamic_agents): Learn how to dynamically represent your agents in your interactive dashboard.
- [Custom Visualization Components](tutorials/6_visualization_custom): Learn how to add custom visual components to your interactive dashboard.
- [Parameter Sweeps](tutorials/7_batch_run): Learn how to conduct parameter sweeps on multiple processors with Mesa's BatchRunner.
- [Comparing Scenarios](tutorials/8_comparing_scenarios): Think through how to analyze your parameter sweep results to find insight in your Mesa simulations.

## Examples
Mesa ships with a collection of example models. These are classic ABMs, so if you are familiar with ABMs and want to get a quick sense of how MESA works, these examples are great place to start. You can find them [here](examples).

## Further resources
To further explore Mesa and its features, we have the following resources available:

### Best practices
- [Mesa best practices](best-practices): an overview of tips and guidelines for using MESA.

### API documentation
- [Mesa API reference](apis): Detailed documentation of Mesa's classes and functions.

### Repository of models built using MESA
- [Mesa Examples repository](https://github.com/projectmesa/mesa-examples): A collection of example models demonstrating various Mesa features and modeling techniques.

### Migration guide
- [Mesa 3.0 Migration guide](migration_guide): If you're upgrading from an earlier version of Mesa, this guide will help you navigate the changes in Mesa 3.0.

### Source Ccode and development
- [Mesa GitHub repository](https://github.com/projectmesa/mesa): Access the full source code of Mesa, contribute to its development, or report issues.
- [Mesa release notes](https://github.com/projectmesa/mesa/releases): View the detailed changelog of Mesa, including all past releases and their features.

### Community and support
- [Mesa GitHub Discussions](https://github.com/projectmesa/mesa/discussions): Join discussions, ask questions, and connect with other Mesa users.
- [Matrix Chat](https://matrix.to/#/#project-mesa:matrix.org): Real-time chat for quick questions and community interaction.

Enjoy modelling with Mesa, and feel free to reach out!





```{toctree}
:hidden: true
:maxdepth: 7

Overview <overview>
Creating Your First Model <tutorials/0_first_model>
Adding Space <tutorials/1_adding_space>
Collecting Data <tutorials/2_collecting_data>
AgentSet <tutorials/3_agentset>
Basic Visualization <tutorials/4_visualization_basic>
Dynamic Agent Visualization <tutorials/5_visualization_dynamic_agents>
Custom Visualization Components <tutorials/6_visualization_custom>
Parameter Sweeps <tutorials/7_batch_run>
Comparing Scenarios <tutorials/8_comparing_scenarios>
Best Practices <best-practices>


```

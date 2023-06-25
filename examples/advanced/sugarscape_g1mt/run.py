import sys

import matplotlib.pyplot as plt
import mesa
import networkx as nx
import pandas as pd
from sugarscape_g1mt.model import SugarscapeG1mt
from sugarscape_g1mt.server import server


# Analysis
def assess_results(results, single_agent):
    # Make dataframe of results
    results_df = pd.DataFrame(results)
    # Plot and show  mean price
    plt.scatter(results_df["Step"], results_df["Price"], s=0.75)
    plt.show()

    if single_agent is not None:
        plt.plot(results_df["Step"], results_df["Trader"])
        plt.show()
    else:
        n = max(results_df["RunId"])
        # Plot number of Traders
        for i in range(n):
            results_explore = results_df[results_df["RunId"] == i]
            plt.plot(results_explore["Step"], results_explore["Trader"])
        plt.show()

    if single_agent is not None:
        results_df = single_agent

    # Show Trade Networks
    #  create graph object
    print("Making Network")
    G = nx.Graph()
    trade = results_df.dropna(subset=["Trade Network"])
    # add agent keys to make initial node set
    G.add_nodes_from(list(trade["AgentID"].unique()))

    # create edge list
    for idx, row in trade.iterrows():
        if len(row["Trade Network"]) > 0:
            for agent in row["Trade Network"]:
                G.add_edge(row["AgentID"], agent)

    # Get Basic Network Statistics
    print(f"Node Connectivity {nx.node_connectivity(G)}")
    print(f"Average Clustering {nx.average_clustering(G)}")
    print(f"Global Efficiency {nx.global_efficiency(G)}")

    # Plot histogram of degree distribution
    degree_sequence = sorted((d for n, d in G.degree()), reverse=True)
    degree_sequence = [d for n, d in G.degree()]
    plt.hist(degree_sequence)
    plt.show()

    # Plot network
    nx.draw(G)
    plt.show()


# Run the model

args = sys.argv[1:]


if args[0] == "runserver":
    server.launch()

elif "s" in args[0] or "Single" in args[0]:
    print("Running Single Model")
    # instantiate the model
    model = SugarscapeG1mt()
    # run the model
    model.run_model()
    # Get results
    model_results = model.datacollector.get_model_vars_dataframe()
    # Convert to make similar to batch_run_results
    model_results["Step"] = model_results.index
    agent_results = model.datacollector.get_agent_vars_dataframe()
    agent_results = agent_results.reset_index()
    # assess the results
    assess_results(model_results, agent_results)

else:
    print("Conducting a Batch Run")
    # Batch Run
    params = {
        "width": 50,
        "height": 50,
        "vision_min": range(1, 4),
        "metabolism_max": [2, 3, 4, 5],
    }

    results_batch = mesa.batch_run(
        SugarscapeG1mt,
        parameters=params,
        iterations=1,
        number_processes=1,
        data_collection_period=1,
        display_progress=True,
    )

    assess_results(results_batch, None)

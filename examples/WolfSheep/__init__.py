from WolfSheep import WolfSheepPredation
from WolfSheepVisualization import WolfSheepVisualization

if __name__ == "__main__":
    model = WolfSheepPredation(grass=True)
    model.run_model()
    # viz = WolfSheepVisualization(model)
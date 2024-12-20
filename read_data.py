import pandas as pd

class HLV_data():
    def __init__(self):
        self.filename = "./dices-dataset/350/diverse_safety_adversarial_dialog_350.csv"
        self.df = pd.read_csv(self.filename)

if __name__ == "__main__":
    hlv = HLV_data()
    print(hlv.df.drop_duplicates(subset="rater_id"))
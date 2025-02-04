import js2py
import os 
import csv

def find_variation_words():
    '''
    This function extracts the words from the dataset which have been annotated by all annotators.
    
    @returns 
        full: list with words that have been annotated by every annotator
        missing: list with words that have not been annotated by every annotator
    '''
    # open stats
    with open("./dwug_en/plots/opt/judgments/stats.js", encoding = "utf-8") as f:
        stats = js2py.eval_js(f.read())

    # find words that are annotated by every annotator
    full = []
    missing = []
    for element in stats:
        full_annotations = True
        for i in range(13):
            if element[f"judgments_annotator{i}"] == '0':
                full_annotations = False
        
        if full_annotations:
            full.append(element["lemma"])
        else:
            missing.append(element["lemma"])

    print(f"\n{len(full)} full annotations: {full}\n")
    print(f"{len(missing)} missing annotations: {missing}\n")

    return full

def compute_avg_num_uses():
    '''
    This function computes the average number of uses per word.

    @returns avg: average number of uses per word
    '''
    num_uses = 0
    words = os.listdir("./dwug_en/data/")
    for path in words:
        with open(f"./dwug_en/data/{path}/uses.csv", encoding="utf-8") as f:
            reader = list(csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE,strict=True))
            num_uses += len(reader)-1

    avg = num_uses/len(words)
    print(f"\nAverage number of uses per word: {avg}\n")
    return avg

def num_annotations(include = []):
    '''
    This function computes the number of annotations in the dataset.

    @param include: list of words to include in the count
    @returns num_annotations: number of annotations (only the included words)
    '''
    num_annotations = 0
    with open("./dwug_en/plots/opt/judgments/data_joint.js", encoding = "utf-8") as f:
        annotations = js2py.eval_js(f.read())

    if include == []:
        num_annotations = len(annotations)
        print(f"\nTotal number of annotations: {num_annotations}\n")
    else:        
        for annotation in annotations:
            if annotation["lemma"] in include:
                num_annotations += 1
        print(f"\nNumber of annotations for visualized words: {num_annotations}\n")

    return num_annotations

if __name__ == "__main__":
    variation_words = find_variation_words()
    #compute_avg_num_uses()
    num_annotations(include = variation_words)


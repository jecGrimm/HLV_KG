import js2py

with open("./dwug_en/plots/opt/judgments/stats.js", encoding = "utf-8") as f:
    stats = js2py.eval_js(f.read())
    #print("stats:", stats)

full = []
missing = []
for element in stats:
    full_annotations = True
    for i in range(13):
        # print(f"judgments_annotator{i}")
        # print(element[f"judgments_annotator{i}"])
        if element[f"judgments_annotator{i}"] == '0':
            full_annotations = False
    
    if full_annotations:
        full.append(element["lemma"])
    else:
        missing.append(element["lemma"])

if __name__ == "__main__":
    print(f"{len(full)} full annotations: {full}")
    print(f"{len(missing)} missing annotations: {missing}")
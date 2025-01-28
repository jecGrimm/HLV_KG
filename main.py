from create_kg import create_kg
from visualize_kg import inspect_instance, create_annotation_pos, get_colors, create_full_annotation_vis, create_single_annotator_vis
import rdflib
from tqdm import tqdm 
from query_kg import category_stats, annotations_per_annotator, filter_variation, get_pos_tags
from collections import defaultdict

# Create a Graph
#g = create_kg()

g = rdflib.Graph()
result = g.parse("./graphs/test_dwug_en.ttl", format='turtle').serialize(format="turtle")
    
# Visualize
# Instance level
no_variation_pair = ["Circle_fic_2007_52477.txt-270-44", "circled_fic_1840_7164.txt-175-23"]
high_variation_pair = ["circled_mag_1856_590750.txt-21-18","circling_fic_1849_7230.txt-2441-6"]
inspect_instance(g, no_variation_pair)
inspect_instance(g, high_variation_pair)

# Full visualization 
pos = create_annotation_pos(g)

for color_mode in ["distinct", "range"]:
    color_dict = get_colors(g, color_mode)
    create_full_annotation_vis(g, pos, color_dict, color_mode)

    # Annotator visualization 
    for i in tqdm(range(13), desc="Creating annotator visualizations"):
        create_single_annotator_vis(g, f"annotator{i}", pos, color_dict, color_mode)

        # only generate once
        if color_mode == "distinct":
            annotations_per_annotator(g, annotator=f"annotator{i}") # get annotated sentences per annotator

# Query
category_stats(g) # count label frequencies
filter_variation(g, start = 1, end=1) # get no variation   
filter_variation(g, start = 2) # get high variation

get_pos_tags(g) # all pos tags in the dataset

"""
Models live in ./catalog/{species}/{model_name}.yaml.

For a given species, this should create the yaml file and fill in the
relevant metadata.

Usage: python convert_models.py [species]
"""

import msprime
import stdpopsim
import demes
import sys, os

species = sys.argv[1]

models = stdpopsim.get_species(species).demographic_models

if len(models) == 0:
    print("No demographic models found for", species)

for model in models:
    b = model.model.to_demes().asdict()
    if b["time_units"] != "generations":
        # demes only takes generation time as a top level
        # field if time units aren't gens
        b["generation_time"] = model.generation_time

    # descriptions have annoying line breaks and added spaces from stdpopsim
    desc = " ".join([_.strip() for _ in model.long_description.strip().splitlines()])
    b["description"] = desc

    # store extra data in metadata
    citations = []
    for c in model.citations:
        citations.append(
            {
                "doi": c.doi,
                "author": c.author,
                "year": c.year,
                "reasons": c.reasons,
            }
        )
    b["metadata"] = {
        "id": model.id,
        "description": model.description,
        "citations": citations,
        "mutation_rate": model.mutation_rate,
    }
    if b["time_units"] == "generations":
        # if time units are generations, we still may have generation times
        # that are given in the model -- put them in metadata
        b["metadata"]["generation_time"] = model.generation_time

    g = demes.Builder.fromdict(b).resolve()

    fpath = f"./catalog/{species}/"
    if not os.path.exists(fpath):
        os.mkdir(fpath)
    fname = os.path.join(fpath, f"{model.id}.yml")
    # output model
    demes.dump(g, fname)

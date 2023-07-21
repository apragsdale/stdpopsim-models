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
    # time units (I believe) are typically (always?) in years...
    # so we need to manually adjust things
    assert b["time_units"] == "generations"
    b["time_units"] = "years"
    gen = model.generation_time
    b["generation_time"] = gen

    # we go through and adjust all times
    # first with demes
    for i, d in enumerate(b["demes"]):
        if "start_time" in d:
            d["start_time"] *= gen
        for j, e in enumerate(d["epochs"]):
            if "start_time" in e:
                e["start_time"] *= gen
            if "end_time" in e:
                e["end_time"] *= gen
            d["epochs"][j] = e
        b["demes"][i] = d
    # then with migrations
    for i, m in enumerate(b["migrations"]):
        if "start_time" in m:
            m["start_time"] *= gen
        if "end_time" in m:
            m["end_time"] *= gen
        b["migrations"][i] = m
    # then with pulses
    for i, p in enumerate(b["pulses"]):
        p["time"] *= gen
        b["pulses"][i] = p

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

    g = demes.Builder.fromdict(b).resolve()

    fpath = f"./catalog/{species}/"
    if not os.path.exists(fpath):
        os.mkdir(fpath)
    fname = os.path.join(fpath, f"{model.id}.yml")
    # output model
    if os.path.exists(fname):
        # protect models that we may have needed to manually fix
        print(fname, "already exists - not overwriting")
    else:
        demes.dump(g, fname)

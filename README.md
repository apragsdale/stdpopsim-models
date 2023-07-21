# stdpopsim-models

Requires `stdpopsim`, `msprime`, and `demes`.

Models for a given species (e.g., humans) can be constructed by
```
python convert_models.py HomSap
```

All implemented models from `stdpopsim` are then stored in `demes` format in
`./catalog/HomSap/`

We can run this script on all species in the catalog within python
(this is a bit ugly):
```python
import stdpopsim
import os
for species in stdpopsim.species.all_species():
    os.system(f"python convert_models.py {species.id}")
"""

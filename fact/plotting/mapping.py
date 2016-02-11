import pkg_resources as res
import pandas as pd
import numpy as np

__bias_to_trigger_patch_map = None

def bias_to_trigger_patch_map():
    global __bias_to_trigger_patch_map
    if __bias_to_trigger_patch_map is None:
        mapfile = res.resource_filename("fact", "resources/FACTmap111030.txt")

        FACTmap = pd.DataFrame(np.genfromtxt(
            mapfile,
            skip_header=14, 
            names=True))

        FACTmap.sort_values("hardID", inplace=True)
        FACTmap["bias_channel"] = FACTmap["HV_B"].astype(
            int) * 32 + FACTmap["HV_C"].astype(int)
        FACTmap["hardID"] = FACTmap["hardID"].astype(int)
        FACTmap["softID"] = FACTmap["softID"].astype(int)
        FACTmap["chid"] = np.arange(len(FACTmap))
        FACTmap["cont_patch_id"] = FACTmap["chid"] // 9

        _, idx = np.unique(FACTmap.bias_channel.values, return_index=True)
        __bias_to_trigger_patch_map = FACTmap.bias_channel.values[np.sort(idx)]

    return __bias_to_trigger_patch_map

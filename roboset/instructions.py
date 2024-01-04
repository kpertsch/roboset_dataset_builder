

ROBOSET_INSTRUCT_MAPPINGS = {
    'slide_open_drawer': "Open the drawer.",
    'pick_butter': "Pick up the butter.",
    'place_butter': "Place the butter on the board.",
    'slide_close_drawer': "Close the drawer.",
    'clean_kitchen_slide_close_drawer': "Close the drawer.",
    'pick_towel': "Pick up the towel.",
    'pick_bowl': "Pick up the bowl.",
    'slide_in_bowl': "Put the bowl in the oven.",
    'open_oven': "Open the oven.",
    'close_oven': "Close the oven.",
    'place_lid': "Place the lid on the board.",
    'pick_tea': "Get a tea bag.",
    'place_tea': "Put the tea in the cup.",
    'pick_lid': "Open the lid of the tea container.",
    'cap_lid': "Put the lid on the tea container.",
    'plunge_toaster': "Turn on the toaster.",
    'pick_toast': "Pick up the toast.",
    'serve_soup_place_bowl': "Put the bowl on the board.",
    'pick_cup': "Pick up the cup.",
    'place_cup': "Place the cup in the drawer.",
}


def path2instruct(file_path):
    for key in ROBOSET_INSTRUCT_MAPPINGS:
        if key in file_path:
            return ROBOSET_INSTRUCT_MAPPINGS[key]
    raise ValueError("No matching instruction!")




ROBOSET_INSTRUCT_MAPPINGS = {
    # teleop data
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

    # kinesthetic data
    'pick_banana_place_in_mug': "Pick Banana and place it in mug.",
    'pick_banana_place_in_strainer': "Pick Banana and place it in strainer.",
    'pick_banana_from_plate_place_on_table': "Pick banana from plate and place on table.",
    'pick_banana_from_toaster_place_on_table': "Pick banana from oven and place on table.",
    'pick_banana_place_on_plate': "Pick banana from table and place on plate.",
    'pick_banana_place_on_toaster': "Pick banana from table and place on oven.",
    'pick_ketchup_place_in_strainer': "Pick Ketchup from the table and place it in strainer.",
    'pick_ketchup_place_in_toaster': "Pick Ketchup from the table and place in oven.",
    'pick_ketchup_from_strainer_place_on_table': "Pick ketchup from strainer and place it on the table",
    'pick_ketchup_from_plate_place_on_table': "Pick ketchup from plate and place it on table.",
    'pick_ketchup_from_toaster_place_on_table': "Pick Ketchup from oven and place it on table.",
    'pick_ketchup_place_on_plate': "Pick ketchup from table and place on plate.",
    'pick_ketchup_place_on_toaster': "Pick ketchup from table and place on oven.",
    'drag_mug_backward': "Drag mug backwards.",
    'drag_mug_forward': "Drag mug forwards.",
    'drag_mug_from_left_to_right': "Drag mug left to right.",
    'drag_mug_from_right_to_left': "Drag mug right to left.",
    'drag_strainer_backward': "Drag strainer backwards.",
    'drag_strainer_forward': "Drag strainer forwards.",
    'drag_strainer_left_to_right': "Drag strainer left to right.",
    'drag_strainer_right_to_left': "Drag strainer right to left.",
    'flap_open_toaster_oven': "Flap open oven.",
    'flap_close_toaster_oven': "Flap close oven."
}


def path2instruct(file_path):
    for key in ROBOSET_INSTRUCT_MAPPINGS:
        if key in file_path:
            return ROBOSET_INSTRUCT_MAPPINGS[key]
    raise ValueError("No matching instruction!")


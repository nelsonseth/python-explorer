
# import dash_mantine_components as dmc

# # local
# from .layout_utils import comp_id, get_package_buttons, get_button_stack

# # the nightmare that is figuring out relative imports
# import sys
# from pathlib import Path
# sys.path.append(Path(__file__).parent.parent)

# # utils is two levels up
# from utils.packagelist import all_packages

# package_buttons = get_package_buttons(all_packages)


# accordian_panel_style = {
#     'height':'60vh',
#     'max-height':'60vh',
#     'width':'100%',
#     'margin':'auto',
#     'overflow':'auto',
# }


# # panel_dict = {
# #     'standard':'Standard Modules (3.10)',
# #     'common':'Common Data Libraries',
# #     'app':'This app is built with:',
# # }

# panel_dict = {
#     'standard':'Standard Modules (3.10)',
#     'site':'Site-Package Libraries',
# }

# def drawer_content(panel_dict):
#     groups = list(panel_dict.keys())
    
#     itemlist = []
#     for g in groups:
#         itemlist.append(
#             dmc.AccordionItem(
#                 [
#                     dmc.AccordionControl(panel_dict[g]),
#                     dmc.AccordionPanel(
#                         dmc.Paper(
#                             children=[
#                                 get_button_stack(
#                                     package_buttons,
#                                     group=g,
#                                 )
#                             ],
#                             style=accordian_panel_style,
#                         )
#                     )
#                 ],
#                 value=g,   
#             )
#         )
    
#     return dmc.Accordion(itemlist)


# drawer = dmc.Drawer(
#     drawer_content(panel_dict),
#     id=comp_id('drawer', 'drawer', 0),
#     title='Choose an item to explore.',
#     closeOnClickOutside=True,
#     closeOnEscape=True,
#     size='25vw',
#     style={
#         'height':'100vh',
#         'overflow':'hidden',
#         'margin':'auto',
#     }
# )

import copy
from aiogram.utils.callback_data import CallbackData

br = '\n'

show_menu = CallbackData('show_menu', 'menu_name')
base_markup_menu = CallbackData('base_markup_menu',
    'id',
    'fav',
    'view',
    'query',
    'menu',
    )

get_by_id_call_menu = copy.deepcopy(base_markup_menu)
get_by_id_call_menu.prefix = 'get_dish'

edit_fav_by_id_call_menu = copy.deepcopy(base_markup_menu)
edit_fav_by_id_call_menu.prefix = 'edit_fav'




filters = {
    'favorites': 'favorites',
    'top-day': 'top-day',
    'category': 'c=',
}

call_filters = {
    'home': 'home',
    'countries': 'countries',
    'categories': 'categories',

}

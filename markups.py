from aiogram.utils.callback_data import CallbackData

show_menu = CallbackData('show_menu', 'menu_name')
show_by_filter_call_menu = CallbackData('show_by_filter', 'filter_name', 'value')
get_by_id_call_menu = CallbackData('get_by_id', 'id', 'view')

edit_fav_by_id_call_menu = CallbackData('edit_fav', 'id', 'is_add')



filters = {
    'favourites': 'favourites',
    'top-day': 'top-day',
    'category': 'c=',
}



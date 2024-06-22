from app.models.show_model import Show
from app.views.show_view import display_show_info

def get_show_info(weekend_number, host_name_and_stage, date):
    show = Show(weekend_number, host_name_and_stage, date)
    return display_show_info(show)

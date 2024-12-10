from .mhwp_info import handle_update_personal_info
from .mhwp_schedule import *
from .mhwp_appointment import *
from .mhwp_view_schedule import *   
from .mhwp_availability import *
# Add other module imports here

__all__ = ['handle_update_personal_info', 'handle_set_schedule', 'setup_mhwp_schedule', 'setup_mhwp_schedule_template', 
           'update_mhwp_schedules', 'generate_time_slots', 'handle_view_schedule', 'handle_modify_availibility', 'handle_manage_appointments']
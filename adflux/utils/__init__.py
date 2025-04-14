"""
Módulo de utilidades para AdFlux.

Este módulo proporciona funciones y clases de utilidad que pueden ser
utilizadas en diferentes partes de la aplicación.
"""

from .date_utils import (
    format_date,
    parse_date,
    get_date_range,
    get_current_date,
    get_current_datetime,
    get_date_diff,
    get_date_add,
    get_date_subtract,
    get_first_day_of_month,
    get_last_day_of_month,
    get_first_day_of_week,
    get_last_day_of_week,
)

from .string_utils import (
    slugify,
    truncate,
    strip_html,
    random_string,
    mask_email,
    mask_phone,
    format_currency,
    format_number,
    format_percentage,
)

from .dict_utils import (
    merge_dicts,
    flatten_dict,
    unflatten_dict,
    filter_dict,
    get_nested_value,
    set_nested_value,
)

from .list_utils import (
    chunk_list,
    flatten_list,
    unique_list,
    sort_list_by_key,
    filter_list_by_key,
    group_by,
)

from .file_utils import (
    get_file_extension,
    get_file_size,
    get_file_mime_type,
    is_valid_image,
    is_valid_document,
    generate_unique_filename,
)

from .decorators import (
    log_execution_time,
    retry,
    cache_result,
    validate_args,
    require_auth,
    rate_limit,
    handle_exceptions,
)

__all__ = [
    # Date utils
    'format_date',
    'parse_date',
    'get_date_range',
    'get_current_date',
    'get_current_datetime',
    'get_date_diff',
    'get_date_add',
    'get_date_subtract',
    'get_first_day_of_month',
    'get_last_day_of_month',
    'get_first_day_of_week',
    'get_last_day_of_week',
    
    # String utils
    'slugify',
    'truncate',
    'strip_html',
    'random_string',
    'mask_email',
    'mask_phone',
    'format_currency',
    'format_number',
    'format_percentage',
    
    # Dict utils
    'merge_dicts',
    'flatten_dict',
    'unflatten_dict',
    'filter_dict',
    'get_nested_value',
    'set_nested_value',
    
    # List utils
    'chunk_list',
    'flatten_list',
    'unique_list',
    'sort_list_by_key',
    'filter_list_by_key',
    'group_by',
    
    # File utils
    'get_file_extension',
    'get_file_size',
    'get_file_mime_type',
    'is_valid_image',
    'is_valid_document',
    'generate_unique_filename',
    
    # Decorators
    'log_execution_time',
    'retry',
    'cache_result',
    'validate_args',
    'require_auth',
    'rate_limit',
    'handle_exceptions',
]

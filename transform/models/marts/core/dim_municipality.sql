select municipality, province, is_capital
from {{ ref('municipalities') }}

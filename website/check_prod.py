import os
is_prod = not ("IS_DEV" in os.environ and os.environ["IS_DEV"] == "yes")
import os
is_prod = "IS_PROD" in os.environ and os.environ["IS_PROD"] == "yes"
print(str(is_prod)*100)
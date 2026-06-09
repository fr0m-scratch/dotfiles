# claude-ip-guard — optional geofence list (EXAMPLE)
# ---------------------------------------------------
# Copy this to  ~/.config/claude-ip-guard/blocked-countries.sh  and edit.
# When this file is absent or the array is empty, the IP guard only LOGS your
# location and never blocks. Populate it only if you intentionally want to
# refuse running Claude from certain ISO-3166 alpha-2 country codes.
#
#   install:  mkdir -p ~/.config/claude-ip-guard
#             cp claude/scripts/blocked-countries.example.sh \
#                ~/.config/claude-ip-guard/blocked-countries.sh
#
# Example (uncomment + edit):
# BLOCKED_COUNTRIES=("KP" "IR")
BLOCKED_COUNTRIES=()

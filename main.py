import whole_foods_bot as wfb
import json

# load the credentials
credentials = json.load(open('credentials.json'))

# create the drivers
driver = wfb.create_driver()

# go to the "slots" page
driver = wfb.go_delivery_page(driver, credentials)

# check the slots
wfb.loop_slot_check(driver, credentials)



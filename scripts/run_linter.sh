#!/bin/bash

export FLASK_APP_ENV=test
pylint scripts/ philips_hue_integration_example/ jira_integration_example/ --disable=C0116,E1101,R0903,C0115,C0103,C0301,C0114,W0621,W0511,E0611,R0801,R0914,R0915